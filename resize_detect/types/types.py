from typing import TypedDict,Literal

class DirReport(TypedDict):
    path:str

    totalImgs:int
    totalSize:float

    overSize:int
    overRes:int
    overBoth:int

    totalSizeOver:float

DirReportStats=Literal[
    "overSize",
    "overRes",
    "overBoth"
]
"""these must all be keys of DirReport and must mean over-limit if above 0"""