'''
Created on May 3, 2013

@author: jason
'''
'''
Created on Apr 30, 2013

@author: jason
'''
import os
import sys
import CheckSubject

%run study.py

reload(CheckSubject)
conn_main = studydata.db_connection_main
conn_qc = studydata.db_connection
SubjectSummary = []
for S in study.subjectlist:
#for i in range(0,5,1):
    #S=study.subjectlist[i]
#for S in study.subjectlist:
    D=CheckSubject.CheckSubject(S)
    #D.InitializeScansCogRes()
    D.InitializeScansILS()
    #D.InitializeScansRANN()
    print "\n-----------------------------"
    print "============================="
    print "========= %s ========="%(D.Subject.subid)
    print "======= %s ======="%("Acquistion Problems")  
    for V in D.Subject.visitlist: 
        Files=os.listdir(V.path)
        D.InspectImages(Files,V.path)
        SubjectSummary.append(D)
    print "======= %s ======="%("Missing Scans")
    D.CheckAllScansCollected()
    print "======= %s ======="%("QC Assessment")
    D.PrintQCAssessment(conn_qc,study.name)
        

    
        
