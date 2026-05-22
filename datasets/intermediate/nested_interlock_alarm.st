IF SafetyOK AND DoorClosed THEN
    IF Pressure > PressureHighLimit THEN
        Alarm := TRUE;
        Pump := FALSE;
    END_IF;
END_IF;
