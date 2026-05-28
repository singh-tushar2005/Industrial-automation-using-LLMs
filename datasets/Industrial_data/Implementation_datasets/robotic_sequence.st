PROGRAM MAIN
VAR
    State : INT := 0;
    T1_Cnt : INT := 0;
    T2_Cnt : INT := 0;

    Si1, Si2, Si3, Si4 : BOOL := FALSE;
    Xi1, Xi4, Xi5, Xi6, Xi7, Xi8, Xi9, Xi10 : BOOL := FALSE;
    Zi1, Zi2, Ri1, Ri2, Ri3, Ri4, Ri5, Zi4 : BOOL := FALSE;

    Ho1, Ho2, Ho3, Ho4, Ho5 : BOOL := FALSE;
    Yo1, Ro1, Ro2, Ro3, Zo1, Zo2 : BOOL := FALSE;

    Parts_Count : INT := 0;
    Alarm_Active : BOOL := FALSE;
END_VAR


(* Timers *)

IF T1_Cnt > 0 THEN
    T1_Cnt := T1_Cnt - 1;
END_IF;

IF T2_Cnt > 0 THEN
    T2_Cnt := T2_Cnt - 1;
END_IF;


(* Alarm Logic *)

IF (Si1 = FALSE)
    OR (Xi1 = FALSE)
    OR (Xi6 = FALSE)
    OR (Xi7 = FALSE)
    OR (Xi8 = FALSE)
    OR (Xi9 = FALSE)
    OR (Ri5 = TRUE)
    OR (Zi4 = TRUE)
THEN
    State := 11;
END_IF;


CASE State OF

    0:
        (* IDLE *)

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
        (* CHECK_SAFETY *)

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
        (* WAIT_START *)

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
        (* ROBOT_TAKE_BLANK *)

        Ro2 := TRUE;
        Ho2 := TRUE;

        IF Ri2 = TRUE THEN
            State := 4;
        END_IF;


    4:
        (* EJECTOR_ON *)

        Yo1 := TRUE;
        Ho2 := TRUE;

        State := 5;


    5:
        (* WAIT_VACUUM *)

        Yo1 := TRUE;
        Ho2 := TRUE;

        IF T1_Cnt = 0 THEN
            T1_Cnt := 500;
        END_IF;

        IF Xi10 = TRUE THEN
            T1_Cnt := 0;
            State := 6;
        END_IF;


    6:
        (* ROBOT_INTERACT *)

        Yo1 := TRUE;
        Ro1 := TRUE;
        Ho2 := TRUE;

        IF Ri2 = TRUE THEN
            State := 7;
        END_IF;


    7:
        (* ROBOT_BLANK_DROP *)

        Yo1 := TRUE;
        Ro1 := TRUE;
        Ho2 := TRUE;

        IF Xi4 = TRUE
            AND Xi5 = TRUE
            AND Ri3 = TRUE
        THEN
            State := 8;
        END_IF;


    8:
        (* PRESS_START *)

        Yo1 := TRUE;
        Zo1 := TRUE;
        Ho2 := TRUE;

        IF T2_Cnt = 0 THEN
            T2_Cnt := 15000;
        END_IF;

        IF Zi2 = TRUE THEN
            T2_Cnt := 0;
            State := 9;
        END_IF;


    9:
        (* ROBOT_TAKE *)

        Yo1 := TRUE;
        Ro2 := TRUE;
        Ho2 := TRUE;

        IF Ri2 = TRUE THEN
            State := 10;
        END_IF;


    10:
        (* ROBOT_PART_DROP *)

        Yo1 := TRUE;
        Ro2 := TRUE;
        Ho2 := TRUE;

        IF Ri4 = TRUE THEN
            Yo1 := FALSE;
            Parts_Count := Parts_Count + 1;
            State := 0;
        END_IF;


    11:
        (* ALARM *)

        Yo1 := TRUE;

        Ho3 := TRUE;
        Ho4 := TRUE;
        Ho5 := TRUE;

        Zo2 := TRUE;
        Ro3 := TRUE;

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

END_CASE;

END_PROGRAM