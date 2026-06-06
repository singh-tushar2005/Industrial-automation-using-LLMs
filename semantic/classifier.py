"""Industrial semantic classifier built on the existing AST visitor system."""

import re

try:
    from semantic.visitor import ASTVisitor
except ModuleNotFoundError:
    from visitor import ASTVisitor


SAFETY_INTERLOCK = "SAFETY_INTERLOCK"
CONTROLLED_STARTUP_SEQUENCE = "CONTROLLED_STARTUP_SEQUENCE"
FAULT_PROTECTION_SEQUENCE = "FAULT_PROTECTION_SEQUENCE"
TIMER_DEPENDENT_CONTROL = "TIMER_DEPENDENT_CONTROL"
ACTUATOR_COORDINATION = "ACTUATOR_COORDINATION"
ALARM_CONDITION = "ALARM_CONDITION"
PROCESS_LIMIT_PROTECTION = "PROCESS_LIMIT_PROTECTION"
MODE_SELECTION_LOGIC = "MODE_SELECTION_LOGIC"
EMERGENCY_SHUTDOWN = "EMERGENCY_SHUTDOWN"
PROCESS_ENABLE_CONDITION = "PROCESS_ENABLE_CONDITION"
PROCESS_SEQUENCING = "PROCESS_SEQUENCING"
INDUSTRIAL_FAULT_RECOVERY = "INDUSTRIAL_FAULT_RECOVERY"

STATE_MACHINE = "STATE_MACHINE"
TASK_SCHEDULING = "TASK_SCHEDULING"
PROGRAM_DEPLOYMENT = "PROGRAM_DEPLOYMENT"
RESOURCE_BINDING = "RESOURCE_BINDING"
RUNTIME_CONFIGURATION = "RUNTIME_CONFIGURATION"
PROCESS_CONTROL = "PROCESS_CONTROL"
PROCESS_MONITORING = "PROCESS_MONITORING"
FB_COORDINATION = "FB_COORDINATION"
MULTI_ACTUATOR_SEQUENCE = "MULTI_ACTUATOR_SEQUENCE"


