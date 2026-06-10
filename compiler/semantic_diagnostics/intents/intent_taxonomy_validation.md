# Intent Taxonomy Validation

## Taxonomy Shape

- Intent names are purpose-level categories, not named industrial applications.
- Rules use behavior, relationship, operation, and evidence distributions.
- `GENERAL_PROCESS_CONTROL` is fallback-only.

## Generalization Audit

Checked `semantic/intent_reasoner.py` for dataset, filename, benchmark, and named-sample dependencies.
- Violations detected: none

## Validation Metrics

- Parsed files: 55
- Distinct detected intents: 10
- Fallback files: 20
- Low-confidence files: 22
- Average confidence: 0.673

## Intent Distribution

- GENERAL_PROCESS_CONTROL: 20
- DATA_INTEGRITY_VERIFICATION: 8
- NUMERICAL_SOLVING: 7
- SEQUENTIAL_CONTROL: 5
- RATE_BASED_MEASUREMENT: 3
- MATRIX_PROCESSING: 3
- MULTI_ACTUATOR_COORDINATION: 3
- PROCESS_AUTOMATION: 3
- EVENT_COUNTING: 2
- STATE_BASED_CONTROL: 1