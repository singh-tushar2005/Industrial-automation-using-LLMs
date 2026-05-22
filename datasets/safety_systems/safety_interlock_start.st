IF StartCommand AND SafetyOK AND GuardClosed AND NOT FaultActive THEN
    ProcessEnable := TRUE;
END_IF;

IF ProcessEnable THEN
    MotorRun := TRUE;
    InletValve := TRUE;
END_IF;
