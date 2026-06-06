# Semantic Integration Architecture Review

## 1. Pipeline Architecture Overview

```
AST → Classifier → ClassificationReport
  ↓
RelationshipExtractor(ClassificationReport, TypeReport)
  ↓
RelationshipReport (with metadata including "classification_tags")
  ↓
GraphBuilder(RelationshipReport)
  ↓
SemanticGraph (nodes + edges)
  ↓
DependencyReasoner(SemanticGraph)
  ↓
ReasoningReport
```

### Critical Observation
The **Classifier** discovers 18 distinct industrial semantic patterns, but these findings **do not influence graph construction or reasoning**. The only downstream consumption is:

- `RelationshipExtractor` copies `classification_report.get("tags", [])` into edge metadata as `"classification_tags"`.
- `GraphBuilder` stores the full metadata on edges but never reads `classification_tags`.
- `DependencyReasoner` operates purely on graph topology (nodes + edges) and ignores all metadata.

**Result: 18 semantic findings are discovered and then discarded.**

---

## 2. Classifier Finding Inventory

| # | Tag | Frequency | Generated In | AST Evidence | Downstream Consumption |
|---|-----|-------------|--------------|--------------|------------------------|
| 1 | `ACTUATOR_COORDINATION` | 647 | `classify_assignment`, `visit_BlockNode` | `AssignmentNode` where `is_actuator_target(target)` | **NO** |
| 2 | `MULTI_ACTUATOR_SEQUENCE` | 73 | `visit_CompilationUnitNode`, `visit_BlockNode` | ≥2 actuator assignments in same body/block | **NO** |
| 3 | `PROCESS_SEQUENCING` | 66 | `visit_FunctionBlockCallNode`, `visit_ForLoopNode`, `visit_WhileLoopNode` | `CTU/CTD/CTUD` FB, `FOR`/`WHILE` loops | **NO** |
| 4 | `TIMER_DEPENDENT_CONTROL` | 27 | `visit_FunctionBlockCallNode`, `classify_condition` | `TON/TOF/TP` FB call, `.Q` timer condition | **NO** |
| 5 | `PROCESS_ENABLE_CONDITION` | 17 | `classify_condition` | `Enable`/`Ready`/`Start`/`AutoMode` in condition | **NO** |
| 6 | `ALARM_CONDITION` | 15 | `classify_assignment` | `Alarm`/`Warning` target with `TRUE` value | **NO** |
| 7 | `SAFETY_INTERLOCK` | 15 | `classify_condition` | `Safety`/`Guard`/`Door`/`EStop`/`Interlock` in condition | **NO** |
| 8 | `PROCESS_MONITORING` | 12 | `visit_CompilationUnitNode` | FUNCTION/FUNCTION_BLOCK with `Status`/`Diagnostic` outputs or pure computation | **NO** |
| 9 | `PROCESS_LIMIT_PROTECTION` | 11 | `classify_condition` | Binary comparison with `Pressure`/`Temp`/`Level`/`Limit` | **NO** |
| 10 | `INDUSTRIAL_FAULT_RECOVERY` | 9 | `classify_assignment` | `Fault` target with `FALSE`/`0` value | **NO** |
| 11 | `STATE_MACHINE` | 7 | `visit_CaseStatementNode` | `CASE` branches assign to selector variable | **NO** |
| 12 | `FAULT_PROTECTION_SEQUENCE` | 5 | `visit_IfStatementNode` | Condition contains `Fault`/`Trip`/`Alarm`/`Overload` | **NO** |
| 13 | `PROCESS_CONTROL` | 4 | `visit_CompilationUnitNode` | `FUNCTION_BLOCK` with `TON/TOF/TP/CTU/CTD/CTUD/PID` or actuator assignments | **NO** |
| 14 | `EMERGENCY_SHUTDOWN` | 4 | `visit_IfStatementNode` | Condition contains `Emergency`/`EStop`/`EmergencyStop` | **NO** |
| 15 | `PROGRAM_DEPLOYMENT` | 3 | `visit_CompilationUnitNode`, `visit_ProgramBindingNode` | `PROGRAM` compilation unit or binding node | **NO** |
| 16 | `FB_COORDINATION` | 2 | `visit_CompilationUnitNode` | ≥2 `FunctionBlockCallNode` in same unit | **NO** |
| 17 | `CONTROLLED_STARTUP_SEQUENCE` | 2 | `classify_assignment` | `StartupStep` assignment | **NO** |
| 18 | `MODE_SELECTION_LOGIC` | 1 | `visit_CaseStatementNode` | `CASE` selector contains `Mode`/`Auto`/`Manual` | **NO** |

