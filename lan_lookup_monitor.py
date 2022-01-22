import imp
import sys, os, socket, json

import collect_resolve as davinci
from splash import SplashScreen

def read_hosts(file):
    with open(file,'r') as jf:
        load_dict = json.load(jf)
    return load_dict

JF = read_hosts(os.path.join(os.path.dirname(__file__), 'config.json'))

LOCAL_BMD = davinci.Resolve()
LOCAL_RESOLVE = LOCAL_BMD.get_resolve_remote()
LOCAL_FUSION = LOCAL_BMD.get_fusion_remote()
UI = LOCAL_FUSION.UIManager
DISP = LOCAL_BMD.bmd().UIDispatcher(UI)
CurrentHostOnPage = len(JF) if len(JF)<=5 else 5


INFOMATIONS = {}

class Workstation_status_UI(object):
    def __init__(self, ui, info) -> None:
        self.ui = ui
        self.name = str(info['name'])
        self.ip = str(JF[self.name])
        self.page = str(info['page'])
        self.db = str(info['database'])
        self.proj_name = str(info['project_name'])

    def hostName(self):
        return self.ui.Label({"Text": self.name,
                "StyleSheet":"border: 1px solid black;background-color: rgb(33,33,33)", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
    
    def dbName(self):
        return self.ui.Label({"Text": self.db,
                #"StyleSheet":"border: 1px solid black;background-color: rgb(33,33,33)", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
    
    def pageName(self):
        return self.ui.Label({"Text": self.page,
                "StyleSheet":"border: 1px solid black;background-color: rgb(33,33,33)", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
    
    def projName(self):
        return self.ui.Label({"Text": self.proj_name,
                "StyleSheet":"border: 1px solid black;background-color: rgb(33,33,33)", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})

    def layout_media(self):
        group = self.ui.Stack([
            self.ui.Label({"StyleSheet": 'background:rgb(40,40,40);border:2px solid grey;border-radius: 10px'}),
            self.ui.VGroup({"Spacing": 10, }, [
                self.ui.HGap(),
                self.ui.HGroup({"Weight": 8},[
                    self.ui.VGap(),
                    self.ui.VGroup({"Weight": 8},[
                        self.hostName(),
                        self.dbName(),
                        self.pageName(),
                        self.projName(),
                        ]),
                    self.ui.VGap()
                ]),
                self.ui.HGap()
                ]),
        ])
        return group
    
    def layout_cut(self):
        return self.ui.VGroup({"Spacing": 10}, [
                self.hostName(),
                self.dbName(),
                self.pageName(),
                self.projName(),
                ])
    
    def layout_edit(self):
        return self.ui.VGroup({"Spacing": 10}, [
                self.hostName(),
                self.dbName(),
                self.pageName(),
                self.projName(),
                ])
    
    def layout_fusion(self):
        return self.ui.VGroup({"Spacing": 10}, [
                self.hostName(),
                self.dbName(),
                self.pageName(),
                self.projName(),
                ])
    
    def layout_color(self):
        return self.ui.VGroup({"Spacing": 10}, [
                self.hostName(),
                self.dbName(),
                self.pageName(),
                self.projName(),
                ])
    
    def layout_fairlight(self):
        return self.ui.VGroup({"Spacing": 10}, [
                self.hostName(),
                self.dbName(),
                self.pageName(),
                self.projName(),
                ])
    
    def layout_deliver(self):
        return self.ui.VGroup({"Spacing": 10}, [
                self.hostName(),
                self.dbName(),
                self.pageName(),
                self.projName(),
                ])
    
    def layout_offline(self):
        return self.ui.VGroup({"Spacing": 10}, [
                self.hostName(),
                self.ui.Label({"Text": 'Resolve Offline'})
                ])

    def render_stack(self):
        if self.page == 'Media':
            return self.layout_media()
        elif self.page == 'Cut':
            return self.layout_cut()
        elif self.page == 'Edit':
            return self.layout_edit()
        elif self.page == 'Fusion':
            return self.layout_fusion()
        elif self.page == 'Color':
            return self.layout_color()
        elif self.page == 'Fairlight':
            return self.layout_fairlight()
        elif self.page == 'Deliver':
            return self.layout_deliver()
        elif self.page == 'Offline':
            return self.layout_offline()
        else:
            return self.ui.Label({"Text": "No Page"})

splashscreen = SplashScreen(UI, DISP)
splash_win = splashscreen.splash_window()
progress_width = splashscreen.splash_progress().GetGeometry()[3]

splash_win.Show()
PROGRESS = 0
for i in JF:
    try:
        INFOMATIONS[i] = davinci.Workstation_info(i, JF[i]).Main_info()
    except:
        INFOMATIONS[i] = {"page": 'Offline', "name": i, 'database': 'na', 'project_name': 'na'}
    PROGRESS += 1
    splashscreen.splash_progress().Resize([
        int((PROGRESS / len(JF))*int(progress_width))
        ,3])

DISP.ExitLoop()
splash_win.Hide()

def single_group(id, info):
    group = []
    for i in JF:
        single_group = Workstation_status_UI(UI, info[i]).render_stack()
        group.append(single_group)
    return UI.Stack({'ID': 'group_'+str(id)}, group)

def build_stacks():
    info = INFOMATIONS
    group = UI.HGroup({"Spacing": 5})
    for i in range(0, len(JF)):
        group.AddChild(single_group(i, info))
    return group

layout = [
    UI.HGroup({'Spacing': 50,},[
        UI.VGroup({'Spacing': 10}, [
            build_stacks(),
            UI.Slider({"ID": "switcher",
            'Events': { 'SliderMoved': True },
            'Weight': 0,
            }),
        ]),]),]

MAINWIN = DISP.AddWindow({ 
                    'WindowTitle': 'Batch Render Tools Pro', 
                    'ID': 'main',
                    'Geometry': [ 
                                200, 200, # x, y
                                600, 300 # w, h
                                ],
                    }, layout)

ITEMS = MAINWIN.GetItems()

for i in range(0, len(JF)):
    ITEMS['group_'+ str(i)].CurrentIndex = i

ITEMS['switcher'].Value = 0
ITEMS['switcher'].Minimum = 0
ITEMS['switcher'].Maximum = len(JF)-1

def _exit(ev):
    DISP.ExitLoop()

def _switch(ev):
    current = ev['Value']
    for i in range(0, CurrentHostOnPage):
        ITEMS['group_'+ str(i)].CurrentIndex = i + current


MAINWIN.On['main'].Close = _exit
MAINWIN.On['switcher'].SliderMoved = _switch

def show_win():
    MAINWIN.Show()
    DISP.RunLoop()
    MAINWIN.Hide()

if __name__ == '__main__':
    show_win()
