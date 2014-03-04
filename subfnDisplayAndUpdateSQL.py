'''
# DEVELOP
'''
#def perform(fun, *args):
#	fun( *args )
import os
from wxPython.wx import *
import pymysql
import glob
import shutil
from Tkinter import *
import tkMessageBox
def DisplayNotes(Notes):
        print "Creating a DIALOG BOX"
        root = Tk()
        root.title('Previous Assessment')
        dlg2 = Label(root)
        dlg2["text"]=Notes
        dlg2.pack()
        
def action1(FileName,Notes=''):
    print "================================================="
    print FileName
    # Take any notes from the SQL and display them
    #print Notes
    #print len(Notes)
    if len(Notes)>0:
        print Notes
        
    conn = pymysql.connect(host='156.145.15.135', port=3306, user='steffejr', passwd='ticabl', db='MRIQualityControl')
    cur = conn.cursor()
	# starting with the file name, split up the path 
    PathName = os.path.dirname(FileName)
#	print 'PathName=' + PathName
    SeriesName = os.path.basename(PathName)
#	print 'Series Name=' + SeriesName
    PathName = os.path.dirname(PathName)
    Visit = os.path.basename(PathName)
#	print 'VisitID=' + Visit
#	print 'PathName=' + PathName
    PathName = os.path.dirname(PathName)
#	print 'PathName=' + PathName
    subid = os.path.basename(PathName)
#	print 'SubID=' + subid
#    print 'Series Name=' + SeriesName
    StudyName = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(PathName))))
    visitid=StudyName+"_"+subid+"_"+Visit
# before calling fslview find out the image intensity range
    Range = os.popen('fslstats ' + FileName + ' -r')
    Range = Range.read()
    Range = Range.split(' ')
    os.system('fslview ' + FileName + ' -b ' + Range[0] + ',' + Range[1])
	#application = wxPySimpleApp()
	# Check to see if this is a recheck or not
    #dlg = wxMessageDialog(None, 'Do NOT include if it is a survey or duplicate', 'Include this scan?', wxYES | wxNO | wxICON_INFORMATION)
    #Output = dlg.ShowModal()
    
    #if Output == wxID_YES: 
    AssessFlag = False
    if len(Notes)>0:
        dlg = wxMessageDialog(None, 'Reassess this scan?', 'Reassess?', wxYES | wxNO | wxICON_INFORMATION)
        Output = dlg.ShowModal()
        if (Output == wxID_YES):
            AssessFlag = True
    else:
        AssessFlag = True
    if AssessFlag:
		#print 'Yes'
