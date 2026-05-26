# Graph Visualizer Deep Dive

> Rendering industrial semantic topology into human-readable dependency diagrams.

---

## 1. Purpose

The graph visualizer transforms an abstract SemanticGraph into a concrete visual diagram. Where the SemanticGraph stores `SafetyOK` as a `signal` node and `Motor` as an `actuator` node connected by an `enables` edge, the visualizer renders this as a blue ellipse labeled "SafetyOK" connected by a green arrow to a green rectangle labeled "Motor".

This is the transition from machine-readable topology to human-readable industrial dependency maps:

```text
SemanticGraph (data structure)
    ↓
Graphviz Digraph (intermediate representation)
    ↓
PNG / SVG (visual output)
```

The visualizer is the final layer in the per-file analysis pipeline. It operates only on existing graph state and produces no new semantic information.

---

## 2. Architectural Position

```text
IEC Logic
    ↓
AST
    ↓
RelationshipExtractor
    ↓
SemanticGraphBuilder
    ↓
SemanticGraph
    ↓
GraphVisualizer          ← this document
    ↓
outputs/graphs/*.png
outputs/graphs/*.svg
```

The visualizer sits downstream of the entire semantic pipeline. It receives a fully populated SemanticGraph and generates visual artifacts. It never feeds back into the semantic inference chain.

---

## 3. Rendering Pipeline

The visualizer converts a SemanticGraph into a Graphviz `Digraph` in a single pass:

```text
SemanticGraph
    ├── nodes[]
    │       └── for each node:
    │               map node_kind → shape
    │               map node_kind → border color
    │               map node_kind → fill color
    │               add to graph (or cluster subgraph)
    │
    └── edges[]
            └── for each edge:
                    map relation → edge color
                    map relation → pen width
                    add labeled directed edge
```

The `build_dot()` method performs this conversion. The `render()` method then calls Graphviz to produce PNG and SVG files.

---

## 4. How Nodes Become Visual Elements

### 4.1 Node-to-Shape Mapping

Each `SemanticGraphNode` carries a `node_kind`. The visualizer maps this kind to a Graphviz shape:

```text
signal           → ellipse
actuator         → box
timer            → hexagon
alarm            → diamond
process_variable → cylinder
counter          → doubleoctagon
mode             → box (with rounded style)
unknown          → ellipse
```

These shapes are chosen for industrial recognizability:
- **ellipse** for signals: soft, input-like, control-flow origins
- **box** for actuators: solid, physical, output-like
- **hexagon** for timers: distinctive, mechanical, time-element feel
- **diamond** for alarms: warning symbol, attention-grabbing
- **cylinder** for process variables: database/sensor metaphor, measured quantities
- **doubleoctagon** for counters: layered, stateful, countable

### 4.2 Node-to-Color Mapping

Each kind also receives a consistent color pair (border + fill):

```text
signal           border=#3498db  fill=#ebf5fb   (blue family)
actuator         border=#27ae60  fill=#e9f7ef   (green family)
timer            border=#f39c12  fill=#fef5e7   (amber family)
alarm            border=#e74c3c  fill=#fdedec   (red family)
process_variable border=#9b59b6  fill=#f4ecf7   (purple family)
counter          border=#1abc9c  fill=#e8f8f5   (teal family)
mode             border=#e67e22  fill=#fef5e7   (orange family)
unknown          border=#7f8c8d  fill=#f2f3f4   (gray family)
```

Border colors are saturated; fill colors are pale tints of the same hue. This creates readable, accessible diagrams without harsh contrast.

### 4.3 Node Rendering Code Path

The `_add_node()` method constructs the Graphviz node statement:

```text
target.node(
    node.node_id,               # Graphviz node identifier
    label=node.node_id,         # displayed text
    shape=shape,                # from NODE_SHAPE_MAP
    color=color,                # border color
    fillcolor=fillcolor,        # background color
    style=style,                # filled, optionally rounded
    fontcolor=color,            # text matches border hue
    penwidth="2.0",             # thicker borders for classified nodes
)
```

Node identifiers are passed through Graphviz as raw strings. Graphviz handles quoting internally.

---

## 5. How Edges Become Topology Connections

### 5.1 Edge-to-Color Mapping

Each `SemanticGraphEdge` carries a `relation`. The visualizer maps this to a visual edge color:

```text
enables    → #27ae60  (green)   penwidth 2.0
disables   → #c0392b  (red)     penwidth 2.2
triggers   → #2980b9  (blue)    penwidth 1.8
activates  → #8e44ad  (purple)  penwidth 1.8
sequences  → #d68910  (orange)  penwidth 1.6
depends_on → #7f8c8d  (gray)    penwidth 1.4
```

Thicker pen widths for semantically stronger relations (`enables`, `disables`) draw visual attention to safety-critical and control-critical edges. Thinner widths for generic dependencies (`depends_on`) recede visually.

### 5.2 Edge Rendering Code Path

The `_render_edges()` method constructs each Graphviz edge statement:

```text
dot.edge(
    edge.source,              # source node_id
    edge.target,              # target node_id
    label=relation,           # displayed relation text
    color=edge_color,         # line color
    fontcolor=edge_color,     # label color matches line
    penwidth=penwidth,        # line thickness
)
```

All edges use `arrowhead="vee"` and `arrowsize="0.9"` for clean, modern directional indicators.

### 5.3 Visual Semantics of Edge Colors

The color choices encode industrial meaning at a glance:

