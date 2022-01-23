from typing import TypedDict

class DirReport(TypedDict):
    path:str

    totalImgs:int
    totalSize:float

    overSize:int
    overRes:int
    overBoth:int

    totalSizeOver:float