CASE StartupStep OF
    0:
        IF StartCommand AND SafetyOK THEN
            StartupStep := 1;
        END_IF;
    1:
        PurgeTimer(IN := TRUE, PT := T#15s);
        IF PurgeTimer.Q THEN
            OutletValve := TRUE;
            StartupStep := 2;
        END_IF;
    2:
        InletValve := TRUE;
        Pump := TRUE;
    ELSE
        Pump := FALSE;
        InletValve := FALSE;
        OutletValve := FALSE;
END_CASE;
