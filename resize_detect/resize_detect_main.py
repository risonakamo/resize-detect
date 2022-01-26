from os import walk
from os.path import getsize,join
from pprint import pprint
from PIL.Image import open as imgopen,Image
from colored import stylize,fg

from typing import List
from resize_detect.types.types import DirReport,DirReportStats

# inputs
TARGET_DIR:str=r"C:\Users\ktkm\Desktop\OGS"
TARGET_SIZE_MB:float=2.5 #in mb
TARGET_WIDTH:int=2100
TARGET_HEIGHT:int=1200
TARGET_TOTALSIZE_MB:float=5

# derived
TARGET_SIZE_B:float=TARGET_SIZE_MB*1e6
TARGET_TOTALSIZE_B:float=TARGET_TOTALSIZE_MB*1e6

def main()->None:
    mixedDirs:List[str]=[]
    dirReports:List[DirReport]=[]

    # process all dirs
    for root,dirs,files in walk(TARGET_DIR):
        root:str
        dirs:List[str]
        files:List[str]

        # mixed dir, report and skip this dir
        if len(files) and len(dirs):
            mixedDirs.append(root)

        # only dirs, skip this dir
        elif len(dirs) and not len(files):
            pass

        # only images in this folder, this folder is an album. perform detection operations
        elif len(files) and not len(dirs):
            dirReports.append(reportImgs(
                dirpath=root,
                imgs=[join(root,x) for x in files],
                widthLimit=TARGET_WIDTH,
                heightLimit=TARGET_HEIGHT,
                sizeLimit=TARGET_SIZE_B,
                totalSizeLimit=TARGET_TOTALSIZE_B
            ))

    dirReports=filterDirReports(dirReports)
    totalReportsSize:float=0

    print(stylize("directories with warnings:",fg("red")))
    for x in dirReports:
        x:DirReport

        printDirReport(x)
        totalReportsSize+=x["totalSize"]

    print(f"size of all dirs: "+stylize(f"{totalReportsSize/1e6} mb",fg("yellow")))

def reportImgs(
    dirpath:str,
    imgs:List[str],
    widthLimit:int,
    heightLimit:int,
    sizeLimit:float, #in bytes
    totalSizeLimit:float
)->DirReport:
    """generate dir report for list of img paths"""

    totaloversize:int=0
    totaloverres:int=0
    totaloverboth:int=0

    totalsize:float=0

    largestSize:float=0
    widestWidth:int=0
    tallestHeight:int=0

    widestImg:str=""
    tallestImg:str=""

    for img in imgs:
        img:str

        oversize:bool=False
        overres:bool=False

        imgsize:float=getsize(img)
        if getsize(img)>sizeLimit:
            oversize=True

        largestSize=max(largestSize,imgsize)

        totalsize+=imgsize

        openedImg:Image=imgopen(img)
        if openedImg.width>widthLimit or openedImg.height>heightLimit:
            overres=True

        if oversize and overres:
            totaloverboth+=1

        elif oversize:
            totaloversize+=1

        elif overres:
            totaloverres+=1

        if openedImg.width>widestWidth:
            widestWidth=openedImg.width
            widestImg=getResString(openedImg)

        if openedImg.height>tallestHeight:
            tallestHeight=openedImg.height
            tallestImg=getResString(openedImg)

    return {
        "path":dirpath,

        "totalImgs":len(imgs),
        "totalSize":totalsize,

        "overSize":totaloversize,
        "overRes":totaloverres,
        "overBoth":totaloverboth,

        "totalSizeOver":totalsize-totalSizeLimit,

        "widestRes":widestImg,
        "tallestRes":tallestImg,
        "largestSize":largestSize
    }

def dirReportWithError(report:DirReport)->bool:
    """return true if the given dir report is actually erroneous"""

    return report["overSize"]>0 or report["overRes"]>0 \
        or report["overBoth"]>0 or report["totalSizeOver"]>0

def filterDirReports(reports:List[DirReport])->List[DirReport]:
    """filter list of dir reports to only those that have problems"""

    return [x for x in reports if dirReportWithError(x)]

def printDirReport(report:DirReport)->None:
    """print out dir report"""

    print(stylize(f"> {report['path']}",fg("light_cyan")))


    # ---- report OVER stats ----
    overStatPrint(report,"overSize","over size")
    overStatPrint(report,"overRes","over resolution")
    overStatPrint(report,"overBoth","over both")
    print()


    # ---- report total size stats ----
    print(
        f"    - total size: "
        +stylize(
            f"{report['totalSize']/1e6} mb",
            fg("yellow")
        )
    )

    if report["totalSizeOver"]>0:
        print(
            f"    - total size over: "
            +stylize(
                f"{report['totalSizeOver']/1e6} mb",
                fg("red")
            )
        )
        print()


    # ---- report greatest single object value stats ----
    if report["widestRes"]==report["tallestRes"]:
        print(
            "    - largest resolution: "
            +stylize(f"{report['widestRes']}",fg("medium_violet_red"))
        )

    else:
        print(
            f"    - widest resolution: "
            +stylize(f"{report['widestRes']}",fg("medium_violet_red"))
        )
        print(
            f"    - tallest resolution: "
            +stylize(f"{report['tallestRes']}",fg("medium_violet_red"))
        )

    print(
        f"    - largest size: "
        +stylize(f"{report['largestSize']/1e6} mb",fg("medium_violet_red"))
    )
    print()

def overStatPrint(report:DirReport,statKey:DirReportStats,errorDescr:str)->None:
    """if the report has an over error in a certain field, print out. should only be called on
    report keys that are numeric and above 0 means that it should be printed out"""

    if report[statKey]:
        print(
            f"    - {errorDescr}: "
            +stylize(f"{report[statKey]}/{report['totalImgs']}",fg("red"))
        )

def getResString(img:Image)->str:
    """get resolution string from image object"""

    return f"{img.width}x{img.height}"

if __name__=="__main__":
    main()