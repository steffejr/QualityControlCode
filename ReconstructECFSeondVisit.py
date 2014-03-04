import os
import glob
import shutil

DataFolder = '/share/studies/ECFf/Subjects'
PathList = []
ProbList = []
for root, subfolders,files in os.walk(DataFolder):
    for file in files:
        if (file.find('.REC') > 0) & (file.find('LS2')>-1):
            if PathList.count(root) == 0:
                
                
                
def reconstruct(subid,DataFolder):
    root = os.path.join(DataFolder,subid,'S0002','ParRecFiles')
    # found new subject folder
    files = glob.glob(os.path.join(root,'*.REC'))
    file = files[0]
    CurrentFile = os.path.join(root, file)
    subid = root.split('/')[-3]
    visitid = root.split('/')[-2]
#       print "subfnPreproc_LSTask('%s','%s')"%(subid,visitid)
    
    VisitFolder = os.path.join(DataFolder,subid,visitid)
    try:
        # reconstruct all files
        os.system('/usr/local/mricron/4.1.2010/dcm2nii -o %s %s'%(root,CurrentFile))

        NIIfiles = glob.glob(os.path.join(root,'*.nii'))
        LSorder = []
        for i in NIIfiles:
            if (not os.path.split(i)[1].startswith('c')) & (not os.path.split(i)[1].startswith('o')):
                if i.find('2X2X3') > -1:
                    imageType = 'LS'
                    # find run number
                    runNum = int(i[i.find('s0')+1:i.find('s0')+4])
                    LSorder.insert(runNum,i)
                elif i.find('FLAIR')>-1:
                    imageType = 'FLAIR'
                    OutFolder = os.path.join(VisitFolder,imageType)
                    if not os.path.exists(OutFolder):
                        os.mkdir(OutFolder)
                    OutFileName = imageType+"_"+subid+"_"+visitid+".nii"
                    shutil.move(i,os.path.join(OutFolder,OutFileName))
                elif i.find('MPRAGE')>-1:
                    imageType = 'T1'
                    OutFolder = os.path.join(VisitFolder,imageType)
                    if not os.path.exists(OutFolder):
                        os.mkdir(OutFolder)                            
                    OutFileName = imageType+"_"+subid+"_"+visitid+".nii"
                    shutil.move(i,os.path.join(OutFolder,OutFileName))
                elif i.find('JAX')>-1:
                    imageType = 'JackTask'
                    OutFolder = os.path.join(VisitFolder,imageType)
                    if not os.path.exists(OutFolder):
                        os.mkdir(OutFolder)                            
                    OutFileName = imageType+"_"+subid+"_"+visitid+".nii"
                    shutil.move(i,os.path.join(OutFolder,OutFileName))
            else:
                os.unlink(i)
        # move the LS files now
        count = 1
        for i in LSorder:
            imageType = "LS_r"+str(count)
            OutFolder = os.path.join(VisitFolder,imageType)
            if not os.path.exists(OutFolder):
                os.mkdir(OutFolder)                    
            OutFileName = imageType+"_"+subid+"_"+visitid+".nii"
            shutil.move(i,os.path.join(OutFolder,OutFileName))
            count = count + 1
    except:
        ProbList.append(root)
        print "ERROR:"+root
        
                

                
                
                

