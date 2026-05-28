CASE SequenceStep OF
    0:
        Conveyor := TRUE;
        Clamp := FALSE;
        Cutter := FALSE;
    1:
        IF SensorPresent THEN
            Conveyor := FALSE;
            Clamp := TRUE;
        END_IF;
    2:
        PulseTimer(IN := Clamp, PT := T#500ms);
        IF PulseTimer.Q THEN
            Cutter := TRUE;
        END_IF;
    ELSE
        Conveyor := FALSE;
        Clamp := FALSE;
        Cutter := FALSE;
END_CASE;
