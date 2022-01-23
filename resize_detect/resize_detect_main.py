from os import walk
from os.path import getsize,join
from pprint import pprint
from PIL.Image import open as imgopen,Image

from typing import List
from resize_detect.types.types import DirReport

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

    pprint(dirReports)

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

    for img in imgs:
        img:str

        oversize:bool=False
        overres:bool=False

        imgsize:float=getsize(img)
        if getsize(img)>sizeLimit:
            oversize=True

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

    return {
        "path":dirpath,

        "totalImgs":len(imgs),
        "totalSize":totalsize,

        "overSize":totaloversize,
        "overRes":totaloverres,
        "overBoth":totaloverboth,

        "totalSizeOver":totalsize-totalSizeLimit
    }

def dirReportWithError(report:DirReport)->bool:
    """return true if the given dir report is actually erroneous"""

    return report["overSize"]>0 or report["overRes"]>0 \
        or report["overBoth"]>0 or report["totalSizeOver"]>0

def filterDirReports(reports:List[DirReport])->List[DirReport]:
    """filter list of dir reports to only those that have problems"""

    return [x for x in reports if dirReportWithError(x)]

if __name__=="__main__":
    main()