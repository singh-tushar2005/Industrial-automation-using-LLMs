FUNCTION FC_AlarmCondition : BOOL

VAR_INPUT
    Si1 : BOOL;
    Xi1 : BOOL;
    Xi6 : BOOL;
    Xi7 : BOOL;
    Xi8 : BOOL;
    Xi9 : BOOL;
    Ri5 : BOOL;
    Zi4 : BOOL;
    T1_Done : BOOL;
    T2_Done : BOOL;
    Xi10 : BOOL;
    Zi2 : BOOL;
END_VAR

FC_AlarmCondition :=
    (NOT Si1)
    OR (NOT Xi1)
    OR (NOT Xi6)
    OR (NOT Xi7)
    OR (NOT Xi8)
    OR (NOT Xi9)
    OR Ri5
    OR Zi4
    OR (T1_Done AND NOT Xi10)
    OR (T2_Done AND NOT Zi2);

END_FUNCTION