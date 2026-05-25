# Semantic Graph Deep Dive

> Execution flow, adjacency mechanics, and topology formation for industrial semantic graph construction.

---

## 1. Purpose

This document explains the internal mechanics of semantic graph construction. It covers:

- how flat relationship edges become connected graph topology
- how nodes are created, normalized, and typed
- how edges are created and deduplicated
- how adjacency mappings are built and maintained
- how the graph supports future industrial reasoning

---

## 2. Graph Construction Execution Flow

The graph is built in a single pass over the relationship extraction output. The execution flow is:

```text
RelationshipExtractor.extract(ast)
    ↓
relationship_report = {
    "relationships": [
        {"source": "SafetyOK", "relation": "enables", "target": "Motor", ...},
        {"source": "PressureHigh", "relation": "disables", "target": "Pump", ...},
        ...
    ]
}
    ↓
SemanticGraphBuilder.build(relationship_report)
    ↓
for each relationship in relationships:
    infer_node_kind(source)  → signal
    infer_node_kind(target)  → actuator
    create SemanticGraphNode(source)
    create SemanticGraphNode(target)
    add nodes to graph (deduplicated by node_id)
    create SemanticGraphEdge(source, relation, target)
    add edge to graph (deduplicated by source+relation+target)
    update outgoing[source] adjacency list
    update incoming[target] adjacency list
    ↓
return SemanticGraph
```

The builder performs no AST traversal. It iterates only over the flat relationship list produced by the extractor.

---

## 3. How Nodes Are Created

### 3.1 Node Creation Trigger

Every relationship has a `source` and a `target`. Both become nodes. Even if the same identifier appears in multiple relationships, it is created only once.

Example:

```text
Relationship 1: SafetyOK enables Motor
Relationship 2: GuardClosed enables Motor
Relationship 3: Motor sequences Conveyor
```

Nodes created:

```text
SafetyOK    (signal)
GuardClosed (signal)
Motor       (actuator)
Conveyor    (actuator)
```

`Motor` appears twice but is stored once. The graph's `add_node` method checks `node_id` before insertion.

### 3.2 Node Kind Inference

Node kinds are determined by `SemanticGraphBuilder.infer_node_kind()`. The inference applies pattern tests in priority order:

```text
1. is_timer(name)          → "timer"
2. is_counter(name)        → "counter"
3. is_alarm(name)          → "alarm"
4. is_actuator(name)       → "actuator"
5. is_process_variable(name) → "process_variable"
6. is_mode(name)           → "mode"
7. is_signal(name)         → "signal"
8. fallback                → "unknown"
```

Priority order matters. A name like `MixTimer` contains both "Mix" (actuator-like) and "Timer" (timer-like), but the timer test runs first and correctly classifies it as `timer`.

### 3.3 Node Metadata

Each node carries a minimal metadata dictionary:

```text
{"inferred_kind": True}
```

This flag indicates that the kind was derived heuristically rather than declared explicitly. Future systems may use this to refine classification with additional context (symbol table types, external device descriptions, manual annotations).

---

## 4. How Edges Are Created

### 4.1 Edge Creation Trigger

Every relationship in the input report generates one edge attempt. The edge is created with:

```text
source   = relationship["source"]
relation = relationship["relation"]
target   = relationship["target"]
metadata = relationship.get("metadata", {})
```

### 4.2 Edge Deduplication

The graph deduplicates edges by `(source, relation, target)`. If the same triple appears more than once in the relationship report, only one edge is stored.

Example from real dataset output:

```text
Relationships (from extractor):
    PulseTimer.Q activates Cutter
    PulseTimer.Q activates Cutter

Graph edges (after deduplication):
    PulseTimer.Q activates Cutter  (stored once)
```

Deduplication is important because the RelationshipExtractor may emit duplicate edges when multiple AST traversal paths encounter the same semantic interaction. The graph layer normalizes these into a clean topology.

### 4.3 Edge Metadata Preservation

Edge metadata carries provenance from the extractor. For a typical condition-gated assignment, the metadata includes:

```text
{
    "condition": "SafetyOK AND GuardClosed",
    "assignment": "Motor := TRUE",
    "node_type": "AssignmentNode",
    "classification_tags": ["SAFETY_INTERLOCK", "PROCESS_ENABLE_CONDITION"]
}
```

This metadata enables future traceability: from a graph edge, one can trace back to the AST node type, the original condition text, and the industrial classifications that justified the relationship.

---

## 5. Adjacency Mapping Logic

### 5.1 Internal Data Structures

The SemanticGraph maintains three internal mappings:

```text
_nodes     dict[node_id] → SemanticGraphNode
_outgoing  dict[node_id] → list[SemanticGraphEdge]
_incoming  dict[node_id] → list[SemanticGraphEdge]
```

When a node is added:

```text
_nodes[node_id] = node
_outgoing[node_id] = []
_incoming[node_id] = []
```

When an edge is added:

```text
_outgoing[edge.source].append(edge)
_incoming[edge.target].append(edge)
```

### 5.2 Adjacency Query Semantics

The adjacency lists support directed graph traversal:

- `outgoing_edges("SafetyOK")` returns all edges where `source == "SafetyOK"`
- `incoming_edges("Motor")` returns all edges where `target == "Motor"`
- `neighbors("SafetyOK")` returns the set of distinct targets reachable from `"SafetyOK"`
- `predecessors("Motor")` returns the set of distinct sources that reach `"Motor"`

These operations are O(1) lookup followed by list iteration. The adjacency lists are built incrementally during graph construction rather than computed lazily, ensuring that summary and traversal operations are fast after construction.

### 5.3 Example Adjacency State

After processing:

```text
SafetyOK enables Motor
GuardClosed enables Motor
Motor sequences Conveyor
```

