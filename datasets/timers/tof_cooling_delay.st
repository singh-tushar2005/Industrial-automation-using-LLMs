StopTimer(IN := StopCommand, PT := T#20s);

IF StopTimer.Q THEN
    CoolingValve := TRUE;
END_IF;

IF NOT StopTimer.Q THEN
    CoolingValve := FALSE;
END_IF;
