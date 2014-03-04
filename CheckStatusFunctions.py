import os
from pandas import DataFrame
os.sys.path.append("/share/users/js2746_Jason/Scripts/QualityControlCode")
import CheckSubject
from getpass import getuser
from datetime import datetime
import pymysql
import pymysql.cursors
import csv
conn = pymysql.connect(host='156.145.15.135', port=3306, user='steffejr', passwd='ticabl', db='cnsdivdb', cursorclass=pymysql.cursors.DictCursor)
conn.cur = conn.cursor()

def get_Age(Subject,conn):
    
    sqlcommand = "SELECT age from ParticipantTable where subid = '%s'"%(Subject.Subject.subid)
    conn.cur.execute(sqlcommand)
    rows = conn.cur.fetchall()
    if len(rows) > 0:
        age = rows[0]['age']
    else:
        age = -9999
    #conn.cur.close()
    return age

def study_DisplayStatus_All_Series(study,studydata):
#    SubjectsSummary = study_Check_All_Subjects(study,studydata)
    # prepare to write a summary of ALL collected/imported scans to a spreadsheet
    if study.name is "Exercise58":
        [SubjectsSummary, QuarantineSummary,ExcludedSummary]=study_Check_All_v3(study,studydata)
    else:
        [SubjectsSummary, QuarantineSummary,ExcludedSummary]=study_Check_All_v2(study,studydata)
    [sSum,sDF]=ConvertSummaryToDataFrame(SubjectsSummary)
    [qSum,qDF]=ConvertSummaryToDataFrame(QuarantineSummary)
    [eSum,eDF]=ConvertSummaryToDataFrame(ExcludedSummary)
    # create a dictionary out of these and return that
    allSum = {'SubjectsSummary':sSum,'QuarantineSummary':qSum,'ExcludedSummary':eSum} 
    allDF = {'Subjects':sDF,'Quarantine':qDF,'Excluded':eDF}
    return allSum,allDF

def ConvertSummaryToDataFrame(SubjectsSummary):
    if len(SubjectsSummary)>0:
        full_list = []
        ColumnNames = []
        ColumnNames.append('subid')
        ColumnNames.append('visitid')
        ColumnNames.append('age')
        for S in SubjectsSummary[0].Scans:
            ColumnNames.append(SubjectsSummary[0].Scans[S]['SeriesName'])
        ColumnNames.append('AllCollected')
        ColumnNames.append('TaskCount')
        NTasks = len(SubjectsSummary[0].TaskList)
        
        for S in SubjectsSummary:
            one_list = []
            count = 0
            #for V in S.Subject.visits:
            one_list.append(S.Subject.subid)
            if S.Visit:
                one_list.append(S.Visit.visid)
            else:
                one_list.append('')
            # need to get visitid written to the file here.
            one_list.append(get_Age(S,conn))
            for j in S.Scans:
                if len(S.Scans[j]['FlagList'])>0:
                    one_list.append(1)
                    L = 1
                    if j in S.TaskList:
                        count = count + 1
                else:
                    one_list.append(0)
                    L = 0
            one_list.append(S.AllCollected)
            one_list.append(count)
            full_list.append(one_list)
            df = DataFrame(full_list, columns=ColumnNames)
    else:
        df = DataFrame()
    return SubjectsSummary,df

def study_Check_All_v2(study,studydata):
    #     check subjects folder
    # DEVELOP
    SubjectsSummary = []
    for S in study.subjectlist:
        D = study_Check_One_Subjects(S.subid,study,studydata)
        SubjectsSummary.append(D)
    # check quarantine folder    
    QuarantineSummary = []
    for S in study.quarantine.subjectlist:
        D = study_Check_One_Quarantine(S.subid,study,studydata)
        QuarantineSummary.append(D)
    # check exclude folder    
    ExcludedSummary = []
    for S in study.excluded.subjectlist:
        D = study_Check_One_Excluded(S.subid,study,studydata)
        ExcludedSummary.append(D)
        
    return SubjectsSummary,QuarantineSummary,ExcludedSummary

def study_Check_All_v3(study,studydata):
    #     check subjects folder
    # DEVELOP
    SubjectsSummary = []
    for S in study.subjectlist:
        for V in S.visitlist:
            D = study_Check_OneVisit_Subjects(S.subid,V.visid,study,studydata)
            SubjectsSummary.append(D)
    # check quarantine folder    
    QuarantineSummary = []
    for S in study.quarantine.subjectlist:
        for V in S.visitlist:
            D = study_Check_OneVisit_Quarantine(S.subid,V.visid,study,studydata)
            QuarantineSummary.append(D)
    # check exclude folder    
    ExcludedSummary = []
    for S in study.excluded.subjectlist:
        for V in S.visitlist:
            D = study_Check_OneVisit_Excluded(S.subid,V.visid,study,studydata)
            ExcludedSummary.append(D)
        
    return SubjectsSummary,QuarantineSummary,ExcludedSummary

