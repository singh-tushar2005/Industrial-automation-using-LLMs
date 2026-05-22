StartTimer(IN := StartCommand AND SafetyOK, PT := T#5s);

IF StartTimer.Q THEN
    Motor := TRUE;
END_IF;
