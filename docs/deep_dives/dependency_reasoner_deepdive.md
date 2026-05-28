# Dependency Reasoner Deep Dive

> Graph traversal mechanics, influence propagation, and industrial topology reasoning.

---

## 1. Purpose

This document explains the internal mechanics of the DependencyReasoner. It covers:

- how graph topology becomes industrial knowledge
- how traversal algorithms discover influence paths
- how influence types are inferred from edge semantics
- how safety and timer chains are identified
- how critical paths are extracted
- why graph reasoning is architecturally distinct from AST analysis

---

## 2. Reasoning Execution Flow

The reasoner processes a SemanticGraph in multiple analytical passes:

```text
SemanticGraph
    ↓
Pass 1: downstream DFS per node
    → direct edges (depth 1)
    → transitive paths (depth ≥ 2)
    → build DependencyChain objects
    ↓
Pass 2: upstream DFS per node
    → reverse-direction chains
    → answer "what influences this?"
    ↓
Pass 3: BFS transitive closure
    → flat set of reachable nodes per source
    ↓
Pass 4: industrial classification of chains
    → safety chains (enables/disables + safety keywords)
    → timer chains (timer nodes)
    → critical paths (maximum depth)
    ↓
Pass 5: subsystem influence mapping
    → aggregate downstream node kinds
    → identify high-impact nodes (≥3 transitive targets)
    ↓
Structured reasoning report
```

Each pass is independent. They can be run selectively or combined into a single report.

---

## 3. How Graph Reasoning Works

### 3.1 From Nodes and Edges to Influence Paths

The SemanticGraph stores flat adjacency:

```text
_nodes:
    SafetyOK    → SemanticGraphNode("SafetyOK", "signal")
    Motor       → SemanticGraphNode("Motor", "actuator")
    Conveyor    → SemanticGraphNode("Conveyor", "actuator")

_outgoing:
    SafetyOK    → [Edge(SafetyOK, enables, Motor)]
    Motor         → [Edge(Motor, activates, Conveyor)]
```

The reasoner discovers that `SafetyOK` can reach `Conveyor` by chaining two edges:

```text
SafetyOK --enables--> Motor --activates--> Conveyor
```

This is a **transitive dependency**. It was not explicitly stored in the graph. The graph only stored the two direct edges. The reasoner composes them into a path.

### 3.2 DFS Downstream Expansion

The `_dfs_downstream` method recursively follows outgoing edges:

```text
def _dfs_downstream(current, path_edges, chains, visited, max_depth):
    if len(path_edges) >= max_depth: return
    if current in visited: return

    visited.add(current)

    for edge in graph.outgoing_edges(current):
        new_path = path_edges + [edge]

        if len(new_path) >= 2:
            chains.append(DependencyChain(
                new_path[0].source, next_node, new_path, len(new_path)
            ))

        _dfs_downstream(edge.target, new_path, chains, visited.copy(), max_depth)
```

Key design choices:
- **Depth limit (10)**: prevents infinite recursion in cyclic graphs
- **Visited copy**: each recursive branch gets its own visited set, allowing the same node to appear in different paths but not in the same path (no self-loops within a chain)
- **Chain recording at depth ≥ 2**: only records transitive chains; direct edges are handled separately

### 3.3 DFS Upstream Expansion

The `_dfs_upstream` method is the reverse of downstream. It follows `incoming_edges` backward:

```text
for edge in graph.incoming_edges(current):
    prev_node = edge.source
    new_path = [edge] + path_edges
    _dfs_upstream(prev_node, new_path, chains, visited.copy(), max_depth)
```

This answers the question: "What nodes can reach the current node through any path?"

### 3.4 BFS Transitive Closure

`find_transitive_dependencies` uses BFS for efficiency when only the set of reachable nodes matters (not the individual paths):

```text
queue = [node_id]
visited = {node_id}
while queue:
    current = queue.popleft()
    for neighbor in graph.neighbors(current):
        if neighbor not in visited:
            visited.add(neighbor)
            reachable.add(neighbor)
            queue.append(neighbor)
```

