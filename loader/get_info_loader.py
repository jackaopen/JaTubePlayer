import json
import os
from typing import Callable
class get_info_loader_:
    '''
    ### this is only for dependency injection
    > you still need target URL

    - ytdlp
    - maxresolution
    - deno_exe
    - ytdlp_log_handle
    - cookies_dir
        '''
    def __init__(self, yt_dlp:object,
                 maxresolution:int,
                 deno_exe:object,
                 ytdlp_log_handle:object,
                 cookie:Callable[[], str],
                 config_dir:str):
        
        self._yt_dlp = yt_dlp
        self._maxresolution = maxresolution
        self._deno_exe = deno_exe
        self._ytdlp_log_handle = ytdlp_log_handle
        self._cookie = cookie
        self.config_dir = config_dir

    def _get_config_ytdlp_use_cookie(self)->bool:
        with open(self.config_dir, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("ytdlp_use_cookie", False)

    #since all are lambda getters, we need to call it first to get the actual value, then we can use it in the function as property
    @property
    def yt_dlp(self):
        return self._yt_dlp()
    @property
    def maxresolution(self):
        return self._maxresolution()
    @property
    def deno_exe(self):
        return self._deno_exe()
    @property
    def ytdlp_log_handle(self):
        return self._ytdlp_log_handle()
    @property
    def cookie(self):
        if self._get_config_ytdlp_use_cookie():
            return self._cookie()
        else:
            return None
        
