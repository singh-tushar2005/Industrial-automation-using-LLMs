# Compiler Infrastructure Change Log

Industrial parser evolution tracking. Each entry records what changed, why it changed,
which IEC construct motivated it, and the resulting diagnostics improvement.

---

## [2026-05-27] Baseline Snapshot

**Files snapshotted:**
- `parser/st_parser.py` → `st_parser_2026_05_27_v1.py`
- `semantic/visitor.py` → `visitor_2026_05_27_v1.py`
- `ast/nodes.py` → `nodes_2026_05_27_v1.py`
- `semantic/classifier.py` → `classifier_2026_05_27_v1.py`
- `semantic/relationship_extractor.py` → `relationship_extractor_2026_05_27_v1.py`
- `compiler/grammar_diagnostics.py` → `grammar_diagnostics_2026_05_27_v1.py`

**Parser maturity at baseline (industrial datasets):**
- Parser average: 70.5%
- AST average: 0.0%
- Visitor average: 0.0%

**Primary bottlenecks identified:**
- `PROGRAM ... END_PROGRAM` compilation-unit wrapper unsupported
- `FUNCTION ... END_FUNCTION` unsupported
- `VAR ... END_VAR` declaration blocks unsupported
- Multiline boolean expressions with newlines between operators
- Comments `(* ... *)` and `// ...` not suppressed

**Motivation:**
Real industrial IEC61131-3 datasets fail at compilation-unit parsing.
Diagnostics confirm 4/4 industrial datasets fail parsing.
Educational datasets parse successfully (26/26).

---

## [2026-05-27] Industrial Parser Generalization Phase

**Files modified:**
- `parser/st_parser.py` → generalized IEC 61131-3 grammar
- `ast/nodes.py` → expanded AST infrastructure
- `semantic/visitor.py` → added traversal for new nodes
- `semantic/classifier.py` → added CompilationUnitNode handler
- `semantic/relationship_extractor.py` → added CompilationUnitNode handler
- `semantic/type_checker.py` → added CompilationUnitNode / VarBlockNode / VariableDeclarationNode handlers

**Files snapshotted (post-change):**
- `parser/st_parser.py` → `st_parser_2026_05_27_v2.py`
- `semantic/visitor.py` → `visitor_2026_05_27_v2.py`
- `ast/nodes.py` → `nodes_2026_05_27_v2.py`
- `semantic/classifier.py` → `classifier_2026_05_27_v2.py`
- `semantic/relationship_extractor.py` → `relationship_extractor_2026_05_27_v2.py`
- `semantic/type_checker.py` → `type_checker_2026_05_27_v2.py`
- `compiler/grammar_diagnostics.py` → `grammar_diagnostics_2026_05_27_v2.py`

### Added Grammar Support

1. **Compilation-unit parsing**
   - `PROGRAM name ... END_PROGRAM`
   - `FUNCTION name : return_type ... END_FUNCTION`
   - `FUNCTION_BLOCK name ... END_FUNCTION_BLOCK`

2. **Variable declaration blocks**
   - `VAR ... END_VAR`
   - `VAR_INPUT ... END_VAR`
   - `VAR_OUTPUT ... END_VAR`
   - `VAR_IN_OUT ... END_VAR`
   - Declarations: `Name : TYPE := default;` and comma-separated names

3. **Comment suppression**
   - Block comments `(* ... *)`
   - Line comments `// ...`

4. **CASE OF maturity**
   - Optional trailing semicolon after `END_CASE`

### Added AST Nodes

- `CompilationUnitNode(kind, name, body, var_blocks, return_type)`
- `VarBlockNode(kind, declarations)`
- `VariableDeclarationNode(names, var_type, default_value)`

### Added Visitor Methods

- `visit_CompilationUnitNode`
- `visit_VarBlockNode`
- `visit_VariableDeclarationNode`

### Diagnostics Improvement

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Parser average | 70.5% | 90.8% | +20.3% |
| AST average | 0.0% | 87.5% | +87.5% |
| Visitor average | 0.0% | 100.0% | +100.0% |

**Per-dataset progression:**
- `robotic_sequence.st`: parser 75% → 92% (↑+17), ast 0% → 90% (↑+90), visitor 0% → 100% (↑+100)
- `sampletext_2.st`: parser 75% → 92% (↑+17), ast 0% → 90% (↑+90), visitor 0% → 100% (↑+100)
- `sampletext_3.st`: parser 75% → 92% (↑+17), ast 0% → 90% (↑+90), visitor 0% → 100% (↑+100)
- `sampletext_4.st`: parser 57% → 87% (↑+30), ast 0% → 80% (↑+80), visitor 0% → 100% (↑+100)

**Status change:** all 4 industrial datasets moved from `failed` → `partial_success`.

**Educational dataset regressions:** none (30/30 still pass).

**Remaining unsupported constructs:**
- `FUNCTION_BLOCK` type references in declarations (e.g., `StateMachine : FB_StateMachine;`)
- `state_machine` keyword patterns (heuristic construct detection)
- `multiline_boolean` heuristic still flagged despite parsing correctly

---