class IndustrialSemanticClassifier(ASTVisitor):
    """Visitor pass that classifies industrial control behavior."""

    def __init__(self, type_report=None):
        self.type_report = type_report or {}
        self.findings = []
        self.condition_stack = []
        self.case_stack = []
        self.assignment_buffer = []
        self.current_unit = None
        self.current_configuration = None
        self.current_resource = None
        self.fb_calls_in_body = []
        self.actuator_assignments_in_body = []
        self.state_machine_selector = None
        self.output_variables = set()
        self.bool_output_variables = set()
        self.memory_mapped_outputs = set()

    def classify(self, ast):
        """Run classification and return structured semantic metadata."""

        self.visit(ast)
        return self.get_results()

    def get_results(self):
        """Return classification metadata for future IR/transformation stages."""

        return {
            "findings": list(self.findings),
            "finding_count": len(self.findings),
            "tags": sorted({finding["tag"] for finding in self.findings}),
            "semantic_model": {
                "conditions_seen": [self.describe_expression(item) for item in self.condition_stack],
                "type_report_available": bool(self.type_report),
            },
        }

    def add_finding(self, tag, description, evidence, node, confidence="medium", hints=None):
        """Record one semantic classification result."""

        self.findings.append(
            {
                "tag": tag,
                "description": description,
                "evidence": evidence,
                "node_type": node.__class__.__name__,
                "confidence": confidence,
                "transformation_hints": hints or [],
            }
        )

    # ------------------------------------------------------------------
    # Recursive traversal
    # ------------------------------------------------------------------

    def visit_ProgramNode(self, node):
        self.visit(node.body)

    def visit_CompilationUnitNode(self, node):
        old_unit = self.current_unit
        self.current_unit = node
        self.fb_calls_in_body = []
        self.actuator_assignments_in_body = []

        if node.kind == "PROGRAM":
            self.add_finding(
                PROGRAM_DEPLOYMENT,
                "PROGRAM compilation unit represents a deployable control application.",
                node.name,
                node,
                confidence="high",
                hints=["map PROGRAM to IEC 61499 application or device deployment unit"],
            )
        elif node.kind == "FUNCTION_BLOCK":
            if self.has_control_patterns(node):
                self.add_finding(
                    PROCESS_CONTROL,
                    "FUNCTION_BLOCK contains control logic (state machine, PID, or actuator sequencing).",
                    node.name,
                    node,
                    confidence="high",
                    hints=["preserve as reusable control function block in transformation IR"],
                )
            if self.has_monitoring_patterns(node):
                self.add_finding(
                    PROCESS_MONITORING,
                    "FUNCTION_BLOCK contains monitoring or diagnostic outputs without direct actuator control.",
                    node.name,
                    node,
                    confidence="medium",
                    hints=["model monitoring outputs as status data points"],
                )
        elif node.kind == "FUNCTION" and node.return_type:
            self.add_finding(
                PROCESS_MONITORING,
                "FUNCTION returns a computed value; likely used for monitoring or diagnostic conversion.",
                node.name,
                node,
                confidence="medium",
                hints=["preserve as pure computation function in transformation IR"],
            )

        for var_block in node.var_blocks or []:
            self.visit(var_block)

        self.visit(node.body)

        if len(self.fb_calls_in_body) > 1:
            fb_names = ", ".join(sorted({fb.name for fb in self.fb_calls_in_body}))
            self.add_finding(
                FB_COORDINATION,
                "Multiple function block instances are coordinated within the same unit.",
                fb_names,
                node,
                confidence="high",
                hints=["model FB interactions as event/data connections"],
            )

        if len(self.actuator_assignments_in_body) >= 2:
            targets = ", ".join(item["target"] for item in self.actuator_assignments_in_body)
            self.add_finding(
                MULTI_ACTUATOR_SEQUENCE,
                "Multiple actuators are commanded in sequence within the same unit.",
                targets,
                node,
                confidence="high",
                hints=["group sequential actuator outputs into coordinated IEC 61499 sequence"],
            )

        self.current_unit = old_unit

    def visit_BlockNode(self, node):
        assignments_before = len(self.assignment_buffer)
        actuator_before = len(self.actuator_assignments_in_body)

        for statement in node.statements:
            self.visit(statement)

        new_assignments = self.assignment_buffer[assignments_before:]
        actuator_assignments = [
            item for item in new_assignments if self.is_actuator_target(item["target"])
        ]

        if len(actuator_assignments) >= 2:
            targets = ", ".join(item["target"] for item in actuator_assignments)
            self.add_finding(
                ACTUATOR_COORDINATION,
                "Multiple actuator commands are coordinated in the same control block.",
                targets,
                node,
                confidence="high",
                hints=["group related actuator outputs into coordinated IEC 61499 control logic"],
            )

        if self.case_stack and len(self.actuator_assignments_in_body) - actuator_before >= 2:
            new_actuator = self.actuator_assignments_in_body[actuator_before:]
            targets = ", ".join(item["target"] for item in new_actuator)
            self.add_finding(
                MULTI_ACTUATOR_SEQUENCE,
                "Multiple actuators are commanded in sequence within a CASE branch.",
                targets,
                node,
                confidence="high",
                hints=["map sequential actuator branch to IEC 61499 state action block"],
            )

    def visit_IfStatementNode(self, node):
        condition_text = self.describe_expression(node.condition)
        self.classify_condition(node.condition, node)
        self.condition_stack.append(node.condition)
        self.visit(node.condition)
        self.visit(node.then_body)

        for elsif_condition, elsif_body in node.elsif_branches:
            self.visit(elsif_condition)
            self.visit(elsif_body)

        if node.else_body is not None:
            self.visit(node.else_body)

        self.condition_stack.pop()

        if self.contains_fault_term(condition_text):
            self.add_finding(
                FAULT_PROTECTION_SEQUENCE,
                "Conditional block protects process behavior when a fault state is present.",
                condition_text,
                node,
                confidence="high",
                hints=["model as a fault-handling event path in IEC 61499"],
            )

        if self.contains_emergency_term(condition_text):
            self.add_finding(
                EMERGENCY_SHUTDOWN,
                "Emergency condition gates shutdown or safe-state logic.",
                condition_text,
                node,
                confidence="high",
                hints=["preserve as high-priority safety event path"],
            )

    def visit_CaseStatementNode(self, node):
        selector_text = self.describe_expression(node.selector)
        tag = PROCESS_SEQUENCING

        if self.contains_mode_term(selector_text):
            tag = MODE_SELECTION_LOGIC

        self.add_finding(
            tag,
            "CASE statement represents stateful mode or sequence selection.",
            selector_text,
            node,
            confidence="high",
            hints=["map selector values to IEC 61499 states or event branches"],
        )

        self.case_stack.append(node)
        self.state_machine_selector = selector_text
        self.visit(node.selector)

        is_state_machine = False
        for branch in node.branches:
            self.visit(branch)
            if self.body_assigns_to_selector(branch.body, selector_text):
                is_state_machine = True

        if is_state_machine:
            self.add_finding(
                STATE_MACHINE,
                "CASE statement branches assign to the selector variable, representing a finite state machine.",
                selector_text,
                node,
                confidence="high",
                hints=["map CASE branches to IEC 61499 states with explicit transitions"],
            )

        if node.else_body is not None:
            self.visit(node.else_body)

        self.state_machine_selector = None
        self.case_stack.pop()

    def visit_CaseBranchNode(self, node):
        self.visit(node.match_value)
        self.visit(node.body)

    def visit_AssignmentNode(self, node):
        target = self.describe_expression(node.target)
        value = self.describe_expression(node.value)

        self.assignment_buffer.append({"target": target, "value": value})
        self.classify_assignment(target, value, node)

        if self.is_actuator_target(target):
            self.actuator_assignments_in_body.append({"target": target, "value": value, "node": node})

        self.visit(node.target)
        self.visit(node.value)

    def visit_FunctionBlockCallNode(self, node):
        fb_name = node.name.upper()
        argument_map = {
            argument.name: self.describe_expression(argument.value)
            for argument in node.arguments
        }

        self.fb_calls_in_body.append(node)

        if (
            fb_name.startswith(("TON", "TOF", "TP"))
            or fb_name in ("TON", "TOF", "TP")
            or "TIMER" in fb_name
        ):
            self.add_finding(
                TIMER_DEPENDENT_CONTROL,
                "Timer function block introduces time-dependent control behavior.",
                f"{node.name}({argument_map})",
                node,
                confidence="high",
                hints=["represent timer elapsed/done output as an event or guard in IEC 61499"],
            )

        if fb_name.startswith(("CTU", "CTD", "CTUD")) or "COUNTER" in fb_name:
            self.add_finding(
                PROCESS_SEQUENCING,
                "Counter function block represents stateful sequencing behavior.",
                f"{node.name}({argument_map})",
                node,
                confidence="high",
                hints=["preserve count state and done output in the transformation IR"],
            )

        if fb_name in ("FT_PID", "FT_PI", "FT_PIWL", "PID", "PI", "PD"):
            self.add_finding(
                PROCESS_CONTROL,
                "PID function block introduces closed-loop process control.",
                f"{node.name}({argument_map})",
                node,
                confidence="high",
                hints=["preserve PID parameters and control output in transformation IR"],
            )

        for argument in node.arguments:
            self.visit(argument.value)

    def visit_FunctionInvocationNode(self, node):
        for argument in node.arguments:
            self.visit(argument.value)

    def visit_InvocationArgumentNode(self, node):
        self.visit(node.value)

    def visit_ForLoopNode(self, node):
        self.add_finding(
            PROCESS_SEQUENCING,
            "FOR loop represents iterative process sequencing or data processing.",
            f"FOR {node.variable} := ...",
            node,
            confidence="medium",
            hints=["preserve loop bounds and body in the transformation IR"],
        )
        self.visit(node.start_expr)
        self.visit(node.end_expr)
        if node.step_expr is not None:
            self.visit(node.step_expr)
        self.visit(node.body)

    def visit_WhileLoopNode(self, node):
        self.add_finding(
            PROCESS_SEQUENCING,
            "WHILE loop represents conditional iterative process behavior.",
            "WHILE ...",
            node,
            confidence="medium",
            hints=["preserve loop condition and body in the transformation IR"],
        )
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
        self.current_configuration = node
        self.add_finding(
            RUNTIME_CONFIGURATION,
            "CONFIGURATION declaration defines the runtime topology of the control system.",
            node.name,
            node,
            confidence="high",
            hints=["map CONFIGURATION to IEC 61499 device or system configuration"],
        )
        self.visit(node.body)
        self.current_configuration = None

    def visit_ResourceNode(self, node):
        self.current_resource = node
        self.add_finding(
            RESOURCE_BINDING,
            "RESOURCE declaration binds hardware target to the control application.",
            f"{node.name} ON {node.on}",
            node,
            confidence="high",
            hints=["map RESOURCE to IEC 61499 device or hardware resource"],
        )
        self.visit(node.body)
        self.current_resource = None

    def visit_TaskNode(self, node):
        self.add_finding(
            TASK_SCHEDULING,
            "TASK declaration defines execution scheduling with interval and priority.",
            node.name,
            node,
            confidence="high",
            hints=["map TASK to IEC 61499 task or event-driven execution unit"],
        )
        for argument in node.arguments:
            if hasattr(argument, "value"):
                self.visit(argument)
            elif isinstance(argument, (tuple, list)) and len(argument) == 2:
                self.visit(argument[1])

    def visit_ProgramBindingNode(self, node):
        self.add_finding(
            PROGRAM_DEPLOYMENT,
            "PROGRAM binding deploys a program instance to a task within a resource.",
            f"{node.instance_name} WITH {node.task_name} : {node.program_type}",
            node,
            confidence="high",
            hints=["map PROGRAM binding to IEC 61499 application instance or FB network"],
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
    # Classification rules
    # ------------------------------------------------------------------

    def classify_condition(self, condition, node):
        condition_text = self.describe_expression(condition)

        if self.is_limit_condition(condition):
            self.add_finding(
                PROCESS_LIMIT_PROTECTION,
                "Comparison condition protects a process limit or threshold.",
                condition_text,
                node,
                confidence="high",
                hints=["map threshold guard into semantic IR condition node"],
            )

        if self.contains_safety_term(condition_text):
            self.add_finding(
                SAFETY_INTERLOCK,
                "Condition includes safety permissive or interlock terms.",
                condition_text,
                node,
                confidence="high",
                hints=["preserve as safety gating logic before actuator commands"],
            )

        if self.contains_enable_term(condition_text):
            self.add_finding(
                PROCESS_ENABLE_CONDITION,
                "Condition enables process execution when permissives are satisfied.",
                condition_text,
                node,
                confidence="medium",
                hints=["model as process enable guard in IEC 61499"],
            )

        if self.contains_timer_done(condition_text):
            self.add_finding(
                TIMER_DEPENDENT_CONTROL,
                "Condition depends on timer completion state.",
                condition_text,
                node,
                confidence="high",
                hints=["connect timer done output to downstream control event"],
            )

    def classify_assignment(self, target, value, node):
        if self.is_alarm_name(target):
            tag = ALARM_CONDITION if value == "TRUE" else INDUSTRIAL_FAULT_RECOVERY
            self.add_finding(
                tag,
                "Assignment changes alarm or fault indication state.",
                f"{target} := {value}",
                node,
                confidence="high",
                hints=["represent alarm state as explicit output behavior"],
            )

        if self.is_actuator_target(target):
            self.add_finding(
                ACTUATOR_COORDINATION,
                "Assignment commands an actuator or field output.",
                f"{target} := {value}",
                node,
                confidence="medium",
                hints=["map actuator command to IEC 61499 output/control block"],
            )

        if self.contains_step_term(target):
            tag = CONTROLLED_STARTUP_SEQUENCE if "Startup" in target else PROCESS_SEQUENCING
            self.add_finding(
                tag,
                "Assignment advances or resets a process sequence state.",
                f"{target} := {value}",
                node,
                confidence="high",
                hints=["map step variable to execution control state"],
            )

        if self.contains_fault_term(target) and value in ("FALSE", "0"):
            self.add_finding(
                INDUSTRIAL_FAULT_RECOVERY,
                "Assignment resets or clears a fault state.",
                f"{target} := {value}",
                node,
                confidence="high",
                hints=["preserve as explicit recovery transition"],
            )

    # ------------------------------------------------------------------
    # Pattern helpers
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

    def is_limit_condition(self, node):
        if node.__class__.__name__ != "BinaryExpressionNode":
            return False

        if node.operator not in (">", ">=", "<", "<="):
            return False

        expression_text = self.describe_expression(node)
        limit_terms = ("Temp", "Temperature", "Pressure", "Level", "Limit", "High", "Low")
        return any(term in expression_text for term in limit_terms)

    def contains_safety_term(self, text):
        return any(
            term in text
            for term in ("Safety", "Guard", "Door", "EmergencyStop", "EStop", "Interlock")
        )

    def contains_emergency_term(self, text):
        return any(term in text for term in ("Emergency", "EStop", "EmergencyStop"))

    def contains_fault_term(self, text):
        return any(term in text for term in ("Fault", "Trip", "Alarm", "Overload"))

    def contains_enable_term(self, text):
        return any(term in text for term in ("Enable", "Ready", "Start", "AutoMode"))

    def contains_mode_term(self, text):
        return any(term in text for term in ("Mode", "Auto", "Manual"))

    def contains_timer_done(self, text):
        return ".Q" in text and any(term in text for term in ("Timer", "TON", "TOF", "TP"))

    def contains_step_term(self, text):
        return any(term in text for term in ("Step", "State", "Sequence"))

    def is_alarm_name(self, name):
        return any(term in name for term in ("Alarm", "Warning", "Fault"))

    def is_actuator_name(self, name):
        return any(
            term in name
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
                "Cylinder",
                "Fan",
                "Blower",
                "Compressor",
                "Solenoid",
            )
        ) or bool(re.match(r"^(Ho\d+|Ro\d+|Zo\d+|Yo\d+|Q\d+)$", name))

    def is_actuator_target(self, target):
        if target in self.memory_mapped_outputs:
            return True
        if target in self.bool_output_variables:
            return True
        return self.is_actuator_name(target)

    def is_output_variable(self, name):
        return name in self.output_variables or name in self.memory_mapped_outputs or name in self.bool_output_variables

    def _is_bool_type(self, var_type):
        if isinstance(var_type, str):
            return var_type == "BOOL"
        if hasattr(var_type, "element_type"):
            return var_type.element_type == "BOOL"
        return False

    def has_control_patterns(self, node):
        return self._node_has_control_patterns(node.body)

    def _node_has_control_patterns(self, node):
        if node is None:
            return False
        node_type = node.__class__.__name__
        if node_type == "CaseStatementNode":
            return True
        if node_type == "IfStatementNode":
            if self.is_limit_condition(node.condition):
                return True
            if self.contains_safety_term(self.describe_expression(node.condition)):
                return True
        if node_type == "FunctionBlockCallNode":
            fb_upper = node.name.upper()
            if fb_upper.startswith(("TON", "TOF", "TP", "CTU", "CTD", "CTUD")):
                return True
            if fb_upper in ("FT_PID", "FT_PI", "FT_PIWL", "PID", "PI", "PD"):
                return True
        if node_type == "AssignmentNode":
            target = self.describe_expression(node.target)
            if self.is_actuator_target(target):
                return True
        if node_type == "BlockNode":
            for stmt in node.statements:
                if self._node_has_control_patterns(stmt):
                    return True
        for attr in ("body", "then_body", "else_body", "statements", "branches", "elsif_branches"):
            child = getattr(node, attr, None)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    if self._node_has_control_patterns(item):
                        return True
            elif self._node_has_control_patterns(child):
                return True
        return False

    def has_monitoring_patterns(self, node):
        if node.kind != "FUNCTION_BLOCK":
            return False
        has_output_status = False
        for var_block in node.var_blocks or []:
            if var_block.kind in ("VAR_OUTPUT", "VAR_IN_OUT"):
                for decl in var_block.declarations:
                    if any("Status" in n or "Diagnostic" in n or "Monitor" in n for n in decl.names):
                        has_output_status = True
        if not has_output_status:
            return False
        return not self._node_has_actuator_assignment(node.body)

    def _node_has_actuator_assignment(self, node):
        if node is None:
            return False
        node_type = node.__class__.__name__
        if node_type == "AssignmentNode":
            target = self.describe_expression(node.target)
            if self.is_actuator_name(target):
                return True
        for attr in ("body", "then_body", "else_body", "statements", "branches", "elsif_branches"):
            child = getattr(node, attr, None)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    if self._node_has_actuator_assignment(item):
                        return True
            elif self._node_has_actuator_assignment(child):
                return True
        return False

    def body_assigns_to_selector(self, body, selector_text):
        if body is None:
            return False
        node_type = body.__class__.__name__
        if node_type == "AssignmentNode":
            target = self.describe_expression(body.target)
            if target == selector_text:
                return True
        if node_type == "BlockNode":
            for stmt in body.statements:
                if self.body_assigns_to_selector(stmt, selector_text):
                    return True
        for attr in ("body", "then_body", "else_body", "statements", "branches", "elsif_branches"):
            child = getattr(body, attr, None)
            if child is None:
                continue
            if isinstance(child, list):
                for item in child:
                    if self.body_assigns_to_selector(item, selector_text):
                        return True
            elif self.body_assigns_to_selector(child, selector_text):
                return True
        return False
