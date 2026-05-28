# Dependency Reasoning Architecture

> Higher-order semantic graph reasoning for industrial dependency propagation and topology interpretation.

---

## 1. Purpose

The dependency reasoning subsystem transforms a static SemanticGraph into interpreted industrial knowledge. Where the graph answers:

```text
What dependencies exist?
```

The reasoner answers:

```text
What do these dependencies imply?
```

It performs:
- transitive influence analysis
- safety chain reasoning
- critical path identification
- upstream and downstream dependency discovery
- subsystem impact mapping

This is the first subsystem in the pipeline that reasons over graph topology rather than AST structure.

---

## 2. Architectural Position

```text
IEC Logic
    ↓
AST
    ↓
Semantic Classification
    ↓
Relationship Extraction
    ↓
GraphBuilder
    ↓
SemanticGraph
    ↓
DependencyReasoner          ← this subsystem
    ↓
reasoning report
    ↓
future: orchestration decisions / safety verification / IR generation
```

The reasoner sits downstream of the graph data structure. It consumes topology and produces structured reasoning. It does not feed back into graph construction or semantic extraction.

---

## 3. Core Distinction: Graph Reasoning vs. AST Traversal

| | AST Traversal | Graph Reasoning |
|---|---|---|
| Question | "What logic structure exists?" | "How industrial behavior propagates?" |
| Structure | tree (nesting) | directed graph (dependencies) |
| Traversal | recursive descent over syntax | DFS/BFS over topology |
| Nodes | `IfStatementNode`, `AssignmentNode` | `Motor`, `SafetyOK`, `TON_Timer` |
| Edges | parent-child containment | `enables`, `disables`, `activates` |
| Output | structural metadata | behavioral influence chains |

This distinction is fundamental. The reasoner does not care how the original Structured Text was parsed. It only cares how industrial entities influence one another through the dependency network.

---

## 4. Core Components

### 4.1 DependencyChain

Represents one transitive influence path through the graph.

```text
source            origin node identifier
target            terminal node identifier
path_edges        ordered list of SemanticGraphEdge objects
depth             number of edges in the path
influence_type    inferred industrial meaning: positive/permissive,
                  negative/protective, sequential, conditional, complex/mixed
summary           human-readable traversal description
```

Example:

```text
source:         EmergencyStop
target:         Pump
path_edges:     [EmergencyStop --disables--> Motor, Motor --activates--> Pump]
depth:          2
influence_type: negative / protective
summary:        EmergencyStop → disables Motor → activates Pump
```

### 4.2 DependencyReasoner

The analysis engine. It consumes a SemanticGraph and provides reasoning methods.

Responsibilities:
- downstream dependency discovery
- upstream dependency discovery
- transitive reachability analysis
- safety chain identification
- timer chain identification
- critical path extraction
- subsystem influence mapping

Not responsible for:
- modifying graph topology
- extracting relationships from AST
- performing semantic classification
- generating visual output

---

## 5. Reasoning Methods

### 5.1 Downstream Dependencies

**Question:** "What systems are affected by this node?"

The reasoner performs DFS from a starting node, following outgoing edges. Each path of length ≥ 2 becomes a DependencyChain. Paths of length 1 are direct dependencies.

Example:

```text
Starting from: SafetyOK
Paths found:
    SafetyOK → enables Motor
    SafetyOK → enables Motor → activates Conveyor
    SafetyOK → enables Motor → sequences Step2
```

### 5.2 Upstream Dependencies

**Question:** "What influences this node?"

The reasoner performs DFS in reverse, following incoming edges backward from a target node.

Example:

```text
Starting from: Motor
Paths found:
    SafetyOK → enables Motor
    GuardClosed → enables Motor
    EmergencyStop --(disables)--> Motor
```

### 5.3 Transitive Dependencies

**Question:** "What is the full set of reachable nodes?"

Uses BFS to compute the transitive closure of reachable targets from a source node. Returns a flat set of node identifiers.

### 5.4 Safety Chain Reasoning

**Question:** "What safety-critical propagation paths exist?"

A safety chain is any DependencyChain that:
- contains an `enables` or `disables` edge, OR
- involves a node whose name contains safety-related terms (Safety, Guard, Door, EStop, Emergency, Interlock, Fault)

These chains represent interlock logic, permissive gating, and protective shutdown paths.

### 5.5 Timer Chain Reasoning

**Question:** "What behavior depends on timer completion?"

