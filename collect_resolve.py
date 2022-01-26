import tempfile
import importlib.util
import signal,functools
import numpy as np
import base64
import cv2
from PIL import ImageDraw, Image
GLOBAL_WAIT_TIME = 1

import pysnooper

clipcolor = {
    'Orange': [0, 110, 235],
    'Apricot': [51, 168, 255],
    'Yellow': [28, 169 ,226],
    'Lime': [21, 198, 159],
    'Olive': [32, 153, 94],
    'Green': [100, 143, 68],
    'Teal': [153, 152, 0],
    'Navy': [119, 50, 31],
    'Blue': [161, 118, 67],
    'Purple': [160, 115, 153],
    'Violet': [141, 87, 208],
    'Pink': [181, 140, 233],
    'Tan': [151, 176, 185],
    'Beige': [119, 160, 198],
    'Brown': [0, 102, 153],
    'Chocolate': [63, 90, 140],
    '': [161, 118, 67]
}

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

    @time_out(GLOBAL_WAIT_TIME)
    def get_resolve_remote(self):
        return self.bmd().scriptapp(self.app, self.ip)
    
    @time_out(GLOBAL_WAIT_TIME)
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

    def edit_mini_timeline(self):
        tHeight = 10
        tl = self.timeline
        total_track = tl.GetTrackCount('video')
        duration = int(self.timeline.GetEndFrame() - self.timeline.GetStartFrame())
        bg_h = tHeight * total_track+2 if total_track>3 else tHeight * 3 + 2
        scale = 1 if duration < 2000 else (2000/duration)
        bg = Image.new('RGB', (int(duration*scale)+3, bg_h), (33,33,33))
        rectangle = ImageDraw.Draw(bg)
        
        for track in range(1, int(total_track)+1):
            in_track_clips = tl.GetItemsInTrack('video', track)
            for clip in in_track_clips:
                clip = in_track_clips[clip]
                clip_in = int((clip.GetStart() - tl.GetStartFrame())* scale)+1
                clip_out = int((clip.GetEnd() - tl.GetStartFrame())* scale)+1
                clip_color = clipcolor[clip.GetClipColor()]
                try:
                    rectangle.rectangle([clip_in, tHeight*(track-1)+1, clip_out, tHeight*track], fill= tuple([clip_color[2], clip_color[1], clip_color[0]]), outline= (23,23,23))
                except:
                    pass
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        bg = bg.transpose(Image.FLIP_TOP_BOTTOM)
        # if duration >= 2000:
        #     bg = bg.resize((2000, tHeight * total_track+1), Image.BICUBIC)
        bg.save(tmp_file)
        # bg.show()
        return tmp_file.name

    def readb64(self, base64_string, width, height):
        nparr = np.fromstring(base64.b64decode(base64_string), np.uint8)
        nparr = nparr.reshape(int(height), int(width), 3)
        return cv2.cvtColor(nparr, cv2.COLOR_RGB2BGR)
    
    def convert_thumbnail(self, currentMediaThumbnail):
        width = currentMediaThumbnail["width"]
        height = currentMediaThumbnail["height"]
        imgstring = currentMediaThumbnail["data"]
        cvimg = self.readb64(imgstring, width, height)
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        cv2.imwrite(tmp_file.name, cvimg)
        return tmp_file.name
    
    @pysnooper.snoop()
    def current_rendering_jobs(self) -> list:
        result = []
        if self.project.IsRenderingInProgress():
            all_jobs = self.project.GetRenderJobList()
            for j in all_jobs:
                id = j['JobId']
                status = self.project.GetRenderJobStatus(id)
                if j['TimelineName'] != self.timeline.GetName():
                    if status['JobStatus'] != 'Rendering':
                        result.append(j)
            return result
        else:
            return None
    
    def rendering_job_progress(self, jobs):
        result = []
        for j in jobs:
            id = j['JobId']
            status = self.project.GetRenderJobStatus(id)
            result.append(status)
        return result
    
    
    def Main_info(self) -> dict:
        '''
        return:: page name db proj_name
        '''
        if self.page == 'media':
            main_info = {
                'page': 'Media',
                'name': self.name,
                'current_bin': self.mediapool.GetCurrentFolder().GetName(),
                'timeline_name': None
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
                'mini_timeline': self.edit_mini_timeline()
            }
        elif self.page =='fusion':
            main_info = {
                'page': 'Fusion',
                'name': self.name,
                'timeline_name': self.timeline.GetName()
            }
        elif self.page =='color':
            thumb_data = self.timeline.GetCurrentClipThumbnailImage()
            main_info = {
                'page': 'Color',
                'name': self.name,
                'timeline_name': self.timeline.GetName(),
                'timeline_duration': int(self.timeline.GetEndFrame() - self.timeline.GetStartFrame()),
                'current_clip': self.timeline.GetCurrentVideoItem(),
                'current_thumb': self.convert_thumbnail(thumb_data),
                'current_position': float((self.timeline.GetCurrentVideoItem().GetStart() - self.timeline.GetStartFrame()) / int(self.timeline.GetEndFrame() - self.timeline.GetStartFrame()))
            }
        elif self.page =='fairlight':
            main_info = {
                'page': 'Fairlight',
                'name': self.name,
                'timeline_name': self.timeline.GetName()
            }
        elif self.page =='deliver':
            current_rendering_job = self.current_rendering_jobs()
            main_info = {
                'page': 'Deliver',
                'name': self.name,
                'timeline_name': self.timeline.GetName(),
                'is_rendering': self.project.IsRenderingInProgress(),
                'render_job_list': self.project.GetRenderJobList(),
                'rendering_jobs': current_rendering_job,
                'rendering_job_progress': self.rendering_job_progress(current_rendering_job) if current_rendering_job is not None else None
            }
        main_info['database'] = self.db_name
        main_info['project_name'] = self.proj_name
        
        return main_info

if __name__ == '__main__':
    info = Workstation_info(hostname='self', ip='127.0.0.1')
    print(info.Main_info())