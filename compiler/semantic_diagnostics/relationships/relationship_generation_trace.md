# Relationship Generation Trace

## Investigation Scope
Trace the complete path from AST node to final graph edge for every `controls` relationship involving `_step`, `run`, `rst`, and `edge` in `SEQUENCE_8.st`.

## Critical Finding: CASE Statement is Desugared

`SEQUENCE_8.st` contains `CASE _step OF ... END_CASE`, but the parser **does NOT emit a `CaseStatementNode`**. Instead, it desugars the `CASE` into a chain of `IfStatementNode` nodes with `ELSIF` branches.

**Consequence**: `visit_CaseStatementNode` in `relationship_extractor.py` is **never invoked** for this file. The `case_stack` is **never populated**. Therefore, the `visit_AssignmentNode` path that generates `case_selector -> sequences -> target` (line 193) **never executes** for `SEQUENCE_8`.

All `_step` → `Q*` edges are produced exclusively by `emit_condition_relationships`.

---

## Path 1: `_step` → `Q0` (sequences)

### AST Node
```
IfStatementNode
  condition: LogicalExpressionNode(operator='AND', operands=[VariableNode('run'), BinaryExpressionNode('_step = 0')])
  then_body: BlockNode
    statements:
      IfStatementNode
        condition: LogicalExpressionNode('NOT q0 AND in0 AND tx - last <= wait0')
        then_body: BlockNode
          statements:
            AssignmentNode(target='Q0', value='TRUE')
```

### Extraction Function
1. `visit_IfStatementNode` (line 109) pushes `condition_context` to `condition_stack`
2. `visit_AssignmentNode` (line 185) iterates `condition_stack` and calls `emit_condition_relationships` for each context
3. `emit_condition_relationships` (line 452) iterates `context["signals"]` (which includes `_step` from `extract_condition_signals`)
4. `relation_for_signal` (line 510) is called with `signal="_step"`, `target="Q0"`

### Source Code Locations
- `relationship_extractor.py:109` — `visit_IfStatementNode` pushes context
- `relationship_extractor.py:189` — `visit_AssignmentNode` calls `emit_condition_relationships`
- `relationship_extractor.py:457` — `relation_for_signal` invoked
- `relationship_extractor.py:461` — `add_relationship` creates the edge

### `relation_for_signal` trace
1. Phase 2: `is_actuator_target("Q0")` → `True` → `candidate = "controls"`
2. Phase 3: `infer_signal_kind("_step")` → `"state"`, `infer_target_kind("Q0")` → `"actuator"` → `candidate = "sequences"`
3. Phase 1: `candidate != "depends_on"` → `PROCESS_CONTROL` and `MULTI_ACTUATOR_SEQUENCE` do **not** override

### Relationship Selected
`sequences`

### Metadata Attached
```python
{
    "condition": "run AND _step = 0",
    "assignment": "Q0 := TRUE",
    "node_type": "AssignmentNode",
    "classification_tags": ["ACTUATOR_COORDINATION", "MULTI_ACTUATOR_SEQUENCE", "PROCESS_CONTROL"],
    "source_kind": "state",
    "target_kind": "actuator",
}
```

### `relation_for_signal()` called?
**YES**

---

## Path 2: `run` → `Q0` (controls)

### AST Node
Same nested `IfStatementNode` → `AssignmentNode` as Path 1.

### Extraction Function
Same as Path 1, but `signal="run"`.

### Source Code Locations
- `relationship_extractor.py:109` — context push
- `relationship_extractor.py:189` — `emit_condition_relationships`
- `relationship_extractor.py:457` — `relation_for_signal`
- `relationship_extractor.py:461` — `add_relationship`

### `relation_for_signal` trace
1. Phase 2: `is_actuator_target("Q0")` → `True` → `candidate = "controls"`
2. Phase 3: `infer_signal_kind("run")` → `"mode"`, `infer_target_kind("Q0")` → `"actuator"` → `candidate = "controls"` (no change)
3. Phase 1: no override

