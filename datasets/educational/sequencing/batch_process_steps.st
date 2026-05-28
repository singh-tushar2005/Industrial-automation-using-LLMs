CASE BatchStep OF
    0:
        IF AutoMode AND TankLevel < LowLevel THEN
            InletValve := TRUE;
            BatchStep := 1;
        END_IF;
    1:
        IF TankLevel >= HighLevel THEN
            InletValve := FALSE;
            Mixer := TRUE;
            MixTimer(IN := TRUE, PT := T#30s);
        END_IF;
    2:
        IF MixTimer.Q THEN
            Mixer := FALSE;
            OutletValve := TRUE;
        END_IF;
END_CASE;