- **green (`enables`)**: permissive, safe, go-ahead
- **red (`disables`)**: stop, fault, protective action
- **blue (`triggers`)**: event initiation, start signal
- **purple (`activates`)**: timer completion, sequence advance
- **orange (`sequences`)**: step ordering, state progression
- **gray (`depends_on`)**: background dependency, data flow

An engineer viewing the diagram can immediately distinguish safety-gating edges from sequencing edges without reading every label.

---

## 6. Subsystem Clustering

### 6.1 Cluster Assignment Logic

The visualizer attempts to group nodes into behavioral subsystems using naming heuristics. The `_assign_clusters()` method checks each node identifier against keyword lists:

```text
safety  → Safety, Guard, Door, EStop, Emergency, Interlock
process → Pressure, Temp, Temperature, Level, Flow, Speed, Limit
actuator → Motor, Pump, Valve, Heater, Mixer, Conveyor, Clamp, Cutter
timer   → TON, TOF, TP, Timer
```

A node belongs to the first subsystem whose keyword list matches its name. Nodes that match no list remain unclustered.

### 6.2 Cluster Visual Rendering

Clustered nodes are placed inside Graphviz `subgraph` blocks with `cluster_` naming. Each cluster receives:

- a rounded, filled background rectangle
- a label (e.g., "Actuator Subsystem")
- a pale color distinct from other clusters

```text
cluster_safety   → background #fadbd8 (light red)
cluster_process  → background #d6eaf8 (light blue)
cluster_actuator → background #d5f5e3 (light green)
cluster_timer    → background #fcf3cf (light amber)
```

Clustering is optional and best-effort. The diagram remains valid and readable even when no clusters are formed.

### 6.3 Cluster Formation Example

For a tank control program:

```text
Nodes:
    TankLevel        → process_variable → cluster_process
    LevelLimit       → process_variable → cluster_process
    InletValve       → actuator         → cluster_actuator
    OutletValve      → actuator         → cluster_actuator
    EmergencyStop    → signal           → cluster_safety
    Alarm            → alarm            → (no cluster match)
```

The resulting diagram shows three colored regions connected by dependency edges crossing cluster boundaries.

---

## 7. Graph Layout

### 7.1 Direction

The visualizer uses `rankdir="LR"` (left-to-right). This aligns with the pipeline's semantic flow: signals and process variables on the left, actuators and alarms on the right.

### 7.2 Spacing

Graphviz parameters:

```text
nodesep="0.55"   horizontal space between nodes
ranksep="1.1"    vertical space between ranks
splines="true"   curved edges (reduces visual overlap)
overlap="false"  prevent node collision
```

These values produce diagrams that are compact but not cluttered.

### 7.3 Title and Metadata

Each diagram includes a title at the top:

```text
Industrial Semantic Dependency Graph
Nodes: 14   Edges: 18
```

The title provides immediate context about graph scale. It is positioned at the top center (`labelloc="t"`, `labeljust="c"`).

---

## 8. Why Visualization Is Separate from Semantic Inference

The visualizer is intentionally isolated from all semantic reasoning. This separation provides several architectural benefits:

1. **Idempotency**: rendering the same graph twice produces identical output. No side effects.
2. **Replaceability**: the visualizer can be replaced with a different rendering backend (e.g., networkx + matplotlib, D3.js, PlantUML) without changing graph construction logic.
3. **Testability**: visual output can be tested independently from semantic correctness.
4. **Performance**: graph construction and visualization can run on different schedules. A CI pipeline might build graphs continuously but render visuals only on demand.
5. **Safety**: the visualizer cannot accidentally modify graph topology, drop edges, or reinterpret semantics.

This follows the same principle that separates `SemanticGraph` (data) from `SemanticGraphBuilder` (construction): each layer has one responsibility.

---

## 9. Integration with main.py

The visualizer integrates into the per-file pipeline as the final stage:

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
run_graph_visualization(semantic_graph, output_name)
    ↓
outputs/graphs/<name>_graph.png
outputs/graphs/<name>_graph.svg
```

The output name is derived from the dataset filename:

```text
datasets/tank_control.st  →  tank_control_graph
datasets/fault_handling/fault_latch_recovery.st  →  fault_latch_recovery_graph
```

After processing all files, `main.py` prints a consolidated list of all generated visualization paths in the Pipeline Summary.

---

## 10. Future Graph Reasoning Possibilities

The visualizer currently produces static diagrams. Future extensions could include:

- **Interactive SVG**: embed JavaScript in SVG output for hover tooltips showing edge metadata (condition text, assignment context, classification tags)
- **Diff visualization**: compare two graph versions to highlight added or removed dependencies
- **Highlighting modes**: color nodes by safety integrity level, by scan cycle, or by transformation priority
- **Layered views**: toggle visibility of specific relation types (show only `enables`/`disables` for safety analysis)
- **Animated sequences**: show `sequences` edge traversal as an animation for step verification

All of these extensions are possible because the visualizer consumes a clean, passive data structure. They require no changes to the parser, visitor, classifier, extractor, or graph builder.

---

## 11. Key Invariants

1. **Read-only**: the visualizer never modifies the input SemanticGraph.
2. **Deterministic**: given the same SemanticGraph, `build_dot()` produces the same Graphviz source.
3. **No inference**: node kinds and edge relations come from the graph; the visualizer does not re-classify.
4. **Fallback-safe**: unknown kinds and relations receive neutral gray styling rather than failing.
5. **Cluster optional**: diagrams are valid with or without subsystem clusters.
