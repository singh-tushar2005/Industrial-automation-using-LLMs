IF FaultActive THEN
    Motor := FALSE;
    Pump := FALSE;
    Alarm := TRUE;
END_IF;

IF FaultReset AND SafetyOK THEN
    FaultActive := FALSE;
    Alarm := FALSE;
END_IF;
