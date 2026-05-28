IF Temperature > TempHighLimit THEN
    Heater := FALSE;
    CoolingValve := TRUE;
    Alarm := TRUE;
END_IF;

IF Pressure > PressureHighLimit THEN
    Pump := FALSE;
    OutletValve := TRUE;
    Alarm := TRUE;
END_IF;
