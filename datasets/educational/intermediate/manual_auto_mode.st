CASE Mode OF
    0:
        IF ManualMode AND StartCommand THEN
            Pump := TRUE;
        END_IF;
    1:
        IF AutoMode AND ProcessEnable THEN
            Pump := TRUE;
            InletValve := TRUE;
        END_IF;
    ELSE
        Pump := FALSE;
        InletValve := FALSE;
END_CASE;
