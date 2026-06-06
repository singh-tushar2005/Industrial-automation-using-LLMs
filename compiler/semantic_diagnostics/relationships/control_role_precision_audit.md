# CONTROL Role Precision Audit

**Scope:** `datasets/Industrial_data/Implementation_datasets`

**Method:** For every `IF` statement, compare the current `classify_condition_roles` output against an independent inference of the actual control variable(s).

## 1. Statistics

| Metric | Count |
|---|---|
| Total IF statements | 121 |
| Current CONTROL detection rate | 12 / 121 (9.9%) |
| Missed CONTROL cases | 70 |
| False CONTROL cases | 0 |

### Control Type Frequencies (Inferred Actual)

| Type | Count | % |
|---|---|---|
| SINGLE_CONTROL | 59 | 48.8% |
| NO_CONTROL_VARIABLE | 39 | 32.2% |
| SENSOR_CONTROL | 11 | 9.1% |
| STATE_CONTROL | 8 | 6.6% |
| TIMER_CONTROL | 4 | 3.3% |

## 2. Why Current CONTROL Classification Fails

### Root Cause: CONTROL rules are too narrow

The current Phase-A classifier only assigns **CONTROL** to three categories:
1. **State variables** (`_step`, `State`, `ToolChangeState`) — only 5 files in the corpus use these.
2. **Timer done signals** (`Timer.Q`) — only 2 files.
3. **Trigger signals** (`edge`) — only 1 file.

Every other variable — sensors, process variables, generic booleans, counters, mode guards — falls into **PERMISSIVE**, even when it is the *sole* variable in the condition and directly controls the branch.

### Failure Mode 1: Generic single-variable conditions are dumped to PERMISSIVE

When a condition is a single variable (e.g., `REV_IN`, `ToolChangeRequired`, `PedestrianButton1`), there is no state/timer/trigger heuristic. The classifier defaults to PERMISSIVE. These are actually **SINGLE_CONTROL** cases.

### Failure Mode 2: Sensor guards are dumped to PERMISSIVE

Sensors (`Xi*`, `in*`, `Proximity`) in direct-control conditions are classified as PERMISSIVE. In industrial logic, a sensor that is the sole or dominant condition of an IF is the control source (e.g., `in0` in `SEQUENCE_8`). These are **SENSOR_CONTROL** cases.

### Failure Mode 3: Process variables are dumped to PERMISSIVE

Process variables (`Pressure`, `Flow`, `Temp`) in limit comparisons are classified as PERMISSIVE. They should be **SENSOR_CONTROL** or **INTERLOCK_CONTROL**.

### Failure Mode 4: Feedback mirrors are classified as PERMISSIVE

Internal feedback variables (`q0`, `q1`) used in `NOT q0` guards are classified as PERMISSIVE. They are neither control nor permissive; they are **CONTEXT** (feedback guard). The classifier has no feedback category.

### Failure Mode 5: Mode variables are classified as PERMISSIVE

Mode variables (`run`) are classified as PERMISSIVE. When `run` is the sole condition, it is a **SINGLE_CONTROL** (mode control). When it ANDs with a state variable, it is a guard, but the classifier does not distinguish these two cases.

## 3. Examples from Target Files

### SEQUENCE_8.st

**Missed CONTROL cases:**

- **Condition:** `NOT init`
  - **Current:** CONTROL=[], PERMISSIVE=['init'], CONTEXT=[]
  - **Actual:** SENSOR_CONTROL → ['init']
  - **Then assigns:** ['last', 'init', 'status']

