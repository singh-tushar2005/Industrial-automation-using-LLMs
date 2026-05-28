IF EmergencyStop OR GuardOpen THEN
    Motor := FALSE;
    Pump := FALSE;
    InletValve := FALSE;
    Alarm := TRUE;
END_IF;
