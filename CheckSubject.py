'''
Created on May 3, 2013

@author: jason
'''
import os
import nibabel as nib
import numpy as np

class CheckSubject:
    def __init__(self,Subject):
        self.Subject = Subject
        
    def is_nifti(self,filename):
        'takes a filename and checks if it is a nifti'
        extension = self.get_nifti_extension(filename)
        if extension == '.nii' or extension == '.nii.gz':
            return True
        return False

    def CheckAllScansNOTCollected(self):
        self.AllCollected = True
        Str = self.Subject.subid
        for scan in self.Scans:
            if not self.Scans[scan]['found']:
                self.AllCollected = False
                Str='%s, %s'%(Str,self.Scans[scan]['SeriesName'])
        if not self.AllCollected:
            print Str

    def CheckAllScansCollected(self):
        self.AllCollected = True
        Str = self.Subject.subid
        for scan in self.Scans:
            if self.Scans[scan]['found']:
                Str='%s, %s'%(Str,self.Scans[scan]['SeriesName'])
        print Str
                                
                
    def CheckAllScansGood(self):
        self.AllGood = True
        for scan in self.Scans:
            if not all(self.Scans[scan]['FlagList']):
                self.AllGood = False
        
    def get_nifti_extension(self,filename):
        filename_split = filename.split('.')
        if filename_split[-1].lower() == 'nii':
            return '.nii'
        elif len(filename_split) > 2 and filename_split[-2].lower() == 'nii' and filename_split[-1].lower() == 'gz':
            return '.nii.gz'
        return None
    
    def PrintQCAssessment(self,conn_qc,StudyName):
        #print "QC Assessment"
        sqlcommand = "SELECT subid,visitid,StudyName" 
        sqlcommand="%s FROM MRIQualityControl.%s where subid = '%s'"%(sqlcommand,StudyName,self.Subject.subid)
        #print sqlcommand
        N=conn_qc.cur.execute(sqlcommand)
        PrintedFlag = False
        if N>0:
           # print "Subject %s has been QC'd"%(self.Subject.subid)
            # cycle all expected scans
            for scan in self.Scans:
                # get the series name
                seriesName = self.Scans[scan]['SeriesName']
                if seriesName == 'x1' or seriesName == 'x2':
                    seriesName = 'pASL'
                if seriesName == 'x1_pASL' or seriesName == 'x2_pASL':
                    seriesName = 'pASL'
                if seriesName == 'x1_FieldMapiLS' or seriesName == 'x2_FieldMapiLS':
                    seriesName = 'FieldMapiLS'
                if seriesName == 'x1_FieldMapTO' or seriesName == 'x2_FieldMapTO':
                    seriesName = 'FieldMapTO'
                if seriesName == 'x3_FieldMapiLS' or seriesName == 'x4_FieldMapiLS':
                    seriesName = 'FieldMapiLS'
                if seriesName == 'x3_FieldMapTO' or seriesName == 'x4_FieldMapTO':
                    seriesName = 'FieldMapTO'
                    
                # check the sql database for the assessment for that scan to see if it 
                # is usable 
                sqlcommand="select %s_Usable from MRIQualityControl.%s where subid='%s'"%(seriesName,StudyName,self.Subject.subid)
                conn_qc.cur.execute(sqlcommand)
                usableFlag = False
                unusableFlag = False
                allRowsUsable = conn_qc.cur.fetchall()
                for row in range(0,len(allRowsUsable),1):
                    if allRowsUsable[row][seriesName+"_Usable"] == '1':
                        usableFlag=True
                        count = row
                    elif allRowsUsable[row][seriesName+"_Usable"] == '0':
                        unusableFlag=True
                        count = row
                if usableFlag:
                # check the sql database for the assessment for that scan to see if it 
                # has warnings
                    sqlcommand="select %s_Warnings from MRIQualityControl.%s where subid='%s'"%(seriesName,StudyName,self.Subject.subid)
                    conn_qc.cur.execute(sqlcommand)
                    allRowsWarning = conn_qc.cur.fetchall()
                    warningFlag = allRowsWarning[count][seriesName+"_Warnings"] == '1'
                    # if there is a warning get what the notes are
                    if warningFlag:
                        sqlcommand="select %s_Notes from MRIQualityControl.%s where subid='%s'"%(seriesName,StudyName,self.Subject.subid)
                        conn_qc.cur.execute(sqlcommand)
                        allRowsNotes = conn_qc.cur.fetchall()
                        notes=allRowsNotes[count][seriesName+"_Notes"]
                        print seriesName+ ", "+notes
                        PrintedFlag = True
                elif unusableFlag:
                    sqlcommand="select %s_Notes from MRIQualityControl.%s where subid='%s'"%(seriesName,StudyName,self.Subject.subid)
                    conn_qc.cur.execute(sqlcommand)
                    allRowsNotes = conn_qc.cur.fetchall()
                    notes=allRowsNotes[count][seriesName+"_Notes"]
                    print seriesName+ ", NOT USABLE, "+notes
                    PrintedFlag = True
                        # image not usable
        else:
            print "Subject %s has NOT been QC'd"%(self.Subject.subid)
        if not PrintedFlag:
            print "Subject %s has NOT been QC'd"%(self.Subject.subid)
        
    def InspectImages(self,Files,VisitPath):
        tol = 0.1 # for checking to see if the dimensions of the images are correct
        for folder in Files:
            folderdir = os.path.join(VisitPath, folder)
            if (not os.path.isdir(folderdir)):
                continue
            try:
                seriesfiles = os.listdir(folderdir)
            except:
                warnings.warn("\nCould not list files in: " + folderdir)
        
            for seriesfile in seriesfiles:
                fullseriespath = os.path.join(folderdir, seriesfile)
                if self.is_nifti(fullseriespath):
                    FileName = os.path.basename(fullseriespath)
                    II = nib.load(fullseriespath)
                    hdr = II.get_header()
                    DIM = hdr.get_data_shape()
                    PIXDIM = hdr.get_zooms()
                    # make sure that the dimensions are 4-D
                    DIM4=[];
                    for j in DIM:
                        DIM4.append(j)
                    if len(DIM) == 3:
                        DIM4.append(1)
                    PIXDIM4=[];
                    for j in PIXDIM:
                        PIXDIM4.append(j)
                    if len(PIXDIM) == 3:
                        PIXDIM4.append(0)
                    for i in self.Scans:
                        if FileName.find(self.Scans[i]['SeriesName']) == 0:
                            self.Scans[i]['found'] = True                            # once the file is found check to see if it matches all the dimensions
                            # I am rounding to the nearest 1/10th
                            self.Scans[i]['FlagList'].append(abs(self.Scans[i]['dim1']-DIM4[0])<tol)
                            self.Scans[i]['FlagList'].append(abs(self.Scans[i]['dim2']-DIM4[1])<tol)
                            self.Scans[i]['FlagList'].append(abs(self.Scans[i]['dim3']-DIM4[2])<tol)
                            self.Scans[i]['FlagList'].append(abs(self.Scans[i]['dim4']-DIM4[3])<tol)
                            self.Scans[i]['FlagList'].append(abs(self.Scans[i]['pixdim1']-PIXDIM4[0])<tol)
                            self.Scans[i]['FlagList'].append(abs(self.Scans[i]['pixdim2']-PIXDIM4[1])<tol)
                            self.Scans[i]['FlagList'].append(abs(self.Scans[i]['pixdim3']-PIXDIM4[2])<tol)
                            self.Scans[i]['FlagList'].append(abs(self.Scans[i]['pixdim4']-PIXDIM4[3])<tol)
                            #self.Scans[i]['FlagList'].append(round(self.Scans[i]['dim1']*10)/10 == round(DIM4[0]*10)/10)
                            #self.Scans[i]['FlagList'].append(round(self.Scans[i]['dim2']*10)/10 == round(DIM4[1]*10)/10)
                            #self.Scans[i]['FlagList'].append(round(self.Scans[i]['dim3']*10)/10 == round(DIM4[2]*10)/10)
                            #self.Scans[i]['FlagList'].append(round(self.Scans[i]['dim4']*10)/10 == round(DIM4[3]*10)/10)
                            #self.Scans[i]['FlagList'].append(round(self.Scans[i]['pixdim1']*10)/10 == round(PIXDIM4[0]*10)/10)
                            #self.Scans[i]['FlagList'].append(round(self.Scans[i]['pixdim2']*10)/10 == round(PIXDIM4[1]*10)/10)
                            #self.Scans[i]['FlagList'].append(round(self.Scans[i]['pixdim3']*10)/10 == round(PIXDIM4[2]*10)/10)
                            #self.Scans[i]['FlagList'].append(round(self.Scans[i]['pixdim4']*10)/10 == round(PIXDIM4[3]*10)/10)
                           # FlagList.append(round(self.Scans[i]['pixdim4']*10)/10 == round(PIXDIM4[3]*10)/10)
                        # check to see if all dimensions are correct
                            if not all(self.Scans[i]['FlagList']):
                                #print fullseriespath+": all good!"
                            #else:
                                Str = fullseriespath
                                Str = "%s,dim1=%d|%d"%(Str,self.Scans[i]['dim1'],round(DIM4[0]*10)/10)
                                Str = "%s,dim2=%d|%d"%(Str,self.Scans[i]['dim2'],round(DIM4[1]*10)/10)
                                Str = "%s,dim3=%d|%d"%(Str,self.Scans[i]['dim3'],round(DIM4[2]*10)/10)
                                Str = "%s,dim4=%d|%d"%(Str,self.Scans[i]['dim4'],round(DIM4[3]*10)/10)
                                Str = "%s,pixdim1=%d|%d"%(Str,self.Scans[i]['pixdim1'],round(PIXDIM4[0]*10)/10)
                                Str = "%s,pixdim2=%d|%d"%(Str,self.Scans[i]['pixdim2'],round(PIXDIM4[1]*10)/10)
                                Str = "%s,pixdim3=%d|%d"%(Str,self.Scans[i]['pixdim3'],round(PIXDIM4[2]*10)/10)
                                Str = "%s,pixdim4=%d|%d"%(Str,self.Scans[i]['pixdim4'],round(PIXDIM4[3]*10)/10)
                                print Str
                                print 

                                #print "Expected: "+str(self.Scans[i]['dim1'])+", found: "+str(round(DIM4[0]*10)/10)
                                #print "Expected: "+str(self.Scans[i]['dim2'])+", found: "+str(round(DIM4[1]*10)/10)
                                #print "Expected: "+str(self.Scans[i]['dim3'])+", found: "+str(round(DIM4[2]*10)/10)
                                #print "Expected: "+str(self.Scans[i]['dim4'])+", found: "+str(round(DIM4[3]*10)/10)
                                #print "Expected: "+str(self.Scans[i]['pixdim1'])+", found: "+str(round(PIXDIM4[0]*10)/10)
                                #print "Expected: "+str(self.Scans[i]['pixdim2'])+", found: "+str(round(PIXDIM4[1]*10)/10)
                                #print "Expected: "+str(self.Scans[i]['pixdim3'])+", found: "+str(round(PIXDIM4[2]*10)/10)
                                #print "Expected: "+str(self.Scans[i]['pixdim4'])+", found: "+str(round(PIXDIM4[3]*10)/10)
                        #else:
                         #   self.Scans[i]['FlagList'] = [False]
        
    def Print_Study_Summary(self,SubjectSummary):
        Str='subid'
        for j in SubjectSummary[0].Scans:
            Str = "%s,%s"%(Str,SubjectSummary[0].Scans[j]['SeriesName'])
        Str = Str+",ALL,NumFunc"
        print Str
        for S in SubjectSummary:
            Str = S.Subject.subid
        # count the functional runs
            count = 0
            for j in S.Scans:
                if len(S.Scans[j]['FlagList'])>0:
                    L = 1
                    if j > 0 and j < 13:
                        count = count + 1
                else:
                    L=0
                Str = "%s,%d"%(Str,L)
            Str="%s,%s,%d"%(Str,S.AllCollected,count)
            print Str
        
    def InitializeScansCogRes(self):
        self.Scans = {}
        # which of the scans are functional task scans, 
        # which would have associated behavior?
        self.TaskList = range(0,9,1)
        for i in range(0,6,1):
            self.Scans[i] = {}
            self.Scans[i]['FlagList'] = []
            self.Scans[i]['SeriesName']='ECF_r'+str(i+1)
            self.Scans[i]['dim1'] = 112.00
            self.Scans[i]['dim2'] = 112.00
            self.Scans[i]['dim3'] = 41.00
            self.Scans[i]['dim4'] = 111.00
            self.Scans[i]['pixdim1'] = 2.00
            self.Scans[i]['pixdim2'] = 2.00
            self.Scans[i]['pixdim3'] = 3.00
            self.Scans[i]['pixdim4'] = 2.00
            self.Scans[i]['found']=False
            
        for i in range(0,3,1):
            self.Scans[len(self.Scans)] = {}
            self.Scans[len(self.Scans)-1]['FlagList'] = []
            self.Scans[len(self.Scans)-1]['SeriesName']='LS_r'+str(i+1)
            self.Scans[len(self.Scans)-1]['dim1'] = 112.00
            self.Scans[len(self.Scans)-1]['dim2'] = 112.00
            self.Scans[len(self.Scans)-1]['dim3'] = 36.00
            self.Scans[len(self.Scans)-1]['dim4'] = 314.00
            self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
            self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
            self.Scans[len(self.Scans)-1]['pixdim3'] = 3.00
            self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
            self.Scans[len(self.Scans)-1]['found']=False    
            
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='FLAIR'
        self.Scans[len(self.Scans)-1]['dim1'] = 288.00
        self.Scans[len(self.Scans)-1]['dim2'] = 288.00
        self.Scans[len(self.Scans)-1]['dim3'] = 30.00
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.7986
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.7986
        self.Scans[len(self.Scans)-1]['pixdim3'] =  4.49999
        self.Scans[len(self.Scans)-1]['pixdim4'] = 11
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []      
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='T1'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 165
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 0.00    
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='x1'
        self.Scans[len(self.Scans)-1]['dim1'] = 64.00
        self.Scans[len(self.Scans)-1]['dim2'] = 64.00
        self.Scans[len(self.Scans)-1]['dim3'] = 15.00
        self.Scans[len(self.Scans)-1]['dim4'] = 150.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim3'] =  6.60
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.72
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='x2'
        self.Scans[len(self.Scans)-1]['dim1'] = 64.00
        self.Scans[len(self.Scans)-1]['dim2'] = 64.00
        self.Scans[len(self.Scans)-1]['dim3'] = 15.00
        self.Scans[len(self.Scans)-1]['dim4'] = 150.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim3'] =  6.60
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.72
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='REST_BOLD'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 37.00
        self.Scans[len(self.Scans)-1]['dim4'] = 285.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00   
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DTI_1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 75.00
        self.Scans[len(self.Scans)-1]['dim4'] = 57.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 7.7
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DTI_2'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 75.00
        self.Scans[len(self.Scans)-1]['dim4'] = 57.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 7.7    
        self.Scans[len(self.Scans)-1]['found']=False 
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
    def InitializeScansRANN(self):
        self.Scans = {}
        # which of the scans are functional task scans, 
        # which would have associated behavior?
        self.TaskList = range(0,12,1)      
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='Syn_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 194.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False  
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='PictName_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 190.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False   
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='PattComp_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 190.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False   
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='LetComp_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 195.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False   
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='DgtSym_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 210.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False   
        self.Scans[len(self.Scans)-1]['FlagList'] = [] 
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='Ant_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 194.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False 
        self.Scans[len(self.Scans)-1]['FlagList'] = []         
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='WordOrder_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 208.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False  
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='PaperFold_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 430.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False 
        self.Scans[len(self.Scans)-1]['FlagList'] = []   
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='PairAssoc_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 99.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False  
        self.Scans[len(self.Scans)-1]['FlagList'] = []  
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='LetSet_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 430.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False   
        self.Scans[len(self.Scans)-1]['FlagList'] = [] 
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='LogMem_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 210.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False      
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={} 
        self.Scans[len(self.Scans)-1]['SeriesName']='MatReas_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 33.00
        self.Scans[len(self.Scans)-1]['dim4'] = 430.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00
        self.Scans[len(self.Scans)-1]['found']=False  
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='T1'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 180
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 0.00    
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='x1'
        self.Scans[len(self.Scans)-1]['dim1'] = 64.00
        self.Scans[len(self.Scans)-1]['dim2'] = 64.00
        self.Scans[len(self.Scans)-1]['dim3'] = 15.00
        self.Scans[len(self.Scans)-1]['dim4'] = 150.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim3'] =  6.60
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.72
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='x2'
        self.Scans[len(self.Scans)-1]['dim1'] = 64.00
        self.Scans[len(self.Scans)-1]['dim2'] = 64.00
        self.Scans[len(self.Scans)-1]['dim3'] = 15.00
        self.Scans[len(self.Scans)-1]['dim4'] = 150.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim3'] =  6.60
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.72
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='REST_BOLD'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 37.00
        self.Scans[len(self.Scans)-1]['dim4'] = 285.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00   
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DTI_1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 75.00
        self.Scans[len(self.Scans)-1]['dim4'] = 57.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 7.6
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DTI_2'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 75.00
        self.Scans[len(self.Scans)-1]['dim4'] = 57.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 7.6    
        self.Scans[len(self.Scans)-1]['found']=False 
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='FLAIR'
        self.Scans[len(self.Scans)-1]['dim1'] = 288.00
        self.Scans[len(self.Scans)-1]['dim2'] = 288.00
        self.Scans[len(self.Scans)-1]['dim3'] = 30.00
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.7986
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.7986
        self.Scans[len(self.Scans)-1]['pixdim3'] =  4.49999
        self.Scans[len(self.Scans)-1]['pixdim4'] = 11
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []           
        
    def InitializeScansILS(self):
        self.Scans = {}
        # which of the scans are functional task scans, 
        # which would have associated behavior?
        self.TaskList = range(0,3,1)
        for i in range(0,3,1):
            self.Scans[i] = {}
            self.Scans[i]['FlagList'] = []
            self.Scans[i]['SeriesName']='iLS_r'+str(i+1)
            self.Scans[i]['dim1'] = 112.00
            self.Scans[i]['dim2'] = 112.00
            self.Scans[i]['dim3'] = 38.00
            self.Scans[i]['dim4'] = 240.00
            self.Scans[i]['pixdim1'] = 2.00
            self.Scans[i]['pixdim2'] = 2.00
            self.Scans[i]['pixdim3'] = 3.50
            self.Scans[i]['pixdim4'] = 2.00
            self.Scans[i]['found']=False
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='TempOrderAV'
        self.Scans[len(self.Scans)-1]['dim1'] = 80.00
        self.Scans[len(self.Scans)-1]['dim2'] = 80.00
        self.Scans[len(self.Scans)-1]['dim3'] = 25.00
        self.Scans[len(self.Scans)-1]['dim4'] = 293.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.80
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.80
        self.Scans[len(self.Scans)-1]['pixdim3'] = 5.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.0    
        self.Scans[len(self.Scans)-1]['found']=False 
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='TempOrderVA'
        self.Scans[len(self.Scans)-1]['dim1'] = 80.00
        self.Scans[len(self.Scans)-1]['dim2'] = 80.00
        self.Scans[len(self.Scans)-1]['dim3'] = 25.00
        self.Scans[len(self.Scans)-1]['dim4'] = 293.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.80
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.80
        self.Scans[len(self.Scans)-1]['pixdim3'] = 5.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.0    
        self.Scans[len(self.Scans)-1]['found']=False 
        self.Scans[len(self.Scans)-1]['FlagList'] = []  
         
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='T1'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 170
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 0.00    
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
     
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='x1_pASL'
        self.Scans[len(self.Scans)-1]['dim1'] = 64.00
        self.Scans[len(self.Scans)-1]['dim2'] = 64.00
        self.Scans[len(self.Scans)-1]['dim3'] = 15.00
        self.Scans[len(self.Scans)-1]['dim4'] = 100.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim3'] =  6.60
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.72
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='x2_pASL'
        self.Scans[len(self.Scans)-1]['dim1'] = 64.00
        self.Scans[len(self.Scans)-1]['dim2'] = 64.00
        self.Scans[len(self.Scans)-1]['dim3'] = 15.00
        self.Scans[len(self.Scans)-1]['dim4'] = 100.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim3'] =  6.60
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.72
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []     
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='ASL_M0'
        self.Scans[len(self.Scans)-1]['dim1'] = 64.00
        self.Scans[len(self.Scans)-1]['dim2'] = 64.00
        self.Scans[len(self.Scans)-1]['dim3'] = 15.00
        self.Scans[len(self.Scans)-1]['dim4'] = 3.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.50
        self.Scans[len(self.Scans)-1]['pixdim3'] =  6.60
        self.Scans[len(self.Scans)-1]['pixdim4'] = 15
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []   

        for i in range(0,4,1):
            self.Scans[len(self.Scans)] = {}
            self.Scans[len(self.Scans)-1]['FlagList'] = []
            self.Scans[len(self.Scans)-1]['SeriesName']='x%d_FieldMapiLS'%(i+1)
            self.Scans[len(self.Scans)-1]['dim1'] = 112.00
            self.Scans[len(self.Scans)-1]['dim2'] = 112.00
            self.Scans[len(self.Scans)-1]['dim3'] = 38.00
            self.Scans[len(self.Scans)-1]['dim4'] = 1.00
            self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
            self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
            self.Scans[len(self.Scans)-1]['pixdim3'] = 3.50
            self.Scans[len(self.Scans)-1]['pixdim4'] = 0.00
            self.Scans[len(self.Scans)-1]['found']=False    
        for i in range(0,4,1):
            self.Scans[len(self.Scans)] = {}
            self.Scans[len(self.Scans)-1]['FlagList'] = []
            self.Scans[len(self.Scans)-1]['SeriesName']='x%d_FieldMapTO'%(i+1)
            self.Scans[len(self.Scans)-1]['dim1'] = 80.00
            self.Scans[len(self.Scans)-1]['dim2'] = 80.00
            self.Scans[len(self.Scans)-1]['dim3'] = 25.00
            self.Scans[len(self.Scans)-1]['dim4'] = 1.00
            self.Scans[len(self.Scans)-1]['pixdim1'] = 2.80
            self.Scans[len(self.Scans)-1]['pixdim2'] = 2.80
            self.Scans[len(self.Scans)-1]['pixdim3'] = 5.00
            self.Scans[len(self.Scans)-1]['pixdim4'] = 0.00
            self.Scans[len(self.Scans)-1]['found']=False                
        
    def InitializeScansWHICAPV3(self):
        self.Scans = {}
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='3DT1'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 165
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 1.000
        self.Scans[len(self.Scans)-1]['pixdim2'] = 1.000
        self.Scans[len(self.Scans)-1]['pixdim3'] = 1.000
        self.Scans[len(self.Scans)-1]['pixdim4'] = 0.006
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='PDT2'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 41
        self.Scans[len(self.Scans)-1]['dim4'] = 2
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.898
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.898
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.000
        self.Scans[len(self.Scans)-1]['pixdim4'] = 4.000
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='T2STAR'
        self.Scans[len(self.Scans)-1]['dim1'] = 512
        self.Scans[len(self.Scans)-1]['dim2'] = 512
        self.Scans[len(self.Scans)-1]['dim3'] = 280
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.429
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.429
        self.Scans[len(self.Scans)-1]['pixdim3'] = 0.499
        self.Scans[len(self.Scans)-1]['pixdim4'] = 0.014
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='3DFLAIR'
        self.Scans[len(self.Scans)-1]['dim1'] = 560
        self.Scans[len(self.Scans)-1]['dim2'] = 560
        self.Scans[len(self.Scans)-1]['dim3'] = 300
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.428
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.428
        self.Scans[len(self.Scans)-1]['pixdim3'] = 0.599
        self.Scans[len(self.Scans)-1]['pixdim4'] = 8.000
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='COR_FLAIR'
        self.Scans[len(self.Scans)-1]['dim1'] = 560
        self.Scans[len(self.Scans)-1]['dim2'] = 560
        self.Scans[len(self.Scans)-1]['dim3'] = 45
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.428
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.428
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.000
        self.Scans[len(self.Scans)-1]['pixdim4'] = 8.000
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='AX_T2W_FLAIR'
        self.Scans[len(self.Scans)-1]['dim1'] = 560
        self.Scans[len(self.Scans)-1]['dim2'] = 560
        self.Scans[len(self.Scans)-1]['dim3'] = 35
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.428
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.428
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.000
        self.Scans[len(self.Scans)-1]['pixdim4'] = 8.000
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DWI'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 37
        self.Scans[len(self.Scans)-1]['dim4'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.898
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.898
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.000
        self.Scans[len(self.Scans)-1]['pixdim4'] = 4.447
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='SB1000'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 37
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.898
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.898
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.000
        self.Scans[len(self.Scans)-1]['pixdim4'] = 4.447
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='dADCMAP'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 37
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.898
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.898
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.000
        self.Scans[len(self.Scans)-1]['pixdim4'] = 4.447
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='SWI'
        self.Scans[len(self.Scans)-1]['dim1'] = 512
        self.Scans[len(self.Scans)-1]['dim2'] = 512
        self.Scans[len(self.Scans)-1]['dim3'] = 150
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.429
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.429
        self.Scans[len(self.Scans)-1]['pixdim3'] = 0.999
        self.Scans[len(self.Scans)-1]['pixdim4'] = 0.015
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='RESTINGSTATE'
        self.Scans[len(self.Scans)-1]['dim1'] = 112
        self.Scans[len(self.Scans)-1]['dim2'] = 112
        self.Scans[len(self.Scans)-1]['dim3'] = 37
        self.Scans[len(self.Scans)-1]['dim4'] = 150
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.000
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.000
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.000
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.000
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DTI'
        self.Scans[len(self.Scans)-1]['dim1'] = 112
        self.Scans[len(self.Scans)-1]['dim2'] = 112
        self.Scans[len(self.Scans)-1]['dim3'] = 81
        self.Scans[len(self.Scans)-1]['dim4'] = 17
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.000
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.000
        self.Scans[len(self.Scans)-1]['pixdim3'] = 2.000
        self.Scans[len(self.Scans)-1]['pixdim4'] = 8.099
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='ASL'
        self.Scans[len(self.Scans)-1]['dim1'] = 64
        self.Scans[len(self.Scans)-1]['dim2'] = 64
        self.Scans[len(self.Scans)-1]['dim3'] = 15
        self.Scans[len(self.Scans)-1]['dim4'] = 150
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.500
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.500
        self.Scans[len(self.Scans)-1]['pixdim3'] = 6.600
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.719
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []

    def InitializeScansAZ2(self):
        self.Scans = {}
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='T1'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 165
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 1
        self.Scans[len(self.Scans)-1]['pixdim2'] = 1
        self.Scans[len(self.Scans)-1]['pixdim3'] = 1
        self.Scans[len(self.Scans)-1]['pixdim4'] = .0065902001
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Food_GoNoGo_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 157
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Food_GoNoGo_r2'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 157
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Food_GoNoGo_r3'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 157
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Food_GoNoGo_r4'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 157
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='FNF'
        self.Scans[len(self.Scans)-1]['dim1'] = 112
        self.Scans[len(self.Scans)-1]['dim2'] = 112
        self.Scans[len(self.Scans)-1]['dim3'] = 41
        self.Scans[len(self.Scans)-1]['dim4'] = 198
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.0
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.0
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.0
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='REST_BOLD'
        self.Scans[len(self.Scans)-1]['dim1'] = 96
        self.Scans[len(self.Scans)-1]['dim2'] = 96
        self.Scans[len(self.Scans)-1]['dim3'] = 42
        self.Scans[len(self.Scans)-1]['dim4'] = 141
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.5
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='AOD_Delay_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 27
        self.Scans[len(self.Scans)-1]['dim4'] = 180
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.4625
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.4625
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.0
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='AOD_Delay_r2'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 27
        self.Scans[len(self.Scans)-1]['dim4'] = 180
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.4625
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.4625
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.0
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='AOD_Accel_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 27
        self.Scans[len(self.Scans)-1]['dim4'] = 180
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.4625
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.4625
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.0
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='AOD_Accel_r2'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 27
        self.Scans[len(self.Scans)-1]['dim4'] = 180
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.4625
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.4625
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.0
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DTI_1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112
        self.Scans[len(self.Scans)-1]['dim2'] = 112
        self.Scans[len(self.Scans)-1]['dim3'] = 75
        self.Scans[len(self.Scans)-1]['dim4'] = 57
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.0
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.0
        self.Scans[len(self.Scans)-1]['pixdim3'] = 2.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 7.7546
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DTI_2'
        self.Scans[len(self.Scans)-1]['dim1'] = 112
        self.Scans[len(self.Scans)-1]['dim2'] = 112
        self.Scans[len(self.Scans)-1]['dim3'] = 75
        self.Scans[len(self.Scans)-1]['dim4'] = 57
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.0
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.0
        self.Scans[len(self.Scans)-1]['pixdim3'] = 2.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 7.7546
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Emo_GoNoGo_r1'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 123
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Emo_GoNoGo_r2'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 123
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Emo_GoNoGo_r3'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 123
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Emo_GoNoGo_r4'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 123
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Emo_GoNoGo_r5'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 123
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='Emo_GoNoGo_r6'
        self.Scans[len(self.Scans)-1]['dim1'] = 80
        self.Scans[len(self.Scans)-1]['dim2'] = 80
        self.Scans[len(self.Scans)-1]['dim3'] = 44
        self.Scans[len(self.Scans)-1]['dim4'] = 123
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 4.0
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.5
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='x1'
        self.Scans[len(self.Scans)-1]['dim1'] = 64
        self.Scans[len(self.Scans)-1]['dim2'] = 64
        self.Scans[len(self.Scans)-1]['dim3'] = 15
        self.Scans[len(self.Scans)-1]['dim4'] = 100
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 6.600
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.720
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='x2'
        self.Scans[len(self.Scans)-1]['dim1'] = 64
        self.Scans[len(self.Scans)-1]['dim2'] = 64
        self.Scans[len(self.Scans)-1]['dim3'] = 15
        self.Scans[len(self.Scans)-1]['dim4'] = 100
        self.Scans[len(self.Scans)-1]['pixdim1'] = 3.5
        self.Scans[len(self.Scans)-1]['pixdim2'] = 3.5
        self.Scans[len(self.Scans)-1]['pixdim3'] = 6.600
        self.Scans[len(self.Scans)-1]['pixdim4'] = 1.720
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []

    def InitializeScansEx58(self):
        self.Scans = {}
        # which of the scans are functional task scans, 
        # which would have associated behavior?
        self.TaskList = range(0,3,1)
        for i in range(0,3,1):
            self.Scans[i] = {}
            self.Scans[i]['FlagList'] = []
            self.Scans[i]['SeriesName']='SS_r'+str(i+1)
            self.Scans[i]['dim1'] = 112.00
            self.Scans[i]['dim2'] = 112.00
            self.Scans[i]['dim3'] = 36.00
            self.Scans[i]['dim4'] = 314.00
            self.Scans[i]['pixdim1'] = 2.00
            self.Scans[i]['pixdim2'] = 2.00
            self.Scans[i]['pixdim3'] = 3.00
            self.Scans[i]['pixdim4'] = 2.00
            self.Scans[i]['found']=False
            
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='FLAIR'
        self.Scans[len(self.Scans)-1]['dim1'] = 288.00
        self.Scans[len(self.Scans)-1]['dim2'] = 288.00
        self.Scans[len(self.Scans)-1]['dim3'] = 30.00
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 0.7986
        self.Scans[len(self.Scans)-1]['pixdim2'] = 0.7986
        self.Scans[len(self.Scans)-1]['pixdim3'] =  4.49999
        self.Scans[len(self.Scans)-1]['pixdim4'] = 11
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []      
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='T1'
        self.Scans[len(self.Scans)-1]['dim1'] = 256
        self.Scans[len(self.Scans)-1]['dim2'] = 256
        self.Scans[len(self.Scans)-1]['dim3'] = 165
        self.Scans[len(self.Scans)-1]['dim4'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 1.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 0.00    
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='REST_BOLD'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 37.00
        self.Scans[len(self.Scans)-1]['dim4'] = 285.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2.00   
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DTI_1'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 75.00
        self.Scans[len(self.Scans)-1]['dim4'] = 57.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 7.7
        self.Scans[len(self.Scans)-1]['found']=False
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='DTI_2'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 75.00
        self.Scans[len(self.Scans)-1]['dim4'] = 57.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 7.7    
        self.Scans[len(self.Scans)-1]['found']=False 
        self.Scans[len(self.Scans)-1]['FlagList'] = []
        self.Scans[len(self.Scans)]={}    
        self.Scans[len(self.Scans)-1]['SeriesName']='FLANKERS'
        self.Scans[len(self.Scans)-1]['dim1'] = 112.00
        self.Scans[len(self.Scans)-1]['dim2'] = 112.00
        self.Scans[len(self.Scans)-1]['dim3'] = 41.00
        self.Scans[len(self.Scans)-1]['dim4'] = 181.00
        self.Scans[len(self.Scans)-1]['pixdim1'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim2'] = 2.00
        self.Scans[len(self.Scans)-1]['pixdim3'] = 3.00
        self.Scans[len(self.Scans)-1]['pixdim4'] = 2    
        self.Scans[len(self.Scans)-1]['found']=False 
        self.Scans[len(self.Scans)-1]['FlagList'] = []