'''
Created on Jun 9, 2011
DEVELOP DEVELOP
@author: jason
'''
import sys
import os
sys.path.append("/share/users/js2746_Jason/Scripts/QualityControlCode")
import FindNIFTIFiles
import subfnFindSubFolder
def RunQA():
    SubFolder = subfnFindSubFolder.PickSub()
    os.chdir(SubFolder)
    FindNIFTIFiles.Display()
    print "All Done"


if __name__ == "__main__":
    RunQA()

print "Hello"
