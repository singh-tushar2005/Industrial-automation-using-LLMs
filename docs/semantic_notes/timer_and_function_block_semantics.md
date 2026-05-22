# Timer And Function Block Semantics

The parser and semantic pipeline now recognize function block invocation
statements and IEC time literals. This is an important step toward realistic
industrial analysis because PLC programs frequently rely on stateful function
blocks.

---

## Supported Function Block Forms

Current examples use named invocation syntax:

```iecst
StartTimer(IN := StartCommand AND SafetyOK, PT := T#5s);
PulseTimer(IN := SensorPresent, PT := T#250ms);
```

The parser represents these as `FunctionBlockCallNode` objects with named
arguments.

```text
FunctionBlockCallNode
├── name: StartTimer
└── arguments
    ├── IN: StartCommand AND SafetyOK
    └── PT: T#5s
```

---

## Timer Semantics

IEC timer blocks are stateful control elements.

| Timer | Common Meaning | Transformation Interpretation |
|---|---|---|
| `TON` | on-delay timer | output becomes true after input stays true for preset time |
| `TOF` | off-delay timer | output remains true for a time after input turns false |
| `TP` | pulse timer | output produces a fixed-duration pulse |

In the current symbolic classifier, timer-related behavior is detected through:

- function block calls
- time literals such as `T#5s`
- `.Q` done/output conditions such as `StartTimer.Q`

---

## Stateful Industrial Behavior

Function blocks are not simple expressions. They often hold internal state:

```text
Timer instance
├── IN input
├── PT preset time
├── elapsed internal state
└── Q output
```

For transformation, that state must be preserved. An IEC 61499 generator should
not flatten timer logic into a stateless expression.

---

## Example: Timer-Dependent Motor Start

Structured Text:

```iecst
StartTimer(IN := StartCommand AND SafetyOK, PT := T#5s);

IF StartTimer.Q THEN
    Motor := TRUE;
END_IF;
```

Semantic interpretation:

```text
StartCommand AND SafetyOK
    ↓
TON input condition
    ↓
StartTimer.Q
    ↓
Motor enable command
```

Classifier output should include:

```text
TIMER_DEPENDENT_CONTROL
PROCESS_ENABLE_CONDITION
ACTUATOR_COORDINATION
```

---

## Future Function Block Semantics

Future parser and semantic work should distinguish:

- timer instances
- counter instances
- PID/control function blocks
- user-defined function blocks
- safety-certified function blocks
- function block input/output ports
- retained internal state

This will allow semantic IR generation to model industrial behavior as stateful
components, which is much closer to IEC 61499 architecture than raw Structured
Text syntax.