def study_Check_All_visits(study,studydata):
    # check subjects folder
    SubjectsSummary = []
    for S in study.subjectlist:
        D = study_Check_One_Subjects(S.subid,study,studydata)
        SubjectsSummary.append(D)
    # check quarantine folder    
    QuarantineSummary = []
    for S in study.quarantine.subjectlist:
        D = study_Check_One_Quarantine(S.subid,study,studydata)
        QuarantineSummary.append(D)
    # check exclude folder    
    ExcludedSummary = []
    for S in study.excluded.subjectlist:
        D = study_Check_One_Excluded(S.subid,study,studydata)
        ExcludedSummary.append(D)
        
    return SubjectsSummary,QuarantineSummary,ExcludedSummary
    
def study_Check_All_Subjects(study,studydata):
    # Check the acquisition paramet# check subjects folderers and 
    # for missing data from all participants
    # in the Subjects folder 
    SubjectsSummary = []
    conn_qc = studydata.db_connection
    for S in study.subjectlist:
        D = CheckSubject.CheckSubject(S)
        #D.InitializeScansCogRes()
        # python does not use switch/case statements
        if study.name is "RANN":
            D.InitializeScansRANN()
        elif study.name is "CogRes":
            D.InitializeScansCogRes()
        elif study.name is "iLS":
            D.InitializeScansILS()
        elif study.name is "WHICAP":
            D.InitializeScansWHICAPV3()    
        elif study.name is "AZ2":
            D.InitializeScansAZ2()   
        elif study.name is "Exercise58":
            D.InitializeScansEx58()   
        else:
            break
            
        print "\n-----------------------------"
        print "============================="
        print "========= %s ========="%(D.Subject.subid)
        print "======= %s ======="%("Acquistion Problems")  
        for V in D.Subject.visitlist: 
            Files=os.listdir(V.path)
            D.InspectImages(Files,V.path)
        print "======= %s ======="%("Found Scans")
        D.CheckAllScansCollected()
        print "======= %s ======="%("Missing Scans")
        D.CheckAllScansNOTCollected()
        print "======= %s ======="%("QC Assessment")
        D.PrintQCAssessment(conn_qc,study.name)
        SubjectsSummary.append(D)
    return SubjectsSummary

def study_GetBehStatus(SubjectsSummary,study,studydata,writer):
    if study.name is "RANN":
        [SubjectsSummary,df] = study_GetBehRANNStatus(SubjectsSummary,study,studydata,writer)
    elif study.name is "CogRes":
        [SubjectsSummary,df] = study_GetBehCogResStatus(SubjectsSummary,study,studydata,writer)
    elif study.name is "iLS":
        [SubjectsSummary,df] = study_GetBehILSStatus(SubjectsSummary,study,studydata,writer)

    # write out codes
    codes = []
    codes.append([0,'no trials correct'])
    codes.append([1,'at least one trial correct'])
    codes.append([-9999,'no data in the database'])
    CodeColNames = ['code','description']
    df_Notes=DataFrame(codes,columns=CodeColNames)
    df_Notes.to_excel(writer,sheet_name="BehavioralData",index=False)
    return df
        
