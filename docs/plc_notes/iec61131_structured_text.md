# IEC 61131-3 Structured Text Notes

Structured Text, often abbreviated ST, is a PLC programming language defined by
IEC 61131-3. It resembles Pascal-like imperative programming and is commonly
used for control logic, calculations, interlocks, and automation sequences.

## Example

```iecst
IF StartButton AND SafetyOK THEN
    Motor := TRUE;
    Alarm := FALSE;
END_IF;
```

This program checks a condition and writes values to variables when the
condition is true.

## Why ST Is Useful For Migration Research

ST contains enough structure to support compiler-style analysis:

- expressions
- assignments
- conditional execution
- variables
- typed values
- nested control logic

Those features can be parsed into ASTs and analyzed before migration to IEC
61499 function block models.
