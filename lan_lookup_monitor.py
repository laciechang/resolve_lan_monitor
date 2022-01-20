import imp
import sys, os, socket, json

import collect_resolve as davinci

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

HOST_GALLERY = 'HOST_GALLERY'


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
                "StyleSheet":"border: 1px solid black;background-color: rgb(33,33,33)", 
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
        return self.ui.VGroup({"Spacing": 10}, [
                self.hostName(),
                self.dbName(),
                self.pageName(),
                self.projName(),                
                ])
    
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
        else:
            return self.ui.Label({"Text": "No Page"})
def collect_info() -> dict:
    for i in JF:
        INFOMATIONS[i] = davinci.Workstation_info(i, JF[i]).Main_info()
    return INFOMATIONS

def single_stack(id):
    stacks = []
    for i in JF:
        single_group = Workstation_status_UI(UI, collect_info()[i]).render_stack()
        stacks.append(single_group)
    print(stacks)
    return UI.Stack({'ID': 'sig_'+str(id)}, stacks)

def build_stacks():
    group = UI.HGroup({"Spacing": 1})
    for i in range(0, len(JF)):
        group.AddChild(single_stack(i))
    return group

layout = [
    UI.HGap(),
    UI.HGroup({'Spacing': 10, "Weight": 9},[
        UI.VGroup({'Spacing': 0}, [
            build_stacks(),
            UI.Slider({"ID": "switcher",
            'Events': { 'SliderMoved': True },
            }),
        ]),
    ]),
    UI.HGap(),
]


MAINWIN = DISP.AddWindow({ 
                    'WindowTitle': 'Batch Render Tools Pro', 
                    'ID': 'main',
                    'Geometry': [ 
                                200, 200, # x, y
                                600, 300 # w, h
                                ],
                    }, UI.HGroup(layout))

ITEMS = MAINWIN.GetItems()
print(ITEMS.keys())

for i in range(0, len(JF)):
    ITEMS['sig_'+ str(i)].CurrentIndex = i

ITEMS['switcher'].Value = 0
ITEMS['switcher'].Minimum = 0
ITEMS['switcher'].Maximum = len(JF)-1

def _exit(ev):
    DISP.ExitLoop()

def _switch(ev):
    current = ev['Value']
    for i in range(0, len(JF)):
        ITEMS['sig_'+ str(i)].CurrentIndex = i + current


MAINWIN.On['main'].Close = _exit
MAINWIN.On['switcher'].SliderMoved = _switch

def show_win():
    MAINWIN.Show()
    DISP.RunLoop()
    MAINWIN.Hide()

if __name__ == '__main__':
    show_win()
