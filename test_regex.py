import re

regex = r"\b(BOOL|BYTE|WORD|DWORD|INT|DINT|UINT|UDINT|REAL|TIME|STRING)#([0-9A-Fa-f_]+|2#[01_]+|16#[0-9A-Fa-f_]+|[0-9._]+|'[^']*')"

tests = [
    "DWORD#16#8000_0000",
    "BYTE#2#0000_0001",
    "BYTE#0",
    "REAL#1.0",
    "STRING#'0'",
    "''",
]

for t in tests:
    m = re.search(regex, t)
    print(f"{t!r}: match={m.group(0) if m else None}")
