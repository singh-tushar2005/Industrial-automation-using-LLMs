IF TankLevel > HighLevel THEN
    InletValve := FALSE;
    Pump := FALSE;
    Alarm := TRUE;
END_IF;

IF EmergencyStop THEN
    InletValve := FALSE;
    OutletValve := FALSE;
    Pump := FALSE;
END_IF;
