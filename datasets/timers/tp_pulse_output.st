PulseTimer(IN := SensorPresent, PT := T#250ms);

IF PulseTimer.Q THEN
    Cutter := TRUE;
END_IF;