### Relationship Selected
`controls`

### Metadata Attached
```python
{
    "condition": "run AND _step = 0",
    "assignment": "Q0 := TRUE",
    "node_type": "AssignmentNode",
    "classification_tags": ["ACTUATOR_COORDINATION", "MULTI_ACTUATOR_SEQUENCE", "PROCESS_CONTROL"],
    "source_kind": "mode",
    "target_kind": "actuator",
}
```

### `relation_for_signal()` called?
**YES**

---

## Path 3: `rst` → `Q0` (controls)

### AST Node
```
IfStatementNode
  condition: VariableNode('rst')
  then_body: BlockNode
    statements:
      AssignmentNode(target='Q0', value='FALSE')
      ...
```

### Extraction Function
1. `visit_IfStatementNode` pushes `rst` to `condition_stack`
2. `visit_AssignmentNode` calls `emit_condition_relationships`
3. `relation_for_signal("rst", "Q0", "FALSE", context)`

### Source Code Locations
- `relationship_extractor.py:109` — context push
- `relationship_extractor.py:189` — `emit_condition_relationships`
- `relationship_extractor.py:457` — `relation_for_signal`
- `relationship_extractor.py:461` — `add_relationship`

### `relation_for_signal` trace
1. Phase 2: `is_actuator_target("Q0")` → `True` → `candidate = "controls"`
2. Phase 3: `infer_signal_kind("rst")` → `"reset_signal"`, `infer_target_kind("Q0")` → `"actuator"`. **No Phase 3 rule for `reset_signal -> actuator`**. `candidate` stays `"controls"`.
3. Phase 1: `candidate != "depends_on"` → no override

### Relationship Selected
`controls`

### Metadata Attached
```python
{
    "condition": "rst",
    "assignment": "Q0 := FALSE",
    "node_type": "AssignmentNode",
    "classification_tags": ["ACTUATOR_COORDINATION", "MULTI_ACTUATOR_SEQUENCE", "PROCESS_CONTROL"],
    "source_kind": "reset_signal",
    "target_kind": "actuator",
}
```

### `relation_for_signal()` called?
**YES**

---

## Path 4: `rst` → `_step` (disables)

### AST Node
```
IfStatementNode
  condition: VariableNode('rst')
  then_body: BlockNode
    statements:
      AssignmentNode(target='_step', value='-1')
      ...
```

### Extraction Function
Same as Path 3, but `target="_step"`.

### `relation_for_signal` trace
1. Phase 2: `is_actuator_target("_step")` → `False` → `candidate = "depends_on"`
2. Phase 3: `infer_signal_kind("rst")` → `"reset_signal"`, `infer_target_kind("_step")` → `"state"` → `candidate = "disables"`
3. Phase 1: `candidate != "depends_on"` → no override

### Relationship Selected
`disables`

### Metadata Attached
```python
{
    "condition": "rst",
    "assignment": "_step := -1",
    "node_type": "AssignmentNode",
    "classification_tags": ["ACTUATOR_COORDINATION", "MULTI_ACTUATOR_SEQUENCE", "PROCESS_CONTROL"],
    "source_kind": "reset_signal",
    "target_kind": "state",
}
```

### `relation_for_signal()` called?
**YES**

---

## Path 5: `edge` → `Q0` (activates)

### AST Node
```
IfStatementNode
  condition: LogicalExpressionNode(operator='AND', operands=[VariableNode('start'), LogicalExpressionNode('NOT edge')])
  then_body: BlockNode
    statements:
      AssignmentNode(target='Q0', value='FALSE')
      ...
```

### Extraction Function
1. `visit_IfStatementNode` pushes `start AND NOT edge` to `condition_stack`
2. `visit_AssignmentNode` calls `emit_condition_relationships`
3. `relation_for_signal("edge", "Q0", "FALSE", context)`

### Source Code Locations
- `relationship_extractor.py:109` — context push
- `relationship_extractor.py:189` — `emit_condition_relationships`
- `relationship_extractor.py:457` — `relation_for_signal`
- `relationship_extractor.py:461` — `add_relationship`