---

## 3. Semantic Flow Tracing

### 3.1 Classifier → Relationship Extractor

```python
# classifier.py produces:
{
    "findings": [...],
    "finding_count": N,
    "tags": ["ACTUATOR_COORDINATION", "STATE_MACHINE", ...],
    "semantic_model": {...}
}

# relationship_extractor.py receives it as:
RelationshipExtractor(classification_report, type_report)

# And uses it exactly once:
"classification_tags": self.classification_report.get("tags", [])
```

**Observation**: The extractor adds the **entire tag list** to every `emit_condition_relationships` call. This means every edge from a conditional assignment receives the same `classification_tags` array containing all tags from the entire program. This is not a per-relationship semantic annotation; it is a coarse program-level copy.

### 3.2 Relationship Extractor → Graph Builder

```python
# graph_builder.py receives:
{
    "relationships": [
        {
            "source": "...",
            "relation": "...",
            "target": "...",
            "metadata": {
                "classification_tags": ["ACTUATOR_COORDINATION", "STATE_MACHINE", ...],
                "condition": "...",
                "source_kind": "...",
                "target_kind": "...",
                ...
            }
        }
    ]
}

# graph_builder.py uses:
metadata.get("source_kind")  → node kind
metadata.get("target_kind")  → node kind

# graph_builder.py IGNORES:
metadata["classification_tags"]
metadata["condition"]
metadata["reason"]
metadata["assignment"]
metadata["node_type"]
```

**Observation**: `GraphBuilder` only extracts `source_kind` and `target_kind` from metadata. It stores the full metadata dict on the `SemanticGraphEdge`, but never reads it again. The `classification_tags` are dead-on-arrival.

### 3.3 Graph Builder → Dependency Reasoner

```python
# dependency_reasoner.py receives:
SemanticGraph(nodes, edges)

# It operates purely on:
graph.nodes()
graph.edges()
graph.neighbors(node_id)
graph.outgoing_edges(node_id)
graph.incoming_edges(node_id)

# It never reads:
edge.metadata
node.metadata["classification_tags"]
node.metadata["inferred_kind"]
```

**Observation**: The entire reasoning layer is topology-blind to semantic metadata. The only metadata used is `node_kind` (already baked into the node). The original classifier evidence, confidence levels, and transformation hints are completely lost.

---

## 4. Lost Semantics Analysis

### Finding: `ACTUATOR_COORDINATION` (647 occurrences)

- **Industrial meaning**: Multiple actuator commands are coordinated in the same control block or unit. This indicates a coordinated multi-output action.
- **Survives into graph?** **NO**.
- **Evidence**: The finding is generated at `AssignmentNode` and `BlockNode` levels. The relationship extractor creates individual `controls`/`depends_on` edges for each assignment, but the *coordination* relationship (that these actuators act together) is lost. The graph has parallel edges but no hyper-edge or grouping node.

### Finding: `MULTI_ACTUATOR_SEQUENCE` (73 occurrences)

- **Industrial meaning**: Multiple actuators are commanded in sequence within the same block or CASE branch.
- **Survives into graph?** **NO**.
- **Evidence**: Similar to ACTUATOR_COORDINATION, but with temporal/sequential semantics. The graph has individual edges, not a sequence group.

### Finding: `STATE_MACHINE` (7 occurrences)

- **Industrial meaning**: A `CASE` statement branches assign to the selector variable, representing a finite state machine.
- **Survives into graph?** **PARTIALLY**.
- **Evidence**: The `relationship_extractor` independently detects `transitions_to` edges from `CASE` branches, and `graph_builder` creates `state` nodes. However, the `STATE_MACHINE` finding itself (the abstraction that this is a single FSM) is lost. The graph has state nodes and transitions but no FSM container or selector binding.

### Finding: `FB_COORDINATION` (2 occurrences)

- **Industrial meaning**: Multiple function block instances are coordinated within the same unit.
- **Survives into graph?** **NO**.
- **Evidence**: The `relationship_extractor` creates `uses` edges from program to FB, and `feeds` edges between FBs. But the *coordination* abstraction (that these FBs work together in a control strategy) is lost.

### Finding: `PROCESS_CONTROL` (4 occurrences)

