"""Industrial semantic classifier built on the existing AST visitor system."""

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


class IndustrialSemanticClassifier(ASTVisitor):
    """Visitor pass that classifies industrial control behavior."""

    def __init__(self, type_report=None):
        self.type_report = type_report or {}
        self.findings = []
        self.condition_stack = []
        self.case_stack = []
        self.assignment_buffer = []

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
        self.visit(node.body)

    def visit_BlockNode(self, node):
        assignments_before = len(self.assignment_buffer)

        for statement in node.statements:
            self.visit(statement)

        new_assignments = self.assignment_buffer[assignments_before:]
        actuator_assignments = [
            item for item in new_assignments if self.is_actuator_name(item["target"])
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
        self.visit(node.selector)

        for branch in node.branches:
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

        self.assignment_buffer.append({"target": target, "value": value})
        self.classify_assignment(target, value, node)
        self.visit(node.target)
        self.visit(node.value)

    def visit_FunctionBlockCallNode(self, node):
        fb_name = node.name.upper()
        argument_map = {
            argument.name: self.describe_expression(argument.value)
            for argument in node.arguments
        }

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

        if self.is_actuator_name(target):
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
            )
        )
