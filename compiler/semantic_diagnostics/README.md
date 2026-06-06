# Semantic Diagnostics

**Generated:** 2026-06-01

This directory contains all diagnostic reports, audits, and metrics produced by the industrial semantic analysis pipeline.

## Directory Structure

| Directory | Purpose |
|---|---|
| `coverage/` | Semantic coverage audits, gap reports, before/after metrics |
| `classifier/` | Industrial vocabulary audits, classifier integration reports, intent reviews |
| `relationships/` | Relationship precision audits, rule frequency analyses, R1 refactor designs |
| `operations/` | Operation extractor reports, operation type frequencies |
| `patterns/` | Pattern library diagnostic reports, semantic evidence metrics |
| `dependency_reasoning/` | Semantic context integration reports, context metrics |
| `corpus/` | Per-dataset semantic outputs, corpus-wide diagnostics, case desugaring impact |
| `archive/` | Older or superseded report versions |

## Major Reports

### Coverage
- `coverage_expansion_report.md` — Coverage expansion from 60% to 99.2%
- `coverage_gap_report.json` — Per-statement gap analysis
- `coverage_before_after.json` — Per-dataset before/after metrics

### Classifier
- `industrial_vocabulary_gap_report.md` — Vocabulary coverage audit
- `integration_phase1_report.md` — Phase 1 classifier-extractor integration

### Relationships
- `relationship_rule_precision_audit.md` — R1–R16 precision assessment
- `r1_refactor_design.md` — R1 refactor design document
- `r1_filtering_report.md` — R1 filtering validation
- `post_filter_precision_audit.md` — Post-filter precision audit

### Operations
- `operation_extractor_report.md` — Operation extractor validation
- `operation_type_frequencies.json` — Operation type frequencies

### Patterns
- `pattern_library_report.md` — Pattern library diagnostic report
- `pattern_library_metrics.json` — Pattern detection metrics

### Dependency Reasoning
- `semantic_context_integration_report.md` — Context integration report

### Corpus
- `case_desugaring_impact.md` — CASE desugaring impact analysis
- `semantic_diagnostics.json` — Full corpus diagnostic data
- `*_semantic.json` — Per-dataset semantic outputs

## Usage

Each report is standalone. Read in the following order for the full narrative:

1. `classifier/industrial_vocabulary_gap_report.md`
2. `relationships/relationship_rule_precision_audit.md`
3. `coverage/coverage_expansion_report.md`
4. `patterns/pattern_library_report.md`
