PROGRAM main

VAR
END_VAR

// Таймеры
IF T1_Cnt > 0 THEN
    T1_Cnt := T1_Cnt - 1;
END_IF;

IF T2_Cnt > 0 THEN
    T2_Cnt := T2_Cnt - 1;
END_IF;

// Авария
IF (Si1 = FALSE) OR (Xi1 = FALSE) OR (Xi6 = FALSE) OR (Xi7 = FALSE)
   OR (Xi8 = FALSE) OR (Xi9 = FALSE) OR (Ri5 = TRUE) OR (Zi4 = TRUE) THEN
    State := 11;
END_IF;

CASE State OF

    0:
        Ho1 := TRUE;
        Ho2 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Yo1 := FALSE;
        Ro1 := FALSE;
        Ro2 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        IF Si4 = TRUE
           AND Xi1 = TRUE
           AND Xi6 = TRUE
           AND Xi7 = TRUE
           AND Xi8 = TRUE
           AND Xi9 = TRUE
           AND Zi1 = TRUE
           AND Ri1 = TRUE
        THEN
            State := 1;
        END_IF;

    1:
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Yo1 := FALSE;

        Ro1 := FALSE;
        Ro2 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        IF Xi1 = TRUE
           AND Xi6 = TRUE
           AND Xi7 = TRUE
           AND Xi8 = TRUE
           AND Xi9 = TRUE
        THEN
            State := 2;
        END_IF;

    2:
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Yo1 := FALSE;

        Ro1 := FALSE;
        Ro2 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        IF Si2 = TRUE THEN
            State := 3;
        END_IF;

    3:
        Ro2 := TRUE;
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Yo1 := FALSE;

        Ro1 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        IF Ri2 = TRUE THEN
            State := 4;
        END_IF;

    4:
        Yo1 := TRUE;
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Ro1 := FALSE;
        Ro2 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        State := 5;

    5:
        Yo1 := TRUE;
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Ro1 := FALSE;
        Ro2 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        IF T1_Cnt = 0 THEN
            T1_Cnt := 500;
        END_IF;

        IF Xi10 = TRUE THEN
            T1_Cnt := 0;
            State := 6;
        END_IF;

    6:
        Yo1 := TRUE;
        Ro1 := TRUE;
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Ro2 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        IF Ri2 = TRUE THEN
            State := 7;
        END_IF;

    7:
        Yo1 := TRUE;
        Ro1 := TRUE;
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Ro2 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        IF Xi4 = TRUE
           AND Xi5 = TRUE
           AND Ri3 = TRUE
        THEN
            State := 8;
        END_IF;

    8:
        Yo1 := TRUE;
        Zo1 := TRUE;
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Ro1 := FALSE;
        Ro2 := FALSE;
        Ro3 := TRUE;

        Zo2 := FALSE;

        IF T2_Cnt = 0 THEN
            T2_Cnt := 15000;
        END_IF;

        IF Zi2 = TRUE THEN
            T2_Cnt := 0;
            State := 9;
        END_IF;

    9:
        Yo1 := TRUE;
        Ro2 := TRUE;
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Ro1 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        IF Ri2 = TRUE THEN
            State := 10;
        END_IF;

    10:
        Yo1 := TRUE;
        Ro2 := TRUE;
        Ho2 := TRUE;

        Ho1 := FALSE;
        Ho3 := FALSE;
        Ho4 := FALSE;
        Ho5 := FALSE;

        Ro1 := FALSE;
        Ro3 := TRUE;

        Zo1 := FALSE;
        Zo2 := FALSE;

        IF Ri4 = TRUE THEN
            Yo1 := FALSE;
            Parts_Count := Parts_Count + 1;
            State := 0;
        END_IF;

    11:
        Yo1 := TRUE;

        Ho3 := TRUE;
        Ho4 := TRUE;
        Ho5 := TRUE;

        Zo2 := TRUE;
        Ro3 := TRUE;

        Ho1 := FALSE;
        Ho2 := FALSE;

        Ro1 := FALSE;
        Ro2 := FALSE;
        Zo1 := FALSE;

        T1_Cnt := 0;
        T2_Cnt := 0;

        IF Xi1 = TRUE
           AND Si3 = TRUE
        THEN
            Yo1 := FALSE;

            Ho3 := FALSE;
            Ho4 := FALSE;
            Ho5 := FALSE;

            Zo2 := FALSE;
            Ro3 := FALSE;

            State := 0;
        END_IF;

END_CASE

END_PROGRAM