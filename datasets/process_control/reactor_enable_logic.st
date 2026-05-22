IF AutoMode AND SafetyOK AND TankLevel >= LowLevel AND Pressure < PressureHighLimit THEN
    ProcessEnable := TRUE;
END_IF;

IF ProcessEnable THEN
    Mixer := TRUE;
    Heater := TRUE;
END_IF;
