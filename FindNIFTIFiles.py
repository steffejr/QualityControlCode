import os
import fnmatch
import pymysql
import glob
import datetime
from wxPython.wx import *
from Tkinter import *
import tkMessageBox
import subfnDisplayAndUpdateSQL
def Display():
	# create the mysql connection
	conn = pymysql.connect(host='156.145.15.135', port=3306, user='steffejr', passwd='ticabl', db='MRIQualityControl')
	cur = conn.cursor()
	# find out who is doing the assesssment
	Rater = os.environ['USER']
	date = datetime.date.today()
	Today = str(date.year) + '-' + str(date.month) + '-' + str(date.day)

	CurrentPath = os.getcwd()
	Subject = os.path.basename(CurrentPath)
	if not Subject.startswith('P'):
		print "Please enter a subject directory"
	else:
		StudyName = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(CurrentPath))))

		# find the visit folders in the subject folder
		dirlist = os.listdir('./')
		# create a selection if there are more than one subject folders
		choices = [];
		for d in dirlist:
			    if os.path.isdir(d) == True:
				if d.startswith('S'):
					print d
					choices.append(d)
		application = wxPySimpleApp()
		choices.sort()
		dialog = wxSingleChoiceDialog (None, 'Which Visit?', '', choices)

		# The user pressed the "OK" button in the dialog
		if dialog.ShowModal() == wxID_OK:
#			print 'Position of selection:', dialog.GetSelection()
#			print 'Selection:', dialog.GetStringSelection()
			Visit = dialog.GetStringSelection()
		dialog.Destroy()
		# find subid used in database
		subid = Subject
		# find the visit directory
		# Visit=glob.glob('S*')[0]
		visitid = StudyName+"_"+subid+"_"+Visit
		# Check to see if this subject is in the dB
		sqlcommand = "insert into "+StudyName+"(subid,visitid,StudyName) values('"+subid+"','"+visitid+"','"+StudyName+"') on duplicate key update "
		sqlcommand = sqlcommand+"subid='"+subid+"',visitid='"+visitid+"',StudyName='"+StudyName+"';"
		print sqlcommand
		cur.execute(sqlcommand)
		matchs = []
		for root, dirnames, files in os.walk(Visit):
	    		for filename in fnmatch.filter(files, '*.nii'):
	    			if os.path.basename(os.path.dirname(filename)) == 'Quarantine':
	    				continue
				# find the current series name
	#			print 'CWD='+CurrentPath
	#			print 'SUBJECTPATH='+Subject
	#			print 'Visitid='+visitid
				FileName = os.path.join(CurrentPath, root, filename)
#				print 'FileName=' + FileName
# Check to see if this subject has already been checked. If so then only display the images that received warnings or unusable
				PathName = os.path.dirname(FileName)
				SeriesName = os.path.basename(PathName)
#				print SeriesName
				# is the data usable?
				sqlcommand = "select "+SeriesName+"_Usable from "+StudyName+" where subid='" + subid + "' and  visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ";"
				#print sqlcommand
				cur.execute(sqlcommand)
				Result=cur.fetchall()
				UsableFlag = Result[0][0]
				#print "UsableFlag = "+UsableFlag
				# does the data have a warning?
				sqlcommand = "select "+SeriesName+"_Warnings from "+StudyName+" where subid='" + subid + "' and  visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ";"
				#print sqlcommand
				cur.execute(sqlcommand)
				Result=cur.fetchall()
				WarningFlag = Result[0][0]
				#print "Warningflag = "+WarningFlag
				# Get any notes
				sqlcommand = "select "+SeriesName+"_Notes from "+StudyName+" where subid='" + subid + "' and  visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ";"
				#print sqlcommand
				cur.execute(sqlcommand)
				Notes=cur.fetchall()[0][0]
				AssessmentString="Usable: "+UsableFlag+", Warning: "+WarningFlag+", Notes: "+Notes
				#print AssessmentString

				# root.destroy()	
				#Data is usable
				if len(UsableFlag) == 0:
					#print "Condition 1"
					#display
					subfnDisplayAndUpdateSQL.action1(FileName)
				elif UsableFlag == '0':
					#print "Condition 2"
					#display
					subfnDisplayAndUpdateSQL.action1(FileName,AssessmentString)
				elif UsableFlag == '-1':
					subfnDisplayAndUpdateSQL.action1(FileName)
				elif WarningFlag == '1':
					#print "Condition 3"
					subfnDisplayAndUpdateSQL.action1(FileName,AssessmentString)

					
					
				
		# update the database with the rater, date and overall assessment of the subject's data.
		sqlcommand = "update " + StudyName + " set QualityCheckBy='" + Rater + "' where subid='" + subid + "' and  visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ";"
#		print sqlcommand
		cur.execute(sqlcommand)
		cur.execute('commit')
		sqlcommand = "update " + StudyName + " set QualityCheckDate='" + Today + "' where subid='" + subid + "' and  visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ";"
#		print sqlcommand
		cur.execute(sqlcommand)
		cur.execute('commit')
		# check to see if this subject should be included 

		dialog = wxMessageDialog(None, 'Should this subject be INCLUDED in further analyses?', 'Include', wxYES | wxNO | wxICON_INFORMATION)

		Output = dialog.ShowModal()
		if Output == wxID_YES:
			sqlcommand = "update " + StudyName + " set IncludeSubject='1' where subid='" + subid + "' and  visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ";"
			cur.execute(sqlcommand)
			cur.execute('commit')
	#	dlg.Destroy()
		elif Output == wxID_NO:
			sqlcommand = "update " + StudyName + " set IncludeSubject='0' where subid='" + subid + "' and  visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ";"
			cur.execute(sqlcommand)
			cur.execute('commit')

#		print Output
		dialog.Destroy()
		# check to see if this subject should be Re-CHECKED 

		dialog = wxMessageDialog(None, "Should this subject's data be RE-CHECKED?", "Include", wxYES | wxNO | wxICON_INFORMATION)
		Output = dialog.ShowModal()
		if Output == wxID_YES:
			sqlcommand = "update " + StudyName + " set ReCheck='1' where subid='" + subid + "' and  visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ";"
			print sqlcommand
			cur.execute(sqlcommand)
			cur.execute('commit')

	#	dlg.Destroy()
		elif Output == wxID_NO:
			sqlcommand = "update " + StudyName + " set ReCheck='0' where subid='" + subid + "' and  visitid='" + visitid + "' AND StudyName=" + "'" + StudyName + "'" + ";"
			print sqlcommand
			cur.execute(sqlcommand)
			cur.execute('commit')
			# move folder out of quarantine
	#	print Output
		dialog.Destroy()
		
		print ""

	# if the person checks out, then they should be moved out of quarantine. 
