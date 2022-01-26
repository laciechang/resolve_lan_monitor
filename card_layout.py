
class Card_UI(object):
    def __init__(self, ui, info, hostlist) -> None:
        self.info = info
        self.ui = ui
        self.name = str(info['name'])
        self.ip = str(hostlist[self.name])
        self.page = str(info['page'])
        self.db = str(info['database'])
        self.proj_name = str(info['project_name'])

    def hostName(self):
        return self.ui.Label({"Text": self.name,
                "StyleSheet":"border: 1px solid black;background-color: rgb(40,40,40);border-radius: 2px", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
    
    def dbName(self):
        return self.ui.Label({"Text": self.db,
                "StyleSheet":"border: 1px solid black;background-color: rgb(40,40,40);border-radius: 2px", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
    
    def pageName(self):
        return self.ui.Label({"Text": self.page,
                "StyleSheet":"border: 1px solid black;background-color: rgb(40,40,40);border-radius: 2px", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
    
    def projName(self):
        name = self.proj_name if len(self.proj_name) <=20 else self.proj_name[:20]+"..."
        label = self.ui.Label({"Text": name, "ToolTip": self.proj_name,
                "StyleSheet":"border: 1px solid black;background-color: rgb(40,40,40);border-radius: 2px", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
        return label
    
    def timelineName(self):
        name = self.info['timeline_name'] if len(self.info['timeline_name']) <=20 else self.info['timeline_name'][:20]+"..."
        label = self.ui.Label({"Text": name, "ToolTip": self.info['timeline_name'],
                "StyleSheet":"border: 1px solid black;background-color: rgb(40,40,40);border-radius: 2px", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
        return label
    
    def baseinfo(self):
        base = [self.dbName(),
                self.pageName(),
                self.projName()]
        if self.info['timeline_name'] is None:
            return self.ui.VGroup(base)
        else:
            base.append(self.timelineName())
            return self.ui.VGroup(base)

    def deliver_renderinfo(self):
        job_list = self.info['render_job_list']
        
        self.ui.VGroup([
            self.ui.Label({"Text": 'Rendering',
                "StyleSheet":"color: green; font-weight: bold;border: 1px solid black;background-color: rgb(40,40,40);border-radius: 2px", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
        ])
    
    def deliver_isrender(self):
        if self.info['is_rendering']:
            return self.ui.Label({"Text": 'Rendering',
                "StyleSheet":"color: green; font-weight: bold;border: 1px solid black;background-color: rgb(40,40,40);border-radius: 2px", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})
        else:
            return self.ui.Label({"Text": 'Standing By',
                "StyleSheet":"color: white; font-weight: bold;border: 1px solid black;background-color: rgb(40,40,40);border-radius: 2px", 
                "Alignment": {"AlignHCenter": True,"AlignVCenter": True,},})

    def main_card(self, content:list):
        group = self.ui.Stack([
                    self.ui.Label({"StyleSheet": 'background:rgb(33,33,33);border:2px solid grey;border-radius: 10px'}),
                    self.ui.HGroup({"Spacing": 10, }, [
                        self.ui.VGap(),
                        self.ui.VGroup({"Weight": 8},[
                            self.ui.VGap(),
                            self.hostName(),
                            self.ui.VGroup({"Weight": 8},content),
                            self.ui.VGap()]),
                        self.ui.VGap()]),])
        return group

    def layout_media(self):
        group = [
                    self.baseinfo()
                ]
        return self.main_card(group)
    
    def layout_cut(self):
        group = [
                    self.baseinfo()
                ]
        return self.main_card(group)
    
    def layout_edit(self):
        icon = self.info['mini_timeline']
        minitimeline = self.ui.Tree({"ID":"minitimeline",'IconSize':[2000, 200], "HeaderHidden": True, "StyleSheet":"background-color:rgb(33,33,33)"})
        img_row = minitimeline.NewItem()
        img_header = minitimeline.NewItem()
        img_header.Text[0] = 'minitimeline'
        minitimeline.SetHeaderItem(img_header)
        img_row.Icon[0] = self.ui.Icon({'File': icon})
        minitimeline.AddTopLevelItems([img_row])
        minitimeline.ColumnWidth[0] = 2000

        group = [
                    self.baseinfo(),
                    minitimeline
                ]
        return self.main_card(group)
    
    def layout_fusion(self):
        group = [
                    self.baseinfo()
                ]
        return self.main_card(group)
    
    def layout_color(self):
        icon = self.info['current_thumb']
        thumb = self.ui.Button({"Icon": self.ui.Icon({'File': icon}), "IconSize": [128, 74], 'Enabled': True, 'Flat': True})
        thumb_stack = self.ui.Stack([thumb, self.ui.HGap()])
        progress = self.ui.Stack([
                        self.ui.HGap(),
                        self.ui.Label({"Alignment": {"AlignHCenter": True}, "StyleSheet": "max-height: 3px; max-width: 160px; background-color: rgb(67,67,67)",}),
                        self.ui.Label({"Alignment": {"AlignHCenter": True}, "StyleSheet": "max-height: 1px; max-width: {w}px; background-color: rgb(145,145,145);border-width: 1px;border-style: solid;border-color: rgb(37,37,37);".format(w=int(self.info['current_position']*160)),}),
                        self.ui.HGap(),
                        ])
        group = [
                    self.baseinfo(),
                    thumb_stack,
                    progress,
                ]
        return self.main_card(group)
    
    def layout_fairlight(self):
        group = [
                    self.baseinfo()
                ]
        return self.main_card(group)
    
    def layout_deliver(self):
        group = [
                    self.baseinfo(),
                    self.deliver_isrender()
                ]
        return self.main_card(group)
    
    def layout_offline(self):
        group = [
                    self.ui.Label({"Text": 'Resolve Offline'})
                ]
        return self.main_card(group)

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
