
from wxPython.wx import *
def PickFolder():
    choices = [];
    #choices.append('/share/data/studies/WHICAP/Quarantine/IncomingDICOMFiles')
    choices.append('/share/studies/CogRes/Quarantine/Subjects')
    choices.append('/share/studies/RANN/Quarantine/IncomingDICOM')
    choices.append('/share/studies/Exercise55/Quarantine/IncomingDICOM')
    choices.append('/share/studies/Exercise58/Quarantine/IncomingDICOM')
    choices.append('/share/studies/iLS/Quarantine/IncomingDICOM')
    choices.append('/share/studies/AZ2/Quarantine/IncomingDICOM')
    choices.append('/share/studies/FNF/Quarantine/IncomingDICOM')
    Names = [];
    #Names.append('WHICAP')
    Names.append('CogRes')
    Names.append('RANN')
    Names.append('Exercise55')
    Names.append('Exercise58')
    Names.append('InterferenceLS')
    Names.append('AZ2')
    Names.append('FNF')
    application = wxPySimpleApp()
    dialog = wxSingleChoiceDialog (None, 'Which Visit?', '', Names)


    if dialog.ShowModal() == wxID_OK:
    #		print 'Position of selection:', dialog.GetSelection()
    #		print 'Selection:', dialog.GetStringSelection()
    	Folder = choices[dialog.GetSelection()]
    	return Folder
    dialog.Destroy()