BFS guarantees the shortest path to each reachable node but does not enumerate all paths. It is used for influence mapping and high-impact node detection.

---

## 4. How Traversal Propagates Influence

### 4.1 Edge Semantics as Propagation Rules

Each edge relation encodes a propagation rule:

| Relation | Propagation Meaning |
|----------|---------------------|
| `enables` | positive permission flows forward |
| `disables` | negative protection flows forward |
| `triggers` | event impulse flows forward |
| `activates` | completion signal flows forward |
| `sequences` | step ordering flows forward |
| `depends_on` | conditional requirement flows forward |

When edges are chained into a path, their combined semantics create a composite influence.

### 4.2 Influence Type Classification

The `DependencyChain._infer_influence()` method classifies each path:

```text
if path contains "disables":
    → negative / protective

elif path contains only positive relations (enables, triggers, activates):
    → positive / permissive

elif path contains only "sequences":
    → sequential

elif path contains only "depends_on":
    → conditional

else:
    → complex / mixed
```

This classification is conservative. A single `disables` edge anywhere in the path marks the entire chain as negative, because a protective shutdown overrides permissive activation.

### 4.3 Propagation Example

Graph:

```text
SafetyOK    --enables-->    Motor
Motor       --activates-->  Conveyor
EmergencyStop --disables--> Motor
```

Chains discovered:

```text
SafetyOK → Motor → Conveyor       [positive / permissive]
EmergencyStop → Motor → Conveyor  [negative / protective]
```

Even though `Motor → Conveyor` is `activates` (positive), the chain from `EmergencyStop` is classified as negative because the first edge is `disables`. This correctly reflects industrial reality: an emergency stop overrides normal activation.

---

## 5. How Dependency Chains Are Discovered

### 5.1 Direct vs. Transitive Chains

Direct chains (depth = 1) are extracted from adjacency lists without DFS:

```text
for edge in graph.outgoing_edges(node_id):
    chains.append(DependencyChain(node_id, edge.target, [edge], 1))
```

Transitive chains (depth ≥ 2) require DFS to compose multiple edges into paths.

### 5.2 Deduplication

The `_deduplicate_chains` method removes duplicate chains that arise from multiple traversal orders or converging paths:

```text
key = (chain.source, chain.target, tuple(
    (edge.source, edge.relation, edge.target) for edge in chain.path_edges
))
```

Two chains are duplicates if they share the same source, target, and identical edge sequence.

### 5.3 Chain Representation

Each chain stores:
- the original `SemanticGraphEdge` objects (with metadata)
- the inferred influence type
- a human-readable summary string
- depth count

This makes the chain self-describing and suitable for both machine processing and human review.

---

## 6. Safety Chain Discovery

### 6.1 Definition

A safety chain is any DependencyChain that meets at least one of:

1. Contains an `enables` or `disables` edge
2. Source or target name contains safety keywords (Safety, Guard, Door, EStop, Emergency, Interlock, Fault)
3. Any intermediate node name contains safety keywords

### 6.2 Discovery Process

```text
for each node in graph:
    chains = find_downstream_dependencies(node.node_id)
    for chain in chains:
        if is_safety_chain(chain):
            record chain
```

The `_is_safety_chain` helper checks all three conditions.

### 6.3 Safety Chain Example

```text
TankLevel --disables--> Pump
TankLevel --disables--> InletValve
LevelLimit --disables--> Pump
LevelLimit --disables--> InletValve
EmergencyStop --disables--> Pump
```

These chains represent protective shutdown logic. The reasoner identifies them as `negative / protective` influence type and flags the high-impact nodes (`TankLevel`, `LevelLimit`, `EmergencyStop`) that initiate multiple protective actions.

---

## 7. Critical Path Extraction

### 7.1 Definition

Critical paths are the longest dependency chains in the graph. They represent the most complex behavioral propagation and are often the most important to verify during transformation.