The internal state is:

```text
_nodes:
    "SafetyOK"    → SemanticGraphNode("SafetyOK", "signal")
    "GuardClosed" → SemanticGraphNode("GuardClosed", "signal")
    "Motor"       → SemanticGraphNode("Motor", "actuator")
    "Conveyor"    → SemanticGraphNode("Conveyor", "actuator")

_outgoing:
    "SafetyOK"    → [Edge(SafetyOK, enables, Motor)]
    "GuardClosed" → [Edge(GuardClosed, enables, Motor)]
    "Motor"       → [Edge(Motor, sequences, Conveyor)]
    "Conveyor"    → []

_incoming:
    "SafetyOK"    → []
    "GuardClosed" → []
    "Motor"       → [Edge(SafetyOK, enables, Motor),
                       Edge(GuardClosed, enables, Motor)]
    "Conveyor"    → [Edge(Motor, sequences, Conveyor)]
```

---

## 6. Semantic Topology Formation

### 6.1 From Flat Edges to Connected Structure

The key transformation performed by the GraphBuilder is converting a flat list of edges into a structure where shared nodes link separate relationships into a connected topology.

Flat relationship view:

```text
SafetyOK enables Motor
GuardClosed enables Motor
Motor sequences Conveyor
PressureHigh disables Pump
```

These are four independent statements. The graph reveals the connected structure:

```text
SafetyOK ──► Motor ──► Conveyor
GuardClosed ──► Motor

PressureHigh ──► Pump
```

`Motor` is a shared node that connects the safety/permissive subgraph to the sequencing subgraph. This shared-node connectivity is the foundation of future dependency analysis.

### 6.2 Subgraph Identification

Shared nodes naturally form boundaries between behavioral regions:

- **Safety subgraph**: nodes reachable from `SafetyOK` via `enables` edges
- **Alarm subgraph**: nodes connected by `triggers` edges to alarm nodes
- **Sequencing chain**: nodes connected by `sequences` edges
- **Timer activation subgraph**: nodes connected by `activates` edges from timer outputs

Future graph reasoning can traverse these subgraphs using the adjacency mappings without re-parsing the original Structured Text.

---

## 7. Relationship-to-Graph Transformation

The transformation from `Relationship` objects to `SemanticGraph` topology is a mechanical assembly process. It does not reinterpret semantics.

| Relationship Field | Graph Counterpart | Transformation |
|--------------------|-------------------|----------------|
| `source` | `SemanticGraphNode.node_id` | create node if absent |
| `relation` | `SemanticGraphEdge.relation` | pass through directly |
| `target` | `SemanticGraphNode.node_id` | create node if absent |
| `metadata` | `SemanticGraphEdge.metadata` | pass through directly |

The only enrichment added by the builder is node kind inference. The builder adds no new edges, modifies no relations, and drops no relationships (except empty source/target identifiers).

---

## 8. Future Industrial Graph Reasoning

The semantic graph is designed to support future reasoning operations that operate on topology rather than AST syntax.

### 8.1 Planned Query Types

**Reachability analysis**: determine whether a safety signal can influence a given actuator through any path.

**Cycle detection**: detect circular dependencies such as `Motor` enabling `Conveyor` and `Conveyor` enabling `Motor`, which may indicate feedback loops or state machine transitions.

**Topological sorting**: order actuator activations by dependency direction for safe startup sequences.

**Critical path analysis**: identify the longest chain of dependencies from a process variable to an actuator for timing analysis.

### 8.2 IEC 61499 Mapping

The graph structure maps naturally to IEC 61499 concepts:

| Graph Concept | IEC 61499 Concept |
|---------------|-------------------|
| node | function block (FB) instance |
| edge | event connection or data connection |
| `enables` / `disables` | event input with guard condition |
| `triggers` | event output triggered by signal change |
| `activates` | timer done output → downstream FB event |
| `sequences` | ECC (Execution Control Chart) transition |
| `depends_on` | data dependency or parameter binding |

Future IR generation will traverse the graph to produce FB network specifications:

```text
for each node in graph.nodes():
    create FB instance from node_kind

for each edge in graph.edges():
    create event/data connection from edge.relation
```

### 8.3 Extensibility

The graph is intentionally passive. Future extensions can add:

- **node attributes**: current value, data type, scan cycle timing
- **edge weights**: propagation delay, safety integrity level (SIL)
- **subgraph annotations**: safety-critical region, non-safety region
- **temporal annotations**: timer preset values, scan cycle constraints

These extensions will not require changes to the core graph structure. They can be added as metadata fields, keeping the system modular and backward-compatible.

---

## 9. Key Invariants

1. **Node uniqueness**: `has_node(node_id)` is true iff `_nodes[node_id]` exists.
2. **Edge uniqueness**: no two edges with identical `(source, relation, target)` are stored.
3. **Adjacency consistency**: every stored edge appears in exactly one `_outgoing[source]` list and one `_incoming[target]` list.
4. **Kind correctness**: every node has a kind in the `NODE_KINDS` set.
5. **Relation correctness**: every edge has a relation in the `EDGE_RELATIONS` set.
6. **Passive behavior**: adding a node or edge never triggers inference, traversal, or side effects.

---

## 10. Integration with the Existing Semantic Pipeline

The graph integrates into the existing pipeline as the final per-file analysis stage. It reuses no traversal logic from the visitor, classifier, or extractor. It only consumes their output.

This means:
- the graph can be rebuilt from cached relationship reports
- the graph can be constructed from manually authored relationship data
- the graph can be tested in isolation without running the parser or visitor
- the graph layer can be replaced with an external graph library (e.g., networkx) without changing the extractor or builder logic

The separation between inference (extractor) and assembly (builder) makes the graph layer robust to future pipeline changes.
