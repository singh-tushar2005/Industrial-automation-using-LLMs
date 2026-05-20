# Semantic Analysis

Syntax checks whether source code has the right shape. Semantic analysis checks
whether that source code makes sense.

Examples:

```iecst
Temp > 100
```

This is semantically valid when `Temp` is numeric.

```iecst
StartButton AND 1
```

This is semantically invalid because logical operators require boolean
operands.

```iecst
Alarm := 42;
```

This is semantically invalid if `Alarm` is a boolean variable.

## Why It Matters In Industrial Automation

Industrial automation software controls physical systems. Type mistakes can
hide logic defects in alarms, safety interlocks, motor commands, counters, and
sensor thresholds.

Semantic checks make migration safer because transformation stages can rely on
facts discovered earlier in the pipeline.

## Semantic Results

Semantic modules should collect and return:

- warnings
- errors
- inferred or known symbols
- analysis metadata

They should not print reports directly. Presentation belongs in `main.py`.