### 7.2 Extraction Process

```text
all_chains = []
for each node:
    all_chains.extend(find_downstream_dependencies(node.node_id))

max_depth = max(chain.depth for chain in all_chains)
critical_paths = [chain for chain in all_chains if chain.depth == max_depth]
```

### 7.3 Critical Path Example

```text
SensorPresent → triggers PulseTimer → depends_on T#250ms [depth=2]
```

This is a timer-dependent activation chain. It shows that a sensor input triggers a timer, which in turn depends on a preset time value. This chain would be critical for IEC 61499 transformation because it crosses signal → timer → parameter boundaries.

---

## 8. Subsystem Influence Mapping

### 8.1 Per-Node Influence Analysis

For each node, the reasoner computes:

```text
direct_targets:      1-hop neighbors
transitive_targets:  all reachable nodes (BFS closure)
influenced_kinds:    set of node kinds among transitive targets
```

### 8.2 High-Impact Node Detection

A node is "high-impact" if it has ≥ 3 transitive targets. This threshold identifies central orchestration signals and safety gates that affect large portions of the control system.

Example from a tank control program:

```text
EmergencyStop:
    direct_targets:     [Motor]
    transitive_targets: [Motor, Pump, InletValve]
    influenced_kinds:   [actuator]
    → high-impact (3 transitive targets)

TankLevel:
    direct_targets:     [Pump, InletValve]
    transitive_targets: [Pump, InletValve]
    influenced_kinds:   [actuator]
    → high-impact (2 transitive targets, wait...)
```

Actually the test showed `TankLevel` as high-impact with more transitive targets. The exact count depends on the graph topology.

---

## 9. Topology Analysis vs. AST Analysis

### 9.1 Structural Differences

| Aspect | AST Analysis | Graph Reasoning |
|--------|------------|-----------------|
| Data structure | tree | directed graph |
| Node meaning | syntax construct | industrial entity |
| Edge meaning | parent-child containment | behavioral dependency |
| Traversal direction | top-down (program → statements) | any direction (follow influence) |
| Typical question | "Does this IF contain an assignment?" | "Does SafetyOK affect Conveyor?" |
| Cycles | impossible (trees are acyclic) | possible (feedback loops) |
| Depth metric | nesting depth | propagation depth |

### 9.2 Why Separate Subsystems

AST analysis is syntactic. It validates that `IF TankLevel > HighLevel THEN Alarm := TRUE` is structurally valid.

Graph reasoning is semantic. It understands that `TankLevel` influences `Alarm` through a protective threshold relationship.

These are different abstraction levels. Mixing them would create a tightly coupled system that is hard to test, replace, or extend. The reasoner exists as a separate layer precisely because graph topology reasoning is a distinct concern from syntax parsing.

---

## 10. Key Invariants

1. **Read-only**: the reasoner never calls `add_node` or `add_edge` on the SemanticGraph.
2. **Bounded**: DFS depth is limited to 10 to prevent infinite recursion.
3. **Deterministic**: given the same graph, the same reasoning report is produced.
4. **Non-inferential**: the reasoner does not derive new edges. It only discovers paths through existing edges.
5. **Semantic-preserving**: influence types are derived from already-extracted edge relations, not reinterpreted.
6. **Idempotent**: running reasoning twice produces identical output.

---

## 11. Future Industrial Graph Reasoning

Planned extensions that build on the current reasoning infrastructure:

- **Cycle detection**: explicitly identify and report circular dependencies
- **Topological sort**: produce safe startup/shutdown ordering
- **Event network inference**: map critical paths to IEC 61499 event connections
- **Safety scoring**: rank nodes by the number of safety-critical paths passing through them
- **Behavioral diffing**: compare reasoning reports across program versions
- **Probabilistic influence**: annotate edges with reliability or failure probability for risk analysis

All of these extensions operate on the same SemanticGraph input and produce structured reports. None require changes to the parser, visitor, or extractor.
