IF ManualMode AND StartCommand AND SafetyOK THEN
    Pump := TRUE;
END_IF;

IF AutoMode AND TankLevel < LowLevel AND SafetyOK THEN
    Pump := TRUE;
    InletValve := TRUE;
END_IF;

IF TankLevel >= HighLevel OR StopCommand THEN
    Pump := FALSE;
    InletValve := FALSE;
END_IF;