A timer chain originates from any node whose name contains timer keywords (TON, TOF, TP, Timer). These chains reveal time-dependent activation sequences.

### 5.6 Critical Path Analysis

**Question:** "What are the longest and most connected dependency chains?"

Critical paths are those with the maximum depth in the graph. They often represent the most complex orchestration sequences and are candidates for careful transformation review.

### 5.7 Subsystem Influence Mapping

**Question:** "What kinds of industrial elements does each node influence?"

For every node, the reasoner computes:
- direct targets (1-hop neighbors)
- transitive targets (all reachable nodes)
- influenced node kinds (e.g., a signal may influence actuators, alarms, and timers)

High-impact nodes are those with ≥ 3 transitive targets. These are often central orchestration signals or safety gates.

---

## 6. Influence Type Inference

The reasoner assigns an `influence_type` to each DependencyChain based on the edge relations along its path:

| Edge Relations | Influence Type | Industrial Meaning |
|----------------|----------------|--------------------|
| `enables`, `triggers`, `activates` only | `positive / permissive` | go-ahead, activation, permission |
| contains `disables` | `negative / protective` | shutdown, fault response, stop |
| `sequences` only | `sequential` | step ordering, mode progression |
| `depends_on` only | `conditional` | data dependency, parameter binding |
| mixed | `complex / mixed` | multiple semantic behaviors combined |

This inference preserves the industrial meaning encoded by the RelationshipExtractor. The reasoner does not re-derive meaning; it classifies the combined semantics of an already-derived path.

---

## 7. Traversal Safety

The reasoner limits DFS depth to `MAX_DEPTH = 10` to prevent infinite recursion in cyclic graphs. Cycles in industrial dependency graphs are uncommon but possible (e.g., mutual enablement logic). The depth limit ensures termination.

Cycle handling:
- visited-node tracking prevents re-traversal within a single path
- depth limit bounds total exploration
- each DFS call receives a copy of the visited set to allow shared nodes across different paths

---

## 8. Output Structures

The `get_reasoning_report()` method returns a structured dictionary:

```text
{
    safety_chains:         [DependencyChain...],
    safety_chain_count:    int,
    timer_chains:          [DependencyChain...],
    timer_chain_count:     int,
    critical_paths:        [DependencyChain...],
    critical_path_count:   int,
    subsystem_influence:   {node_id: {direct_targets, transitive_targets, influenced_kinds}},
    high_impact_nodes:     [node_id...],
    graph_node_count:      int,
    graph_edge_count:      int,
}
```

This output is designed for:
- pipeline reporting
- future safety verification
- transformation priority ranking
- human engineering review

---

## 9. Integration with main.py

The reasoner integrates behind a `--reason` CLI flag:

```text
python main.py          → pipeline runs, no reasoning
python main.py --reason → pipeline runs + dependency reasoning per file
```

The reasoning section appears in the per-file report when enabled:

```text
Industrial Dependency Reasoning
-------------------------------
  Safety Chains:
    - EmergencyStop → disables Motor [negative / protective, depth=1]
    - TankLevel → disables InletValve [negative / protective, depth=1]

  Critical Paths:
    - SensorPresent → triggers PulseTimer → depends_on T#250ms [depth=2]

  High-Impact Nodes: EmergencyStop, LevelLimit, TankLevel
```

---

## 10. Responsibility Separation

| Layer | Responsible For | Not Responsible For |
|---|---|---|
| RelationshipExtractor | Extracting flat semantic edges from AST | Building graph topology, graph reasoning |
| SemanticGraphBuilder | Converting edges to graph structures | Reasoning, inference, topology analysis |
| SemanticGraph | Storing topology | Reasoning, visualization, extraction |
| DependencyReasoner | Analyzing graph topology for transitive influence | Modifying graph, extracting relationships, AST traversal |

The reasoner is strictly read-only. It queries `outgoing_edges`, `incoming_edges`, `neighbors`, and `predecessors` but never calls `add_node` or `add_edge`.

---

## 11. Future Direction

Planned extensions:

- **Cycle detection**: identify and report circular dependencies explicitly
- **Topological sorting**: produce safe startup/shutdown ordering from dependency direction
- **Safety integrity ranking**: score nodes by how many safety-critical paths pass through them
- **Event network inference**: derive IEC 61499 event connections from critical paths
- **Diff reasoning**: compare reasoning reports across program versions to highlight behavioral changes

All extensions can be added without changing SemanticGraph, GraphBuilder, or RelationshipExtractor.