def study_GetBehRANNStatus(SubjectsSummary,study,studydata,writer):
#    for i in range(0,len(SubjectsSummary),1):
#        print "%d %s"%(i,SubjectsSummary[i].Subject.subid)
    conn_qc = studydata.db_connection    
    Measures = ['NumCor']
    full_list = []
    # create the column names for the output spreadsheet
    ColumnNames = []
    ColumnNames.append('subid')
    for index in SubjectsSummary[0].TaskList:
            for meas in Measures:
                ColumnNames.append("%s_%s"%(SubjectsSummary[0].Scans[index]['SeriesName'],meas))
    # extract the data from SQL for the spreadsheet
    for j in range(0,len(SubjectsSummary),1):
        for index in SubjectsSummary[0].TaskList:
            task = SubjectsSummary[j].Scans[index]['SeriesName']
            sqlcommand = "SELECT subid"
            for meas in Measures: 
                sqlcommand = sqlcommand+", %s_%s"%(task[0:-3],meas)
            if study.name is "RANN":
                sqlcommand=sqlcommand+" FROM cnsdivdb.RANNBehav where subid='%s'"%(SubjectsSummary[j].Subject.subid)
            else:
                pass
 #           print sqlcommand
            try:
                conn_qc.cur.execute(sqlcommand)
                for row_dict in conn_qc.cur.fetchall():
                    for meas in Measures:
                        if row_dict[task[0:-3]+"_"+meas]>-1:
                            #print row_dict[task[0:-3]+"_"+meas]
                            SubjectsSummary[j].Scans[index][meas]=row_dict[task[0:-3]+"_"+meas]
            except:
                pass
    # put the data into the spreadsheet     
    for S in SubjectsSummary:
        one_list = []
        Str = S.Subject.subid
        one_list.append(S.Subject.subid)
        for index in SubjectsSummary[0].TaskList:
             for meas in Measures:
                if meas in S.Scans[index]:
                    if S.Scans[index][meas] > 0:
                        one_list.append(1)
                    else:
                        one_list.append(0)
                else:
                    one_list.append(-9999)
        full_list.append(one_list)
        
    df=DataFrame(full_list, columns=ColumnNames)
    df.to_excel(writer,sheet_name="BehavioralData",index=False)
    return SubjectsSummary,df

def study_GetBehCogResStatus(SubjectsSummary,study,studydata,writer):
    for i in range(0,len(SubjectsSummary),1):
        print "%d %s"%(i,SubjectsSummary[i].Subject.subid)
    conn_qc = studydata.db_connection    
    ECFMeasure = 'DualNonComp_NCor'
    LSMeasure = 'NumCor_6r'
    full_list = []
    # create the column names for the output spreadsheet
    ColumnNames = []
    ColumnNames.append('subid')
    # since ECF behavioral data is collapsed across runs only one value is
    # extracted from the dB
    ECFFlag = True
    # cycle over the series in the Scan list and make sure to only check
    # the ECF behavior once
    for index in SubjectsSummary[0].TaskList:
        if ECFFlag and SubjectsSummary[0].Scans[index]['SeriesName'].find('ECF') >-1:
            ECFFlag = False
            ColumnNames.append("%s_%s"%('ECF',ECFMeasure))
        elif SubjectsSummary[0].Scans[index]['SeriesName'].find('LS') >-1:
            LSRun = SubjectsSummary[0].Scans[index]['SeriesName'][-1]
            ColumnNames.append("%s_%s%s"%(SubjectsSummary[0].Scans[index]['SeriesName'][0:-3],LSMeasure,LSRun))
    # extract the data from SQL for the spreadsheet
    
    for j in range(0,len(SubjectsSummary),1):
        one_list = []
        one_list.append(SubjectsSummary[j].Subject.subid)
        # search through the COlumn Name list 
        for index in range(1,len(ColumnNames),1):
            task = ColumnNames[index]
            sqlcommand = "SELECT subid"
            sqlcommand="%s,%s"%(sqlcommand,task)
            if task.find('ECF') > -1:
                sqlcommand=sqlcommand+" FROM cnsdivdb.ECFBehav where subid='%s'"%(SubjectsSummary[j].Subject.subid)    
            elif task.find('LS') > -1:
                sqlcommand=sqlcommand+" FROM cnsdivdb.LSBehav where subid='%s'"%(SubjectsSummary[j].Subject.subid)                
            else:
                pass
           # print sqlcommand
            try:
                # ret is the number of rows returned
                ret = conn_qc.cur.execute(sqlcommand)
                if ret is 0:
                    one_list.append(-9999)
                elif ret is 1:
                    row_dict = conn_qc.cur.fetchall()
                    value = row_dict[0][ColumnNames[index]]
                    if value > 0:
                        one_list.append(value)
                    else:
                        one_list.append(0)
                elif ret > 1:
                    MultipleRowFlag = True
                    for row_dict in conn_qc.cur.fetchall():   
                        # value from first row
                        if MultipleRowFlag:
                            value = row_dict[ColumnNames[index]]
                            if value > 0:
                                one_list.append(value)
                                MultipleRowFlag = False
                    if MultipleRowFlag:
                        # if this flag is still true then there are multiple
                        # rows in the dB with no data in them
                        one_list.append(-9999)
                                
            except:
                one_list.append(-9999)
        full_list.append(one_list)
 
    df=DataFrame(full_list, columns=ColumnNames)
    df.to_excel(writer,sheet_name="BehavioralData",index=False)
    return SubjectsSummary,df

