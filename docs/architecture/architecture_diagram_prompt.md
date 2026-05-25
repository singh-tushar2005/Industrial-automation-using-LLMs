Create a professional layered pipeline architecture diagram for an industrial semantic analysis and transformation system based on IEC61131-3 Structured Text.

The diagram should visually resemble a research-grade industrial systems pipeline similar to compiler infrastructure and semantic transformation architectures.

The visual style should be clean, modern, technical, layered, and presentation-ready — not a beginner flowchart or UML diagram.

The architecture should flow horizontally from left to right and visually show how industrial control logic evolves through multiple semantic processing stages.

Start with an “IEC61131-3 Structured Text Datasets” layer containing examples such as:
- safety systems
- tank control
- motor control
- sequencing systems
- timer logic
- process automation
- emergency stop logic
- actuator coordination

Then flow into a “Parsing and Syntax Recognition Layer” representing:
- parser.py
- pyparsing grammar rules
- parse actions
- recursive grammar handling
- AST object generation

Show transformation from raw IEC code into structured syntax representation.

Then move into an “AST Representation Layer” visually showing recursive tree structures using:
- ProgramNode
- IfStatementNode
- AssignmentNode
- LogicalExpressionNode
- FunctionBlockCallNode
- CaseStatementNode

The AST section should visually look hierarchical and recursive.

Then create a central “Recursive Semantic Traversal Engine” layer representing visitor.py.

This should be the visual core of the architecture.

Show:
visit(node)
→ dynamic dispatch
→ visit_NodeType()
→ recursive child traversal

Visually emphasize that the SAME recursive visitor infrastructure is reused by multiple semantic systems.

From this traversal engine branch into three semantic processing subsystems:

1. TypeChecker
- semantic legality checks
- type inference
- symbol table propagation
- assignment validation

Show symbol table flow:
variable → inferred type

2. IndustrialSemanticClassifier
- industrial behavior understanding
- safety logic interpretation
- timer semantics
- process control semantics
- actuator coordination

Include labels such as:
- SAFETY_INTERLOCK
- TIMER_DEPENDENT_CONTROL
- PROCESS_ENABLE_CONDITION
- EMERGENCY_SHUTDOWN

3. RelationshipExtractor
- semantic dependency extraction
- condition stack propagation
- semantic context tracking
- industrial interaction reasoning

Show examples such as:
SafetyOK enables Motor
PressureHigh disables Pump
TON_Timer activates Mixer

Visually emphasize that these are semantic dependency relationships, not AST parent-child relationships.

Then flow into a “Semantic Graph Generation Layer” representing:
- graph_builder.py
- semantic_graph.py

Show:
Relationship Objects
→ GraphBuilder
→ SemanticGraph topology

Visually represent:
- graph nodes
- dependency edges
- adjacency mappings
- industrial interaction topology

Use graph-like connected structures resembling industrial dependency networks.

Finally, create a faded/dashed “Future Transformation Infrastructure” layer showing:
- Industrial IR Generation
- IEC61499 Transformation
- Semantic Verification
- Dependency Orchestration
- Industrial Graph Reasoning

The entire diagram should visually communicate:
syntax → structure → traversal → semantic understanding → dependency inference → graph topology → future industrial transformation.

Use grouped layers, elegant directional arrows, semantic grouping, recursive traversal indicators, dependency-flow visuals, and modern industrial systems aesthetics.