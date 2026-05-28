BatchCounter(CU := SensorPresent, R := FaultReset, PV := 10);

IF CounterDone THEN
    Conveyor := FALSE;
    Clamp := TRUE;
    SequenceStep := 2;
END_IF;