- **Condition:** `rst`
  - **Current:** CONTROL=[], PERMISSIVE=['rst'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['rst']
  - **Then assigns:** ['_step', 'Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'status', 'run']

**Representative cases:**

- **Condition:** `NOT init`
  - **Current:** CONTROL=[], PERMISSIVE=['init'], CONTEXT=[]
  - **Actual:** SENSOR_CONTROL → ['init']
  - **Then assigns:** ['last', 'init', 'status']

- **Condition:** `rst`
  - **Current:** CONTROL=[], PERMISSIVE=['rst'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['rst']
  - **Then assigns:** ['_step', 'Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'status', 'run']

- **Condition:** `status > TypedLiteralNode(type_name='BYTE', value='0') AND status < TypedLiteralNode(type_name='BYTE', value='100') AND stop_on_error`
  - **Current:** CONTROL=[], PERMISSIVE=['status', 'stop_on_error'], CONTEXT=[]
  - **Actual:** NO_CONTROL_VARIABLE → []
  - **Then assigns:** []

- **Condition:** `run AND _step = 0`
  - **Current:** CONTROL=['_step'], PERMISSIVE=['run'], CONTEXT=[]
  - **Actual:** STATE_CONTROL → ['_step']
  - **Then assigns:** ['Q0', 'last', 'status', 'run', '_step', 'last']

- **Condition:** `NOT q0 AND in0 AND tx - last <= wait0`
  - **Current:** CONTROL=[], PERMISSIVE=['q0', 'in0'], CONTEXT=['tx', 'last', 'wait0']
  - **Actual:** NO_CONTROL_VARIABLE → []
  - **Then assigns:** ['Q0', 'last']

- **Condition:** `run AND _step = 1`
  - **Current:** CONTROL=['_step'], PERMISSIVE=['run'], CONTEXT=[]
  - **Actual:** STATE_CONTROL → ['_step']
  - **Then assigns:** ['Q0', 'Q1', 'last', 'status', 'q0', 'run', '_step', 'last']

- **Condition:** `NOT q1 AND in1 AND tx - last <= wait1`
  - **Current:** CONTROL=[], PERMISSIVE=['q1', 'in1'], CONTEXT=['tx', 'last', 'wait1']
  - **Actual:** NO_CONTROL_VARIABLE → []
  - **Then assigns:** ['Q0', 'Q1', 'last']

- **Condition:** `run AND _step = 2`
  - **Current:** CONTROL=['_step'], PERMISSIVE=['run'], CONTEXT=[]
  - **Actual:** STATE_CONTROL → ['_step']
  - **Then assigns:** ['Q1', 'Q2', 'last', 'status', 'q1', 'run', '_step', 'last']


### TRAFFIC_CTRL.st

**Missed CONTROL cases:**

- **Condition:** `PedestrianButton1`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianButton1'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianButton1']
  - **Then assigns:** ['PedestrianRequest1']

- **Condition:** `PedestrianButton2`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianButton2'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianButton2']
  - **Then assigns:** ['PedestrianRequest2']

- **Condition:** `PedestrianRequest1`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianRequest1'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianRequest1']
  - **Then assigns:** ['PedestrianLight1', 'PedestrianCrossing']

- **Condition:** `PedestrianRequest2`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianRequest2'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianRequest2']
  - **Then assigns:** ['PedestrianLight2', 'PedestrianCrossing']

- **Condition:** `PedestrianCrossing`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianCrossing'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianCrossing']
  - **Then assigns:** ['PedestrianRequest1', 'PedestrianRequest2', 'PedestrianLight1', 'PedestrianLight2', 'PedestrianCrossing', 'LightState']

**Representative cases:**

- **Condition:** `PedestrianButton1`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianButton1'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianButton1']
  - **Then assigns:** ['PedestrianRequest1']

- **Condition:** `PedestrianButton2`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianButton2'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianButton2']
  - **Then assigns:** ['PedestrianRequest2']

- **Condition:** `PedestrianRequest1 OR PedestrianRequest2`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianRequest1', 'PedestrianRequest2'], CONTEXT=[]
  - **Actual:** NO_CONTROL_VARIABLE → []
  - **Then assigns:** ['LightState']

- **Condition:** `Timer.Q`
  - **Current:** CONTROL=['Timer.Q'], PERMISSIVE=[], CONTEXT=[]
  - **Actual:** TIMER_CONTROL → ['Timer.Q']
  - **Then assigns:** ['LightState']

- **Condition:** `Timer.Q`
  - **Current:** CONTROL=['Timer.Q'], PERMISSIVE=[], CONTEXT=[]
  - **Actual:** TIMER_CONTROL → ['Timer.Q']
  - **Then assigns:** ['LightState']

- **Condition:** `PedestrianRequest1`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianRequest1'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianRequest1']
  - **Then assigns:** ['PedestrianLight1', 'PedestrianCrossing']

- **Condition:** `PedestrianRequest2`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianRequest2'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianRequest2']
  - **Then assigns:** ['PedestrianLight2', 'PedestrianCrossing']