#		choices = ['Good', 'MRI Artifact', 'Motion', 'Physiological', 'Bad Recon', 'Fuzzy', 'Strong Warping', 'Slice Dropout', 'Time Series Prob', 'Missing Slices','No Data', 'Other']
		choices = ['Usable','Usable with Warnings','Not Usable']
		dialog = wxSingleChoiceDialog (None, 'Was the data usable?', 'MRI Assessment', choices)
		# The user pressed the "OK" button in the dialog
		dialog.ShowModal()

		Response = str(dialog.GetStringSelection())
		UsableFlag = -1;
		if Response == 'Usable':
			sqlcommand = "update " + StudyName + " set " + SeriesName + "_Usable='1' where (subid='" + subid + "' AND visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ");"
			#print sqlcommand
			cur.execute(sqlcommand)
			cur.execute('commit')
			sqlcommand = "update " + StudyName + " set " + SeriesName + "_Warnings='0' where (subid='" + subid + "' AND visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ");"
			#print sqlcommand
			cur.execute(sqlcommand)
			cur.execute('commit')
			#print subid+","+visitid+","+SeriesName+","+Response+",,"+FileName
			UsableFlag = 1;
		elif Response == 'Usable with Warnings':
			sqlcommand = "update " + StudyName + " set " + SeriesName + "_Usable='1' where (subid='" + subid + "' AND visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ");"
			#print sqlcommand
			cur.execute(sqlcommand)
			cur.execute('commit')
			sqlcommand = "update " + StudyName + " set " + SeriesName + "_Warnings='1' where (subid='" + subid + "' AND visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ");"
			#print sqlcommand
			cur.execute(sqlcommand)
			cur.execute('commit')
			#print subid+","+visitid+","+SeriesName+","+Response+",,"+FileName
			UsableFlag = 0;
		else:
			# why was it not usable
			#sqlcommand = "update " + StudyName + " set " + SeriesName + "_NotUsable_Reason='" + Response + "'," + SeriesName + "_Usable='N'  where (subid='" + subid + "' AND visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ");"
			sqlcommand = "update " + StudyName + " set " + SeriesName + "_Usable='0' where (subid='" + subid + "' AND visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ");"
			#print sqlcommand
			cur.execute(sqlcommand)
			cur.execute('commit')
			sqlcommand = "update " + StudyName + " set " + SeriesName + "_Warnings='1' where (subid='" + subid + "' AND visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ");"
			#print sqlcommand
			cur.execute(sqlcommand)
			cur.execute('commit')
			UsableFlag = 0;
		if 	UsableFlag == 0:
			choices = ['MRI Artifact', 'Motion', 'Physiological', 'Bad Recon', 'Fuzzy', 'Strong Warping', 'Slice Dropout', 'Time Series Prob', 'Missing Slices','No Data', 'Other']
			dialog = wxSingleChoiceDialog (None, 'Why is this data unusable or has warnings?', 'MRI Assessment', choices)
			# The user pressed the "OK" button in the dialog
			dialog.ShowModal()
			Response = str(dialog.GetStringSelection())
			dialog2 = wxTextEntryDialog (None, 'Enter any notes:', 'Image notes', '')
		# If the user presses, "OK", print the value. Otherwise, print another message.
			if dialog2.ShowModal() == wxID_OK:
				#print dialog2.GetValue()
				sqlcommand = "update " + StudyName + " set " + SeriesName + "_Notes='" + Response+": "+dialog2.GetValue() + "' where (subid='" + subid + "' AND visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ");"
				#print sqlcommand					
				cur.execute(sqlcommand)
				cur.execute('commit')
			else:
				print 'You did not push the "OK" button.'
			dialog.Destroy()
	#print subid+","+visitid+","+SeriesName+","+Response+","+dialog2.GetValue()+","+FileName
#        dlg.Destroy()
    #elif Output == wxID_NO:
		#print 'No'
		#print FileName
#		PathName = os.path.dirname(FileName)
#		File = os.path.basename(FileName)
		#print PathName
#		OutFileName = os.path.join(PathName, 'X_' + File)
#		print OutFileName
#		shutil.move(FileName, OutFileName)
	#print Output
    #dlg.Destroy()
		
def JustDisplayImages(args):
	FileName = args
	conn = pymysql.connect(host='156.145.15.135', port=3306, user='steffejr', passwd='ticabl', db='MRIQualityControl')
	cur = conn.cursor()
	# starting with the file name, split up the path 
	PathName = os.path.dirname(FileName)
#	print 'PathName=' + PathName
	SeriesName = os.path.basename(PathName)
#	print 'Series Name=' + SeriesName
	PathName = os.path.dirname(PathName)
	Visit = os.path.basename(PathName)
	
#	print 'VisitID=' + Visit
#	print 'PathName=' + PathName
	PathName = os.path.dirname(PathName)
#	print 'PathName=' + PathName
	subid = os.path.basename(PathName)
#	print 'SubID=' + subid
#	print 'Series Name=' + SeriesName
	StudyName = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(PathName))))
	visitid=StudyName+"_"+subid+"_"+Visit
	
# before calling fslview find out the image intensity range
	Range = os.popen('fslstats ' + FileName + ' -r')
	Range = Range.read()
	Range = Range.split(' ')
	os.system('fslview ' + FileName + ' -b ' + Range[0] + ',' + Range[1])	
		
	
def TestingGround():
    application = wxPySimpleApp()
    dialog = wxMessageBox (None, 'Which Subject?','caption')
    dialog.Destroy()
    
    
def YesNo(parent, question, caption = 'Yes or no?'):
    dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.ICON_QUESTION)
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    return result
def Info(parent, message, caption = 'Insert program title'):
    dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
def Warn(parent, message, caption = 'Warning!'):
    dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_WARNING)
    dlg.ShowModal()
    dlg.Destroy()
    
    
    