def study_GetBehILSStatus(SubjectsSummary,study,studydata,writer):
#    for i in range(0,len(SubjectsSummary),1):
#        print "%d %s"%(i,SubjectsSummary[i].Subject.subid)
    conn_qc = studydata.db_connection    
    Measures = ['iLS6_propHT']
    full_list = []
    # create the column names for the output spreadsheet
    ColumnNames = []
    ColumnNames.append('subid')

    for meas in Measures:
        ColumnNames.append(meas)
            
    for j in range(0,len(SubjectsSummary),1):
        one_list = []
        one_list.append(SubjectsSummary[j].Subject.subid)
        # search through the COlumn Name list 
        for index in range(1,len(ColumnNames),1):
            task = ColumnNames[index]
            sqlcommand = "SELECT subid"
            sqlcommand="%s,%s"%(sqlcommand,task)
            sqlcommand=sqlcommand+" FROM cnsdivdb.iLSBehav where subid='%s'"%(SubjectsSummary[j].Subject.subid)    
                
           # print sqlcommand
            try:
                # ret is the number of rows returned
                ret = conn_qc.cur.execute(sqlcommand)
                if ret is 0:
                    one_list.append(-9999)
                elif ret is 1:
                    row_dict = conn_qc.cur.fetchall()
                    value = row_dict[0][ColumnNames[index]]
                    if value > 0:
                        one_list.append(1)
                    else:
                        one_list.append(0)
                elif ret > 1:
                    MultipleRowFlag = True
                    for row_dict in conn_qc.cur.fetchall():   
                        # value from first row
                        if MultipleRowFlag:
                            value = row_dict[ColumnNames[index]]
                            if value > 0:
                                one_list.append(1)
                                MultipleRowFlag = False
                    if MultipleRowFlag:
                        # if this flag is still true then there are multiple
                        # rows in the dB with no data in them
                        one_list.append(-9999)
                                
            except:
                one_list.append(-9999)
        full_list.append(one_list)
 
    df=DataFrame(full_list, columns=ColumnNames)
    df.to_excel(writer,sheet_name="BehavioralData",index=False)
    return SubjectsSummary,df

def study_GetPreProcStatus(SubjectsSummary,study,writer):
    HeaderFlag = True
    # cycle over subjects
    # this will hold data for all subjects
    full_list = []
    for j in range(0,len(SubjectsSummary),1):
        Str = SubjectsSummary[j].Subject.subid
        # this will hold data for ONE subject  
        one_list = []
        one_list.append(SubjectsSummary[j].Subject.subid)
        # create the column names ONCE
        if HeaderFlag is True:
            ColumnNames = []
            ColumnNames.append('subid')
            for index in SubjectsSummary[0].TaskList:
                ColumnNames.append(SubjectsSummary[j].Scans[index]['SeriesName'])
            ColumnNames.append("AllProcessed")
        count = 0    
        for index in SubjectsSummary[0].TaskList:
            task = SubjectsSummary[j].Scans[index]['SeriesName']
            foundfileFlag = False
            foundProcessFlag = False
            
            for visit in SubjectsSummary[j].Subject.visitlist:
                if task in visit.niftis[task]:
                    foundFileFlag = True
                    filePath = visit.niftis[task][task].path
                    #print visit.niftis[task][task].path
                    # take this file and see if there is a preprocessed version of it
                    if study.name is 'iLS':
                        Prefix = 'swau'
                    else:
                        Prefix = 'swa'
                    spmVer = 'spm8'
                    testFile = os.path.join(os.path.dirname(filePath),spmVer,Prefix+os.path.basename(filePath))
                    if os.path.exists(testFile):
                        foundProcessFlag = True
            if foundProcessFlag is True:
                one_list.append(2)
                count = count + 2
                Str="%s,%d"%(Str,2)
            elif foundfileFlag is True:
                one_list.append(1)
                count = count + 2
                Str="%s,%d"%(Str,1)
            else:
                one_list.append(0)
                count = count + 0
                Str="%s,%d"%(Str,0)
            # append the one subject list to the full list
        if count is len(SubjectsSummary[0].TaskList)*2:
            one_list.append("TRUE")
        else:
            one_list.append("FALSE")
        full_list.append(one_list)
        print Str
    # now create the data frame for pandas
    df=DataFrame(full_list, columns=ColumnNames)
    # format it for Excel and write it to a file
    df.to_excel(writer,sheet_name="PreProcessedData",index=False)
    # write out codes
    codes = []
    codes.append([0,'no data'])
    codes.append([1,'data not processed'])
    codes.append([2,'data preprocessed'])
    CodeColNames = ['code','description']
    df_Notes=DataFrame(codes,columns=CodeColNames)
    df_Notes.to_excel(writer,sheet_name="PreProcessedData",index=False)
    return df