- **Industrial meaning**: A FUNCTION_BLOCK contains control logic (state machine, PID, or actuator sequencing).
- **Survives into graph?** **NO**.
- **Evidence**: The FB call is represented as a node (possibly `function_block` kind), but the *control strategy* classification is not represented. The graph cannot distinguish a control FB from a utility FB.

### Finding: `PROCESS_MONITORING` (12 occurrences)

- **Industrial meaning**: A FUNCTION/FUNCTION_BLOCK contains monitoring or diagnostic outputs without direct actuator control.
- **Survives into graph?** **NO**.
- **Evidence**: The FB/function is represented as a node, but the monitoring vs. control distinction is lost.

### Finding: `PROGRAM_DEPLOYMENT` (3 occurrences)

- **Industrial meaning**: A PROGRAM compilation unit or binding represents a deployable control application.
- **Survives into graph?** **PARTIALLY**.
- **Evidence**: The `relationship_extractor` creates `uses`, `schedules`, `contains` edges that reflect the deployment hierarchy. The graph captures the hierarchy but not the *deployment* semantic.

### Finding: `TASK_SCHEDULING` / `RESOURCE_BINDING` / `RUNTIME_CONFIGURATION`

- **Industrial meaning**: Hierarchical IEC 61131-3 runtime topology (CONFIGURATION → RESOURCE → TASK → PROGRAM).
- **Survives into graph?** **YES**.
- **Evidence**: The `relationship_extractor` creates `contains` and `schedules` edges. The graph captures this hierarchy fully. However, the *classification* of these nodes as runtime topology elements is not stored explicitly.

### Finding: `SAFETY_INTERLOCK` / `EMERGENCY_SHUTDOWN` / `FAULT_PROTECTION_SEQUENCE` / `PROCESS_LIMIT_PROTECTION`

- **Industrial meaning**: Safety/permissive/limit/fault conditions that gate control behavior.
- **Survives into graph?** **NO**.
- **Evidence**: The conditions are encoded in `depends_on`/`enables`/`disables`/`triggers` edges, but the *safety classification* is lost. The graph cannot distinguish a safety-critical path from a normal control path.

### Finding: `TIMER_DEPENDENT_CONTROL` / `PROCESS_SEQUENCING`

- **Industrial meaning**: Time-dependent or counter-dependent sequencing behavior.
- **Survives into graph?** **PARTIALLY**.
- **Evidence**: Timer/counter nodes are created with `timer`/`counter` kind, and `triggers`/`activates` edges are created. The graph knows about timers and counters, but the *sequencing dependency* (that this is a time-driven sequence) is not explicitly represented.

### Finding: `ALARM_CONDITION` / `INDUSTRIAL_FAULT_RECOVERY`

- **Industrial meaning**: Alarm state changes or fault recovery actions.
- **Survives into graph?** **NO**.
- **Evidence**: The alarm/fault variable is represented as a node, but the *alarm semantics* (is it an alarm, what triggers it, what resets it) are lost.

### Finding: `PROCESS_ENABLE_CONDITION`

- **Industrial meaning**: Process execution is enabled when permissives are satisfied.
- **Survives into graph?** **NO**.
- **Evidence**: The enable signal is represented as a node, but the *permissive* semantics are lost.

### Finding: `CONTROLLED_STARTUP_SEQUENCE`

- **Industrial meaning**: Startup step sequence.
- **Survives into graph?** **NO**.
- **Evidence**: The `startup_step` variable is represented as a `state` or `mode` node, but the *startup sequence* semantics are lost.

### Finding: `MODE_SELECTION_LOGIC`

- **Industrial meaning**: Mode selection via CASE.
- **Survives into graph?** **NO**.
- **Evidence**: The mode selector is represented as a node, but the *mode selection* abstraction is lost.

---

## 5. Proposed Graph-Level Representations

### Priority: HIGH

#### `STATE_MACHINE`
- **Proposed nodes**: `StateMachine` node (kind: `state_machine`) containing the selector variable.
- **Proposed edges**: `contains` edges from `StateMachine` to each `state` node.
- **Proposed metadata**: `selector`, `state_count`, `is_cyclic`.
- **Expected impact**: Enables state-machine-aware reasoning (reachable states, terminal states, unreachable states). HIGH frequency in industrial logic.