### `relation_for_signal` trace
1. Phase 2: `is_actuator_target("Q0")` → `True` → `candidate = "controls"`
2. Phase 3: `infer_signal_kind("edge")` → `"trigger_signal"`, `infer_target_kind("Q0")` → `"actuator"` → `candidate = "activates"`
3. Phase 1: `candidate != "depends_on"` → no override

### Relationship Selected
`activates`

### Metadata Attached
```python
{
    "condition": "start AND NOT edge",
    "assignment": "Q0 := FALSE",
    "node_type": "AssignmentNode",
    "classification_tags": ["ACTUATOR_COORDINATION", "MULTI_ACTUATOR_SEQUENCE", "PROCESS_CONTROL"],
    "source_kind": "trigger_signal",
    "target_kind": "actuator",
}
```

### `relation_for_signal()` called?
**YES**

---

## Path 6: `edge` → `_step` (triggers)

### AST Node
Same as Path 5, but `target="_step"`.

### `relation_for_signal` trace
1. Phase 2: `is_actuator_target("_step")` → `False` → `candidate = "depends_on"`
2. Phase 3: `infer_signal_kind("edge")` → `"trigger_signal"`, `infer_target_kind("_step")` → `"state"` → `candidate = "triggers"`
3. Phase 1: no override

### Relationship Selected
`triggers`

### Metadata Attached
```python
{
    "condition": "start AND NOT edge",
    "assignment": "_step := 0",
    "node_type": "AssignmentNode",
    "classification_tags": ["ACTUATOR_COORDINATION", "MULTI_ACTUATOR_SEQUENCE", "PROCESS_CONTROL"],
    "source_kind": "trigger_signal",
    "target_kind": "state",
}
```

### `relation_for_signal()` called?
**YES**

---

## Summary: ALL Paths That Create `controls` Relationships

### Universal Path
Every `controls` edge in the output follows this identical path:

```
AST AssignmentNode
  → visit_IfStatementNode (pushes context to condition_stack)
    → visit_AssignmentNode
      → emit_condition_relationships (line 452)
        → relation_for_signal (line 510)
          → add_relationship (line 65)
            → graph_builder.build (line 91)
              → SemanticGraphEdge
```

### `controls` Decision Points in `relation_for_signal`

| Source | Target | Phase 2 Result | Phase 3 Result | Final Result | Line |
|---|---|---|---|---|---|
| `run` | `Q0` | `controls` | `mode -> actuator` → `controls` | `controls` | 564 |
| `rst` | `Q0` | `controls` | `reset_signal -> actuator` → no rule | `controls` | 538 |
| `edge` | `Q0` | `controls` | `trigger_signal -> actuator` → `activates` | `activates` | 572 |
| `_step` | `Q0` | `controls` | `state -> actuator` → `sequences` | `sequences` | 562 |

### No Other Paths Generate `controls`

- `visit_CaseStatementNode` — **never called** (parser desugars `CASE`)
- `visit_AssignmentNode` (case_stack path) — **never called** (case_stack empty)
- `visit_FunctionBlockCallNode` — generates `triggers`, `depends_on`, `feeds`, never `controls`
- `visit_ProgramBindingNode` — generates `schedules`, `uses`, never `controls`
- `visit_ConfigurationNode` / `visit_ResourceNode` / `visit_TaskNode` — generates `contains`, never `controls`

### Graph Builder Path

```
relationship_extractor.py:461  add_relationship()
  → relationships.py:17  Relationship.__init__()
    → main.py:307  run_graph_generation()
      → graph_builder.py:47  build()
        → graph_builder.py:70  _resolve_node_kind()
          → graph_builder.py:114  infer_node_kind()
        → semantic_graph.py:91  SemanticGraphEdge()
        → semantic_graph.py:174  SemanticGraph.add_node()
        → semantic_graph.py:203  SemanticGraph.add_edge()
```

