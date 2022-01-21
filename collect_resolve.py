import importlib.util

import signal,functools
from time import time
class TimeoutError(Exception):pass #定义一个超时错误类
def time_out(seconds,error_msg='TIME_OUT_ERROR:No connection were found in limited time!'):
#带参数的装饰器
    def decorated(func):
        result = ''
        def signal_handler(signal_num,frame): # 信号机制的回调函数，signal_num即为信号，frame为被信号中断那一时刻的栈帧
            global result
            result = error_msg
            raise TimeoutError(error_msg) #raise显式地引发异常。一旦执行了raise语句，raise后面的语句将不能执行
        
        def wrapper(*args,**kwargs):  #def wrapper(func,*args,**kwargs):
            global result
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(seconds) #如果time是非0，这个函数则响应一个SIGALRM信号并在time秒后发送到该进程。
            # print('time out~')
            try:
                result = func(*args,**kwargs) 
                #若超时，此时alarm会发送信息激活回调函数signal_handler，从而引发异常终止掉try的代码块
            finally:
                signal.alarm(0) #假如在callback函数未执行的时候，要取消的话，那么可以使用alarm(0)来取消调用该回调函数
                # print('finish')
                return result
        return functools.wraps(func)(wrapper) #return wrapper 
    return decorated

class Resolve(object):
    def __init__(self, app= 'Resolve',ip='127.0.0.1'):
        self.app = app
        self.ip = ip

    def load_dynamic(self, module, path):
        loader = importlib.machinery.ExtensionFileLoader(module, path)
        module = loader.load_module()
        return module

    def bmd(self):
        pylib = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
        return self.load_dynamic('fusionscript', pylib)

    @time_out(1)
    def get_resolve_remote(self):
        return self.bmd().scriptapp(self.app, self.ip)
    
    @time_out(1)
    def get_fusion_remote(self):
        return self.bmd().scriptapp('Fusion', self.ip)

class Workstation_info(object):
    def __init__(self, hostname, ip) -> None:
        self.name = hostname
        self.ip = ip
        self.resolve = Resolve(ip = self.ip).get_resolve_remote()

        self.page = self.resolve.GetCurrentPage()
        self.proj_mng = self.resolve.GetProjectManager()
        self.project = self.proj_mng.GetCurrentProject()
        self.timeline = self.project.GetCurrentTimeline()
        self.mediapool = self.project.GetMediaPool()

        self.db_name = self.proj_mng.GetCurrentDatabase()['DbName']
        self.proj_name = self.project.GetName()
    
    def Main_info(self) -> dict:
        '''
        return:: page name db proj_name
        '''
        if self.page == 'media':
            main_info = {
                'page': 'Media',
                'name': self.name,
                'current_bin': self.mediapool.GetCurrentFolder().GetName(),
            }
        elif self.page == 'cut':
            main_info = {
                'page': 'Cut',
                'name': self.name,
                'timeline_name': self.timeline.GetName()
            }
        elif self.page == 'edit':
            main_info = {
                'page': 'Edit',
                'name': self.name,
                'timeline_name': self.timeline.GetName(),
                'timeline_duration':self.timeline.GetEndFrame(),
            }
        elif self.page =='fusion':
            main_info = {
                'page': 'Fusion',
                'name': self.name,
                'timeline name': self.timeline.GetName()
            }
        elif self.page =='color':
            main_info = {
                'page': 'Color',
                'name': self.name,
                'timeline_name': self.timeline.GetName(),
                'current_clip': self.timeline.GetCurrentVideoItem(),
                'current_thumb': self.timeline.GetCurrentClipThumbnailImage(),
                'current_position': self.timeline.GetCurrentVideoItem().GetStart()
            }
        elif self.page =='fairlight':
            main_info = {
                'page': 'Fairlight',
                'name': self.name,
                'timeline_name': self.timeline.GetName()
            }
        elif self.page =='deliver':
            main_info = {
                'page': 'Deliver',
                'name': self.name,
                'timeline_name': self.timeline.GetName(),
                'is_rendering': self.project.IsRenderingInProgress(),
                'render_job_list': self.project.GetRenderJobList()
            }
        main_info['database'] = self.db_name
        main_info['project_name'] = self.proj_name
        
        return main_info