#### `ACTUATOR_COORDINATION` / `MULTI_ACTUATOR_SEQUENCE`
- **Proposed nodes**: `ActuatorGroup` node (kind: `actuator_group`) containing the coordinated actuators.
- **Proposed edges**: `contains` edges from `ActuatorGroup` to each actuator; `sequences` edges between actuators in temporal order.
- **Proposed metadata**: `coordination_type` ("parallel" vs "sequential"), `source_block`.
- **Expected impact**: Enables group-level reasoning (affect all actuators in a group, find coordination chains). VERY HIGH frequency (647+73).

#### `SAFETY_INTERLOCK` / `EMERGENCY_SHUTDOWN` / `FAULT_PROTECTION_SEQUENCE` / `PROCESS_LIMIT_PROTECTION`
- **Proposed nodes**: `SafetyGuard` node (kind: `safety_guard`) representing the protective condition.
- **Proposed edges**: `enables` or `disables` from `SafetyGuard` to protected actuators; `guards` edge from condition signals to `SafetyGuard`.
- **Proposed metadata**: `guard_type` ("safety", "emergency", "fault", "limit"), `condition_text`.
- **Expected impact**: Enables safety-path analysis, SIL-level reasoning, and fault-tree construction. Critical for industrial safety.

#### `TIMER_DEPENDENT_CONTROL` / `PROCESS_SEQUENCING`
- **Proposed nodes**: `Sequence` node (kind: `sequence`) representing the time/counter-driven sequence.
- **Proposed edges**: `sequences` from `Sequence` to each step; `triggers` from timer/counter to `Sequence`.
- **Proposed metadata**: `sequence_type` ("timer", "counter", "step"), `step_count`.
- **Expected impact**: Enables sequence-aware reasoning (step reachability, deadlock detection).

### Priority: MEDIUM

#### `FB_COORDINATION`
- **Proposed nodes**: `FBNetwork` node (kind: `fb_network`) containing the coordinated FBs.
- **Proposed edges**: `contains` from `FBNetwork` to each FB; `feeds` between FBs.
- **Proposed metadata**: `coordination_strategy`, `fb_count`.
- **Expected impact**: Enables FB-network analysis (data flow, event propagation). Low frequency (2) but high industrial value.

#### `PROCESS_CONTROL` / `PROCESS_MONITORING`
- **Proposed nodes**: `ControlStrategy` or `MonitorStrategy` node (kind: `control_strategy` / `monitor_strategy`).
- **Proposed edges**: `contains` to the FB/FUNCTION; `controls` to downstream actuators; `monitors` to process variables.
- **Proposed metadata**: `strategy_type` ("PID", "state_machine", "sequencer", "monitor"), `confidence`.
- **Expected impact**: Enables strategy-level reasoning (this unit is a PID controller, not a utility). Medium frequency (4+12).

#### `PROGRAM_DEPLOYMENT` / `TASK_SCHEDULING` / `RESOURCE_BINDING` / `RUNTIME_CONFIGURATION`
- **Proposed nodes**: `Deployment` node (kind: `deployment`) representing the runtime hierarchy.
- **Proposed edges**: `contains` hierarchy already exists; add `deploys` from `Deployment` to `Program`.
- **Proposed metadata**: `runtime_level` ("configuration", "resource", "task", "program").
- **Expected impact**: Enables deployment-aware reasoning (which program runs on which resource). Low frequency but high structural value.

### Priority: LOW

#### `ALARM_CONDITION` / `INDUSTRIAL_FAULT_RECOVERY`
- **Proposed nodes**: `Alarm` node (kind: `alarm`) representing the alarm state machine.
- **Proposed edges**: `triggers` from condition to `Alarm`; `resets` from recovery action to `Alarm`.
- **Proposed metadata**: `alarm_type`, `trigger_condition`, `reset_condition`.
- **Expected impact**: Enables alarm management reasoning. Medium frequency (15+9) but limited reasoning value.

#### `PROCESS_ENABLE_CONDITION`
- **Proposed nodes**: `Permissive` node (kind: `permissive`) representing the enable condition.
- **Proposed edges**: `enables` from `Permissive` to downstream actuators.
- **Proposed metadata**: `permissive_signals`.
- **Expected impact**: Enables permissive-path analysis. Low frequency (17).

#### `CONTROLLED_STARTUP_SEQUENCE` / `MODE_SELECTION_LOGIC`
- **Proposed nodes**: `StartupSequence` or `ModeSelector` node (kind: `mode` or `sequence`).
- **Proposed edges**: `sequences` to steps; `selects` to modes.
- **Proposed metadata**: `selector_variable`, `mode_count`.
- **Expected impact**: Enables startup/mode reasoning. Very low frequency (2+1).

