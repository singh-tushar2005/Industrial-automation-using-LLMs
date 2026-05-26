# Semantic Graph Architecture

> Connected industrial semantic topology for transformation-oriented behavior modeling.

---

## 1. Purpose

The semantic graph subsystem transforms isolated semantic relationship edges into a connected industrial topology. Where the RelationshipExtractor identifies that `SafetyOK enables Motor`, the semantic graph represents `SafetyOK` and `Motor` as typed nodes connected by a directed `enables` edge within an explorable graph structure.

This is the transition from flat edge extraction toward structured topology modeling:

```text
isolated relationship edges
    ↓
connected semantic graph
    ↓
future dependency analysis / IR generation
```

The graph is:
- **symbolic**: no machine learning, no external databases
- **transformation-oriented**: designed for future IEC 61499 event network and industrial IR generation
- **passive**: it stores topology; it does not infer meaning or traverse AST structures

---

## 2. Architectural Position

```text
parser
    ↓
AST
    ↓
type checker ─────▶ type report
    ↓                 │
classifier ◀─────────┘
    ↓
relationship extractor
    ↓
relationship objects (flat)
    ↓
semantic graph builder
    ↓
semantic graph topology
    ↓
graph visualizer
    ↓
visual output (PNG / SVG)
    ↓
future: graph reasoning / IR generation / IEC 61499 transformation
```

The graph layer sits downstream of all semantic inference. It consumes structured relationship data and produces a queryable topology. The visualizer is the final presentation layer: it renders topology into human-readable diagrams without modifying graph structure.

---

## 3. Core Components

### 3.1 SemanticGraphNode

Represents one industrial entity.

```text
node_id          unique identifier (variable name, signal name)
node_kind        industrial classification: signal, actuator, timer, alarm,
                 process_variable, counter, mode, unknown
metadata         optional transformation-oriented annotations
```

Nodes are deduplicated by `node_id`. Two nodes with the same identifier are considered the same industrial entity regardless of how they were introduced.

### 3.2 SemanticGraphEdge

Represents one directed semantic dependency.

```text
source           node_id of the origin entity
relation         behavioral type: enables, disables, triggers, activates,
                 sequences, depends_on
target           node_id of the affected entity
metadata         provenance from relationship extraction (condition text,
                 assignment context, classification tags)
```

Edges are directed and deduplicated by `(source, relation, target)`.

### 3.3 SemanticGraph

The connected topology container.

Responsibilities:
- store nodes and edges
- maintain adjacency mappings (`outgoing`, `incoming`)
- support traversal queries (`neighbors`, `predecessors`, `outgoing_edges`, `incoming_edges`)
- expose summary statistics and serialization

Not responsible for:
- semantic inference
- AST traversal
- relationship extraction
- visualization rendering

---

## 4. Node Kind Inference

Node kinds are inferred from industrial naming conventions using symbolic pattern matching. The inference layer recognizes terms common in IEC 61131-3 Structured Text programs.

| Kind | Example Names | Pattern Terms |
|------|---------------|---------------|
| signal | `SafetyOK`, `StartButton`, `AutoMode` | Safety, Guard, Door, Start, Stop, Button, Command, Enable, Ready, Mode, Run, Done |
| actuator | `Motor`, `Pump`, `InletValve` | Motor, Pump, Valve, Heater, Mixer, Conveyor, Clamp, Cutter, Contactor, Cylinder, Fan, Blower, Compressor, Solenoid |
| timer | `TON_Delay`, `PulseTimer` | TON, TOF, TP, Timer |
| alarm | `HighTempAlarm`, `FaultWarning` | Alarm, Warning, Fault, Trip |
| process_variable | `PressureHigh`, `TankLevel` | Pressure, Temp, Temperature, Level, Limit, Flow, Speed, Position, Current, Voltage, Torque |
| counter | `PartCounter`, `CTU_Steps` | CTU, CTD, CTUD, Counter |
| mode | `AutoMode`, `SequenceStep` | Mode, Auto, Manual, State, Step, Sequence |
| unknown | `X`, `T#250ms`, numeric literals | fallback when no pattern matches |