- **Condition:** `PedestrianCrossing`
  - **Current:** CONTROL=[], PERMISSIVE=['PedestrianCrossing'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['PedestrianCrossing']
  - **Then assigns:** ['PedestrianRequest1', 'PedestrianRequest2', 'PedestrianLight1', 'PedestrianLight2', 'PedestrianCrossing', 'LightState']


### TOOL_CHANGER.st

**Missed CONTROL cases:**

- **Condition:** `ToolChangeRequired`
  - **Current:** CONTROL=[], PERMISSIVE=['ToolChangeRequired'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['ToolChangeRequired']
  - **Then assigns:** []

**Representative cases:**

- **Condition:** `ToolChangeRequired`
  - **Current:** CONTROL=[], PERMISSIVE=['ToolChangeRequired'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['ToolChangeRequired']
  - **Then assigns:** []

- **Condition:** `ToolCarouselPosition <> DesiredToolNumber`
  - **Current:** CONTROL=[], PERMISSIVE=['ToolCarouselPosition'], CONTEXT=['DesiredToolNumber']
  - **Actual:** NO_CONTROL_VARIABLE → []
  - **Then assigns:** ['RotateCarousel', 'ToolChangeState']

- **Condition:** `ToolCarouselPosition = DesiredToolNumber`
  - **Current:** CONTROL=[], PERMISSIVE=['ToolCarouselPosition'], CONTEXT=['DesiredToolNumber']
  - **Actual:** NO_CONTROL_VARIABLE → []
  - **Then assigns:** ['RotateCarousel', 'LockTool', 'ToolChangeState']


### robotic_sequence.st

**Missed CONTROL cases:**

- **Condition:** `T1_Cnt > 0`
  - **Current:** CONTROL=[], PERMISSIVE=['T1_Cnt'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['T1_Cnt']
  - **Then assigns:** ['T1_Cnt']

- **Condition:** `T2_Cnt > 0`
  - **Current:** CONTROL=[], PERMISSIVE=['T2_Cnt'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['T2_Cnt']
  - **Then assigns:** ['T2_Cnt']

- **Condition:** `Xi1 = TRUE AND Xi6 = TRUE AND Xi7 = TRUE AND Xi8 = TRUE AND Xi9 = TRUE`
  - **Current:** CONTROL=[], PERMISSIVE=['Xi1', 'Xi6', 'Xi7', 'Xi8', 'Xi9'], CONTEXT=[]
  - **Actual:** SENSOR_CONTROL → ['Xi1', 'Xi6', 'Xi7', 'Xi8', 'Xi9']
  - **Then assigns:** ['State']

- **Condition:** `Si2 = TRUE`
  - **Current:** CONTROL=[], PERMISSIVE=['Si2'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['Si2']
  - **Then assigns:** ['State']

- **Condition:** `Ri2 = TRUE`
  - **Current:** CONTROL=[], PERMISSIVE=['Ri2'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['Ri2']
  - **Then assigns:** ['State']

**Representative cases:**

- **Condition:** `T1_Cnt > 0`
  - **Current:** CONTROL=[], PERMISSIVE=['T1_Cnt'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['T1_Cnt']
  - **Then assigns:** ['T1_Cnt']

- **Condition:** `T2_Cnt > 0`
  - **Current:** CONTROL=[], PERMISSIVE=['T2_Cnt'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['T2_Cnt']
  - **Then assigns:** ['T2_Cnt']

- **Condition:** `Si1 = FALSE OR Xi1 = FALSE OR Xi6 = FALSE OR Xi7 = FALSE OR Xi8 = FALSE OR Xi9 = FALSE OR Ri5 = TRUE OR Zi4 = TRUE`
  - **Current:** CONTROL=[], PERMISSIVE=['Si1', 'Xi1', 'Xi6', 'Xi7', 'Xi8', 'Xi9', 'Ri5', 'Zi4'], CONTEXT=[]
  - **Actual:** NO_CONTROL_VARIABLE → []
  - **Then assigns:** ['State']

- **Condition:** `Si4 = TRUE AND Xi1 = TRUE AND Xi6 = TRUE AND Xi7 = TRUE AND Xi8 = TRUE AND Xi9 = TRUE AND Zi1 = TRUE AND Ri1 = TRUE`
  - **Current:** CONTROL=[], PERMISSIVE=['Si4', 'Xi1', 'Xi6', 'Xi7', 'Xi8', 'Xi9', 'Zi1', 'Ri1'], CONTEXT=[]
  - **Actual:** NO_CONTROL_VARIABLE → []
  - **Then assigns:** ['State']

- **Condition:** `Xi1 = TRUE AND Xi6 = TRUE AND Xi7 = TRUE AND Xi8 = TRUE AND Xi9 = TRUE`
  - **Current:** CONTROL=[], PERMISSIVE=['Xi1', 'Xi6', 'Xi7', 'Xi8', 'Xi9'], CONTEXT=[]
  - **Actual:** SENSOR_CONTROL → ['Xi1', 'Xi6', 'Xi7', 'Xi8', 'Xi9']
  - **Then assigns:** ['State']

- **Condition:** `Si2 = TRUE`
  - **Current:** CONTROL=[], PERMISSIVE=['Si2'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['Si2']
  - **Then assigns:** ['State']

- **Condition:** `Ri2 = TRUE`
  - **Current:** CONTROL=[], PERMISSIVE=['Ri2'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['Ri2']
  - **Then assigns:** ['State']

- **Condition:** `T1_Cnt = 0`
  - **Current:** CONTROL=[], PERMISSIVE=['T1_Cnt'], CONTEXT=[]
  - **Actual:** SINGLE_CONTROL → ['T1_Cnt']
  - **Then assigns:** ['T1_Cnt']


## 4. Missed CONTROL Cases (Top 10)

- **CRC_GEN.st** — `REV_IN`
  - Current CONTROL: []
  - Actual: SINGLE_CONTROL → ['REV_IN']

- **CRC_GEN.st** — `REV_IN`
  - Current CONTROL: []
  - Actual: SINGLE_CONTROL → ['REV_IN']

- **CRC_GEN.st** — `_CRC_GEN AND TypedLiteralNode(type_name='DWORD', value='16#8000_0000') > TypedLiteralNode(type_name='DWORD', value='0')`
  - Current CONTROL: []
  - Actual: SINGLE_CONTROL → ['_CRC_GEN']

- **CRC_GEN.st** — `_CRC_GEN AND TypedLiteralNode(type_name='DWORD', value='16#8000_0000') > TypedLiteralNode(type_name='DWORD', value='0')`
  - Current CONTROL: []
  - Actual: SINGLE_CONTROL → ['_CRC_GEN']

- **CRC_GEN.st** — `REV_OUT`
  - Current CONTROL: []
  - Actual: SINGLE_CONTROL → ['REV_OUT']

- **FLOW_METER.st** — `NOT init`
  - Current CONTROL: []
  - Actual: SENSOR_CONTROL → ['init']

- **FLOW_METER.st** — `RST`
  - Current CONTROL: []
  - Actual: SINGLE_CONTROL → ['RST']

- **FLOW_METER.st** — `X > 1.0`
  - Current CONTROL: []
  - Actual: SINGLE_CONTROL → ['X']

- **FT_PIDWL.st** — `rst`
  - Current CONTROL: []
  - Actual: SINGLE_CONTROL → ['rst']

- **FT_PIDWL.st** — `TN = 0.0`
  - Current CONTROL: []
  - Actual: SINGLE_CONTROL → ['TN']

## 5. False CONTROL Cases (Top 10)

---

## Conclusion

The current CONTROL detection rate is **9.9%** (12/121).
**70** cases (57.9%) have actual control variables that are classified as PERMISSIVE.
**0** cases (0.0%) have false CONTROL assignments.

To fix this, the CONTROL rules must be expanded to include:
1. **SINGLE_CONTROL**: Any single variable that is the sole condition of an IF (unless it is a literal or history).
2. **SENSOR_CONTROL**: Sensors and process variables that are the dominant condition.
3. **CONTEXT for feedback**: Internal feedback mirrors (`q0`, `q1`) should be CONTEXT, not PERMISSIVE.
4. **Guard vs. Control distinction**: When a mode variable (`run`) ANDs with a state variable, the mode is a guard (PERMISSIVE); when it is the sole condition, it is control (SINGLE_CONTROL).
