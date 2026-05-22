IF AutoMode AND SafetyOK AND NOT EmergencyStop THEN
    StartTimer(IN := StartCommand, PT := T#10s);
    IF StartTimer.Q THEN
        MotorContactor := TRUE;
        CoolingValve := TRUE;
    END_IF;
END_IF;

IF Pressure > PressureHighLimit THEN
    Alarm := TRUE;
    MotorContactor := FALSE;
    CoolingValve := TRUE;
END_IF;