Inference is best-effort and symbolic. It does not use type information from the symbol table. This keeps the graph layer decoupled from the type checker while providing useful industrial categorization for downstream analysis.

---

## 5. Graph Semantics

The semantic graph is **not** an AST graph. AST graphs represent syntactic nesting: an `IfStatementNode` contains a `BinaryExpressionNode` which contains `VariableNode` operands. The semantic graph represents industrial behavioral dependencies across control entities.

```text
AST graph (syntax):
    IfStatementNode
        ├── BinaryExpressionNode
        │       ├── VariableNode(SafetyOK)
        │       └── VariableNode(GuardClosed)
        └── BlockNode
                └── AssignmentNode
                        ├── VariableNode(Motor)
                        └── BooleanNode(TRUE)

Semantic graph (behavior):
    SafetyOK ── enables ──► Motor
    GuardClosed ── enables ──► Motor
```

The semantic graph encodes:
- **industrial dependencies**: which signals affect which actuators
- **behavioral topology**: the control flow of the process, not the syntax tree
- **process interactions**: safety interlocks, permissives, alarms, sequencing
- **semantic propagation**: how conditions propagate through the control system
- **sequencing behavior**: stateful orderings such as CASE branch progression

---

## 6. Relationship Edge Flow

Relationship edges flow from the RelationshipExtractor through the GraphBuilder into the SemanticGraph. The extractor performs semantic inference; the builder performs graph assembly. This separation is strict.

```text
RelationshipExtractor
    infers:  "SafetyOK enables Motor"
    produces: Relationship(source="SafetyOK", relation="enables", target="Motor")

SemanticGraphBuilder
    consumes: Relationship objects
    infers node kinds: SafetyOK → signal, Motor → actuator
    creates: SemanticGraphNode, SemanticGraphEdge
    assembles: SemanticGraph with adjacency mappings
```

The builder does not re-derive whether `SafetyOK` should `enable` or `disable` `Motor`. That decision was made by the extractor. The builder only translates the already-derived relationship into graph structure.

---

## 7. Semantic Dependency Propagation

Dependencies in the graph propagate according to edge direction. The adjacency mappings make this propagation queryable:

- **Downstream analysis**: from `SafetyOK`, follow `outgoing_edges` to discover all actuators gated by the safety signal.
- **Upstream analysis**: from `Motor`, follow `incoming_edges` to discover all conditions that must be satisfied before the motor can run.
- **Sequencing chains**: follow `sequences` edges to reconstruct stateful orderings such as `Step1 → Step2 → Step3`.
- **Fault isolation**: from an alarm node, trace `triggers` and `activates` edges backward to find root causes.

These queries support future transformation tasks such as:
- event network construction for IEC 61499 function blocks
- safety integrity level analysis
- actuator coordination group identification
- timer dependency chain extraction

---

## 8. Graph Generation Pipeline

The graph is generated as the final stage of the per-file analysis pipeline in `main.py`:

```text
parse_st_file(file)
    ↓
run_semantic_traversal(ast)
    ↓
run_type_checking(ast)
    ↓
run_industrial_classification(ast, type_report)
    ↓
run_relationship_extraction(ast, classification_report, type_report)
    ↓
run_graph_generation(relationship_report)
    ↓
SemanticGraph object
```

The graph is included in the per-file result dictionary and printed in both normal and debug reporting modes. The output shows:
- node count
- edge count
- node-kind distribution
- dependency listing

---

## 9. Future IR Integration Direction

The semantic graph is designed as an intermediate structure between relationship extraction and industrial IR generation.

Planned future integration:

```text
SemanticGraph
    ↓
graph traversal / dependency analysis
    ↓
industrial IR nodes
    ↓
IEC 61499 event network generation
    ↓
FB mapping and distributed execution modeling
```

