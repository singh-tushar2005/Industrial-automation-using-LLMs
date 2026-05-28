"""Visitor-based extraction of industrial semantic relationships."""

try:
    from semantic.relationships import Relationship
    from semantic.visitor import ASTVisitor
except ModuleNotFoundError:
    from relationships import Relationship
    from visitor import ASTVisitor


class RelationshipExtractor(ASTVisitor):
    """Extract transformation-oriented behavior relationships from an AST.

    The extractor is a semantic layer above classification. It reuses the
    existing visitor infrastructure and consumes classifier/type outputs as
    context. It does not print and does not build a full graph yet; it returns
    relationship edges that are compatible with future graph construction.
    """

    def __init__(self, classification_report=None, type_report=None):
        self.classification_report = classification_report or {}
        self.type_report = type_report or {}
        self.relationships = []
        self.condition_stack = []
        self.case_stack = []

    def extract(self, ast):
        """Run relationship extraction and return structured results."""

        self.visit(ast)
        return self.get_results()

    def get_results(self):
        """Return relationship data and summary counts."""

        relationship_data = [relationship.to_dict() for relationship in self.relationships]
        relation_counts = {}

        for relationship in self.relationships:
            relation_counts[relationship.relation] = (
                relation_counts.get(relationship.relation, 0) + 1
            )

        return {
            "relationships": relationship_data,
            "relationship_count": len(relationship_data),
            "relation_counts": dict(sorted(relation_counts.items())),
            "sources": sorted({item["source"] for item in relationship_data}),
            "targets": sorted({item["target"] for item in relationship_data}),
            "interpretation_summary": self.build_interpretation_summary(),
        }

    def add_relationship(self, source, relation, target, metadata=None):
        """Add one semantic edge if it has not already been recorded."""

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
        self.visit(node.body)

    def visit_BlockNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_IfStatementNode(self, node):
        context = self.condition_context(node.condition)
        self.condition_stack.append(context)
        self.visit(node.condition)
        self.visit(node.then_body)

        for elsif_condition, elsif_body in node.elsif_branches:
            self.visit(elsif_condition)
            self.visit(elsif_body)

        if node.else_body is not None:
            self.visit(node.else_body)

        self.condition_stack.pop()

    def visit_CaseStatementNode(self, node):
        selector = self.describe_expression(node.selector)
        self.case_stack.append(selector)
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
                    },
                )

            previous_branch = current_branch
            self.visit(branch)

        if node.else_body is not None:
            self.visit(node.else_body)

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
            self.add_relationship(
                input_signal,
                "triggers",
                fb_name,
                {
                    "function_block": fb_name,
                    "kind": "timer",
                    "reason": "timer input starts time-dependent behavior",
                },
            )

            self.add_relationship(
                fb_name,
                "depends_on",
                argument_map.get("PT", "<preset_time>"),
                {
                    "function_block": fb_name,
                    "kind": "timer",
                    "reason": "timer behavior depends on preset time",
                },
            )

        if "COUNTER" in fb_upper or fb_upper.startswith(("CTU", "CTD", "CTUD")):
            count_input = argument_map.get("CU", argument_map.get("CD", "<count_input>"))
            self.add_relationship(
                count_input,
                "triggers",
                fb_name,
                {
                    "function_block": fb_name,
                    "kind": "counter",
                    "reason": "counter input advances stateful sequence behavior",
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

    # ------------------------------------------------------------------
    # Relationship rules
    # ------------------------------------------------------------------

    def emit_condition_relationships(self, context, target, value, node):
        for signal in context["signals"]:
            relation = self.relation_for_signal(signal, target, value, context)
            source = self.source_for_signal(signal, context)

            self.add_relationship(
                source,
                relation,
                target,
                {
                    "condition": context["text"],
                    "assignment": f"{target} := {value}",
                    "node_type": node.__class__.__name__,
                    "classification_tags": self.classification_report.get("tags", []),
                },
            )

        if context["kind"] == "process_limit":
            limit_source = self.limit_source_name(context)
            relation = "triggers" if self.is_alarm_target(target) else "disables"
            self.add_relationship(
                limit_source,
                relation,
                target,
                {
                    "condition": context["text"],
                    "assignment": f"{target} := {value}",
                    "reason": "process limit condition controls downstream action",
                },
            )

        if context["kind"] == "timer":
            timer_source = context["primary_signal"]
            self.add_relationship(
                timer_source,
                "activates",
                target,
                {
                    "condition": context["text"],
                    "assignment": f"{target} := {value}",
                    "reason": "timer done condition activates controlled behavior",
                },
            )

    def relation_for_signal(self, signal, target, value, context):
        if self.is_safety_signal(signal):
            return "enables"

        if self.is_start_signal(signal):
            return "triggers"

        if self.is_emergency_or_fault_signal(signal):
            return "disables" if value == "FALSE" or self.is_actuator_target(target) else "triggers"

        if context["kind"] == "process_limit":
            return "triggers" if self.is_alarm_target(target) else "disables"

        if context["kind"] == "timer":
            return "activates"

        if self.is_enable_signal(signal):
            return "enables"

        return "depends_on"

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

    def is_actuator_target(self, target):
        return any(
            term in target
            for term in (
                "Motor",
                "Pump",
                "Valve",
                "Heater",
                "Mixer",
                "Conveyor",
                "Clamp",
                "Cutter",
                "Contactor",
            )
        )
