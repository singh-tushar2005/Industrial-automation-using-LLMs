IF OverloadTrip OR EmergencyStop THEN
    MotorContactor := FALSE;
    Alarm := TRUE;
END_IF;

IF StartCommand AND SafetyOK AND NOT OverloadTrip THEN
    MotorContactor := TRUE;
END_IF;