The graph topology can be queried to produce:
- **event connections**: which timer done outputs should trigger which actuator function blocks
- **data flow**: which process variables should feed into which comparison guards
- **safety regions**: clusters of nodes connected by `enables` and `disables` edges that form safety-critical subgraphs
- **sequencing state machines**: chains of `sequences` edges that map to IEC 61499 ECC (Execution Control Chart) transitions

Because the graph is passive and serializable (`to_dict`), future IR generators can consume it without depending on the AST, parser, or visitor systems.

---

## 10. Graph Visualization Architecture

The visualization layer (`semantic/graph_visualizer.py`) renders SemanticGraph topology into industrial dependency diagrams using Graphviz.

### 10.1 Design Principle

The visualizer is **strictly a rendering layer**. It does not:
- perform semantic inference
- modify graph topology
- extract new relationships
- rebuild graph logic

It only:
- consumes an existing SemanticGraph
- maps node kinds to visual shapes and colors
- maps edge relations to visual colors and labels
- generates PNG and SVG output files

### 10.2 Visual Encoding

**Node shapes by kind:**

| Kind | Graphviz Shape | Visual Meaning |
|------|----------------|----------------|
| signal | ellipse | control signal, permissive, input |
| actuator | box | physical output, motor, pump, valve |
| timer | hexagon | time-dependent function block |
| alarm | diamond | fault indication, warning state |
| process_variable | cylinder | measured value, sensor reading |
| counter | doubleoctagon | stateful counting element |
| mode | box (rounded) | operational mode, state selector |
| unknown | ellipse | unclassified entity |

**Edge colors by relation:**

| Relation | Color | Visual Meaning |
|----------|-------|----------------|
| enables | green | permissive or safety-gating behavior |
| disables | red | protective shutdown or fault response |
| triggers | blue | event-like activation (timers, alarms) |
| activates | purple | timer-done or sequence activation |
| sequences | orange | stateful ordering or step progression |
| depends_on | gray | generic dependency edge |

### 10.3 Subsystem Clusters

The visualizer groups nodes into cluster subgraphs when node names match subsystem heuristics:

- **Safety Subsystem**: Safety, Guard, Door, EStop, Emergency, Interlock
- **Process Subsystem**: Pressure, Temp, Temperature, Level, Flow, Speed, Limit
- **Actuator Subsystem**: Motor, Pump, Valve, Heater, Mixer, Conveyor, Clamp, Cutter
- **Timer Subsystem**: TON, TOF, TP, Timer

Clusters use distinct background colors and rounded borders to visually separate behavioral regions.

### 10.4 Output

Rendered files are stored in `outputs/graphs/`:

```text
outputs/graphs/
    tank_control_graph.png
    tank_control_graph.svg
    emergency_shutdown_graph.png
    emergency_shutdown_graph.svg
```

Each file includes a title with node count and edge count.

---

## 11. Responsibility Separation

| Layer | Responsible For | Not Responsible For |
|-------|-----------------|---------------------|
| RelationshipExtractor | Semantic inference, AST traversal, deriving industrial meaning from conditions and assignments | Building graph topology, managing adjacency, creating graph traversal systems |
| SemanticGraph (semantic_graph.py) | Storing nodes, edges, adjacency mappings; supporting graph queries | Semantic extraction, AST traversal, industrial inference, visualization rendering |
| SemanticGraphBuilder (graph_builder.py) | Converting relationships to graph structures, node kind inference, assembling connected topology | AST traversal, relationship inference, re-implementing extraction logic |
| SemanticGraphVisualizer (graph_visualizer.py) | Rendering graph topology into visual diagrams (PNG/SVG) | Semantic inference, graph modification, relationship extraction |

The dependency direction is:

```text
graph_builder.py
        ↓
semantic_graph.py
        ↓
graph_visualizer.py
```

`semantic_graph.py` does not depend on `graph_builder.py` or `graph_visualizer.py`. It remains a reusable, independent data structure layer. The visualizer depends only on the graph data structure, not on the builder, extractor, or parser.
