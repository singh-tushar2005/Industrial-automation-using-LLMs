"""Visitor-based extraction of industrial semantic relationships."""

import re

try:
    from semantic.relationships import Relationship
    from semantic.visitor import ASTVisitor
    from semantic.context.test_detector import TestDetector
except ModuleNotFoundError:
    from relationships import Relationship
    from visitor import ASTVisitor
    from context.test_detector import TestDetector


class RelationshipExtractor(ASTVisitor):
    """Extract transformation-oriented behavior relationships from an AST.

    The extractor is a semantic layer above classification. It reuses the
    existing visitor infrastructure and consumes classifier/type outputs as
    context. It does not print and does not build a full graph yet; it returns
    relationship edges that are compatible with future graph construction.
    """

    def __init__(self, classification_report=None, type_report=None, context=None, test_detector=None):
        self.classification_report = classification_report or {}
        self.type_report = type_report or {}
        self.context = context
        self.test_detector = test_detector or TestDetector()
        self.relationships = []
        self.condition_stack = []
        self.case_stack = []
        self.current_configuration = None
        self.current_resource = None
        self.current_task = None
        self.current_program = None
        self.current_unit_kind = None
        self.current_unit_name = None
        self.case_selector = None
        self.output_variables = set()
        self.bool_output_variables = set()
        self.memory_mapped_outputs = set()
        self._condition_role_examples = []  # DIAGNOSTIC: Phase A condition roles
        self._filtered_r1_signals = []      # DIAGNOSTIC: R1 filtering

    def extract(self, ast):
        """Run relationship extraction and return structured results."""

        self.test_detector.detect(ast)
        self.visit(ast)
        return self.get_results()

    def get_condition_role_examples(self):
        """Return collected condition role classification examples."""
        return self._condition_role_examples

    def get_filtered_r1_signals(self):
        """Return signals filtered by the R1 edge-worthiness check."""
        return self._filtered_r1_signals

    def get_results(self):
        """Return relationship data and summary counts."""

        relationship_data = [relationship.to_dict() for relationship in self.relationships]
        relation_counts = {}

        for relationship in self.relationships:
            relation_counts[relationship.relation] = (
                relation_counts.get(relationship.relation, 0) + 1
            )

        # Segregate by semantic_scope
        industrial = [r for r in self.relationships if r.metadata.get("semantic_scope") == "INDUSTRIAL"]
        test = [r for r in self.relationships if r.metadata.get("semantic_scope") == "TEST"]
        industrial_data = [r.to_dict() for r in industrial]
        test_data = [r.to_dict() for r in test]
        industrial_counts = {}
        for r in industrial:
            industrial_counts[r.relation] = industrial_counts.get(r.relation, 0) + 1
        test_counts = {}
        for r in test:
            test_counts[r.relation] = test_counts.get(r.relation, 0) + 1

        return {
            "relationships": relationship_data,
            "relationship_count": len(relationship_data),
            "relation_counts": dict(sorted(relation_counts.items())),
            "sources": sorted({item["source"] for item in relationship_data}),
            "targets": sorted({item["target"] for item in relationship_data}),
            "interpretation_summary": self.build_interpretation_summary(),
            "industrial_relationships": industrial_data,
            "industrial_relationship_count": len(industrial_data),
            "industrial_relation_counts": dict(sorted(industrial_counts.items())),
            "test_relationships": test_data,
            "test_relationship_count": len(test_data),
            "test_relation_counts": dict(sorted(test_counts.items())),
        }

    def add_relationship(self, source, relation, target, metadata=None):
        """Add one semantic edge if it has not already been recorded."""

        if source == target:
            return

        # Determine semantic scope: if either end is test-related, mark as TEST
        semantic_scope = "INDUSTRIAL"
        if self.is_test_harness_entity(source) or self.is_test_harness_entity(target):
            semantic_scope = "TEST"

        metadata = metadata or {}
        metadata["semantic_scope"] = semantic_scope

        relationship = Relationship(source, relation, target, metadata)

        for existing in self.relationships:
            if existing.to_dict() == relationship.to_dict():
                return

        self.relationships.append(relationship)

    # ------------------------------------------------------------------
    # Visitor traversal
    # ------------------------------------------------------------------

    def visit_ProgramNode(self, node):
        self.visit(node.body)

    def visit_CompilationUnitNode(self, node):
        old_program = self.current_program
        old_unit_kind = self.current_unit_kind
        old_unit_name = self.current_unit_name
        self.current_unit_kind = node.kind
        self.current_unit_name = node.name
        if node.kind == "PROGRAM":
            self.current_program = node.name
        for var_block in node.var_blocks or []:
            self.visit(var_block)
        self.visit(node.body)
        self.current_program = old_program
        self.current_unit_kind = old_unit_kind
        self.current_unit_name = old_unit_name

    def visit_BlockNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_IfStatementNode(self, node):
        # DIAGNOSTIC: Phase A condition role classification
        roles = self.classify_condition_roles(node.condition)
        self._condition_role_examples.append({
            "condition_text": self.describe_expression(node.condition),
            "roles": roles,
            "unit_name": self.current_unit_name,
        })

        context = self.condition_context(node.condition)
        self.condition_stack.append(context)
        self.visit(node.condition)
        self.visit(node.then_body)

        for elsif_condition, elsif_body in node.elsif_branches:
            # Pop the parent condition, push the elsif condition, then restore
            self.condition_stack.pop()
            elsif_context = self.condition_context(elsif_condition)
            self.condition_stack.append(elsif_context)
            self.visit(elsif_condition)
            self.visit(elsif_body)
            self.condition_stack.pop()
            self.condition_stack.append(context)

        if node.else_body is not None:
            # Clear the condition stack for the else branch to avoid
            # attributing parent IF signals to else assignments.
            self.condition_stack.pop()
            self.visit(node.else_body)
            self.condition_stack.append(context)

        self.condition_stack.pop()

    def visit_CaseStatementNode(self, node):
        selector = self.describe_expression(node.selector)
        self.case_stack.append(selector)
        self.case_selector = selector
        self.visit(node.selector)

        previous_branch = None
        for branch in node.branches:
            current_branch = self.describe_expression(branch.match_value)

            if previous_branch is not None:
                self.add_relationship(
                    previous_branch,
                    "sequences",
                    current_branch,
                    {
                        "selector": selector,
                        "reason": "CASE branch order represents stateful sequencing",
                        "source_kind": "state",
                        "target_kind": "state",
                    },
                )

            # Detect state transitions
            next_state = self.extract_state_assignment(branch.body, selector)
            if next_state is not None:
                self.add_relationship(
                    current_branch,
                    "transitions_to",
                    next_state,
                    {
                        "selector": selector,
                        "reason": "CASE branch assigns next state to selector",
                        "source_kind": "state",
                        "target_kind": "state",
                    },
                )

            previous_branch = current_branch
            self.visit(branch)

        if node.else_body is not None:
            self.visit(node.else_body)

        self.case_selector = None
        self.case_stack.pop()

    def visit_CaseBranchNode(self, node):
        self.visit(node.match_value)
        self.visit(node.body)

    def visit_AssignmentNode(self, node):
        target = self.describe_expression(node.target)
        value = self.describe_expression(node.value)

        for context in self.condition_stack:
            self.emit_condition_relationships(context, target, value, node)

        if self.case_stack:
            self.add_relationship(
                self.case_stack[-1],
                "sequences",
                target,
                {
                    "assignment": f"{target} := {value}",
                    "reason": "CASE-selected state controls assignment",
                    "source_kind": "state",
                    "target_kind": self.infer_target_kind(target),
                },
            )

        self.visit(node.target)
        self.visit(node.value)

    def visit_FunctionBlockCallNode(self, node):
        fb_name = node.name
        fb_upper = fb_name.upper()
        argument_map = {
            argument.name: self.describe_expression(argument.value) for argument in node.arguments
        }

        if "TIMER" in fb_upper or fb_upper.startswith(("TON", "TOF", "TP")):
            input_signal = argument_map.get("IN", "<input>")
            if not self.is_literal_value(input_signal):
                self.add_relationship(
                    input_signal,
                    "triggers",
                    fb_name,
                    {
                        "function_block": fb_name,
                        "kind": "timer",
                        "reason": "timer input starts time-dependent behavior",
                        "source_kind": "signal",
                        "target_kind": "timer",
                    },
                )

            preset_time = argument_map.get("PT", "<preset_time>")
            if not self.is_literal_value(preset_time):
                self.add_relationship(
                    fb_name,
                    "depends_on",
                    preset_time,
                    {
                        "function_block": fb_name,
                        "kind": "timer",
                        "reason": "timer behavior depends on preset time",
                        "source_kind": "timer",
                        "target_kind": "timer",
                    },
                )

            # TIMER -> STATE_TRANSITION
            if self.case_selector and not self.is_literal_value(fb_name):
                self.add_relationship(
                    fb_name,
                    "triggers",
                    self.case_selector,
                    {
                        "kind": "timer_state_transition",
                        "reason": "timer done inside CASE branch triggers state transition",
                        "source_kind": "timer",
                        "target_kind": "state",
                    },
                )

        if "COUNTER" in fb_upper or fb_upper.startswith(("CTU", "CTD", "CTUD")):
            count_input = argument_map.get("CU", argument_map.get("CD", "<count_input>"))
            if not self.is_literal_value(count_input):
                self.add_relationship(
                    count_input,
                    "triggers",
                    fb_name,
                    {
                        "function_block": fb_name,
                        "kind": "counter",
                        "reason": "counter input advances stateful sequence behavior",
                        "source_kind": "signal",
                        "target_kind": "counter",
                    },
                )

        # PROGRAM -> FUNCTION_BLOCK
        if self.current_program:
            self.add_relationship(
                self.current_program,
                "uses",
                fb_name,
                {
                    "reason": "program calls function block instance",
                    "source_kind": "program",
                    "target_kind": "function_block",
                },
            )

        # FUNCTION_BLOCK -> FUNCTION_BLOCK (output of one FB feeds another)
        for argument in node.arguments:
            arg_value = self.describe_expression(argument.value)
            if "." in arg_value:
                referenced_fb = arg_value.split(".")[0]
                # FIX 2: Skip literal values (e.g. "1.0" split into "1")
                if self.is_literal_value(referenced_fb):
                    continue
                if referenced_fb != fb_name:
                    self.add_relationship(
                        referenced_fb,
                        "feeds",
                        fb_name,
                        {
                            "argument": argument.name,
                            "value": arg_value,
                            "reason": "function block output feeds another function block input",
                            "source_kind": "function_block",
                            "target_kind": "function_block",
                        },
                    )

        for argument in node.arguments:
            self.visit(argument.value)

    def visit_FunctionInvocationNode(self, node):
        for argument in node.arguments:
            self.visit(argument.value)

    def visit_InvocationArgumentNode(self, node):
        self.visit(node.value)

    def visit_ForLoopNode(self, node):
        self.visit(node.start_expr)
        self.visit(node.end_expr)
        if node.step_expr is not None:
            self.visit(node.step_expr)
        self.visit(node.body)

    def visit_WhileLoopNode(self, node):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_RepeatLoopNode(self, node):
        self.visit(node.body)
        self.visit(node.condition)

    def visit_ExitNode(self, node):
        return None

    def visit_ReturnNode(self, node):
        if node.value is not None:
            self.visit(node.value)

    def visit_TypedLiteralNode(self, node):
        return None

    def visit_ArrayIndexNode(self, node):
        self.visit(node.array)
        self.visit(node.index)

    def visit_ArrayTypeNode(self, node):
        return None

    def visit_BinaryExpressionNode(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_LogicalExpressionNode(self, node):
        for operand in node.operands:
            self.visit(operand)

    def visit_VariableNode(self, node):
        return None

    def visit_BooleanNode(self, node):
        return None

    def visit_NumberNode(self, node):
        return None

    def visit_TimeLiteralNode(self, node):
        return None

    def visit_ConfigurationNode(self, node):
        self.current_configuration = node.name
        self.visit(node.body)
        self.current_configuration = None

    def visit_ResourceNode(self, node):
        if self.current_configuration:
            self.add_relationship(
                self.current_configuration,
                "contains",
                node.name,
                {"reason": "configuration contains resource", "source_kind": "configuration", "target_kind": "resource"},
            )
        self.current_resource = node.name
        self.visit(node.body)
        self.current_resource = None

    def visit_TaskNode(self, node):
        if self.current_resource:
            self.add_relationship(
                self.current_resource,
                "contains",
                node.name,
                {"reason": "resource contains task", "source_kind": "resource", "target_kind": "task"},
            )
        self.current_task = node.name
        for argument in node.arguments:
            if hasattr(argument, "value"):
                self.visit(argument)
            elif isinstance(argument, (tuple, list)) and len(argument) == 2:
                self.visit(argument[1])
        self.current_task = None

    def visit_ProgramBindingNode(self, node):
        if node.task_name and self.current_task == node.task_name:
            self.add_relationship(
                node.task_name,
                "schedules",
                node.instance_name,
                {"program_type": node.program_type, "reason": "task schedules program instance", "source_kind": "task", "target_kind": "program"},
            )
        self.add_relationship(
            node.instance_name,
            "uses",
            node.program_type,
            {"reason": "program instance uses program type", "source_kind": "program", "target_kind": "function_block"},
        )

    def visit_MemoryMappingNode(self, node):
        return None

    def visit_StringLiteralNode(self, node):
        return None

    def visit_VarBlockNode(self, node):
        if node.kind in ("VAR_OUTPUT", "VAR_IN_OUT"):
            for declaration in node.declarations:
                for name in declaration.names:
                    self.output_variables.add(name)
                if self._is_bool_type(declaration.var_type):
                    for name in declaration.names:
                        self.bool_output_variables.add(name)
        for declaration in node.declarations:
            self.visit(declaration)

    def visit_VariableDeclarationNode(self, node):
        if node.at_mapping is not None:
            address = node.at_mapping.address
            if address.startswith("%Q"):
                for name in node.names:
                    self.memory_mapped_outputs.add(name)
            self.visit(node.at_mapping)
        if node.default_value is not None:
            self.visit(node.default_value)

    # ------------------------------------------------------------------
    # Relationship rules
    # ------------------------------------------------------------------

    def emit_condition_relationships(self, context, target, value, node):
        target_kind = self.infer_target_kind(target)
        for signal in context["signals"]:
            if self.is_literal_value(signal):
                continue
            # STEP 1: R1 filtering — edge-worthy vs context-only
            if not self.is_edge_worthy(signal, context):
                self._filtered_r1_signals.append({
                    "signal": signal,
                    "condition": context["text"],
                    "target": target,
                    "target_kind": target_kind,
                })
                continue
            relation = self.relation_for_signal(signal, target, value, context)
            source = self.source_for_signal(signal, context)
            source_kind = self.infer_signal_kind(signal, context)

            self.add_relationship(
                source,
                relation,
                target,
                {
                    "condition": context["text"],
                    "assignment": f"{target} := {value}",
                    "node_type": node.__class__.__name__,
                    "classification_tags": self.classification_report.get("tags", []),
                    "source_kind": source_kind,
                    "target_kind": target_kind,
                },
            )

        if context["kind"] == "process_limit":
            limit_source = self.limit_source_name(context)
            relation = "triggers" if self.is_meaningful_trigger_target(target) else "disables"
            if not self.is_literal_value(limit_source):
                self.add_relationship(
                    limit_source,
                    relation,
                    target,
                    {
                        "condition": context["text"],
                        "assignment": f"{target} := {value}",
                        "reason": "process limit condition controls downstream action",
                        "source_kind": "process_variable",
                        "target_kind": target_kind,
                    },
                )

        if context["kind"] == "timer":
            timer_source = context["primary_signal"]
            if not self.is_literal_value(timer_source):
                self.add_relationship(
                    timer_source,
                    "activates",
                    target,
                    {
                        "condition": context["text"],
                        "assignment": f"{target} := {value}",
                        "reason": "timer done condition activates controlled behavior",
                        "source_kind": "timer",
                        "target_kind": target_kind,
                    },
                )

    def relation_for_signal(self, signal, target, value, context):
        # Phase 2: Existing extractor rules (compute candidate)
        candidate = "depends_on"
        if self.is_safety_signal(signal):
            candidate = "enables"
        elif self.is_start_signal(signal):
            if self.is_meaningful_trigger_target(target):
                candidate = "triggers"
            elif self.is_actuator_target(target):
                candidate = "controls"
            else:
                candidate = "depends_on"
        elif self.is_emergency_or_fault_signal(signal):
            if self.is_actuator_target(target):
                candidate = "disables"
            elif self.is_meaningful_trigger_target(target):
                candidate = "triggers"
            else:
                candidate = "depends_on"
        elif context["kind"] == "process_limit":
            if self.is_meaningful_trigger_target(target):
                candidate = "triggers"
            else:
                candidate = "disables"
        elif context["kind"] == "timer":
            candidate = "activates"
        elif self.is_enable_signal(signal):
            candidate = "enables"
        elif self.is_actuator_target(target):
            if self.is_meaningful_control_source(signal):
                candidate = "controls"
            else:
                candidate = "depends_on"
        elif self.is_timer_target(target):
            if self.is_meaningful_control_source(signal):
                candidate = "triggers"
            else:
                candidate = "depends_on"
        elif self.is_function_block_target(target):
            candidate = "feeds"

        # Phase 3: Semantic role-based conversion
        source_kind = self.infer_signal_kind(signal, context)
        target_kind = self.infer_target_kind(target)

        if source_kind == "sensor" and target_kind == "state":
            candidate = "triggers"
        if source_kind == "sensor" and target_kind == "actuator":
            candidate = "controls"
        if source_kind == "register" and target_kind == "state":
            candidate = "enables"
        if source_kind == "register" and target_kind == "actuator":
            candidate = "controls"
        if source_kind == "state" and target_kind == "actuator":
            candidate = "sequences"
        if source_kind == "mode" and target_kind == "actuator":
            candidate = "controls"
        if source_kind == "reset_signal" and target_kind == "state":
            candidate = "disables"
        if source_kind == "reset_signal" and target_kind == "counter":
            candidate = "disables"
        if source_kind == "trigger_signal" and target_kind == "state":
            candidate = "triggers"
        if source_kind == "trigger_signal" and target_kind == "actuator":
            candidate = "activates"
        if source_kind == "history" and target_kind == "state":
            candidate = "triggers"

        # Phase 4: SemanticContext-aware adjustments
        if self.context:
            # State machine context: prioritize sequences/transitions_to, reduce generic controls
            if self.context.state_machine_detected:
                if source_kind == "state" and target_kind == "actuator":
                    candidate = "sequences"
                if source_kind == "mode" and target_kind == "actuator":
                    # Mode guards in state machines should not directly control actuators
                    candidate = "enables"
                if source_kind == "sensor" and target_kind == "actuator":
                    # Sensor guards in state machines should trigger transitions, not control actuators
                    candidate = "triggers"

            # Measurement system context: avoid actuator semantics from arithmetic variables
            if self.context.measurement_system_detected:
                if source_kind in ("process_variable", "sensor", "unknown") and target_kind == "actuator":
                    # Downgrade to depends_on instead of false controls
                    candidate = "depends_on"

            # Data processing context: suppress control-oriented edges from computational variables
            if self.context.data_processing_detected:
                if source_kind == "unknown" and target_kind == "actuator":
                    candidate = "depends_on"
                if source_kind == "register" and target_kind == "actuator":
                    candidate = "depends_on"

        # Phase 1: Classifier-aware overrides (only for depends_on or when more specific)
        if self.classification_report:
            for finding in self.classification_report.get("findings", []):
                if finding.get("confidence") not in ("high", "medium"):
                    continue
                tag = finding.get("tag", "")
                evidence = finding.get("evidence", "")

                # Condition-level findings (highly specific, always override)
                if context["text"] == evidence:
                    if tag == "SAFETY_INTERLOCK":
                        candidate = "enables"
                    if tag in ("EMERGENCY_SHUTDOWN", "FAULT_PROTECTION_SEQUENCE"):
                        candidate = "disables"
                    if tag == "PROCESS_ENABLE_CONDITION":
                        candidate = "enables"
                    if tag == "TIMER_DEPENDENT_CONTROL":
                        candidate = "activates"

                # State machine → transitions_to
                if tag == "STATE_MACHINE" and context["kind"] == "state_change":
                    candidate = "transitions_to"

                # MULTI_ACTUATOR_SEQUENCE and PROCESS_CONTROL only override generic depends_on
                if candidate == "depends_on":
                    if tag == "MULTI_ACTUATOR_SEQUENCE":
                        if target in [t.strip() for t in evidence.split(",")]:
                            candidate = "sequences"
                    if tag == "PROCESS_CONTROL" and self.current_unit_name == evidence:
                        if self.is_actuator_target(target):
                            candidate = "controls"

        return candidate

    def condition_context(self, condition):
        text = self.describe_expression(condition)
        signals = self.extract_condition_signals(condition)
        kind = "general"

        if self.is_process_limit_condition(condition):
            kind = "process_limit"
        elif any(self.is_timer_signal(signal) for signal in signals):
            kind = "timer"
        elif any(self.is_emergency_or_fault_signal(signal) for signal in signals):
            kind = "fault_or_emergency"
        elif any(self.is_safety_signal(signal) for signal in signals):
            kind = "safety"

        return {
            "text": text,
            "signals": signals,
            "kind": kind,
            "primary_signal": signals[0] if signals else text,
            "condition_node": condition,
        }

    def build_interpretation_summary(self):
        relations = {relationship.relation for relationship in self.relationships}
        summaries = []

        if "enables" in relations:
            summaries.append("safety-gated or permissive-controlled behavior")

        if "triggers" in relations:
            summaries.append("event-like trigger behavior for alarms, timers, or actions")

        if "disables" in relations:
            summaries.append("protective shutdown or process limit response")

        if "activates" in relations:
            summaries.append("timer-dependent actuator activation")

        if "sequences" in relations:
            summaries.append("stateful process sequencing or mode-driven behavior")

        if "depends_on" in relations:
            summaries.append("explicit dependency edges for future semantic graph modeling")

        if "contains" in relations:
            summaries.append("hierarchical configuration-resource-task containment")

        if "schedules" in relations:
            summaries.append("task-driven program scheduling")

        if "uses" in relations:
            summaries.append("program-to-function-block type usage")

        if "transitions_to" in relations:
            summaries.append("finite state machine transitions")

        if "controls" in relations:
            summaries.append("control signal to actuator command paths")

        if "feeds" in relations:
            summaries.append("function block data flow chaining")

        return summaries

    # ------------------------------------------------------------------
    # AST description helpers
    # ------------------------------------------------------------------

    def describe_expression(self, node):
        if node is None:
            return "<none>"

        node_type = node.__class__.__name__

        if node_type == "VariableNode":
            return node.name

        if node_type == "BooleanNode":
            return "TRUE" if node.value else "FALSE"

        if node_type == "NumberNode":
            return str(node.value)

        if node_type == "TimeLiteralNode":
            return node.value

        if node_type == "BinaryExpressionNode":
            left = self.describe_expression(node.left)
            right = self.describe_expression(node.right)
            return f"{left} {node.operator} {right}"

        if node_type == "LogicalExpressionNode":
            operands = [self.describe_expression(operand) for operand in node.operands]

            if node.operator == "NOT":
                return f"NOT {operands[0]}"

            return f" {node.operator} ".join(operands)

        return repr(node)

    def extract_condition_signals(self, node):
        node_type = node.__class__.__name__

        if node_type == "VariableNode":
            return [node.name]

        if node_type == "BinaryExpressionNode":
            return self.extract_condition_signals(node.left)

        if node_type == "LogicalExpressionNode":
            signals = []
            for operand in node.operands:
                signals.extend(self.extract_condition_signals(operand))
            return signals

        return []

    def is_test_harness_entity(self, name):
        """Return True if the name is a test-harness artifact."""
        return any(
            term in name
            for term in (
                "Failed",
                "Passed",
                "totalTests",
                "TestBlock",
                "Test_",
            )
        )

    def is_literal_value(self, value):
        """Return True if the value string represents a literal constant."""
        if value in ("TRUE", "FALSE", "<none>", "<input>", "<preset_time>", "<count_input>"):
            return True
        if value.startswith(("T#", "t#", '"')):
            return True
        try:
            float(value)
            return True
        except ValueError:
            pass
        return False

    def is_literal_node(self, node):
        """Return True if the AST node is a literal constant."""
        return node.__class__.__name__ in (
            "NumberNode",
            "BooleanNode",
            "TimeLiteralNode",
            "StringLiteralNode",
            "TypedLiteralNode",
        )

    def is_meaningful_control_source(self, signal):
        """Return True for non-literal PLC variables that can be control sources."""
        return not self.is_literal_value(signal)

    def is_meaningful_trigger_target(self, target):
        """Return True if the target is a timer, alarm, event, or state transition."""
        return (
            self.is_timer_target(target)
            or self.is_alarm_target(target)
            or self.is_counter(target)
            or "Event" in target
            or "Request" in target
            or self.is_mode(target)
        )

    def is_process_limit_condition(self, node):
        if node.__class__.__name__ != "BinaryExpressionNode":
            return False

        if node.operator not in (">", ">=", "<", "<="):
            return False

        text = self.describe_expression(node)
        return any(
            term in text
            for term in ("Pressure", "Temp", "Temperature", "Level", "Limit", "High", "Low")
        )

    def limit_source_name(self, context):
        if context["signals"]:
            signal = context["signals"][0]

            if "Pressure" in signal:
                return "PressureHigh"

            if "Temp" in signal or "Temperature" in signal:
                return "TemperatureHigh"

            if "Level" in signal:
                return "LevelLimit"

            return f"{signal}Limit"

        return context["text"]

    def source_for_signal(self, signal, context):
        if context["kind"] == "timer":
            return signal

        return signal

    def is_safety_signal(self, signal):
        return any(term in signal for term in ("Safety", "Guard", "Door"))

    def is_start_signal(self, signal):
        return any(term in signal for term in ("Start", "Button", "Command"))

    def is_enable_signal(self, signal):
        return any(term in signal for term in ("Enable", "Ready", "AutoMode", "ManualMode"))

    def is_emergency_or_fault_signal(self, signal):
        return any(term in signal for term in ("Emergency", "EStop", "Fault", "Trip", "Overload"))

    def is_timer_signal(self, signal):
        return ".Q" in signal and "Timer" in signal

    def is_alarm_target(self, target):
        return any(term in target for term in ("Alarm", "Warning", "Fault"))

    def is_actuator_name(self, name):
        return any(
            term in name
            for term in (
                "Motor", "Pump", "Valve", "Heater", "Mixer", "Conveyor",
                "Clamp", "Cutter", "Contactor", "Cylinder", "Fan",
                "Blower", "Compressor", "Solenoid",
            )
        ) or bool(re.match(r"^(Ho\d+|Ro\d+|Zo\d+|Yo\d+|Q\d+)$", name))

    def is_actuator_target(self, target):
        if target in self.memory_mapped_outputs:
            return True
        if target in self.bool_output_variables:
            return True
        return self.is_actuator_name(target)

    def is_sensor(self, name):
        return any(
            term in name
            for term in (
                "Sensor", "Switch", "Proximity", "Encoder", "Transducer",
                "Detector", "Probe", "Photo", "Inductive", "Capacitive",
            )
        )

    def _is_bool_type(self, var_type):
        if isinstance(var_type, str):
            return var_type == "BOOL"
        if hasattr(var_type, "element_type"):
            return var_type.element_type == "BOOL"
        return False

    def is_control_signal(self, signal):
        return any(
            term in signal
            for term in (
                "Start",
                "Stop",
                "Button",
                "Command",
                "Enable",
                "Ready",
                "AutoMode",
                "ManualMode",
                "Safety",
                "Guard",
                "Door",
                "EStop",
                "Emergency",
                "Interlock",
                "Permissive",
                "Run",
                "Done",
                "Si",
                "Xi",
                "Zi",
                "Ri",
            )
        )

    def is_mode(self, name):
        return any(term in name for term in ("Mode", "Auto", "Manual", "State", "Step", "Sequence"))

    def is_counter(self, name):
        return any(term in name for term in ("CTU", "CTD", "CTUD", "Counter"))

    def is_process_variable(self, name):
        return any(
            term in name
            for term in (
                "Pressure", "Temp", "Temperature", "Level", "Limit", "Flow",
                "Speed", "Position", "Current", "Voltage", "Torque",
            )
        )

    def is_signal(self, name):
        return any(
            term in name
            for term in (
                "Safety", "Guard", "Door", "Start", "Stop", "Button", "Command",
                "Enable", "Ready", "AutoMode", "ManualMode", "EStop", "Emergency",
                "Interlock", "Permissive", "Run", "Done", "Q",
            )
        )

    def is_timer_target(self, target):
        fb_upper = target.upper()
        return "TIMER" in fb_upper or fb_upper.startswith(("TON", "TOF", "TP"))

    def is_function_block_target(self, target):
        fb_upper = target.upper()
        return fb_upper.startswith(("FB_", "TON", "TOF", "TP", "CTU", "CTD", "CTUD", "FT_", "PID")) or target.endswith("Block")

    def infer_target_kind(self, target):
        if target in self.memory_mapped_outputs:
            return "actuator"
        if target in self.bool_output_variables:
            return "actuator"
        if self.is_actuator_name(target):
            return "actuator"
        if self.is_alarm_target(target):
            return "alarm"
        if self.is_timer_target(target):
            return "timer"
        if self.is_function_block_target(target):
            return "function_block"
        if self.is_mode(target):
            return "mode"
        if self.is_counter(target):
            return "counter"
        if self.is_process_variable(target):
            return "process_variable"
        if self.is_signal(target):
            return "signal"
        if target.startswith("Xi"):
            return "sensor"
        if target.startswith("Ri"):
            return "register"
        if target.startswith("Si"):
            return "signal"
        if target == "_step":
            return "state"
        if target == "run":
            return "mode"
        if target == "rst":
            return "reset_signal"
        if target == "edge":
            return "trigger_signal"
        return "unknown"

    def infer_signal_kind(self, signal, context):
        if signal.startswith("Xi"):
            return "sensor"
        if signal.startswith("Ri"):
            return "register"
        if signal.startswith("Si"):
            return "signal"
        if signal == "_step":
            return "state"
        if signal == "run":
            return "mode"
        if signal == "rst":
            return "reset_signal"
        if signal == "edge":
            return "trigger_signal"
        if self.is_safety_signal(signal):
            return "signal"
        if self.is_control_signal(signal):
            return "control_signal"
        if self.is_timer_signal(signal):
            return "timer"
        if context["kind"] == "process_limit":
            return "process_variable"
        return "signal"

    def extract_state_assignment(self, body, selector_text):
        if body is None:
            return None
        node_type = body.__class__.__name__
        if node_type == "AssignmentNode":
            target = self.describe_expression(body.target)
            if target == selector_text:
                return self.describe_expression(body.value)
        if node_type == "BlockNode":
            for stmt in body.statements:
                result = self.extract_state_assignment(stmt, selector_text)
                if result is not None:
                    return result
        for attr in ("body", "then_body", "else_body", "statements", "branches", "elsif_branches"):
            child = getattr(body, attr, None)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    result = self.extract_state_assignment(item, selector_text)
                    if result is not None:
                        return result
            else:
                result = self.extract_state_assignment(child, selector_text)
                if result is not None:
                    return result
        return None

    # ------------------------------------------------------------------
    # Phase A — Condition Role Classification
    # ------------------------------------------------------------------

    def classify_condition_roles(self, condition):
        """Classify every variable in a condition into CONTROL, PERMISSIVE, or CONTEXT.

        CONTROL:
            - state variables (_step, State, ToolChangeState)
            - timer done signals (Timer.Q)
            - trigger signals (edge)

        PERMISSIVE:
            - mode variables (run)
            - sensors (Xi*, in*)
            - control signals (Si*)

        CONTEXT:
            - history variables (last, previous)
            - timer arithmetic variables
            - comparison-only variables (right side of comparison)

        Returns:
            {
                "control": [...],
                "permissive": [...],
                "context": [...]
            }
        """
        vars_info = self._extract_all_variables_with_positions(condition)
        control = []
        permissive = []
        context = []

        for info in vars_info:
            name = info["name"]
            role = self._classify_single_role(name, info["path"])
            if role == "control":
                control.append(name)
            elif role == "permissive":
                permissive.append(name)
            else:
                context.append(name)

        # Deduplicate preserving order
        control = list(dict.fromkeys(control))
        permissive = list(dict.fromkeys(permissive))
        context = list(dict.fromkeys(context))

        return {"control": control, "permissive": permissive, "context": context}

    def _extract_all_variables_with_positions(self, node, path=None):
        """Recursively extract all VariableNode names with their AST path."""
        if path is None:
            path = []

        node_type = node.__class__.__name__

        if node_type == "VariableNode":
            return [{"name": node.name, "path": path.copy()}]

        if node_type == "BinaryExpressionNode":
            results = []
            left_path = path + [("binop", node.operator, "left")]
            right_path = path + [("binop", node.operator, "right")]
            results.extend(self._extract_all_variables_with_positions(node.left, left_path))
            results.extend(self._extract_all_variables_with_positions(node.right, right_path))
            return results

        if node_type == "LogicalExpressionNode":
            results = []
            for i, operand in enumerate(node.operands):
                operand_path = path + [("logic", node.operator, i)]
                results.extend(self._extract_all_variables_with_positions(operand, operand_path))
            return results

        # Recurse into other common child attributes
        results = []
        for attr in ("left", "right", "operands", "operand", "value", "target",
                     "condition", "then_body", "else_body", "body", "statements",
                     "branches", "arguments"):
            child = getattr(node, attr, None)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    results.extend(self._extract_all_variables_with_positions(item, path))
            else:
                results.extend(self._extract_all_variables_with_positions(child, path))
        return results

    def _classify_single_role(self, name, path):
        """Return 'control', 'permissive', or 'context' for a single variable."""
        # CONTEXT: history variables
        if self.is_history(name):
            return "context"

        # CONTEXT: timer arithmetic variables
        arithmetic_ops = ("+", "-", "*", "/")
        is_in_arithmetic = any(p[0] == "binop" and p[1] in arithmetic_ops for p in path)
        if is_in_arithmetic:
            return "context"

        # CONTEXT: comparison-only variables (right side of comparison)
        comparison_ops = ("=", "<>", "<", ">", "<=", ">=")
        is_in_comparison_rhs = any(
            p[0] == "binop" and p[1] in comparison_ops and p[2] == "right" for p in path
        )
        if is_in_comparison_rhs:
            return "context"

        # CONTROL: state variables
        if self.is_state_variable(name):
            return "control"

        # CONTROL: timer done signals
        if self.is_timer_signal(name):
            return "control"

        # CONTROL: trigger signals
        if self.is_trigger_signal(name):
            return "control"

        # PERMISSIVE: mode variables
        if self.is_mode_variable(name):
            return "permissive"

        # PERMISSIVE: sensors
        if self.is_sensor(name) or name.startswith("Xi") or name.startswith("in"):
            return "permissive"

        # PERMISSIVE: control signals
        if self.is_control_signal(name) or name.startswith("Si"):
            return "permissive"

        # Default: PERMISSIVE
        return "permissive"

    def is_history(self, name):
        """Return True if the name matches history/memory retention patterns."""
        return (
            name == "last"
            or name.endswith("_last")
            or name.startswith("previous")
            or name.startswith("old")
        )

    def is_state_variable(self, name):
        """Return True if the name is a state-machine selector variable."""
        return name in (
            "_step", "State", "LightState", "ToolChangeState",
            "StartupStep", "BatchStep",
        ) or name.endswith("State")

    def is_trigger_signal(self, name):
        """Return True if the name is a one-shot trigger signal."""
        return name == "edge" or name.lower() in ("start", "trigger")

    def is_mode_variable(self, name):
        """Return True if the name is a mode or execution guard variable."""
        return name == "run" or name in ("auto", "manual", "Auto", "Manual") or name.endswith("Mode")

    def is_edge_worthy(self, signal, context):
        """Return True if the signal should generate a relationship (EDGE_WORTHY).

        EDGE_WORTHY:
            - state variables
            - sensors
            - trigger signals
            - reset signals
            - timer done signals
            - counters

        CONTEXT_ONLY (implicit fallback):
            - history variables
            - arithmetic operands
            - comparison-only variables
            - timing variables used only in expressions
            - local bookkeeping variables
        """
        if self.is_literal_value(signal):
            return False

        # State variables
        if self.is_state_variable(signal):
            return True

        # Sensors
        if self.is_sensor(signal) or signal.startswith("Xi") or signal.startswith("in"):
            return True

        # Trigger signals
        if self.is_trigger_signal(signal):
            return True

        # Reset signals
        if signal.lower() == "rst" or self.infer_signal_kind(signal, context) == "reset_signal":
            return True

        # Timer done signals
        if ".Q" in signal and any(term in signal for term in ("Timer", "TON", "TOF", "TP")):
            return True

        # Counters
        if self.is_counter(signal):
            return True

        return False
