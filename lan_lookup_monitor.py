import os,json

import collect_resolve as davinci
from splash import SplashScreen
from card_layout import Card_UI

def read_hosts(file):
    with open(file,'r') as jf:
        load_dict = json.load(jf)
    return load_dict

JF = read_hosts(os.path.join(os.path.dirname(__file__), 'config.json'))

MAXCARD = 5

LOCAL_BMD = davinci.Resolve()
LOCAL_RESOLVE = LOCAL_BMD.get_resolve_remote()
LOCAL_FUSION = LOCAL_BMD.get_fusion_remote()
UI = LOCAL_FUSION.UIManager
DISP = LOCAL_BMD.bmd().UIDispatcher(UI)
CurrentHostOnPage = len(JF) if len(JF)<=MAXCARD else MAXCARD


INFOMATIONS = {}
def load_info(i):
    try:
        INFOMATIONS[i] = davinci.Workstation_info(i, JF[i]).Main_info()
    except:
        INFOMATIONS[i] = {"page": 'Offline', "name": i, 'database': 'na', 'project_name': 'na'}

splashscreen = SplashScreen(UI, DISP)
splash_win = DISP.AddWindow({ 
                    'WindowTitle': 'Monitor Splash', 
                    'ID': 'Splash',
                    'WindowFlags': {'Popup': True},
                    'Geometry': [ 
                                600, 400, # x, y
                                400, 200 # w, h
                                ],
                    }, splashscreen.splash_window())
splashitem = splash_win.GetItems()
progressbar = splashitem['loading_progress']
progress_width = progressbar.GetGeometry()[3]
splash_win.Show()
PROGRESS = 0
progressbar.Resize([1,3])
for i in JF:
    load_info(i)
    PROGRESS += 1
    pg_width = int(float(PROGRESS / (len(JF)+3))*int(progress_width))
    progressbar.Resize([pg_width,3])

DISP.ExitLoop()
splash_win.Hide()

def single_group(id, info):
    group = []
    for i in JF:
        single_group = Card_UI(UI, info[i], JF).render_stack()
        group.append(single_group)
    return UI.Stack({'ID': 'group_'+str(id)}, group)

def build_stacks(info = INFOMATIONS):
    # info = INFOMATIONS
    group = []
    for i in range(0, CurrentHostOnPage):
        group.append(single_group(i, info))
    return UI.HGroup({"Spacing": 5,}, group)

layout = [
    UI.HGroup({'Spacing': 50,},[
        UI.VGroup({'Spacing': 10}, [
            UI.Stack({"ID": "main_group"}, [build_stacks()]),
            UI.HGroup({'Weight': 0.1}, [
                UI.HGap(),
                UI.Slider({"ID": "switcher",
                'Events': { 'SliderMoved': True },
                'Weight': 1,
                }),
                UI.HGap(),
                UI.Button({"ID":"refresher", "Text": "Refresh", "Visible": False})
            ]),
        ]),]), 
    ]

MAINWIN = DISP.AddWindow({ 
                    'WindowTitle': 'DaVinci Resolve LAN Monitor', 
                    'ID': 'main',
                    'Geometry': [ 
                                200, 200, # x, y
                                1000, 400 # w, h
                                ],
                    }, layout)

ITEMS = MAINWIN.GetItems()
# print(ITEMS)

for i in range(0, CurrentHostOnPage):
    ITEMS['group_'+ str(i)].CurrentIndex = i

if len(JF) <= MAXCARD:
    ITEMS['switcher'].Visible = False
else:
    ITEMS['switcher'].Visible = True
    ITEMS['switcher'].Value = 0
    ITEMS['switcher'].Minimum = 0
    ITEMS['switcher'].Maximum = len(JF)-CurrentHostOnPage

def _exit(ev):
    DISP.ExitLoop()

def _switch(ev):
    current = ev['Value']
    for i in range(0, CurrentHostOnPage):
        ITEMS['group_'+ str(i)].CurrentIndex = i + current

def _refresh(ev):
    for i in JF:
        load_info(i)
    print(INFOMATIONS)
    ITEMS['refresher'].Enabled = False
    new_stacks = build_stacks(info=INFOMATIONS)
    ITEMS['main_group'].RemoveChild()
    ITEMS['main_group'].AddChild(new_stacks)
    ITEMS['refresher'].Enabled = True


MAINWIN.On['main'].Close = _exit
MAINWIN.On['switcher'].SliderMoved = _switch
MAINWIN.On['refresher'].Clicked = _refresh

def show_win():
    MAINWIN.Show()
    DISP.RunLoop()
    MAINWIN.Hide()

if __name__ == '__main__':
    show_win()