def study_GetStatsStatus(SubjectsSummary,study,writer):
    spmVer = 'spm8'
    HeaderFlag = True
    # cycle over subjects
    # this will hold data for all subjects
    full_list = []
    for j in range(0,len(SubjectsSummary),1):
        Str = SubjectsSummary[j].Subject.subid
        # this will hold data for ONE subject  
        one_list = []
        one_list.append(SubjectsSummary[j].Subject.subid)
        # create the column names ONCE
        if HeaderFlag is True:
            ColumnNames = []
            ColumnNames.append('subid')
            for index in SubjectsSummary[0].TaskList:
                ColumnNames.append(SubjectsSummary[j].Scans[index]['SeriesName'])
            ColumnNames.append("AllStatsProcessed")
        count = 0    
        for index in SubjectsSummary[0].TaskList:
            task = SubjectsSummary[j].Scans[index]['SeriesName']
            # strip run numbers from the task name
            task=task.split('_r')[0]
            
            foundStatsFlag = False
            for visit in SubjectsSummary[j].Subject.visitlist:
                filePath=os.path.join(visit.path,'fmriStats',task,spmVer,'spmT_0001.img')
                if os.path.exists(filePath):
                    foundStatsFlag = True
                        
            if foundStatsFlag is True:
                one_list.append(1)
                count = count + 1
            else:
                one_list.append(0)
                count = count + 0
            # append the one subject list to the full list
        if count is len(SubjectsSummary[0].TaskList):
            one_list.append("TRUE")
        else:
            one_list.append("FALSE")
        full_list.append(one_list)
        print Str
    # now create the data frame for pandas
    df=DataFrame(full_list, columns=ColumnNames)
    # format it for Excel and write it to a file
    df.to_excel(writer,sheet_name="StatsData",index=False)
    # write out codes
    codes = []
    codes.append([0,'stats NOT done'])
    codes.append([1,'stats done'])
    CodeColNames = ['code','description']
    df_Notes=DataFrame(codes,columns=CodeColNames)
    df_Notes.to_excel(writer,sheet_name="StatsData",index=False)
    return df

def study_CheckSubject(D,study,studydata,conn_qc):
    # generic subject checker regardless of where the subject is
        if study.name is "RANN":
            D.InitializeScansRANN()
        elif study.name is "CogRes":
            D.InitializeScansCogRes()
        elif study.name is "iLS":
            D.InitializeScansILS()
        elif study.name is "WHICAP":
            D.InitializeScansWHICAPV3()
        elif study.name is "AZ2":
            D.InitializeScansAZ2()   
        elif study.name is "Exercise58":
            D.InitializeScansEx58()    
        else:
            pass
        if D.Visit:
            # only echk one visit
            D.InspectImages(os.listdir(D.Visit.path),D.Visit.path)
        else:
            # check all visitis
            for V in D.Subject.visitlist:
                Files=os.listdir(V.path)
                D.InspectImages(Files,V.path)
#        print "========= %s ========="%(subid)
#        print "======= %s ======="%("Acquistion Problems")  
#        for V in D.Subject.visitlist:
#            print "========= %s ========="%(V.visid)
#            Files=os.listdir(V.path)
#            D.InspectImages(Files,V.path)
#        print "======= %s ======="%("Found Scans")
        D.CheckAllScansCollected()
#        print "======= %s ======="%("Missing Scans")
        D.CheckAllScansNOTCollected()
#        print "======= %s ======="%("QC Assessment")
        D.PrintQCAssessment(conn_qc,study.name)
#        print "======= %s ======="%("Behavior")
#        check_behavior(subid,studydata,study)
#        print "======= %s ======="%("Notes")
#        ReadmeFile = os.path.join(D.Subject.path,"%s_README.txt"%(subid))
#        if os.path.exists(ReadmeFile):
#            # read the notes file
#            fid = open(ReadmeFile)
#            Contents = fid.readlines()
#            for line in Contents:
#                print line
#            fid.close()
#        else:
#            print "--> No notes <--"    
        return D
                
def check_subject(subid,study,studydata):
    
     location = find_subject(subid,study)
     for loc in location:
         if loc is 'subjects':
             print "\n-----------------------------"
             print "==== LOOKING IN THE SUBJECTS FOLDER ===="
             study_Check_One_Subjects(subid,study,studydata)
         elif loc is 'quarantine':
             print "\n-----------------------------"
             print "==== LOOKING IN THE QUARANTINE FOLDER ===="
             study_Check_One_Quarantine(subid,study,studydata)
         elif loc is 'excluded':
             print "\n-----------------------------"
             print "==== LOOKING IN THE EXCLUDED FOLDER ===="
             study_Check_One_Excluded(subid,study,studydata)
       
       
