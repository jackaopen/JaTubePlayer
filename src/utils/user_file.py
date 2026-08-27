# init user file for different users
import os
import json
import shutil
from account.Account import account_handle

DEFAULT_CONFIG_DICT = {
    "quickstartup_init": {
        "mode": 0,
        "playlistmode_playlist_ID": "",
        "localfoldermode_folder_Path": "",
        "playlistmode_playlist_Name": "",
        "searchmode_keyword": ""
    },
    "keyboard_hotkeys": {
        "play_pause": "<ctrl>+<shift>+p",
        "next": "<ctrl>+<shift>+n",
        "previous": "<ctrl>+<shift>+b",
        "stop": "<ctrl>+<shift>+s",
        "mode_repeat": "<ctrl>+<shift>+r",
        "mode_continuous": "<ctrl>+<shift>+c",
        "mode_random": "<ctrl>+<shift>+x",
        "volume_up": "<ctrl>+<shift>+<up>",
        "volume_down": "<ctrl>+<shift>+<down>",
        "toggle_minimize": "<ctrl>+<shift>+m"
    },
    "cache": {
        "demuxer_max_bytes": 512,
        "demuxer_max_back_bytes": 512,
        "cache_pause_wait": 1,
        "audio_wait_open": 1
    },
    "max_result_count": {
        "Recommendations": 100,
        "sub": 100,
        "search": 100,
        "like": 5000
    },
    "ytdlp_use_cookie": False,
    "ytdlp_use_nightly_build": False,
    "vercheck": True,
    "max_resolution": 1080,
    "auto_sub_refresh": True,
    "auto_like_refresh": False,
    "blur": True,
    "run_flask": True,
    "open_with_fullscreen": False,
    "enable_discord_presence": True,
    "discord_presence_show_playing": True,
    "show_cache": False,
    "hover_fullscreen": True,
    "download_path": "[appdata]/JaTubePlayer/saved_file",
    "fullscreenmode": 0,
    "blur_hexColor": "#101010",
    "chrome_ext_server_port": 5000,
    "discord_idle_presence_wording": "[Idling & Chillin' like a potato \ud83e\udd54]"
}

class UserFile_handle:
    '''init user file for different users'''
    def __init__(self,
                 user_data_dir:str,
                 current_dir:str):

        self.JaTubeplayer_data = os.path.join(user_data_dir, "JaTubePlayer")

        self.chrome_ext_origin = os.path.join(current_dir, "chrome_ext_pack")
        self.chrome_ext_user_data = os.path.join(self.JaTubeplayer_data, "chrome_ext_pack")

        self.config_file = os.path.join(self.JaTubeplayer_data, "config.json")
        self.star_vid_file = os.path.join(self.JaTubeplayer_data, "starred_vid.json")

        self.aes_key_file = os.path.join(self.JaTubeplayer_data, "AES_key.enc")
        self.cookie_dir = os.path.join(self.JaTubeplayer_data, "cookie_key.enc")
        self._init_user_file()

    def _init_user_file(self):
        if not os.path.exists(self.JaTubeplayer_data):
            os.makedirs(self.JaTubeplayer_data)

        if not os.path.exists(self.config_file):
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG_DICT, f, indent=4)

        if not os.path.exists(self.star_vid_file):
            with open(self.star_vid_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

        shutil.copytree(self.chrome_ext_origin, 
                        self.chrome_ext_user_data,
                        dirs_exist_ok=True)

        if not os.path.exists(self.aes_key_file) and not os.path.exists(self.cookie_dir):
            account_handle.silent_create_AES_key(self.aes_key_file)