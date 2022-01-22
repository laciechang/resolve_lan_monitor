class SplashScreen(object):
    def __init__(self, ui, disp):
        self.ui = ui
        self.disp = disp
        self.progressid = 'loading_progress'
        self.loading_info = 'loading_info'
        

    def splash_window(self):
        layout = self.ui.VGroup({'Spacing': 5}, [
            self.ui.Label({"Text":"DaVinci Resolve LAN Node Monitor",
            "Alignment": {"AlignHCenter": True,"AlignVCenter": True,}}),
            # self.ui.Stack({"ID": "pg_set",},[
            #             # self.ui.Label({"ID": 'ProgressBarBG',  "StyleSheet": "max-height: 3px; background-color: rgb(37,37,37)",}),
            #             ]),
            self.ui.Label({"ID": self.progressid,  "StyleSheet": "max-height: 3px; background-color: rgb(102, 221, 39);border-width: 1px;border-style: solid;border-color: rgb(37,37,37);",}),
            self.ui.Label({"ID":self.loading_info ,"Text":"Loading Nodes",
            "Alignment": {"AlignHCenter": True,"AlignVCenter": True,}}),
        ])
        win = self.disp.AddWindow({ 
                    'WindowTitle': 'Monitor Splash', 
                    'ID': 'Splash',
                    # 'WindowFlags': 'Popup',
                    'Geometry': [ 
                                200, 200, # x, y
                                700, 200 # w, h
                                ],
                    }, layout)
        return layout

    def splash_progress(self):
        bar = self.splash_window().GetItems()[self.progressid]
        return bar
    def splash_loading_info(self):
        return self.splash_window().GetItems()[self.loading_info]
    
    def splash_window_item(self):
        return self.splash_window().GetItems()['Splash']