def study_Check_OneVisit_Subjects(subid,visid,study,studydata):
    # Check the acquisition parameters and 
    # for missing data from one participant
    # expected to be in quarantine 
    SubjectsSummary = []
    conn_qc = studydata.db_connection
    D=[]
    # Check this one subject
    if subid in study.subjects:
        # extract the subject structure
        S = study.subjects[subid]
        if visid in S.visits:
            V = S.visits[visid]
            # initialize a scan structure for this subject
            D = CheckSubject.CheckSubject(S,V)
            # fill in the structure based on what was found
            # but this step collapses across visits
            study_CheckSubject(D,study,studydata,conn_qc)
    else:
        print "Subject: %s not imported"%(subid)
    return D
         
def study_Check_One_Subjects(subid,study,studydata):
    # Check the acquisition parameters and 
    # for missing data from one participant
    # expected to be in quarantine 
    SubjectsSummary = []
    conn_qc = studydata.db_connection
    D=[]
    # Check this one subject
    if subid in study.subjects:
        # extract the subject structure
        S = study.subjects[subid]
        # initialize a scan structure for this subject
        D = CheckSubject.CheckSubject(S)
        # fill in the structure based on what was found
        # but this step collapses across visits
        study_CheckSubject(D,study,studydata,conn_qc)
    else:
        print "Subject: %s not imported"%(subid)
    return D
        
def study_Check_OneVisit_Quarantine(subid,visid,study,studydata):
    # Check the acquisition parameters and 
    # for missing data from one participant
    # expected to be in quarantine 
    SubjectsSummary = []
    conn_qc = studydata.db_connection
    D=[]
    # Check this one subject
    if subid in study.quarantine.subjects:
        # extract the subject structure
        S = study.quarantine.subjects[subid]
        if visid in S.visits:
            V = S.visits[visid]
            # initialize a scan structure for this subject
            D = CheckSubject.CheckSubject(S,V)
            # fill in the structure based on what was found
            # but this step collapses across visits
            study_CheckSubject(D,study,studydata,conn_qc)
    else:
        print "Subject: %s not imported"%(subid)
    return D
        
def study_Check_One_Quarantine(subid,study,studydata):
    # Check the acquisition parameters and 
    # for missing data from one participant
    # expected to be in quarantine 
    SubjectsSummary = []
    conn_qc = studydata.db_connection
    D=[]
    if subid in study.quarantine.subjects:
        S = study.quarantine.subjects[subid]
        D=CheckSubject.CheckSubject(S)
        study_CheckSubject(D,study,studydata,conn_qc)
    else:
        print "Subject: %s not imported"%(subid)
    return D

def study_Check_OneVisit_Excluded(subid,visid,study,studydata):
    # Check the acquisition parameters and 
    # for missing data from one participant
    # expected to be in quarantine 
    SubjectsSummary = []
    conn_qc = studydata.db_connection
    D=[]
    # Check this one subject
    if subid in study.excluded.subjects:
        # extract the subject structure
        S = study.excluded.subjects[subid]
        if visid in S.visits:
            V = S.visits[visid]
            # initialize a scan structure for this subject
            D = CheckSubject.CheckSubject(S,V)
            # fill in the structure based on what was found
            # but this step collapses across visits
            study_CheckSubject(D,study,studydata,conn_qc)
    else:
        print "Subject: %s not imported"%(subid)
    return D

def study_Check_One_Excluded(subid,study,studydata):
    # Check the acquisition parameters and 
    # for missing data from one participant
    # expected to be in quarantine 
    SubjectsSummary = []
    conn_qc = studydata.db_connection
    D=[]
    if subid in study.excluded.subjects:
        S = study.excluded.subjects[subid]
        D=CheckSubject.CheckSubject(S)
        study_CheckSubject(D,study,studydata,conn_qc)
    else:
        print "Subject: %s not imported"%(subid)
    return D      
        
def check_behavior(subid,studydata,study):
    if study.name is "RANN":
        check_RANN_Subject_Behav(subid,studydata,study)
    elif study.name is "CogRes":
        check_CogRes_Subject_Behav(subid,studydata,study)
        
