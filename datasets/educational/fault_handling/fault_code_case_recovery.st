CASE FaultCode OF
    1:
        Motor := FALSE;
        Alarm := TRUE;
    2:
        Pump := FALSE;
        InletValve := FALSE;
        Alarm := TRUE;
    3:
        Heater := FALSE;
        CoolingValve := TRUE;
        Alarm := TRUE;
    ELSE
        Alarm := FALSE;
END_CASE;
