class SplashScreen(object):
    def __init__(self, ui, disp):
        self.ui = ui
        self.disp = disp
        self.progressid = 'loading_progress'
        self.loading_info = 'loading_info'
        

    def splash_window(self):
        layout = [
            self.ui.Label({"Text":"DaVinci Resolve LAN Node Monitor",
            "Alignment": {"AlignHCenter": True,"AlignVCenter": True,}}),
            self.ui.Stack([
                self.ui.Label({"ID":self.progressid ,"StyleSheet":"max-height: 2px; background-color:rgb(223，189，100)"}),
                self.ui.Label({"ID":"progress-bg",
                "StyleSheet":"max-height: 2px; background-color:rgb(33，33，33);border:1px solid black"}),
            ]),
            self.ui.Label({"ID":self.loading_info ,"Text":"DaVinci Resolve LAN Node Monitor",
            "Alignment": {"AlignHCenter": True,"AlignVCenter": True,}}),
        ]
        win = self.disp.AddWindow({ 
                    'WindowTitle': 'Monitor Splash', 
                    'ID': 'splash',
                    'WindowFlags': { 'SplashScreen': True },
                    'Geometry': [ 
                                200, 200, # x, y
                                600, 300 # w, h
                                ],
                    }, layout)
        return win

    def splash_progress(self):
        return self.splash_window().GetItems()[self.progressid]
    def splash_loading_info(self):
        return self.splash_window().GetItems()[self.loading_info]