def check_CogRes_Subject_Behav(subid,studydata,study):
    # Do this to initialize the list of scans 
    D = CheckSubject.CheckSubject(subid)
    D.InitializeScansCogRes()

    conn_qc = studydata.db_connection    
    # create list of measures to look at
    ECFMeasure = 'DualNonComp_NCor'
    LSMeasure = 'NumCor_6r'
    # create the column names for the output spreadsheet
    ColumnNames = []
    # since ECF behavioral data is collapsed across runs only one value is
    # extracted from the dB
    ECFFlag = True
    # cycle over the series in the Scan list and make sure to only check
    # the ECF behavior once
    
    for index in D.TaskList:
        if ECFFlag and D.Scans[index]['SeriesName'].find('ECF') >-1:
            ECFFlag = False
            ColumnNames.append("%s_%s"%('ECF',ECFMeasure))
        elif D.Scans[index]['SeriesName'].find('LS') >-1:
            LSRun = D.Scans[index]['SeriesName'][-1]
            ColumnNames.append("%s_%s%s"%(D.Scans[index]['SeriesName'][0:-3],LSMeasure,LSRun))

    one_list = []
    for index in range(0,len(ColumnNames),1):
        task = ColumnNames[index]
        sqlcommand = "SELECT subid"
        sqlcommand="%s,%s"%(sqlcommand,task)
        if task.find('ECF') > -1:
            sqlcommand=sqlcommand+" FROM cnsdivdb.ECFBehav where subid='%s'"%(subid)    
        elif task.find('LS') > -1:
            sqlcommand=sqlcommand+" FROM cnsdivdb.LSBehav where subid='%s'"%(subid)                
        else:
            pass
       # print sqlcommand
        try:
            # ret is the number of rows returned
            ret = conn_qc.cur.execute(sqlcommand)
            if ret is 0:
                one_list.append(-9999)
            elif ret is 1:
                row_dict = conn_qc.cur.fetchall()
                value = row_dict[0][ColumnNames[index]]
                if value > 0:
                    one_list.append(1)
                else:
                    one_list.append(0)
            elif ret > 1:
                MultipleRowFlag = True
                for row_dict in conn_qc.cur.fetchall():   
                    # value from first row
                    if MultipleRowFlag:
                        value = row_dict[ColumnNames[index]]
                        if value > 0:
                            one_list.append(1)
                            MultipleRowFlag = False
                if MultipleRowFlag:
                    # if this flag is still true then there are multiple
                    # rows in the dB with no data in them
                    one_list.append(-9999)
        except:
            one_list.append(-9999)
            
    print "Behavioral Summary: %s"%(subid)
    for i in range(0,len(ColumnNames),1):
        print "%s\t%d"%(ColumnNames[i],one_list[i])
        
def check_RANN_Subject_Behav(subid,studydata,study):
    D = CheckSubject.CheckSubject(subid)
        # python does not use switch/case statements
    D.InitializeScansRANN()
    RANNBehav={}
#    Tasks = ['DgtSym','LetComp','PaperFold','LetSet','Syn','Ant','LogMem','MatReas','PairAssoc','PattComp','WordOrder']
    Measures = ['PropOnTimeCor','medianAllRT']
    conn_qc = studydata.db_connection
    for index in D.TaskList:
        task = D.Scans[index]['SeriesName'][0:-3]
        #print task
        RANNBehav[task]={}
        sqlcommand = "SELECT subid"
        for meas in Measures: 
            sqlcommand = sqlcommand+", %s_%s"%(task,meas)
        sqlcommand=sqlcommand+" FROM cnsdivdb.RANNBehav where subid='%s'"%(subid)
        #print sqlcommand
        try:
            conn_qc.cur.execute(sqlcommand)
            for row_dict in conn_qc.cur.fetchall():
                for meas in Measures:
                    if row_dict[task+"_"+meas]>-1:
                        RANNBehav[task][meas]=row_dict[task+"_"+meas]
        except:
            for meas in Measures:
                RANNBehav[task][meas] = -9999
                           
    print subid
    for task in RANNBehav.iteritems():
        Str="%15s:"%(task[0])
        for meas in Measures:
            if len(task[1])>0:
                Str="%s %s=%3.4f,"%(Str,meas,task[1][meas])
            else:
                Str="%s no data found"%(Str)
        if len(task[1])>0:
            if task[1][Measures[0]]<0.5:
                Str="%s <<<<<< "%(Str)
        print Str
        
def find_subject(subid,study):
    Flag = []
    # check quarantine folder
    for S in study.quarantine.subjectlist:
        if subid == S.subid:
            Flag.append('quarantine')
    for S in study.subjectlist:
        if subid == S.subid:
            Flag.append('subjects')
    for S in study.excluded.subjectlist:
        if subid == S.subid:
            Flag.append('excluded')
    return Flag
    
