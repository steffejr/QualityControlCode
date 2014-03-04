#!/usr/local/epd/bin/python
'''
Created on Jun 9, 2011

@author: jason
'''
import os
import sys
sys.path.append("/share/users/js2746_Jason/Scripts/QualityControlCode")
#import mymod
import glob
import subfnPickFolder
from wxPython.wx import *
def PickSub():
    # select study path
    BasePath=subfnPickFolder.PickFolder()
    # enter the study folder
    os.chdir(BasePath)
    # go up out of the Incoming Folder and into the Subjects Folder
    os.chdir('../Subjects')
    
    CurrentPath=os.getcwd()
    #print "CurrentPath = "+CurrentPath
    # find Subject folders in Quarantine
    SubFolders = glob.glob('P*')
    SubFolders.sort()
    # Create list the subject folders
    choices = [];
    Names = [];
    for i in SubFolders: 
        CurrentChoice=os.path.join(CurrentPath,i)
        #print "Choice="+CurrentChoice    
        choices.append(CurrentChoice)
        CurrentName = i
        Names.append(CurrentName)
    # Ask which subject folder
    Names.sort()
    choices.sort()
    application = wxPySimpleApp()
    dialog = wxSingleChoiceDialog(None, 'Which Subject?', '', Names )
    
    if dialog.ShowModal() == wxID_OK:
        Folder=choices[dialog.GetSelection()]
#        print "Folder="+Folder
        return Folder
    dialog.Destroy()
    
    