---

## 6. Integration Architecture Recommendations

### 6.1 Immediate Fix: Per-Relationship Classification Tags

**Current**: Every relationship receives the entire program-level tag list.

**Proposed**: Only emit tags that are relevant to the specific relationship. For example:
- An `AssignmentNode` to `MotorA` should only receive `ACTUATOR_COORDINATION`.
- A `CaseStatementNode` should only receive `STATE_MACHINE` and `MODE_SELECTION_LOGIC`.

### 6.2 Medium Fix: Add Classifier-Aware Node/Edge Metadata

**Proposed**: Extend `SemanticGraphNode` and `SemanticGraphEdge` to include:
- `industrial_tags`: list of classifier tags relevant to this node/edge
- `industrial_confidence`: confidence level from classifier
- `industrial_hints`: transformation hints from classifier

**Proposed**: Extend `DependencyReasoner` to:
- Read `industrial_tags` from nodes and edges
- Use tags for path filtering (e.g., `analyze_safety_paths` should only follow paths tagged with `SAFETY_INTERLOCK` or `EMERGENCY_SHUTDOWN`)
- Use tags for severity scoring (e.g., a path through a `SafetyGuard` node is higher severity)

### 6.3 Long-Term Fix: Add Abstract Nodes

**Proposed**: Add a second layer of "abstract nodes" to the graph:
- `StateMachine` nodes that contain `state` nodes
- `ActuatorGroup` nodes that contain `actuator` nodes
- `SafetyGuard` nodes that guard `actuator` nodes
- `FBNetwork` nodes that contain `function_block` nodes

**Proposed**: Add a `SemanticGraphBuilder` extension that:
- Scans the relationship report for classifier findings
- Creates abstract nodes and containment edges
- Links abstract nodes to concrete nodes

### 6.4 Priority Ranking Summary

| Priority | Findings | Industrial Value | Corpus Frequency | Reasoning Impact |
|----------|----------|------------------|-------------------|-------------------|
| **HIGH** | `STATE_MACHINE`, `ACTUATOR_COORDINATION`, `MULTI_ACTUATOR_SEQUENCE`, `SAFETY_INTERLOCK`, `EMERGENCY_SHUTDOWN`, `FAULT_PROTECTION_SEQUENCE`, `PROCESS_LIMIT_PROTECTION`, `TIMER_DEPENDENT_CONTROL`, `PROCESS_SEQUENCING` | Very High | High (7-647) | Enables FSM reasoning, group reasoning, safety reasoning, sequence reasoning |
| **MEDIUM** | `FB_COORDINATION`, `PROCESS_CONTROL`, `PROCESS_MONITORING`, `PROGRAM_DEPLOYMENT`, `TASK_SCHEDULING`, `RESOURCE_BINDING`, `RUNTIME_CONFIGURATION` | High | Medium (2-12) | Enables strategy reasoning, deployment reasoning, FB network reasoning |
| **LOW** | `ALARM_CONDITION`, `INDUSTRIAL_FAULT_RECOVERY`, `PROCESS_ENABLE_CONDITION`, `CONTROLLED_STARTUP_SEQUENCE`, `MODE_SELECTION_LOGIC` | Medium | Low (1-17) | Enables alarm reasoning, permissive reasoning, startup reasoning |

---

## 7. Conclusion

The current semantic pipeline discovers rich industrial semantics but **does not preserve them** into the graph or reasoning layers. The loss occurs at two levels:

1. **Relationship Extractor** copies the entire program-level tag list to every conditional relationship, losing per-relationship semantic specificity.
2. **Graph Builder** and **Dependency Reasoner** ignore all metadata, including `classification_tags`, `condition`, `reason`, and `assignment`.

**Impact**: The graph is a purely topological model. It knows that `A` depends on `B`, but it does not know that `B` is a safety interlock, that `A` is part of a coordinated actuator group, or that the dependency is inside a state machine. As a result, downstream reasoning is limited to generic graph algorithms (shortest path, cycle detection) and cannot perform industrial-specific reasoning (safety impact analysis, actuator group coordination, state machine reachability).

**Recommendation**: The highest-impact fix is to add **abstract nodes** (`StateMachine`, `ActuatorGroup`, `SafetyGuard`) and **per-edge classification tags** to the graph. This would enable the reasoning layer to answer industrial questions like: "What actuators are in this safety group?" or "Which state machines contain unreachable states?" without changing the graph topology.