def write_notes(subid,study):
    # find the subject
    location = find_subject(subid,study)
    # create a time stamp
    cur = datetime.now()
    timeStamp = "%d:%d, %d/%d/%d -- %s"%(cur.hour,cur.minute,cur.month,cur.day,cur.year,getuser())
    print "Type any notes for subject %s"%(subid)
    print "Press enter after an empty line to end"
    
    
    if location is 'quarantine':
        ReadmeFile = os.path.join(study.quarantine.subjects[subid].path,"%s_README.txt"%(subid))
    elif location is 'subjects':
        ReadmeFile = os.path.join(study.subjects[subid].path,"%s_README.txt"%(subid))
    elif location is 'excluded':
        ReadmeFile = os.path.join(study.excluded.subjects[subid].path,"%s_README.txt"%(subid))
        
    print "\n====== Current Notes ======="
    if os.path.exists(ReadmeFile):
        # read the notes file
        fid = open(ReadmeFile)
        Contents = fid.readlines()
        for line in Contents:
            print line.strip()
        fid.close()
    else:
        print "--> No notes <--"    
    print "======= New Notes ======="
    # open the file
    fid=open(ReadmeFile,'a')
    OneLine = 'BLANK'
    fid.write("%s\n"%(timeStamp))
    while len(OneLine) > 0:
        OneLine = raw_input('>>> ')    
        fid.write("%s\n"%(OneLine))
    fid.close()
    print "=================================="
    print "======= The file now reads ======="
    fid = open(ReadmeFile)
    Contents = fid.readlines()
    for line in Contents:
        print line.strip()
    fid.close()
      
def CreateParticipantsCSV(study,studydata,Output):
    conn = pymysql.connect(host='156.145.15.135', port=3306, user='steffejr', passwd='ticabl', db='Participants')
    cur = conn.cursor()
    sqlcommand = "Select * from %sonlyALL"%(study.name)
    cur.execute(sqlcommand)
    fid = open(os.path.join(study.path,Output),'w')
    rows = cur.fetchall()
    # write the header
    header = cur.description
    count = 0
    DQColumn = -1
    for i in header:
        if i[0] == 'any DQ':
            DQColumn = count
        count = count + 1 
        fid.write("%s,"%(i[0]))
    fid.write('\r\n')
    count = 1
    for row in rows:
        ColCount = 0
        for i in row:
            fid.write(str(i)+',')
        fid.write('\r\n')
        #print "Row: %d"%(count)
        count = count + 1 
    fid.close()
    conn.cur.close()
    
def Create_ref_list_CSV(study):
    conn = pymysql.connect(host='156.145.15.135', port=3306, user='steffejr', passwd='ticabl', db='cnsdivdb', cursorclass=pymysql.cursors.DictCursor)
    conn.cur = conn.cursor()
    
    sqlcommand = "select subid, `MRI1 id`, `MRI2 id`,`MRI3 id`, dob,gender,`MRI1 date`,`MRI2 date`,`MRI3 date`, `MRI1 perf`, `MRI2 perf`,`MRI3 perf`,`any DQ` from ParticipantTable where StudyName = '%s'"%(study.name)
    
    conn.cur.execute(sqlcommand)
    
    rows = conn.cur.fetchall()
    csv_path_out='CSV/Subject_List/ref_list.csv'
    fid = open(csv_path_out, 'wb')
    csv_writer = csv.writer(fid)
    csv_writer.writerow(['Subid', 'Visid', 'DOB', 'Gender', 'VisDate', 'VisTime', 'DQ', 'Performance'])
    
    for row in rows:
        # write MRI1
        GoodToWriteFlag = True
        for j in range(1,4,1):
            if row['MRI%d date'%(j)] is not None:
                out_row=8*['']
                out_row[0]=row['subid']
                out_row[1]=row['MRI%d id'%(j)]
                dob = row['dob']
                if dob is not None:
                    dob=dob.strftime('%m/%d/%Y')
                else:
                    GoodToWriteFlag = False
                out_row[2]=dob
                out_row[3]=row['gender']
                Fvisitdate=row['MRI%d date'%(j)]
                Fvisitdate=Fvisitdate.strftime('%m/%d/%Y')
                out_row[4]=Fvisitdate
                if row['any DQ'] is None:
                    out_row[6]='N'
                else:
                    out_row[6]='Y'
                out_row[7]=row['MRI%d perf'%(j)]
                #print out_row
                if GoodToWriteFlag:
                    csv_writer.writerow(out_row)
    fid.close()
    conn.cur.close()
    #            if ColCount == DQColumn:
    #                if i is None:
    #                    i = ''
    #                    print "HELLO"
#            ColCount = ColCount + 1
