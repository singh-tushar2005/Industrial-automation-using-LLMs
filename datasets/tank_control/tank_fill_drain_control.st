IF TankLevel < LowLevel AND AutoMode THEN
    InletValve := TRUE;
    OutletValve := FALSE;
END_IF;

IF TankLevel >= HighLevel THEN
    InletValve := FALSE;
    OutletValve := TRUE;
END_IF;
