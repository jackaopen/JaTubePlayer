import time
_TimeStartImport = time.time()

import asyncio
import aiohttp
import tkinter as tk
from tkinter import ttk,filedialog
from tkinter import *
import os
import io
import json
import sys
import sv_ttk
import threading
import webbrowser
import sys
import time
import math
import queue
import win32gui
from PIL import Image
from copy import *
from typing import Literal
import customtkinter as ctk
from customtkinter import CTkImage
import ctypes


from utils.get_scaling import *
from utils.load_yt_dlp import *
from utils.download_to_local import download_to_local
from utils.check_internet import *
from utils.check_internet import check_internet
from utils.get_media_info import *
from utils.color_picker.ctk_color_picker import AskColor  
from utils.additional_utils import lenght_convertor
from utils.load_font import load_private_font
from utils.log_handle import log_handler_
from loader.get_info_loader import get_info_loader_
from loader.media_data_list import media_data_list_template

from notification.wintoast_notify import ToastNotification
from notification.ctkmessagebox import ctk_messagebox

from effect.blur_for_client import blur
from ui.video_info_frame import vid_info_frame
from ui.Treeview_and_thumbnail import ThumbnailLoader

from system.tray import Playertray
from system.dnd_winsys import *
from system.keyboard import *
from system.presence import DiscordPresence

from video_media_control.media_list_page_control import MediaList_PageControl_,MediaType
from collections import deque

ctk.set_appearance_mode("dark")
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Jackaopen.JaTubePlayer')

def dnd_mode_change_status(sta:int):
    '''
    mainly for dnd
    will change the global var playing_vid_mode to sta
    '''
    global playing_vid_mode
    playing_vid_mode = sta


current_dir = None
'''
current_dir is the path to /src
'''
if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)
    _internal_dir = os.path.join(current_dir, "_internal")
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    _internal_dir = os.path.join(os.path.dirname(current_dir), "_internal")
    

'''
_internal_dir is the path to the /_internal outside /src
'''
icondir = os.path.join(_internal_dir, "jtp.ico")
appdata_dir = os.getenv('APPDATA')

os.makedirs(os.path.join(appdata_dir,'JaTubePlayer'),exist_ok=True)
os.makedirs(os.path.join(appdata_dir,'JaTubePlayer','ytdlp_update'),exist_ok=True)
os.makedirs(os.path.join(appdata_dir,'JaTubePlayer','saved_file'),exist_ok=True)






load_private_font(_internal_dir)

BASE_WIDTH = 1452
BASE_HEIGHT = 748


os.environ["PATH"] = os.path.join(_internal_dir) + os.pathsep + os.environ["PATH"]
import mpv
#### remember to add yt_dlp.exe from github to _iternal!!!
root = ctk.CTk()
hwnd = win32gui.FindWindow(None, root.title())
tkinter_scaling = get_window_dpi(hwnd)
root.geometry(f"{int(BASE_WIDTH*tkinter_scaling)}x{int(BASE_HEIGHT*tkinter_scaling)}+0+0")
ver='3.0'
root.title(f'JaTubePlayer {ver} ')
root.iconbitmap(icondir)
 
print(f"Tkinter scaling factor: {tkinter_scaling}")

effective_scaling = get_effective_scaling(hwnd,root)
ctk.set_widget_scaling(effective_scaling)


ui_queue = queue.Queue()

log_queue = deque(maxlen=5000)
messagebox = ctk_messagebox(root,_internal_path=_internal_dir)
log_handler = log_handler_(ui_queue=ui_queue,
                           ver=ver,
                           log_queue=log_queue,
                           messagebox=messagebox,
                           force_stop_loading = lambda: set_force_stop_loading(True),
                           root=root,
                           icondir=icondir,
                           blur_callable=lambda: (blur_hexColor.get(),blur_window.get()),
                           appdata_dir=appdata_dir
                           )
log_handle = log_handler.log_handle
ytdlp_log_handle = log_handler.ytdlp_log_handler




def _process_ui_queue():
    try:
        for _ in range(200):
            f = ui_queue.get_nowait()
            try:f()
            except Exception as e:log_handle(
                                      content=e,
                                      errtype='error',
                                      component='ui_queue',
                                  )
    except queue.Empty:pass
    root.after(20, _process_ui_queue)
root.after(20, _process_ui_queue)


def set_force_stop_loading(value=True):
      global force_stop_loading
      force_stop_loading = value

def _toggle_minimize():
    if root.state() == 'normal':
        root.lift()
        root.iconify()
    else:
        root.deiconify()

def dump(filename,content):
    try:
        with open(os.path.join(current_dir,'temp_data',f'{filename}.json'),'w') as f:
            json.dump(content,f,indent=4)
    except:pass


Frame_for_mpv = tk.Frame(root)
Frame_for_mpv.place(relx=0.011, rely=0.084, relwidth=0.595, relheight=0.664)
Frame_for_mpv.bind('<Button-1>',lambda event :pause(1))
motto_label = ctk.CTkLabel(Frame_for_mpv,
                           text="Uninterrupted,\njust how you like it",
                           font=('Satisfy',51.5),
                           text_color="#676767",
                           bg_color='transparent',
                           padx=20,
                           pady=14,
                           )
motto_label.place(relx=0.5,rely=0.5,anchor='center')


# ==== 播放器控制 ====
player = None
stream = False
playing_vid_mode = 0
"""
Playing video mode:
  0 = YouTube
  1 = Single / Open With
  2 = Folder
  3 = Chrome
  4 = Starred video (mixed mode — local or online, determined by URL schema)
"""
selected_song_number = None
yt_dlp = None
youtube = None
user_playlists_name = []
user_playlists_selected_name = ''
load_thread_queue = queue.Queue()
'''
This accept a tuple (chosen_file,direct_url)
'''
playing_vid_info_dict = {}
player_speed = tk.DoubleVar()
player_speed.set(1.0)
deno_exe = os.path.join(_internal_dir,'deno.exe')

subtitle_namelist = ['No subtitles']
subtitle_urllist = []

subtitle_selection_idx = tk.IntVar()
subtitle_selection_idx.set(0)

max_search_result_count = tk.StringVar()
max_recommendation_result_count = tk.StringVar()
max_sub_result_count = tk.StringVar()
max_like_result_count = tk.StringVar()


# ==== UI 控制變數 ====

playlistID = tk.StringVar()
autoretry = tk.BooleanVar()
fullscreenwithconsole = tk.BooleanVar()
maxresolution = tk.IntVar()
selected_song_title = tk.StringVar()
downloadhooktext = tk.StringVar()

info = None
with Image.open(os.path.join(_internal_dir,"banner.png")) as title_icon_source:
    title_icon_image = title_icon_source.copy()




# ==== 狀態控制 ====

loadingplaylist = False
loadingvideo = False
insert_treeview_quene = queue.Queue()
load_thread_queue = queue.Queue()   
auto_check_ver = tk.BooleanVar()
init_quickstartup_mode = tk.StringVar()
init_quickstartup_playlist_mode = tk.StringVar()
init_toggle_quickstartup = tk.BooleanVar()
auto_sub_refresh = tk.BooleanVar()
auto_like_refresh = tk.BooleanVar()
setting_run_chrome_extension_server = tk.BooleanVar()
chrome_extension_port = tk.StringVar(value='5000')
audio_only = tk.BooleanVar()
open_with_fullscreen = tk.BooleanVar()
show_cache = tk.BooleanVar()
force_stop_loading = False
is_downloading = tk.BooleanVar()
is_downloading.set(False)
hover_fullscreen = tk.BooleanVar()
demuxer_max_bytes = tk.IntVar()
demuxer_max_back_bytes = tk.IntVar()
cache_pause_wait = tk.DoubleVar()
audio_wait_open= tk.IntVar()
download_path = tk.StringVar()
enable_discord_presence = tk.BooleanVar()
discord_presence_show_playing = tk.BooleanVar()
discord_idle_presence_wording = tk.StringVar()
fullscreenmode = tk.IntVar()
ytdlp_use_cookie = tk.BooleanVar()
ytdlp_use_nightly_build = tk.BooleanVar()
current_ctk_scaling = 1.0
fullscreen_loading = False
'''
0 = normal 
1 = fullscreen with all widget
2 = fullscreen to window (not monitor)
'''
fullscreen_status = 0
'''
0 = normal
1 = zoomed
'''
dnd_handle = None
discord_presence = None
google_control = None
get_info_loader = None
media_data_list = media_data_list_template()
'''
    ### This class it the loader template for media data for playlisttreebox
    - vid_url
    - playlisttitles
    - playlist_channel
    - playlist_thumbnails
'''




def save_config():
    '''
    This function saves the current configuration to the config.json file. It gathers the current values of all relevant configuration variables and writes them to the file in JSON format.
    '''
    global CONFIG
    with open(os.path.join(appdata_dir,'JaTubePlayer','config.json'),'w') as f:
        json.dump(CONFIG,f,indent=4)
def load_config():
    global CONFIG
    with open(os.path.join(appdata_dir,'JaTubePlayer','config.json'),'r') as f:
        CONFIG = json.load(f)
load_config()

# ==== async for thumbnail ====
async_task = [] # task to add thumbnail

# ==== others ====

liked_vid_url = []
page_num = 0

# =====playerinit=====

position = 0
scaler_start_seeked= False
player_mode_selector = tk.StringVar()
player_mode_selector.set('continue')
stopthreadevent = threading.Event() 
play_song_while_playing = False

stoped = False # For thread using
pos_for_label = tk.StringVar()
pauseStr = tk.StringVar()
paused = False
finish_break = True

# ==== blur ====
blur_hexColor = tk.StringVar()
blur_window = tk.BooleanVar()
blur_window.set(CONFIG.get('blur'))
blur_hexColor.set(CONFIG.get('blur_hexColor'))
if blur_window.get():blur(hwnd,  hexColor=blur_hexColor.get())  

'''
win32gui.FindWindow(class_name, window_name)
    class_name → we pass None → “I don’t care about the class; match any class.”
    window_name → we pass root.title() → “find the window whose title is exactly this text.”'''


def get_selected_vid(event=None):
    global selected_song_number,star_vid_handle
    try:selected_song_number = playlisttreebox.index(playlisttreebox.selection()[0]) + (media_list_page_controller.current_page -1)*50
    except:pass
    try:
        if star_vid_handle.search(media_data_list.vid_url[selected_song_number]):
            star_btn_ui_functions.star_starred()
        else:
            star_btn_ui_functions.star_regular()
    except:pass

class star_btn_ui_functions:
    @staticmethod
    def star_regular():
        ui_queue.put(lambda: star_btn.configure(
            text='☆',
            fg_color='#3A3A3A',
            hover_color='#505050',
            text_color='#B0B0B0',
            font=('Segoe UI', 14.5, 'bold')
        ))
    @staticmethod
    def star_starred():
        ui_queue.put(lambda: star_btn.configure(
            text='★',
            fg_color='#D4A017',
            hover_color='#E8B820',
            text_color='#FFFDE7',
            font=('Segoe UI', 14.5, 'bold')
        ))

class Chrome_ext_server_ui_functions:
    '''
    for both ChromeExtServer and dnd_winsys
    '''
    @staticmethod
    def direct_url(reset_star = True):
        global playing_vid_mode,selected_song_number

        playing_vid_mode = 3
        selected_song_number = None
        if reset_star:
            star_btn_ui_functions.star_regular()

        insert_textbox(playlist_name_textbox, "Direct URL")
    @staticmethod
    def show_star_video():
        get_starred_vid()
    @staticmethod
    def get_playing_vid_mode()->int:
        '''
        check the playing_vid_mode\n
        function for ChromeExtensionServer
        '''
        return playing_vid_mode
    @staticmethod
    def add_to_end():
        global playing_vid_mode,selected_song_number,star_vid_handle
   

        if playing_vid_mode ==0 or playing_vid_mode == 3 or playing_vid_mode == 4:
            try:
                modetitle = playlist_name_textbox.get("1.0", "end").strip()

                ui_queue.put(lambda: playlist_name_textbox.configure(state="normal"))
                if "[with added video]" not in modetitle:
                    ui_queue.put(lambda mt=modetitle: (
                        playlist_name_textbox.delete(1.0, tk.END),
                        playlist_name_textbox.insert(tk.END, f"{mt} [with added video]")
                    ))
                ui_queue.put(lambda: playlist_name_textbox.configure(state="disabled"))


                if playing_vid_mode == 3:
                    #add to end in direct url mode, we need to switch to youtube mode to add to playlist
                    playing_vid_mode = 0
                    selected_song_number = None

                ToastNotification().notify(app_id="JaTubePlayer", 
                                            title=f'JaTubePlayer {ver}', 
                                            msg='Added video to playlist\nFetching data...', 
                                            duration='short', 
                                            icon=icondir)
                               
            except Exception as e:
                log_handle(
                    content=f"Error adding video to playlist: {e}",
                    errtype='error',
                    component='playlist',
                )
                messagebox.showerror(f'JaTubePlayer {ver}', f"Failed to add video to playlist.\nError: {e}")    
        else:
            ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}', "You are in local media mode, cannot add video to playlist.\nYou can star the video to add it to the starred list, then go to starred mode to watch it."))

class dnd_ui_functions:
    @staticmethod
    def single_file():
        global playing_vid_mode,selected_song_number
        playing_vid_mode = 1
        selected_song_number = 0
        star_btn_ui_functions.star_regular()
        insert_textbox(playlist_name_textbox, "[Drag&Drop] Single file")

    @staticmethod
    def folder_and_files():
        global playing_vid_mode,selected_song_number
        playing_vid_mode = 2
        selected_song_number = None
        star_btn_ui_functions.star_regular()
        insert_textbox(playlist_name_textbox, "[Drag&Drop] Folder/Multiple Files")
    


class AccountInfo:
    def __init__(self):
        self.account_name = ''
        self.account_avator_url = '' 
        self.clear_account_info()

    async def _get_avator_pic(self)->CTkImage|None:
        '''55
        use aiohttp to get the avator pic and return a CTkImage object
        '''
        if self.account_avator_url != '':
            async with aiohttp.ClientSession() as session:
                async with session.get(self.account_avator_url) as response:
                    imgdata = await response.read()
                    img = Image.open(io.BytesIO(imgdata))
                    img = img.resize(
                        (int(39 * tkinter_scaling / 1.25), int(39 * tkinter_scaling / 1.25)),
                        Image.LANCZOS
                )
                
                return CTkImage(light_image=img, size=img.size)
        else:
            return None


    def set_account_avator(self,force:bool = False)->None:
        '''
        use self.account_avator_url to get the avator pic and set it to google_status_profile_pic_label
        '''
        from utils.parser import innertube_parser
        try:
            payload = account_innertube_handler.preInit_buildPayload("home",
                                                                    use_matching_page=True,
                                                                    force = force)         
            if not payload:
                messagebox.showerror(f'JaTubePlayer {ver}', "Failed to build payload for account info. Please check the log for more details.")
                log_handle(
                    content="Failed to build payload for account info",
                    errtype='error',
                    component='account',
                )
                return                                     
            account_response = account_innertube_handler.get_innertube_response(payload=payload, 
                                                                            get_account=True)
            parsed_account_info = innertube_parser().parse_account_info(account_response)
            self.account_name, self.account_avator_url = parsed_account_info.get("name"), parsed_account_info.get("thumb")

            if self.account_name != '' and self.account_avator_url != '':
                
                avator_pic = asyncio.run(self._get_avator_pic())
                ui_queue.put(lambda: google_status_profile_pic_label.configure(image=avator_pic))
                insert_textbox(google_status_text, self.account_name)
                google_status_text.configure(text_color = "#d4d4d4")
        except Exception as e:
            log_handle(
                content=f"Failed to get account avator: {e}",
                errtype='error',
                component='account',
            )
            self.account_avator_url = ''
            self.clear_account_info()

    def clear_account_info(self):
        self.account_name = ''
        self.account_avator_url = ''
        ui_queue.put(lambda: google_status_profile_pic_label.configure(image=None))
        insert_textbox(google_status_text, "No login yet!")
        google_status_text.configure(text_color = "#777777")




def insert_textbox(widget:ctk.CTkTextbox,
                   text:str,
                   disabled_widget:bool=True):
    ui_queue.put(lambda: widget.configure(state='normal'))
    ui_queue.put(lambda: widget.delete(1.0, tk.END))
    ui_queue.put(lambda: widget.insert(tk.END, text))
    if disabled_widget:
        ui_queue.put(lambda: widget.configure(state='disabled'))

        
def _switch_local_server(mode:int)->None|str:
    '''
    mode: 0=start ,1=stop

    This function is used to start/stop the local server for chrome extension communication
    This function includes CONFIG and bool var setting_run_chrome_extension_server update
    '''
    global chrome_extension_flask_thread,setting_run_chrome_extension_server
    if mode == 0:


        try:
            chrome_extension_flask_thread = threading.Thread(daemon = True,target=lambda:chrome_extension_flask.run_flask_app(icondir=icondir))
            chrome_extension_flask_thread.start()
            setting_run_chrome_extension_server.set(True)
            try:
                root.after(0, chrome_ext_status_run)
            except:pass

            
        except Exception as e:
            return str(e)
        
    elif mode == 1:
        log_handle(
            content="Shutting down local server for chrome extension communication...",
            errtype='info',
            component='account',
        )
        try:
            setting_run_chrome_extension_server.set(False)
            chrome_extension_flask.shutdown(icondir=icondir)
            try:
                root.after(0, chrome_ext_status_close)
            except:pass
        except Exception as e:
            return str(e)
        
    CONFIG["run_flask"] = setting_run_chrome_extension_server.get()
    save_config()

def video_info_frame_main(mode:int):
    global info
    info = vid_info_frame(mode,
                          log_handle=log_handle,
                          playing_vid_mode=playing_vid_mode,
                          selected_song_number=selected_song_number,
                          ui_queue=ui_queue,
                          ver=ver,
                          messagebox=messagebox,
                          root=root,
                          icondir=icondir,
                          playing_vid_info_dict=playing_vid_info_dict,
                          vid_url = media_data_list.vid_url,
                          get_info_loader = get_info_loader,
                          blur_window = blur_window,
                          blur_hexColor = blur_hexColor)
    


def setting_frame():
    global maxresolutioncombobox,setting,setting_closed,init_playlist_combobox,subtitlecombobox
    setting_btn.configure(state="disabled")
    root.after(200, lambda: setting_btn.configure(state="normal"))
    try:
        if setting and setting.winfo_exists():
            setting.deiconify()
            setting.lift()
            setting.iconbitmap(icondir) # Ensure icon is set even when window already exists
        else: 
            raise Exception("Settings window does not exist")
    except:
        
        setting = ctk.CTkToplevel(root,fg_color='#242424')
        setting.title('settings')
        setting_frame_wdith = 720*current_ctk_scaling
        setting_frame_height = 500*current_ctk_scaling
        setting.geometry(f"{setting_frame_wdith}x{setting_frame_height}")
        setting.resizable(False, False)
        formats = tk.IntVar()
        formats.set(-1)
        #setting.resizable(False, False)
        setting_closed = False
        root.after(800, lambda: (setting.lift(), setting.iconbitmap(icondir)))
        if blur_window.get():blur(win32gui.FindWindow(None,setting.title()),  hexColor=blur_hexColor.get())

        setting_tab = ctk.CTkTabview(setting, width=700, height=500,fg_color='#242424')
        setting_tab.grid(row=0, column=0, padx=0, pady=20, sticky="nsew")

        user_playlist_id_list = []
        user_playlists_name= []

       
        @check_internet
        def google_login_setting():
            try:
                googlelogin_btn.configure(state="disabled")
                if not account_handler.Start_wv_process(0):
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Failed to login, please check the log for more details'))
                    ui_queue.put(lambda: messagebox.showwarning(f'JaTubePlayer {ver}','since login failed, we have logged out the previous account if logged in, please login again'))
                    google_logout_setting()
                    return
            except Exception as e:
                log_handle(
                    content=f" err:{e}",
                    errtype="error",
                    component="google_login_setting"
                )
            finally:
                googlelogin_btn.configure(state='normal')
        def google_logout_setting():
            try:
                googlelogout_btn.configure(state="disabled")
                if not account_handler.clear_login_data(cookie_only=True):
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Failed to clear login data, please check the log for more details'))
                    return
                account_info_handler.clear_account_info()
                innertube_handler.clear_header()
                account_innertube_handler.clear_header()
            except Exception as e:
                log_handle(
                    content=f" err:{e}",
                    errtype="error",
                    component="google_logout_setting"
                )
            finally:
                googlelogout_btn.configure(state='normal')

        def deletesyskey():
            try:
                deletesyskey_btn.configure(state="disabled")
                if messagebox.askyesno(f'JaTubePlayer {ver}','This will delete the system key and all login data, including cookies and AES key\nAre you sure?'):
                    if not account_handler.clear_login_data(cookie_only=False):
                        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Failed to clear login data, please check the log for more details'))
                        return
                    account_info_handler.clear_account_info()
                    innertube_handler.clear_header()
                    account_innertube_handler.clear_header()
            except Exception as e:
                log_handle(
                    content=f" err:{e}",
                    errtype="error",
                    component="delete sys key setting"
                )
            finally:
                deletesyskey_btn.configure(state='normal')
            
        @check_internet
        def get_resolution_setting():

            if playing_vid_mode == 0 or playing_vid_mode == 4:
                if playing_vid_mode == 4 and not media_data_list.vid_url[selected_song_number].startswith(('https://','http://')):
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','The selected video is a local file, downloading is not supported'))
                    return
                try:
                    if selected_song_number != None:
                        ui_queue.put(lambda: resolution_title.configure(text='⏳ Loading resolutions...'))
                        ui_queue.put(lambda: get_resoltion_btn.configure(state='disabled'))

                        res = get_resoltion(target_url=media_data_list.vid_url[selected_song_number],
                                            loader=get_info_loader)
                        
                        ui_queue.put(lambda r=res: resoltion_combox.configure(values=r))
                        ui_queue.put(lambda: resoltion_combox._open_dropdown_menu())
                        ui_queue.put(lambda: resolution_title.configure(text='Video Resolution'))
                    else:
                        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','selected a video first'))

                except Exception as e:log_handle(
                                          content=str(e),
                                          errtype='error',
                                          component='download',
                                      )
                finally:
                    ui_queue.put(lambda: get_resoltion_btn.configure(state='normal'))
            elif playing_vid_mode == 3:
                try:
                    ui_queue.put(lambda: resolution_title.configure(text='⏳ Loading resolutions...'))
                    ui_queue.put(lambda: get_resoltion_btn.configure(state='disabled'))

                    res = get_resoltion(target_url=playing_vid_info_dict.get('original_url'), 
                                        loader=get_info_loader)
                    
                    ui_queue.put(lambda r=res: resoltion_combox.configure(values=r))
                    ui_queue.put(lambda: resoltion_combox._open_dropdown_menu())
                    ui_queue.put(lambda: resolution_title.configure(text='Video Resolution'))

                except Exception as e :log_handle(
                                           content=str(e),
                                           errtype='error',
                                           component='download',
                                       )
                finally:
                    ui_queue.put(lambda: get_resoltion_btn.configure(state='normal'))
                
            else:
                   
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','You cant download local file !'))
                


        def download_select_mode_setting(mode : int):
            """
            mode: 0 = mp3 , 1 = MP4
            """
            if mode == 0:
                resoltion_combox.configure(state='disabled')
                get_resoltion_btn.configure(state='disabled')
            elif mode == 1:
                resoltion_combox.configure(state='normal')
                get_resoltion_btn.configure(state='normal')
            

        @check_internet
        def download_to_loacl_setting():
            if is_downloading.get():
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Another download is in progress, please wait until it finishes'))
                return
            else:

                ui_queue.put(lambda: downloadselectedsong.configure(state = "disabled"))
                is_downloading.set(True)
                _vid_url = list(media_data_list.vid_url)
                _playlisttitles = list(media_data_list.playlisttitles)
                _dict = dict(playing_vid_info_dict) if playing_vid_info_dict else {}
                _selected_idx = selected_song_number
                if not playing_vid_mode == 1 and not playing_vid_mode == 2:
                    
                    if formats.get() == -1:
                        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please select resolution and format first'))
                        is_downloading.set(False)
                        return
                    if playing_vid_mode == 0 or playing_vid_mode == 4:
                        if _selected_idx == None:
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please select a video first'))
                            is_downloading.set(False)
                            return
                        if resoltion_combox.get() != '' and resoltion_combox.get().isdigit() and int(resoltion_combox.get()) >=144:pass
                        else:
                            if formats.get() == 1:
                                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please select a valid resolution first'))
                                is_downloading.set(False)
                                return
                        if _vid_url[_selected_idx].startswith(('https://','http://')):
                            ToastNotification().notify(
                            title=f"JaTubePlayer {ver}",
                            msg="Preparing to download...\n Checking video valiability and fetching info",
                            icon=icondir,
                            )
                            log_handle(
                                content=f"Start fetching video info for downloading, url: {_vid_url[_selected_idx]}",
                                errtype='info',
                                component='download',
                            )
                            _,info_dict = get_info(loader=get_info_loader,
                                            target_url=_vid_url[_selected_idx],
                                            )
                            log_handle(
                                content=f"Finished fetching video info for downloading, info: {info_dict}",
                                errtype='info',
                                component='download',
                            )
                            if not info_dict:
                                log_handle(
                                    content="Failed to fetch video information for download",
                                    errtype="error",
                                    component="download",
                                )
                                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Failed to fetch video info, the video may be unavailable or private\nPlease check the log for more details'))
                                is_downloading.set(False)
                                return
                            if info_dict.get('live_status') == "is_live":
                                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Live video downloading is not supported'))
                                is_downloading.set(False)
                                return
                            else:
                                url = _vid_url[_selected_idx]
                                title = _playlisttitles[_selected_idx]
                        else:
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','The selected video is a local file, downloading is not supported'))
                            is_downloading.set(False)
                            return
                    
                    elif playing_vid_mode == 3:
                        if formats.get() == 1 :
                            if resoltion_combox.get() != '' and resoltion_combox.get().isdigit() and int(resoltion_combox.get()) >=144:pass
                            else:
                                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please select a valid resolution first'))
                                is_downloading.set(False)
                                return
                        if _dict.get('live_status') == 'is_live':
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Live video downloading is not supported'))
                            is_downloading.set(False)
                            return
                        else:
                            url = _dict.get('original_url')
                            title = _dict.get('title','unknown_title')
                    if download_path.get() != '[appdata]/JaTubePlayer/saved_file':
                        if not os.path.exists(download_path.get()):
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','The specified download path does not exist'))
                            is_downloading.set(False)
                            return
                    ui_queue.put(lambda: downloadselectedsong.configure(state = "disabled"))


                    download_to_local(
                        res=resoltion_combox.get(),
                        mode=formats.get(),
                        cookie=account_handler.get_cookie() if ytdlp_use_cookie.get() else None,
                        yt_dlp=yt_dlp,
                        target_vid_url=url,
                        title=title,
                        download_path=download_path.get(),
                        _internal_dir=_internal_dir,
                        icondir=icondir,
                        ver=ver,
                        root=root,   
                        appdata_dir=appdata_dir,
                        ytdlp_log_handle=ytdlp_log_handle,
                        is_downloading = is_downloading,
                        deno_path=deno_exe,
                        ctk_messagebox=messagebox,
                        log_handle=log_handle
                        )
                    log_handle(
                        content=f"downloaded {title  }",
                        errtype='info',
                        component='download',
                    )
                    
                    time.sleep(2)
                    ui_queue.put(lambda: downloadselectedsong.configure(state = "normal"))
                    ui_queue.put(lambda: downloadhooktext.set(''))
                else:
                    
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','You cant download local file !'))
                    

            
        @check_internet
        def updateplaylists():
            updateuserplaylists_btn.configure(text='⏳ loading...')
            get_user_playlists(forcereload=True)
            updateuserplaylists_btn.configure(text='update Playlist ')

        def remove_selected_from_playlist_setting():
            global selected_song_number,media_data_list
            if selected_song_number is None:
                messagebox.showerror(f'JaTubePlayer {ver}', 'No item selected in the playlist!')
                return
            if selected_song_number == media_list_page_controller.media_data_list.current_playing_idx_num:
                messagebox.showerror(f"JatubePlayer {ver}",
                                      "You cannot remove the current playing item!")
                return
            try:
                item_id = playlisttreebox.get_children()[selected_song_number%50]
                media_list_page_controller.clear_selected(selected_idx=selected_song_number, 
                                                          selected_tree_ID=item_id)
                media_data_list = media_list_page_controller.media_data_list
                selected_song_number = None

            except Exception as e:
                log_handle(
                    content=f"Failed to remove selected playlist item: {e}",
                    errtype="error",
                    component="playlist",
                )
                messagebox.showerror(f'JaTubePlayer {ver}', f'Failed to remove item from playlist:\n{e}')

        def leave():
            global setting_closed
            
            setting_closed = True

            setting.destroy()
        setting.protocol('WM_DELETE_WINDOW',leave)

        def save_autovercheck_option_ver(event = None):
            CONFIG['vercheck'] = auto_check_ver.get()
            save_config()

        def setting_init_toggle_quickstartup():
            '''
            change widget based on the stats of the main check btn
            '''
            global init_toggle_quickstartup
            if init_toggle_quickstartup.get():
                init_search_btn.configure(state='normal')
                init_playlist_btn.configure(state='normal')
                init_local_folder_btn.configure(state='normal')

                init_search_entry.configure(state='disabled')
                init_search_set_btn.configure(state='disabled')
                init_select_local_folder_btn.configure(state='disabled')

                init_yt_playlist_btn.configure(state='disabled')
                init_playlist_like_btn.configure(state='disabled')
                init_playlist_sub_btn.configure(state='disabled')
                init_playlist_recommendation_btn.configure(state='disabled')
                init_playlist_combobox.configure(state='disabled')
                init_get_playlist_btn.configure(state='disabled')
                init_playlist_set_btn.configure(state='disabled')

                if init_quickstartup_mode.get() == 'search':
                    init_search_select()
                elif init_quickstartup_mode.get() == 'playlist':
                    init_playlist_select()
                elif init_quickstartup_mode.get() == 'local_playlist':
                    init_local_playlist()
            else:
                CONFIG["quickstartup_init"]['mode']=0
                save_config()
                init_quickstartup_mode.set('')
                init_quickstartup_playlist_mode.set('')
                init_playlist_combobox.set('')
                init_search_entry.delete(0,tk.END)

                init_search_btn.configure(state='disabled')
                init_search_entry.configure(state='disabled')
                init_search_set_btn.configure(state='disabled')
                init_playlist_btn.configure(state='disabled')
                init_local_folder_btn.configure(state='disabled')
                init_select_local_folder_btn.configure(state='disabled')

                init_yt_playlist_btn.configure(state='disabled')
                init_playlist_like_btn.configure(state='disabled')
                init_playlist_sub_btn.configure(state='disabled')
                init_playlist_recommendation_btn.configure(state='disabled')
                init_playlist_combobox.configure(state='disabled')
                init_get_playlist_btn.configure(state='disabled')
                init_playlist_set_btn.configure(state='disabled')

        def init_search_select(event=None):
            init_search_entry.configure(state='normal')
            init_search_set_btn.configure(state='normal')
            init_select_local_folder_btn.configure(state='disabled')

            init_quickstartup_playlist_mode.set('')
            init_yt_playlist_btn.configure(state='disabled')
            init_playlist_like_btn.configure(state='disabled')
            init_playlist_sub_btn.configure(state='disabled')
            init_playlist_recommendation_btn.configure(state='disabled')
            init_playlist_combobox.configure(state='disabled')
            init_get_playlist_btn.configure(state='disabled')
            init_playlist_set_btn.configure(state='disabled')

        def init_playlist_select(event=None):
            init_search_entry.configure(state='disabled')
            init_search_set_btn.configure(state='disabled')
            init_select_local_folder_btn.configure(state='disabled')

            init_yt_playlist_btn.configure(state='normal')
            init_playlist_like_btn.configure(state='normal')
            init_playlist_sub_btn.configure(state='normal')
            init_playlist_recommendation_btn.configure(state='normal')

            if init_quickstartup_playlist_mode.get() == 'yt_playlist':
                init_yt_playlist_select()
            else:
                init_playlist_combobox.configure(state='disabled')
                init_get_playlist_btn.configure(state='disabled')
                init_playlist_set_btn.configure(state='disabled')

        def init_yt_playlist_select():
            init_playlist_combobox.configure(state='readonly')
            init_get_playlist_btn.configure(state='normal')
            init_playlist_set_btn.configure(state='normal')

        def init_playlist_like_select():
            init_playlist_combobox.configure(state='disabled')
            init_get_playlist_btn.configure(state='disabled')
            init_playlist_set_btn.configure(state='disabled')
            init_playlist_set()

        def init_playlist_sub_select():
            init_playlist_combobox.configure(state='disabled')
            init_get_playlist_btn.configure(state='disabled')
            init_playlist_set_btn.configure(state='disabled')
            init_playlist_set()

        def init_playlist_recommendation_select():
            init_playlist_combobox.configure(state='disabled')
            init_get_playlist_btn.configure(state='disabled')
            init_playlist_set_btn.configure(state='disabled')
            init_playlist_set()

        def init_search_set():
            CONFIG["quickstartup_init"]['mode'] = 1
            CONFIG["quickstartup_init"]['searchmode_keyword'] = init_search_entry.get()
            save_config()
            messagebox.showinfo(f'JaTubePlayer {ver}',f'Quick startup init search keyword set to: {init_search_entry.get()}')

        @check_internet
        def init_playlist_get():
            nonlocal user_playlist_id_list
            if not account_handler.check_aes_key():
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Invalid AES key, please clear account data and restart the app'))
                return
                
            if account_handler.check_cookie_exist() == False:
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','please set your login first'))
                return
            ui_queue.put(lambda: init_get_playlist_btn.configure(state='disabled'))
            def _get_user_playlists_thread():
                nonlocal user_playlist_id_list,user_playlists_name
                user_playlists_name = []
                user_playlist_id_list = []
                media_list_page_controller.youtube_init_and_reload(media_data_list=media_data_list, page=playlist_type.PLAYLISTS)
                for playlist_dict in media_list_page_controller.user_playlist_dict_list:
                    user_playlists_name.append(playlist_dict['name'])
                    user_playlist_id_list.append(playlist_dict['url'])
                ui_queue.put(lambda: init_playlist_combobox.configure(values=user_playlists_name))
                ui_queue.put(lambda: init_playlist_combobox.set(''))
                ui_queue.put(lambda: init_playlist_combobox._open_dropdown_menu())

                ui_queue.put(lambda: init_get_playlist_btn.configure(state='normal'))
            threading.Thread(target=_get_user_playlists_thread, daemon=True).start()
            
        def init_playlist_set():
            nonlocal user_playlist_id_list,user_playlists_name
            selected_playlist_id = ''
            selected_playlist_name = ''
            match init_quickstartup_playlist_mode.get():
                case "yt_playlist":
                    selected_idx = user_playlists_name.index(init_playlist_combobox.get())
                    selected_playlist_id = user_playlist_id_list[selected_idx]
                    selected_playlist_name = user_playlists_name[selected_idx]
                case "like":
                    selected_playlist_id = 'like'
                    selected_playlist_name = 'Liked Videos'
                case "sub":
                    selected_playlist_id = 'sub'
                    selected_playlist_name = 'Subscriptions'
                case "home":
                    selected_playlist_id = 'home'
                    selected_playlist_name = 'Recommendations'
                case _:
                    messagebox.showerror(f'JaTubePlayer {ver}','Please select a playlist type first')
                    return
            CONFIG["quickstartup_init"]['mode'] = 2
            CONFIG["quickstartup_init"]['playlistmode_playlist_ID'] = selected_playlist_id
            CONFIG["quickstartup_init"]['playlistmode_playlist_Name'] = selected_playlist_name
            save_config()
            messagebox.showinfo(f'JaTubePlayer {ver}',f'Quick startup init playlist set to: {selected_playlist_name}')

        def init_local_playlist(event=None):
            init_search_entry.configure(state='disabled')
            init_search_set_btn.configure(state='disabled')
            init_select_local_folder_btn.configure(state='normal')

            init_quickstartup_playlist_mode.set('')
            init_yt_playlist_btn.configure(state='disabled')
            init_playlist_like_btn.configure(state='disabled')
            init_playlist_sub_btn.configure(state='disabled')
            init_playlist_recommendation_btn.configure(state='disabled')
            init_playlist_combobox.configure(state='disabled')
            init_get_playlist_btn.configure(state='disabled')
            init_playlist_set_btn.configure(state='disabled')

        def init_select_local_folder():
            CONFIG["quickstartup_init"]['mode'] = 3
            folder_path = filedialog.askdirectory()
            if folder_path:
                CONFIG["quickstartup_init"]['localfoldermode_folder_Path'] = folder_path
                save_config()
                messagebox.showinfo(f'JaTubePlayer {ver}', f'Local folder set to: {folder_path}')
            else:
                messagebox.showwarning(f'JaTubePlayer {ver}', 'No folder selected. Please select a folder to use this mode.')



        def switch_flask_server():
            global chrome_extension_flask_thread
            if setting_run_chrome_extension_server.get():
                chrome_extension_server_checkbtn.configure(state='disabled')
                _switch_local_server(0)

                root.after(2000,lambda:chrome_extension_server_checkbtn.configure(state='normal'))
            else:
                chrome_extension_server_checkbtn.configure(state='disabled')
                
                if _switch_local_server(1) :
                    log_handle(
                        content="Failed to stop the Chrome extension server",
                        errtype="error",
                        component="chrome_ext",
                    )
                    messagebox.showerror(f'JaTubePlayer {ver}','Failed to stop the chrome extension server')
                
                root.after(2000,lambda:chrome_extension_server_checkbtn.configure(state='normal'))

        def save_chrome_extension_port_setting():
            if not chrome_extension_port_textbox.get().isdigit():
                messagebox.showerror(f'JaTubePlayer {ver}','Please enter a valid port number (1024-65535)')
                return
            if int(chrome_extension_port_textbox.get()) < 1024 or int(chrome_extension_port_textbox.get()) > 65535:
                messagebox.showerror(f'JaTubePlayer {ver}','Please enter a valid port number (1024-65535)')
                return
            CONFIG['chrome_ext_server_port'] = int(chrome_extension_port_textbox.get())
            save_config()

            if setting_run_chrome_extension_server.get():
                messagebox.showinfo(f'JaTubePlayer {ver}','Port number changed, please restart the chrome extension server for the change to take effect')

            messagebox.showinfo(f'JaTubePlayer {ver}',"Please make sure to assign the chrome extension to the same port")
            chrome_extension_flask.server_port = CONFIG['chrome_ext_server_port']

        def save_discord_idle_presence_wording_setting(default=False):
            global discord_presence,discord_idle_presence_wording
            if default:
                discord_idle_presence_wording.set("[Idling & Chillin' like a potato 🥔]")
            else:
                discord_idle_presence_wording.set(discord_idle_presence_wording_textbox.get())
            CONFIG['discord_idle_presence_wording'] = discord_idle_presence_wording.get()
            save_config()
            
            messagebox.showinfo(f'JaTubePlayer {ver}',f'Discord idle presence wording set to: {CONFIG["discord_idle_presence_wording"]}')
            discord_presence.discord_idle_presence_wording = CONFIG['discord_idle_presence_wording']

        def switch_blur_window():
            global blur_window
            CONFIG['blur'] = blur_window.get()
            save_config()
            try:
                if blur_window.get():
                    blur(hwnd, hexColor=blur_hexColor.get()) 
                    blur(win32gui.FindWindow(None,setting.title()), hexColor=blur_hexColor.get())
                    try:blur(win32gui.FindWindow(None,log_handler.log_handle_frame.log_frame.title()), hexColor=blur_hexColor.get())
                    except:pass
                    try:blur(win32gui.FindWindow(None,info.title()), hexColor=blur_hexColor.get())
                    except:pass
                else:
                    blur(hwnd,disable=True)
                    blur(win32gui.FindWindow(None,setting.title()), disable=True)
                    try:blur(win32gui.FindWindow(None,log_handler.log_handle_frame.log_frame.title()), disable=True)
                    except:pass
                    try:blur(win32gui.FindWindow(None,info.title()), disable=True)
                    except:pass
            except Exception as e:
                log_handle(
                    content=str(e),
                    errtype='error',
                    component='settings',
                )    
                
        def max_resolution_select(event=None):
            maxresolution.set(int(maxresolutioncombobox.get()))
            CONFIG["max_resolution"] = maxresolution.get()
            save_config()

        @check_internet
        def update_ytdlp():
            global yt_dlp,utils,ytdlpver
            ui_queue.put(lambda: auto_update_ytdlp_btn.configure(state='disabled'))
            ui_queue.put(lambda: auto_update_ytdlp_btn.configure(text='⏳ updating...'))
            result = ytdlp_updater.download_and_extract_dlp(using_nightly=ytdlp_use_nightly_build.get())
            if not result:
                log_handle(
                    content="yt-dlp update failed or cancelled",
                    errtype="warning",
                    component="settings",
                )
                ui_queue.put(lambda: messagebox.showwarning(f'JaTubePlayer {ver}','ytdlp Update failed or cancelled, please check log file'))
            else:
                messagebox.showinfo(f'JaTubePlayer {ver}',(f'ytdlp Update successful! new version: {result}'
                                                           '\nPlease restart the app to apply the update!'))
                threading.Thread(daemon=True,target=get_version_setting_thread).start()

                ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='New version installed!', duration='short',icon=icondir)
                
            ui_queue.put(lambda: auto_update_ytdlp_btn.configure(state='normal'))
            ui_queue.put(lambda: auto_update_ytdlp_btn.configure(text='update yt-dlp'))

        def switch_audio_only():
            if audio_only.get():
                try:player["vid"] = "no"
                except:pass
            else:
                try:player["vid"] = "auto"
                except:pass

        def autofullscreen_setting():
            CONFIG['open_with_fullscreen'] = open_with_fullscreen.get()
            save_config()

        def switch_show_cache():
            CONFIG['show_cache'] = show_cache.get()
            save_config()

        def switch_hover_fullscreen():
            CONFIG['hover_fullscreen'] = hover_fullscreen.get()
            save_config()

        def _save_cache_settings():
            CONFIG['cache']['demuxer_max_bytes'] = int(demuxer_max_bytes.get())
            CONFIG['cache']['demuxer_max_back_bytes'] = int(demuxer_max_back_bytes.get())
            CONFIG['cache']['cache_pause_wait'] = int(cache_pause_wait.get())
            CONFIG['cache']['audio_wait_open'] = int(audio_wait_open.get())
            save_config()

        def _demuxer_max_bytes_slider_change(value):
            demuxer_max_bytes.set(int(float(value)))
            demuxer_max_bytes_value_label.configure(text=f'{demuxer_max_bytes.get()}M')

        def _demuxer_max_back_bytes_slider_change(value):
            demuxer_max_back_bytes.set(int(float(value)))
            demuxer_max_back_bytes_value_label.configure(text=f'{demuxer_max_back_bytes.get()}M')

        def _cache_pause_wait_slider_change(value):
            cache_pause_wait.set(float(value))
            cache_pause_wait_value_label.configure(text=f'{cache_pause_wait.get():.1f}s')

        def _audio_wait_open_slider_change(value):
            audio_wait_open.set(int(value))
            audio_wait_open_value_label.configure(text=f'{audio_wait_open.get()}s')

        def _apply_cache_slider_settings(event=None):
            _save_cache_settings()

        def subtitle_combobox_callback(event):
            subtitle_selection_idx.set(subtitlecombobox.cget('values').index(subtitlecombobox.get()))
            log_handle(
                content=f'selected subtitle idx{subtitle_selection_idx.get()}',
                errtype='info',
                component='settings',
            )
            if subtitle_selection_idx.get() != 0:
                try:player.sub_add(subtitle_urllist[subtitle_selection_idx.get()-1])
                except:pass
            else:
                try:player["sid"] = 'no'
                except:pass

        def switch_discord_presence():
            CONFIG['enable_discord_presence'] = enable_discord_presence.get()
            save_config()
            if enable_discord_presence.get():
                discord_presence.idle()
                ui_queue.put(lambda: discord_presence_show_playing_btn.configure(state='normal'))
                try:
                    global playing_vid_info_dict
                    
                    if playing_vid_mode ==0 or playing_vid_mode ==3:
                        if discord_presence_show_playing.get():
                            discord_presence.update(song_title=playing_vid_info_dict['title'])
                        else:discord_presence.idle()
                    elif playing_vid_mode ==1 or playing_vid_mode ==2:
                        if discord_presence_show_playing.get():
                            discord_presence.update(song_title="A local media file :)")
                        else:discord_presence.idle()
                    elif playing_vid_mode ==4:
                        if discord_presence_show_playing.get():
                            if media_data_list.vid_url[selected_song_number].startswith(('https://','http://')):
                                discord_presence.update(song_title=media_data_list.playlisttitles[selected_song_number])
                            else:
                                discord_presence.update(song_title="A local media file :)")
                        else:discord_presence.idle()
                    else:raise Exception("No title found")
                except Exception as e:
                    log_handle(
                        content=str(e),
                        errtype='error',
                        component='settings',
                    )
                    discord_presence.idle()
            else:
                ui_queue.put(lambda: discord_presence_show_playing_btn.configure(state='disabled'))
                discord_presence.clear()
            ui_queue.put(lambda: enable_discord_presence_btn.configure(state='disabled'))
            time.sleep(3)
            try:ui_queue.put(lambda: enable_discord_presence_btn.configure(state='normal'))
            except:pass

        
        def switch_discord_presence_show_playing():
            CONFIG['discord_presence_show_playing'] = discord_presence_show_playing.get()
            if not discord_presence_show_playing.get():discord_presence.idle()
            else:threading.Thread(target=switch_discord_presence,daemon=True).start()
            
            save_config()

        def set_force_stop_loading():
            global force_stop_loading,loadingvideo
            if loadingvideo:force_stop_loading = True


        def set_keymem_setting_thread():
            '''
            Run this in a thread to avoid blocking the main UI
            '''
            if hotkey_set_keymem_function_combobox.get():
                ui_queue.put(lambda: setting.iconify())
                fun_name = hotkey_set_keymem_function_combobox.get()
                KeyMemHotkey.set_keymem(fun_name)
                
                while KeyMemHotkey.is_setting_keymem:
                    time.sleep(0.1)
                if KeyMemHotkey.newhotkey:
                    CONFIG['keyboard_hotkeys'][fun_name] = KeyMemHotkey.newhotkey
                save_config()
                load_config()
                ui_queue.put(lambda: setting.deiconify())
                threading.Thread(daemon=True,target=get_hotkey_setting_thread).start()
                if KeyMemHotkey.newhotkey:ToastNotification().notify(app_id="JaTubePlayer", 
                                            title=f'JaTubePlayer {ver}', 
                                            msg=f'Hotkey for {fun_name} set to {KeyMemHotkey.newhotkey}', 
                                            duration='short', 
                                                icon=icondir)
                else:
                    ToastNotification().notify(app_id="JaTubePlayer", 
                                                title=f'JaTubePlayer {ver}', 
                                                msg=f'Since nothing was pressed, the hotkey setting for {fun_name} was cancelled', 
                                                duration='short', 
                                                    icon=icondir)
            else:messagebox.showerror(f'JaTubePlayer {ver}','Please select a function first')

        def set_keymem_default_setting():
            '''
            Set ALL of them to default
            '''
            try:
                KeyMemHotkey.destory_global_hotkeys()
            except:pass
            if messagebox.askyesno(f'JaTubePlayer {ver}','This will reset ALL hotkeys to default\nProcceed?'):
                CONFIG['keyboard_hotkeys'] = {
                        "play_pause": "<ctrl>+<shift>+p",      
                        "next": "<ctrl>+<shift>+n",         
                        "previous": "<ctrl>+<shift>+b",        
                        "stop": "<ctrl>+<shift>+s",        
                        "mode_repeat": "<ctrl>+<shift>+r",    
                        "mode_continuous": "<ctrl>+<shift>+c", 
                        "mode_random": "<ctrl>+<shift>+x",     
                        "volume_up": "<ctrl>+<shift>+<up>",    
                        "volume_down": "<ctrl>+<shift>+<down>",
                        "toggle_minimize":"<ctrl>+<shift>+m"
                    }
                save_config()
                load_config()
                threading.Thread(daemon=True,target=get_hotkey_setting_thread).start()  
                check_keyboard()

        def set_player_speed_setting(event=None):
            try:
                playerspeed_speed_label.configure(text=f'{player_speed.get():.1f}x')
            except Exception as e:
                log_handle(
                    content=str(e),
                    errtype='error',
                    component='settings',
                )
        
        def apply_player_speed_setting(event=None):
            try:
                player.speed = player_speed.get()
            except Exception as e:
                log_handle(
                    content=str(e),
                    errtype='error',
                    component='settings',
                )

        def select_download_path():
            path =filedialog.askdirectory()
            if path:
                CONFIG['download_path'] = path
                download_path.set(path)
                save_config()
                insert_textbox(download_path_textbox, download_path.get())
                
                messagebox.showinfo(f'JaTubePlayer {ver}',f'Download path set to {path}')
            else:messagebox.showinfo(f'JaTubePlayer {ver}','Cancelled!')
            setting.focus_force()

        def reveal_download_path():
            if (os.path.exists(download_path.get()) or 
                download_path.get() == "[appdata]/JaTubePlayer/saved_file"):
                
                try:
                    if download_path.get() == "[appdata]/JaTubePlayer/saved_file":
                        os.startfile(os.path.join(appdata_dir,"JaTubePlayer","saved_file"))
                    else:
                        os.startfile(download_path.get())
                except Exception as e:
                    log_handle(
                        content=str(e),
                        errtype='error',
                        component='settings',
                    )
                    messagebox.showerror(f'JaTubePlayer {ver}',f'Failed to open download path\n{e}')
            else:
                messagebox.showerror(f'JaTubePlayer {ver}','The specified download path does not exist')
            setting.focus_force()

        def set_default_download_path():
            if messagebox.askyesno(f'JaTubePlayer {ver}','This will reset the download path to default\nProcceed?'):
                CONFIG['download_path'] = "[appdata]/JaTubePlayer/saved_file" 
                download_path.set("[appdata]/JaTubePlayer/saved_file")
                save_config()
                insert_textbox(download_path_textbox, download_path.get())
                
                messagebox.showinfo(f'JaTubePlayer {ver}',f'Download path reset to default\n{CONFIG["download_path"]}')
            setting.focus_force()

        def SetFullscreenmode(event=None):
            CONFIG['fullscreenmode'] = fullscreenmode.get()
            save_config()

        def set_gradient_color(default:bool=False):
            global blur_hexColor
            if not default:
                color_picker = AskColor(title="Choose gradient color")
                color_picker.brightness_slider_value.set(50)

                color_picker.update_colors()
                color = color_picker.get()

            else:
                color = "#101010"
            if color:
                CONFIG['blur_hexColor'] = color
                blur_hexColor.set(color)
                save_config()
                try:
                    switch_blur_window()
                except Exception as e:
                    log_handle(
                        content=str(e),
                        errtype='error',
                        component='settings',
                    )
            else:messagebox.showinfo(f'JaTubePlayer {ver}','Cancelled!')

        def setting_switch_ytdlp_use_cookie():
            CONFIG['ytdlp_use_cookie'] = ytdlp_use_cookie.get()
            save_config()

        def save_max_result_count_setting(event=None):
            previous_values = CONFIG.get("max_result_count", {})
            err = False

            try:
                recommendation_value = int(recommendation_result_count_entry.get().strip())
                subscription_value = int(subscription_result_count_entry.get().strip())
                search_value = int(search_result_count_entry.get().strip())
                liked_video_value = int(liked_video_result_count_entry.get().strip())
            except (ValueError, tk.TclError):
                messagebox.showerror(f'JaTubePlayer {ver}', 'Max result counts must be whole numbers')
                log_handle(
                    content="Invalid max result count input type, reverting to previous values",
                    errtype='warning',
                    component='settings',
                )
                err = True
            else:
                if recommendation_value not in range(10, 301):
                    messagebox.showerror(f'JaTubePlayer {ver}','Recommendations result count must be between 10 and 300')
                    err = True
                elif subscription_value not in range(10, 301):
                    messagebox.showerror(f'JaTubePlayer {ver}','Subscriptions result count must be between 10 and 300')
                    err = True
                elif search_value not in range(10, 151):
                    messagebox.showerror(f'JaTubePlayer {ver}','Search result count must be between 10 and 150')
                    err = True
                elif liked_video_value not in range(10, 5001):
                    messagebox.showerror(f'JaTubePlayer {ver}','Liked videos result count must be between 10 and 5000')
                    err = True

            if err:
                new_values = previous_values
                max_recommendation_result_count.set(previous_values.get("Recommendations", 100))
                max_sub_result_count.set(previous_values.get("sub", 100))
                max_search_result_count.set(previous_values.get("search", 100))
                max_like_result_count.set(previous_values.get("like", 5000))
                log_handle(
                    content="Invalid max result count input, reverting to previous values",
                    errtype='warning',
                    component='settings',
                )
            else:
                max_recommendation_result_count.set(recommendation_value)
                max_sub_result_count.set(subscription_value)
                max_search_result_count.set(search_value)
                max_like_result_count.set(liked_video_value)
                new_values = {
                    "Recommendations": recommendation_value,
                    "sub": subscription_value,
                    "search": search_value,
                    "like": liked_video_value,
                }

            CONFIG["max_result_count"] = new_values
            save_config()

            playlist_retriever.maxresults_like = new_values["like"]
            playlist_retriever.maxresults_sub = new_values["sub"]
            playlist_retriever.maxresults_recommendation = new_values["Recommendations"]
            media_list_page_controller.max_search_result_count = new_values["search"]

        def ytdlp_switch_use_nightly_build():
            '''Refresh the displayed release for the selected yt-dlp channel.'''
            use_nightly = ytdlp_use_nightly_build.get()
            CONFIG['ytdlp_use_nightly_build'] = use_nightly
            save_config()

            def _get_selected_ver():
                latest_version = get_latest_dlp_version(using_nightly=use_nightly)
                label = f'Nightly: {latest_version}' if use_nightly else str(latest_version)
                ui_queue.put(lambda value=label: ytdlp_ver_lastest_label.configure(text=value))

            threading.Thread(target=_get_selected_ver, daemon=True).start()


        player_tab = setting_tab.add("Advanced Player setting")
        account_playlist_tab = setting_tab.add("Account & Playlist")
        download_tab = setting_tab.add("Saving")
        quick_init_tab = setting_tab.add("Quick Init")
        external_services_tab = setting_tab.add("External Services")
        version_info_tab = setting_tab.add("Version Info")
        hotkey_tab = setting_tab.add("Hotkeys")

        
        '''
        Columns with weight 0 do not expand when the window grows. Columns with weight > 0 get a share of the extra space.
        The actual extra width each weighted
        '''
        account_playlist_tab.grid_columnconfigure(0, weight=1)
        account_playlist_tab.grid_columnconfigure(1, weight=1)
        account_playlist_tab.grid_rowconfigure(0, weight=1)

        account_playlist_scroll_frame = ctk.CTkScrollableFrame(
            account_playlist_tab,
            width=680,
            height=380,
            fg_color='#242424',
        )
        account_playlist_scroll_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
        account_playlist_scroll_frame.grid_columnconfigure(0, weight=1)
        account_playlist_scroll_frame.grid_columnconfigure(1, weight=1)

        player_tab.grid_columnconfigure(0, weight=1)
        player_tab.grid_columnconfigure(1, weight=1)
    
        
        download_tab.grid_columnconfigure(0, weight=1)
        download_tab.grid_columnconfigure(1, weight=1)

        external_services_tab.grid_columnconfigure(0, weight=1)
        external_services_tab.grid_rowconfigure(0, weight=1)
        
        version_info_tab.grid_columnconfigure(0, weight=1)
        version_info_tab.grid_columnconfigure(1, weight=1)

        quick_init_tab.grid_columnconfigure(0, weight=1)
        quick_init_tab.grid_columnconfigure(1, weight=1)
        quick_init_tab.grid_rowconfigure(1, weight=0)
        quick_init_tab.grid_rowconfigure(2, weight=0)


        # ══════════ Account & Playlist — Card-style sections ══════════
        youtube_data_frame = ctk.CTkFrame(account_playlist_scroll_frame, fg_color='#2B2B2B', corner_radius=8)
        youtube_data_frame.grid_columnconfigure(0, weight=1)
        youtube_data_frame.grid_columnconfigure(1, weight=1)
        
        google_account_frame = ctk.CTkFrame(account_playlist_scroll_frame, fg_color='#2B2B2B', corner_radius=8)
        google_account_frame.grid_columnconfigure(0, weight=1)
        google_account_frame.grid_columnconfigure(1, weight=1)
        google_account_frame.grid_columnconfigure(2, weight=1)
        
        # YouTube Data Section
        youtube_title = ctk.CTkLabel(youtube_data_frame, text='  \u25b8 YouTube Data', font=('Arial', 15, 'bold'), text_color='#FF6B8A', anchor='w')
        updateuserplaylists_btn = ctk.CTkButton(youtube_data_frame, text='Update Playlists', width=160, command=updateplaylists,
                                                 text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')

        result_count_separator = ctk.CTkFrame(youtube_data_frame, height=1, fg_color='#4A4A4A')
        result_count_title = ctk.CTkLabel(youtube_data_frame, text='  \u25b8 Maximum Results', font=('Arial', 15, 'bold'), text_color='#80C8E0', anchor='w')
        result_count_note = ctk.CTkLabel(
            youtube_data_frame,
            text='NOTE: Recommendations/subscriptions: 10–300  •  Search: 10-150 •  Liked videos: 10–5,000.\n'
                 'press [Enter] to apply.',
            height=56, font=('Arial', 14), text_color='#AFAFAF', fg_color='#242424',
            corner_radius=6, anchor='w', justify='left', wraplength=610)

        result_count_controls_frame = ctk.CTkFrame(youtube_data_frame, fg_color='transparent')

        #register lambda to tcl/tk interpreter
        result_count_integer_validation = (
            root.register(lambda value: value == '' or (value.isascii() and value.isdigit())),
            '%P',
        )
        recommendation_result_count_label = ctk.CTkLabel(
            result_count_controls_frame, text='Recommendations', font=('Arial', 13), text_color='#B0B0B0')
        
        recommendation_result_count_entry = ctk.CTkEntry(
            result_count_controls_frame, width=130, height=28,
            textvariable=max_recommendation_result_count, justify='center',
            font=('Arial', 13), fg_color='#1a1a1a', corner_radius=6,
            validate='key', validatecommand=result_count_integer_validation)

        subscription_result_count_label = ctk.CTkLabel(
            result_count_controls_frame, text='Subscriptions', font=('Arial', 13), text_color='#B0B0B0')
        subscription_result_count_entry = ctk.CTkEntry(
            result_count_controls_frame, width=130, height=28,
            textvariable=max_sub_result_count, justify='center',
            font=('Arial', 13), fg_color='#1a1a1a', corner_radius=6,
            validate='key', validatecommand=result_count_integer_validation)

        search_result_count_label = ctk.CTkLabel(
            result_count_controls_frame, text='Search', font=('Arial', 13), text_color='#B0B0B0')
        search_result_count_entry = ctk.CTkEntry(
            result_count_controls_frame, width=130, height=28,
            textvariable=max_search_result_count, justify='center',
            font=('Arial', 13), fg_color='#1a1a1a', corner_radius=6,
            validate='key', validatecommand=result_count_integer_validation)

        liked_video_result_count_label = ctk.CTkLabel(
            result_count_controls_frame, text='Liked videos', font=('Arial', 13), text_color='#B0B0B0')
        liked_video_result_count_entry = ctk.CTkEntry(
            result_count_controls_frame, width=130, height=28,
            textvariable=max_like_result_count, justify='center',
            font=('Arial', 13), fg_color='#1a1a1a', corner_radius=6,
            validate='key', validatecommand=result_count_integer_validation)

        recommendation_result_count_entry.bind('<FocusOut>', save_max_result_count_setting)
        subscription_result_count_entry.bind('<FocusOut>', save_max_result_count_setting)
        search_result_count_entry.bind('<FocusOut>', save_max_result_count_setting)
        liked_video_result_count_entry.bind('<FocusOut>', save_max_result_count_setting)
        recommendation_result_count_entry.bind('<Return>', lambda event: setting.focus_set())
        subscription_result_count_entry.bind('<Return>', lambda event: setting.focus_set())
        search_result_count_entry.bind('<Return>', lambda event: setting.focus_set())
        liked_video_result_count_entry.bind('<Return>', lambda event: setting.focus_set())

        recommendation_result_count_label.grid(row=0, column=0, padx=5, pady=(2, 2))
        subscription_result_count_label.grid(row=0, column=1, padx=5, pady=(2, 2))
        search_result_count_label.grid(row=0, column=2, padx=5, pady=(2, 2))
        liked_video_result_count_label.grid(row=0, column=3, padx=5, pady=(2, 2))

        recommendation_result_count_entry.grid(row=1, column=0, padx=5, pady=(0, 10))
        subscription_result_count_entry.grid(row=1, column=1, padx=5, pady=(0, 10))
        search_result_count_entry.grid(row=1, column=2, padx=5, pady=(0, 10))
        liked_video_result_count_entry.grid(row=1, column=3, padx=5, pady=(0, 10))

        # Playlist Item Removal Section
        playlist_remove_frame = ctk.CTkFrame(account_playlist_scroll_frame, fg_color='#2B2B2B', corner_radius=8)
        playlist_remove_frame.grid_columnconfigure(0, weight=1)
        playlist_remove_frame.grid_columnconfigure(1, weight=1)

        playlist_remove_title = ctk.CTkLabel(playlist_remove_frame, text='  \u25b8 Remove from Playlist', font=('Arial', 15, 'bold'), text_color='#E08080', anchor='w')
        playlist_remove_btn = ctk.CTkButton(playlist_remove_frame, text='Remove Selected', width=160,
                                             command=remove_selected_from_playlist_setting,
                                             text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        playlist_remove_note = ctk.CTkLabel(playlist_remove_frame,
                                             text='NOTE: Removing an item only clears it from the current playlist view.\n'
                                                  'It does not affect the original source (YouTube, local folder, etc.).',
                                             height=56, font=('Arial', 14), text_color='#AFAFAF', fg_color='#242424',
                                             corner_radius=6, anchor='w', justify='left', wraplength=610)

        # ── Google Account Card ──
        google_title = ctk.CTkLabel(google_account_frame, text='  \u25b8 Google Account', font=('Arial', 15, 'bold'), text_color='#FFB347', anchor='w')
        googlelogin_btn = ctk.CTkButton(google_account_frame, text='Login Google', width=200,
                                         command=lambda:threading.Thread(daemon=True,target=google_login_setting).start(),
                                         text_color='white', font=('Arial', 14, 'bold'), fg_color='#3E62DC', hover_color='#4A70F0')
        googlelogout_btn = ctk.CTkButton(google_account_frame, text='Logout Google', width=200, command=google_logout_setting,
                                          text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        deletesyskey_btn = ctk.CTkButton(google_account_frame, text='Delete System Key', width=200, command=deletesyskey,
                                          text_color='#D98C8C', font=('Arial', 14, 'bold'),
                                          fg_color='#3A3A3A', hover_color='#4A3030',
                                          border_width=2, border_color='#8A4A4A')
        ytdlp_use_cookie_checkbtn = ctk.CTkCheckBox(google_account_frame, text='Use account cookie with yt-dlp',
                                                    variable=ytdlp_use_cookie, command=setting_switch_ytdlp_use_cookie,
                                                    fg_color='#3A3A3A', hover_color='#505050',
                                                    text_color='#C8C8C8', font=('Arial', 13))
        ytdlp_use_cookie_note = ctk.CTkLabel(
            google_account_frame,
            text='NOTE: Using account cookies may occasionally add a short wait and slightly increase\n'
                 'the chance of temporary account access restrictions.',
            height=56, font=('Arial', 14), text_color='#AFAFAF', fg_color='#242424',
            corner_radius=6, anchor='w', justify='left', wraplength=610)

        google_title.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky='w')
        ytdlp_use_cookie_checkbtn.grid(row=1, column=0, padx=(24, 8), pady=6, columnspan=3, sticky='w')
        ytdlp_use_cookie_note.grid(row=2, column=0, padx=16, pady=(0, 8), columnspan=3, sticky='ew')
        googlelogin_btn.grid(row=3, column=0, padx=(24, 4), pady=(6, 12))
        googlelogout_btn.grid(row=3, column=1, padx=4, pady=(6, 12))
        deletesyskey_btn.grid(row=3, column=2, padx=(4, 24), pady=(6, 12))
        
        
        # ══════════ Download — Card-style sections ══════════
        download_info_frame = ctk.CTkFrame(download_tab, fg_color='#2B2B2B', corner_radius=8)
        download_info_frame.grid_columnconfigure(0, weight=1)
        
        format_frame = ctk.CTkFrame(download_tab, fg_color='#2B2B2B', corner_radius=8)
        format_frame.grid_columnconfigure(0, weight=1)
        format_frame.grid_columnconfigure(1, weight=1)
        
        resolution_frame = ctk.CTkFrame(download_tab, fg_color='#2B2B2B', corner_radius=8)
        resolution_frame.grid_columnconfigure(0, weight=1)
        resolution_frame.grid_columnconfigure(1, weight=1)
        
        # Video Info Section
        info_title = ctk.CTkLabel(download_info_frame, text='  I. Selected Video', font=('Arial', 15, 'bold'), text_color='#E0A07E', anchor='w')
        download_seleted_title_text = ctk.CTkTextbox(download_info_frame, font=('Arial', 15), width=650, height=55, fg_color='#1a1a1a', text_color='#C8C8C8', corner_radius=6)
        download_seleted_title_text.configure(state='disabled')
        
        # Format Selection Section
        format_title = ctk.CTkLabel(format_frame, text='  II. Format', font=('Arial', 15, 'bold'), text_color='#D4A0E0', anchor='w')
        download_mp3 = ctk.CTkRadioButton(format_frame, text='Audio (MP3)', variable=formats, value=0, command=lambda:download_select_mode_setting(0),
                                           font=('Arial', 13), text_color='#C8C8C8')
        download_mp4 = ctk.CTkRadioButton(format_frame, text='Video (MP4)', variable=formats, value=1, command=lambda:download_select_mode_setting(1),
                                           font=('Arial', 13), text_color='#C8C8C8')
        
        # Resolution Section
        resolution_title = ctk.CTkLabel(resolution_frame, text='  III. Resolution', font=('Arial', 15, 'bold'), text_color='#80C8E0', anchor='w')
        resoltion_combox = ctk.CTkComboBox(resolution_frame, font=('Arial', 13), width=200, values=[],state='readonly',
                                            dropdown_fg_color='#333333', button_color='#444444')
        get_resoltion_btn = ctk.CTkButton(resolution_frame, text='Get Available', width=140,
                                           command=lambda:threading.Thread(daemon=True,target=get_resolution_setting).start(),
                                           text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        
        # ── Download Path Card ──
        download_path_frame = ctk.CTkFrame(download_tab, fg_color='#2B2B2B', corner_radius=8)
        download_path_frame.grid_columnconfigure(0, weight=0)
        download_path_frame.grid_columnconfigure(1, weight=1)
        download_path_frame.grid_columnconfigure(2, weight=0)
        download_path_frame.grid_columnconfigure(3, weight=0)

        download_path_title = ctk.CTkLabel(download_path_frame, text='  IV. Saving Path', font=('Arial', 15, 'bold'), text_color='#A8D8A8', anchor='w')
        download_path_label = ctk.CTkLabel(download_path_frame, font=('Arial', 13), text='Save to:', text_color='#B0B0B0')
        download_path_textbox = ctk.CTkTextbox(download_path_frame, font=('Arial', 13), height=28, text_color='#C8C8C8',
                                               fg_color='#1a1a1a', corner_radius=6, wrap='none', activate_scrollbars=False)
        download_path_textbox.configure(state='disabled')
        select_download_path_btn = ctk.CTkButton(download_path_frame, text='Select Path', width=130,
                                                  command=select_download_path,
                                                  text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        open_download_path_btn = ctk.CTkButton(download_path_frame, text='Open Folder', width=130,
                                                command=reveal_download_path,
                                                text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        set_default_download_path_btn = ctk.CTkButton(download_path_frame, text='Set Default', width=130,
                                                       command=set_default_download_path,
                                                       text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')

        # Download Action
        downloadselectedsong = ctk.CTkButton(download_tab, text='Save Selected Video', width=400,
                                              command=lambda:threading.Thread(daemon=True,target=download_to_loacl_setting).start(),
                                              text_color='#86C98A', font=('Arial', 15, 'bold'),
                                              fg_color='#3A3A3A', hover_color='#314735', corner_radius=8,
                                              border_width=2, border_color='#4F8A55')
        downloadhooklabel = ctk.CTkLabel(download_tab, font=('Arial', 13), textvariable=downloadhooktext, text_color='#80C8E0')


        # Create scrollable frame for player settings
        player_scrollable_frame = ctk.CTkScrollableFrame(player_tab, width=680, height=400, fg_color='#242424')
        player_scrollable_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        player_scrollable_frame.grid_columnconfigure(0, weight=1)
        player_scrollable_frame.grid_columnconfigure(1, weight=1)

        # ══════════════════════════════════════════════════════
        # PLAYER SETTINGS — Card-style organized sections
        # ══════════════════════════════════════════════════════

        # ── General Playback Card ──
        general_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8,
                                      border_width=1, border_color='#3A3A3A')
        general_frame.grid_columnconfigure(0, weight=0, minsize=180)
        general_frame.grid_columnconfigure(1, weight=1)
        general_frame.grid_columnconfigure(2, weight=0, minsize=50)

        general_header = ctk.CTkLabel(general_frame, text='  ▸ General', font=('Arial', 15, 'bold'), text_color='#7EB8E0', anchor='w')
        maxresolutionlabel = ctk.CTkLabel(general_frame, font=('Arial', 13), text='Max Resolution', text_color='#B0B0B0')
        maxresolutioncombobox = ctk.CTkComboBox(general_frame, font=('Arial', 13), width=130, state='readonly',
                                                 values=['480', '720', '1080', '1440', '2160', '4320'],
                                                 dropdown_fg_color='#333333', button_color='#444444')
        maxresolutioncombobox.set(str(maxresolution.get()))
        maxresolutioncombobox.configure(command=max_resolution_select)
        autoretry_btn = ctk.CTkCheckBox(general_frame, text='Auto retry on error', variable=autoretry,
                                         fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 13))
        audio_only_checkbtn = ctk.CTkCheckBox(general_frame, text='Audio only mode', variable=audio_only,
                                               fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 13), command=switch_audio_only)

        # ── Speed & Subtitle controls (directly inside General) ──
        general_playback_divider = ctk.CTkFrame(general_frame, height=1, fg_color='#444444', corner_radius=0)
        playerspeed_title_label = ctk.CTkLabel(general_frame, font=('Arial', 13), text='Playback Speed', text_color='#B0B0B0')
        playerspeed_slider = ctk.CTkSlider(general_frame, variable=player_speed, from_=0.3, to=3.0, width=200,
                                            number_of_steps=27, command=set_player_speed_setting,
                                            progress_color='#4A9E6E', button_color='#7EE0A8', button_hover_color='#98F0C0')
        playerspeed_slider.bind('<ButtonRelease-1>', apply_player_speed_setting)
        playerspeed_speed_label = ctk.CTkLabel(general_frame, font=('Arial', 13, 'bold'), text='1.0x', text_color='#7EE0A8')
        subtitle_label = ctk.CTkLabel(general_frame, text='Subtitle', font=('Arial', 13), text_color='#B0B0B0')
        subtitlecombobox = ctk.CTkComboBox(general_frame, font=('Arial', 13), width=220, state='readonly',
                                            values=subtitle_namelist, command=subtitle_combobox_callback,
                                            dropdown_fg_color='#333333', button_color='#444444')

        # ── Cache & Buffer Card ──
        cache_buffer_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        cache_buffer_frame.grid_columnconfigure(0, weight=0, minsize=180)
        cache_buffer_frame.grid_columnconfigure(1, weight=1)
        cache_buffer_frame.grid_columnconfigure(2, weight=0, minsize=50)

        _slider_kw = dict(progress_color='#8E7A4A', button_color='#E0C48C', button_hover_color='#F0D8A0')
        cache_buffer_header = ctk.CTkLabel(cache_buffer_frame, text='  ▸ Cache & Buffer', font=('Arial', 15, 'bold'), text_color='#E0C48C', anchor='w')

        cache_buffer_note = ctk.CTkLabel(
            cache_buffer_frame,
            text='NOTE: Front and back buffer limits are added together as the total cache budget.\n'
                 'Unused front-buffer space may be shared with the back buffer, but not the reverse.',
            height=56, font=('Arial', 14), text_color='#AFAFAF', fg_color='#242424',
            corner_radius=6, anchor='w', justify='left', wraplength=610)

        demuxer_max_bytes_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 13), text='Max front Buffer Size', text_color='#B0B0B0')
        demuxer_max_bytes_slider = ctk.CTkSlider(cache_buffer_frame, variable=demuxer_max_bytes, from_=16, to=2048, width=200,
                                                  number_of_steps=2032, command=_demuxer_max_bytes_slider_change, **_slider_kw)
        demuxer_max_bytes_slider.bind('<ButtonRelease-1>', _apply_cache_slider_settings)
        demuxer_max_bytes_value_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 13, 'bold'), text=f'{demuxer_max_bytes.get()}M', text_color='#E0C48C')

        demuxer_max_back_bytes_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 13), text='Max Back Buffer Size', text_color='#B0B0B0')
        demuxer_max_back_bytes_slider = ctk.CTkSlider(cache_buffer_frame, variable=demuxer_max_back_bytes, from_=16, to=2048, width=200,
                                                       number_of_steps=2032, command=_demuxer_max_back_bytes_slider_change, **_slider_kw)
        demuxer_max_back_bytes_slider.bind('<ButtonRelease-1>', _apply_cache_slider_settings)
        demuxer_max_back_bytes_value_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 13, 'bold'), text=f'{demuxer_max_back_bytes.get()}M', text_color='#E0C48C')

        cache_pause_wait_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 13), text='Cache Pause Wait', text_color='#B0B0B0')
        cache_pause_wait_slider = ctk.CTkSlider(cache_buffer_frame, variable=cache_pause_wait, from_=0.1, to=20.0, width=200,
                                                       number_of_steps=199, command=_cache_pause_wait_slider_change, **_slider_kw)
        cache_pause_wait_slider.bind('<ButtonRelease-1>', _apply_cache_slider_settings)
        cache_pause_wait_value_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 13, 'bold'), text=f'{cache_pause_wait.get():.1f}s', text_color='#E0C48C')

        audio_wait_open_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 13), text='Audio Wait Open', text_color='#B0B0B0')
        audio_wait_open_slider = ctk.CTkSlider(cache_buffer_frame, variable=audio_wait_open, from_=1, to=10, width=200,
                                                number_of_steps=9, command=_audio_wait_open_slider_change, **_slider_kw)
        audio_wait_open_slider.bind('<ButtonRelease-1>', _apply_cache_slider_settings)
        audio_wait_open_value_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 13, 'bold'), text=f'{audio_wait_open.get()}s', text_color='#E0C48C')

        # ── Fullscreen Settings Card ──
        fullscreen_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        fullscreen_frame.grid_columnconfigure(0, weight=1)
        fullscreen_frame.grid_columnconfigure(1, weight=1)
        fullscreen_frame.grid_columnconfigure(2, weight=1)

        fullscreen_title = ctk.CTkLabel(fullscreen_frame, text='  ▸ Fullscreen', font=('Arial', 15, 'bold'), text_color='#C0A0E0', anchor='w')
        openwith_fullscreen_btn = ctk.CTkCheckBox(fullscreen_frame, text='Auto fullscreen on open', variable=open_with_fullscreen,
                                                    fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 13), command=autofullscreen_setting)
        hover_fullscreen_btn = ctk.CTkCheckBox(fullscreen_frame, text='Hover Fullscreen', variable=hover_fullscreen,
                                                fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 13), command=lambda:switch_hover_fullscreen)
        fullscreen_mode_label = ctk.CTkLabel(fullscreen_frame, text='Fullscreen Mode:', font=('Arial', 13), text_color='#B0B0B0', anchor='w')
        fullscreen_mode_normal_btn = ctk.CTkRadioButton(fullscreen_frame, text='Normal', variable=fullscreenmode, value=0,
                                                         text_color='#C8C8C8', font=('Arial', 13),command=SetFullscreenmode)
        fullscreen_mode_all_widget_btn = ctk.CTkRadioButton(fullscreen_frame, text='Fullscreen (all widgets)', variable=fullscreenmode, value=1,
                                                              text_color='#C8C8C8', font=('Arial', 13),command=SetFullscreenmode)
        fullscreen_mode_window_btn = ctk.CTkRadioButton(fullscreen_frame, text='Fullscreen to window', variable=fullscreenmode, value=2,
                                                         text_color='#C8C8C8', font=('Arial', 13),command=SetFullscreenmode )

        # ── Advanced Settings Card ──
        advanced_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        advanced_frame.grid_columnconfigure(0, weight=1)
        advanced_frame.grid_columnconfigure(1, weight=1)

        advanced_title = ctk.CTkLabel(advanced_frame, text='  ▸ Advanced', font=('Arial', 15, 'bold'), text_color='#E08080', anchor='w')

        mpvlogbtn = ctk.CTkButton(advanced_frame, text='Show MPV Log', width=160, command=log_handler.log_handle_frame.show_mpv_log,
                                   text_color='#6EA0FF', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#334766',
                                   border_width=2, border_color='#6EA0FF')
        force_stop_loading_btn = ctk.CTkButton(advanced_frame, text='Force Stop Loading', width=160, command=set_force_stop_loading,
                                                text_color='#FF8A8A', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#55383A',
                                                border_width=2, border_color='#FF8A8A')
        show_cache_btn = ctk.CTkCheckBox(advanced_frame, text='Show Cache Info', variable=show_cache,
                                          fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 13), command=switch_show_cache)

        # ── Background ──
        advanced_blur_frame = ctk.CTkFrame(advanced_frame, fg_color='#242424', corner_radius=6,
                                            border_width=1, border_color='#3A3A3A')
        advanced_blur_frame.grid_columnconfigure(0, weight=1)
        advanced_blur_frame.grid_columnconfigure(1, weight=1)
        advanced_blur_title = ctk.CTkLabel(advanced_blur_frame, text='  ▸ Background', font=('Arial', 14, 'bold'),
                                            text_color='#C0A0E0', anchor='w')
        blurbtn = ctk.CTkCheckBox(advanced_blur_frame, text='Acrylic blur effect', variable=blur_window,
                                   fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 13), command=switch_blur_window)
        blur_gradient_name_label = ctk.CTkLabel(advanced_blur_frame, text='Blur Gradient Color', font=('Arial', 13), text_color='#B0B0B0', anchor='w')
        blur_gradient_value_label = ctk.CTkLabel(advanced_blur_frame, textvariable=blur_hexColor, font=('Arial', 13, 'bold'), text_color='#C8C8C8',
                                                  fg_color='#1a1a1a', corner_radius=6, anchor='w', padx=8)
        blur_gradient_choose_btn = ctk.CTkButton(advanced_blur_frame, text='Choose Color', width=140,
                                                  command=lambda: set_gradient_color(), 
                                                  text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        blur_gradient_default_btn = ctk.CTkButton(advanced_blur_frame, text='Set Default', width=140,
                                                   command=lambda: set_gradient_color(default=True),  
                                                   text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')

        # ══════════ External Services — Separate cards ══════════
        external_services_frame = ctk.CTkFrame(external_services_tab, fg_color='#242424', corner_radius=0)
        external_services_frame.grid_columnconfigure(0, weight=1)
        external_services_frame.grid(row=0, column=0, sticky="nsew")

        chrome_extension_frame = ctk.CTkFrame(external_services_frame, fg_color='#2B2B2B', corner_radius=8)
        chrome_extension_frame.grid_columnconfigure(0, weight=0)
        chrome_extension_frame.grid_columnconfigure(1, weight=1)
        chrome_extension_frame.grid_columnconfigure(2, weight=0)

        chrome_extension_title = ctk.CTkLabel(chrome_extension_frame, text='  ▸ Chrome Extension', font=('Arial', 15, 'bold'), text_color='#80C0E0', anchor='w')
        chrome_extension_server_checkbtn = ctk.CTkSwitch(chrome_extension_frame, text='Chrome extension server', variable=setting_run_chrome_extension_server,
                                                          command=switch_flask_server, text_color='#C8C8C8', font=('Arial', 13))
        chrome_extension_port_label = ctk.CTkLabel(chrome_extension_frame, text='Server port', font=('Arial', 13), text_color='#B0B0B0', anchor='w')
        chrome_extension_port_textbox = ctk.CTkEntry(chrome_extension_frame, textvariable=chrome_extension_port, font=('Arial', 13))
        chrome_extension_port_set_btn = ctk.CTkButton(chrome_extension_frame, text='Set Port', width=100,
                                                       command=save_chrome_extension_port_setting,
                                                       text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')

        discord_presence_frame = ctk.CTkFrame(external_services_frame, fg_color='#2B2B2B', corner_radius=8)
        discord_presence_frame.grid_columnconfigure(0, weight=0)
        discord_presence_frame.grid_columnconfigure(1, weight=1)
        discord_presence_frame.grid_columnconfigure(2, weight=0)
        discord_presence_frame.grid_columnconfigure(3, weight=0)

        discord_presence_title = ctk.CTkLabel(discord_presence_frame, text='  ▸ Discord Rich Presence', font=('Arial', 15, 'bold'), text_color='#B9A0E0', anchor='w')
        enable_discord_presence_btn = ctk.CTkSwitch(discord_presence_frame, text='Discord Rich Presence', variable=enable_discord_presence,
                                                     text_color='#C8C8C8', font=('Arial', 13),
                                                     command=lambda:threading.Thread(daemon=True,target=switch_discord_presence).start())
        discord_presence_show_playing_btn = ctk.CTkCheckBox(discord_presence_frame, text='Show playing on Discord', variable=discord_presence_show_playing,
                                                             fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 13), command=switch_discord_presence_show_playing)
        discord_idle_presence_wording_label = ctk.CTkLabel(discord_presence_frame, text='Idling presence wording', font=('Arial', 13), text_color='#B0B0B0', anchor='w')
        discord_idle_presence_wording_textbox = ctk.CTkEntry(discord_presence_frame, textvariable=discord_idle_presence_wording, font=('Arial', 13))
        discord_idle_presence_wording_set_btn = ctk.CTkButton(discord_presence_frame, text='Set Wording', width=100,
                                                               command=save_discord_idle_presence_wording_setting,
                                                               text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        discord_idle_presence_wording_default_btn = ctk.CTkButton(discord_presence_frame, text='Set Default', width=100,
                                                                   command=lambda: save_discord_idle_presence_wording_setting(default=True),
                                                                   text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')


        # ══════════ Version Info — Card-style sections ══════════
        ytdlp_frame = ctk.CTkFrame(version_info_tab, fg_color='#2B2B2B', corner_radius=8)
        ytdlp_frame.grid_columnconfigure(0, weight=1)
        ytdlp_frame.grid_columnconfigure(1, weight=1)
        
        player_frame = ctk.CTkFrame(version_info_tab, fg_color='#2B2B2B', corner_radius=8)
        player_frame.grid_columnconfigure(0, weight=1)
        player_frame.grid_columnconfigure(1, weight=1)

        # YT-DLP Section
        ytdlp_title = ctk.CTkLabel(ytdlp_frame, text='  \u25b8 YT-DLP', font=('Arial', 15, 'bold'), text_color='#7EE0A8', anchor='w')
        go_ytdlp_web = ctk.CTkButton(ytdlp_frame, text='Visit Website', width=120,
                                      command=lambda:webbrowser.open('https://github.com/yt-dlp/yt-dlp/releases'),
                                      text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        auto_update_ytdlp_btn = ctk.CTkButton(ytdlp_frame, text='Update', width=120,
                                               command=lambda:threading.Thread(daemon=True,target=update_ytdlp).start(),
                                               text_color='#86C98A', font=('Arial', 14, 'bold'),
                                               fg_color='#3A3A3A', hover_color='#314735',
                                               border_width=2, border_color='#4F8A55')
        ytdlp_use_nightly_build_checkbtn = ctk.CTkCheckBox(ytdlp_frame, text='Nightly build',
                                                            variable=ytdlp_use_nightly_build,
                                                            command=ytdlp_switch_use_nightly_build,
                                                            fg_color='#3A3A3A', hover_color='#505050',
                                                            text_color='#C8C8C8', font=('Arial', 13))

        # JaTubePlayer Section
        player_title = ctk.CTkLabel(player_frame, text='  \u25b8 JaTubePlayer', font=('Arial', 15, 'bold'), text_color='#7EB8E0', anchor='w')
        go_player_web = ctk.CTkButton(player_frame, text='Visit Website', width=120,
                                       command=lambda:webbrowser.open('https://github.com/jackaopen/JaTubePlayer/releases'),
                                       text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')

        # Version Sub-frames
        ytdlp_current_versions_frame = ctk.CTkFrame(ytdlp_frame, fg_color='#1a1a1a', corner_radius=6)
        ytdlp_latest_versions_frame = ctk.CTkFrame(ytdlp_frame, fg_color='#1a1a1a', corner_radius=6)
        player_current_versions_frame = ctk.CTkFrame(player_frame, fg_color='#1a1a1a', corner_radius=6)
        player_latest_versions_frame = ctk.CTkFrame(player_frame, fg_color='#1a1a1a', corner_radius=6)

        ytdlp_current_versions_frame_title = ctk.CTkLabel(ytdlp_current_versions_frame, text='Current', font=('Arial', 13, 'bold'), text_color='#B0B0B0')
        ytdlp_latest_versions_frame_title = ctk.CTkLabel(ytdlp_latest_versions_frame, text='Latest', font=('Arial', 13, 'bold'), text_color='#B0B0B0')
        player_current_versions_frame_title = ctk.CTkLabel(player_current_versions_frame, text='Current', font=('Arial', 13, 'bold'), text_color='#B0B0B0')
        player_latest_versions_frame_title = ctk.CTkLabel(player_latest_versions_frame, text='Latest', font=('Arial', 13, 'bold'), text_color='#B0B0B0')

        ytdlp_ver_current_label = ctk.CTkLabel(ytdlp_current_versions_frame, width=220, font=('Arial', 15), text_color='#7EE0A8', anchor='w')
        ytdlp_ver_lastest_label = ctk.CTkLabel(ytdlp_latest_versions_frame, width=220, font=('Arial', 15), text_color='#80C8E0', anchor='w')

        player_ver_current_label = ctk.CTkLabel(player_current_versions_frame, width=220, font=('Arial', 15), text_color='#7EE0A8', anchor='w')
        player_ver_latest_label = ctk.CTkLabel(player_latest_versions_frame, width=220, font=('Arial', 15), text_color='#80C8E0', anchor='w')

        # Settings
        auto_check_ver_btn = ctk.CTkCheckBox(version_info_tab, text='Check version at startup', variable=auto_check_ver, command=save_autovercheck_option_ver,
                                              fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 13))





        # ══════════ Hotkeys — Card-style sections ══════════
        hotkey_scrollable_frame = ctk.CTkScrollableFrame(hotkey_tab, width=680, height=400, fg_color='#242424')
        hotkey_scrollable_frame.grid(row=0, column=0)
        hotkey_scrollable_frame.grid_columnconfigure(0, weight=1)

        _hk_card_kw = dict(fg_color='#2B2B2B', corner_radius=8)
        _hk_textbox_kw = dict(font=('Arial', 13), width=200, height=1, state='disabled', fg_color='#1a1a1a', text_color='#C8C8C8', corner_radius=6)

        hotkey_playback_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)
        hotkey_mode_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)
        hotkey_volume_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)
        hotkey_player_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)
        hotkey_set_keymem_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)

        hotkey_set_keymem_title = ctk.CTkLabel(hotkey_set_keymem_frame, text='  \u25b8 Set Hotkey', font=('Arial', 15, 'bold'), text_color='#E0C48C', anchor='w')
        hotkey_set_keymem_function_combobox = ctk.CTkComboBox(hotkey_set_keymem_frame, font=('Arial', 13), width=200, state='readonly',
                                                               values=['play_pause','next','previous','stop', 'volume_up','volume_down','mode_random','mode_continuous','mode_repeat','toggle_minimize'],
                                                               dropdown_fg_color='#333333', button_color='#444444')
        hotkey_set_keymem_startlisten_btn = ctk.CTkButton(hotkey_set_keymem_frame, text='Set Hotkey', width=160, command=set_keymem_setting_thread,
                                                            text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        hotkey_set_keymem_set_default_btn = ctk.CTkButton(hotkey_set_keymem_frame, text='Reset All to Default', width=160, command=set_keymem_default_setting,
                                                            text_color='#D98C8C', font=('Arial', 14, 'bold'),
                                                            fg_color='#3A3A3A', hover_color='#4A3030',
                                                            border_width=2, border_color='#8A4A4A')

        hotkey_playback_frame_title = ctk.CTkLabel(hotkey_playback_frame, text='  \u25b8 Playback', font=('Arial', 15, 'bold'), text_color='#FF6B8A', anchor='w')
        hotkey_mode_frame_title = ctk.CTkLabel(hotkey_mode_frame, text='  \u25b8 Playback Mode', font=('Arial', 15, 'bold'), text_color='#7EE0A8', anchor='w')
        hotkey_volume_frame_title = ctk.CTkLabel(hotkey_volume_frame, text='  \u25b8 Volume', font=('Arial', 15, 'bold'), text_color='#80C8E0', anchor='w')
        hotkey_player_frame_title = ctk.CTkLabel(hotkey_player_frame, text='  \u25b8 Player', font=('Arial', 15, 'bold'), text_color='#C0A0E0', anchor='w')

        hotkey_playback_play_pause_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 13), text='Play / Pause', text_color='#B0B0B0')
        hotkey_playback_stop_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 13), text='Stop', text_color='#B0B0B0')
        hotkey_playback_next_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 13), text='Next Video', text_color='#B0B0B0')
        hotkey_playback_prev_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 13), text='Previous Video', text_color='#B0B0B0')
    
        hotkey_mode_repeat_label = ctk.CTkLabel(hotkey_mode_frame, font=('Arial', 13), text='Repeat Mode', text_color='#B0B0B0')
        hotkey_mode_random_label = ctk.CTkLabel(hotkey_mode_frame, font=('Arial', 13), text='Random Mode', text_color='#B0B0B0')
        hotkey_mode_continuous_label = ctk.CTkLabel(hotkey_mode_frame, font=('Arial', 13), text='Continuous Play', text_color='#B0B0B0')

        hotkey_volume_up_label = ctk.CTkLabel(hotkey_volume_frame, font=('Arial', 13), text='Volume Up', text_color='#B0B0B0')
        hotkey_volume_down_label = ctk.CTkLabel(hotkey_volume_frame, font=('Arial', 13), text='Volume Down', text_color='#B0B0B0')
        hotkey_toggle_minimize_label = ctk.CTkLabel(hotkey_player_frame, font=('Arial', 13), text='Toggle Minimize', text_color='#B0B0B0')

        hotkey_playback_play_pause_textbox = ctk.CTkTextbox(hotkey_playback_frame, **_hk_textbox_kw)
        hotkey_playback_stop_textbox = ctk.CTkTextbox(hotkey_playback_frame, **_hk_textbox_kw)
        hotkey_playback_next_textbox = ctk.CTkTextbox(hotkey_playback_frame, **_hk_textbox_kw)
        hotkey_playback_prev_textbox = ctk.CTkTextbox(hotkey_playback_frame, **_hk_textbox_kw)

        hotkey_mode_repeat_textbox = ctk.CTkTextbox(hotkey_mode_frame, **_hk_textbox_kw)
        hotkey_mode_random_textbox = ctk.CTkTextbox(hotkey_mode_frame, **_hk_textbox_kw)
        hotkey_mode_continuous_textbox = ctk.CTkTextbox(hotkey_mode_frame, **_hk_textbox_kw)

        hotkey_volume_up_textbox = ctk.CTkTextbox(hotkey_volume_frame, **_hk_textbox_kw)
        hotkey_volume_down_textbox = ctk.CTkTextbox(hotkey_volume_frame, **_hk_textbox_kw)
        hotkey_toggle_minimize_textbox = ctk.CTkTextbox(hotkey_player_frame, **_hk_textbox_kw)
        
        hotkey_playback_frame.grid_columnconfigure(0, weight=0, minsize=160)
        hotkey_mode_frame.grid_columnconfigure(0, weight=0, minsize=160)
        hotkey_volume_frame.grid_columnconfigure(0, weight=0, minsize=160)
        hotkey_player_frame.grid_columnconfigure(0, weight=0, minsize=160)
        hotkey_playback_frame.grid_columnconfigure(1, weight=1)
        hotkey_mode_frame.grid_columnconfigure(1, weight=1)
        hotkey_volume_frame.grid_columnconfigure(1, weight=1)
        hotkey_player_frame.grid_columnconfigure(1, weight=1)


        ytdlp_ver_current_label.configure(text=f'Loading...')
        ytdlp_ver_lastest_label.configure(text=f'Loading...')
        player_ver_current_label.configure(text=f'Loading...')
        player_ver_latest_label.configure(text=f'Loading...')


        def init_quickstart_data():
            '''
            load data(if exist) into the according frame
            '''
            quickstartconfig = CONFIG['quickstartup_init']
            mode = quickstartconfig['mode']
            if mode == 0:
                init_toggle_quickstartup.set(False)
                setting_init_toggle_quickstartup()
            else:
                init_toggle_quickstartup.set(True)
                setting_init_toggle_quickstartup()
                if mode == 1:
                    init_quickstartup_mode.set('search')
                    init_search_select()

                    init_search_entry.delete(0,tk.END)
                    init_search_entry.insert(tk.END,quickstartconfig['searchmode_keyword'])
                    init_search_select()
                elif mode == 2:
                    init_quickstartup_mode.set('playlist')
                    
                    
                    if quickstartconfig['playlistmode_playlist_Name']:
                        if quickstartconfig['playlistmode_playlist_ID'] not in ['sub','like','home']:
                            init_playlist_combobox.set(quickstartconfig['playlistmode_playlist_Name'])
                            init_quickstartup_playlist_mode.set('yt_playlist')
                        else:
                            init_quickstartup_playlist_mode.set(quickstartconfig['playlistmode_playlist_ID'])
                        init_playlist_select()
                    else:
                        log_handle(
                            content=f'No playlist name found in config for quick startup mode.',
                            errtype='warning',
                            component='settings',
                        )
                        return
                
                        

                elif mode == 3:
                    init_quickstartup_mode.set('local_playlist')
                    init_local_playlist()


        def get_hotkey_setting_thread():
            try:
                insert_textbox(hotkey_playback_play_pause_textbox, CONFIG['keyboard_hotkeys'].get('play_pause', 'Not set'))
                insert_textbox(hotkey_playback_stop_textbox, CONFIG['keyboard_hotkeys'].get('stop', 'Not set'))
                insert_textbox(hotkey_playback_next_textbox, CONFIG['keyboard_hotkeys'].get('next', 'Not set'))
                insert_textbox(hotkey_playback_prev_textbox, CONFIG['keyboard_hotkeys'].get('previous', 'Not set'))
                insert_textbox(hotkey_mode_repeat_textbox, CONFIG['keyboard_hotkeys'].get('mode_repeat', 'Not set'))
                insert_textbox(hotkey_mode_random_textbox, CONFIG['keyboard_hotkeys'].get('mode_random', 'Not set'))
                insert_textbox(hotkey_mode_continuous_textbox, CONFIG['keyboard_hotkeys'].get('mode_continuous', 'Not set'))
                insert_textbox(hotkey_volume_up_textbox, CONFIG['keyboard_hotkeys'].get('volume_up', 'Not set'))
                insert_textbox(hotkey_volume_down_textbox, CONFIG['keyboard_hotkeys'].get('volume_down', 'Not set'))
                insert_textbox(hotkey_toggle_minimize_textbox, CONFIG['keyboard_hotkeys'].get('toggle_minimize', 'Not set'))
            except Exception as e:
                log_handle(
                    content=f"Error loading hotkey settings: {e}",
                    errtype='error',
                    component='settings',
                )
                
        
        def get_version_setting_thread():
            try:
                if check_internet_socket():
                    
                    ui_queue.put(lambda: ytdlp_ver_current_label.configure(text=f'{ytdlpver.__version__}'))
                    ui_queue.put(lambda: player_ver_current_label.configure(text=f'{ver}'))
                    ui_queue.put(lambda v=get_latest_player_version(): player_ver_latest_label.configure(text=f'{v}'))
                    ui_queue.put(lambda v=get_latest_dlp_version(ytdlp_use_nightly_build.get()): ytdlp_ver_lastest_label.configure(text=f'{v}' if not ytdlp_use_nightly_build.get() else f'Nightly: {v}'))
                else:
                    ui_queue.put(lambda: ytdlp_ver_lastest_label.configure(text=f'No internet'))
                    ui_queue.put(lambda: ytdlp_ver_current_label.configure(text=f'{ytdlpver.__version__}'))
                    ui_queue.put(lambda: player_ver_current_label.configure(text=f'{ver}'))
                    ui_queue.put(lambda: player_ver_latest_label.configure(text=f'No internet'))
            except Exception as e:log_handle(
                                      content=str(e),
                                      errtype='error',
                                      component='settings',
                                  )




        def setting_frame_listener():#looping thread to check selected video and quick startup mode
            '''
            looping thread to check selected video and quick startup mode
            check downloadability of the selected video
            '''
            
            nonlocal init_quick_startup_mode_text
            while not setting_closed:

                try:
                    try:
                        quickstartconfig = CONFIG['quickstartup_init']
                        mode = quickstartconfig['mode']
                        if mode == 0:insert_textbox(init_quick_startup_mode_text, 'Not selected')
                        elif mode == 1:insert_textbox(init_quick_startup_mode_text, f'search : {CONFIG["quickstartup_init"]["searchmode_keyword"]}')
                        elif mode == 2:
                            insert_textbox(init_quick_startup_mode_text, f'playlist : {CONFIG["quickstartup_init"]["playlistmode_playlist_Name"]}')
                        elif mode == 3:insert_textbox(init_quick_startup_mode_text, f'Local folder : {CONFIG["quickstartup_init"]["localfoldermode_folder_Path"]}')


                    except Exception as e:log_handle(
                                              content=str(e),
                                              errtype='error',
                                              component='settings',
                                          )

                    
                    ui_queue.put(lambda: download_seleted_title_text.configure(state='normal'))
                    ui_queue.put(lambda: download_seleted_title_text.delete(0.0,tk.END))
                    
                    if playing_vid_mode ==3 and playing_vid_info_dict:ui_queue.put(lambda: download_seleted_title_text.insert(tk.END,f'{playing_vid_info_dict["title"]}'))
                    elif selected_song_number != None and media_data_list.playlisttitles:ui_queue.put(lambda: download_seleted_title_text.insert(tk.END,f'{media_data_list.playlisttitles[selected_song_number]}'))
                    else:ui_queue.put(lambda: download_seleted_title_text.insert(tk.END,'Select a video first!'))
                    
                    ui_queue.put(lambda: download_seleted_title_text.configure(state='disabled'))
                        
                    
                        
                    
                    try:
                        _info_dict = playing_vid_info_dict if playing_vid_info_dict else {}
                        if (playing_vid_mode == 0 and _info_dict.get('live_status') == 'is_live'
                            and media_data_list.current_playing_idx_num == selected_song_number):
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        elif playing_vid_mode ==1 or playing_vid_mode ==2:
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        elif playing_vid_mode ==3 and _info_dict.get('live_status') == 'is_live':
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        elif playing_vid_mode ==4 and not media_data_list.vid_url[selected_song_number].startswith(('http://','https://')):
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        else:
                            try:
                                if not is_downloading.get():
                                    ui_queue.put(lambda: downloadselectedsong.configure(state='normal'))
                                else:
                                    ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                            except Exception as e :pass

                    except Exception as e :pass
                    
                           
                except Exception as e :pass
                time.sleep(1)


        threading.Thread(daemon=True,target=lambda:root.after(200,init_quickstart_data)).start()
        threading.Thread(daemon=True,target=get_version_setting_thread).start()
        threading.Thread(daemon=True,target=get_hotkey_setting_thread).start()
        root.after(200, lambda: threading.Thread(daemon=True, target=setting_frame_listener).start())

        ui_queue.put(lambda:subtitlecombobox.configure(values=subtitle_namelist))
        ui_queue.put(lambda:subtitlecombobox.set(subtitle_namelist[subtitle_selection_idx.get()]))

        insert_textbox(download_path_textbox, download_path.get())
        
        # ══════════ Layout: Account & Playlist Tab ══════════
        youtube_data_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(10, 4), sticky='ew')
        youtube_title.grid(row=0, column=0, columnspan=4, padx=8, pady=(10, 6), sticky='w')
        updateuserplaylists_btn.grid(row=1, column=0, columnspan=4, padx=(24, 8), pady=(5, 12), sticky='w')
        result_count_separator.grid(row=2, column=0, columnspan=4, padx=12, pady=(2, 6), sticky='ew')
        result_count_title.grid(row=3, column=0, columnspan=4, padx=8, pady=(2, 6), sticky='w')
        result_count_controls_frame.grid(row=4, column=0, columnspan=4, pady=(0, 2))
        result_count_note.grid(row=5, column=0, columnspan=4, padx=16, pady=(2, 12), sticky='ew')
        
        google_account_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=4, sticky='ew')

        playlist_remove_frame.grid(row=2, column=0, columnspan=2, padx=16, pady=4, sticky='ew')
        playlist_remove_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky='w')
        playlist_remove_btn.grid(row=1, column=0, columnspan=2, padx=(24, 8), pady=(5, 8), sticky='w')
        playlist_remove_note.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 12), sticky='ew')

        account_playlist_bottom_spacer = ctk.CTkFrame(account_playlist_scroll_frame, height=40, fg_color='transparent')
        account_playlist_bottom_spacer.grid(row=3, column=0, columnspan=2, sticky='ew')



        # ══════════ Layout: Download Tab ══════════
        download_info_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(10, 4), sticky="ew")
        info_title.grid(row=0, column=0, padx=8, pady=(10, 6), sticky="w")
        download_seleted_title_text.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
        
        format_frame.grid(row=1, column=0, padx=(16, 4), pady=4, sticky="nsew")
        format_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        download_mp3.grid(row=1, column=0, padx=(24, 8), pady=(5, 12), sticky="w")
        download_mp4.grid(row=1, column=1, padx=8, pady=(5, 12), sticky="w")
        
        resolution_frame.grid(row=1, column=1, padx=(4, 16), pady=4, sticky="nsew")
        resolution_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        resoltion_combox.grid(row=1, column=0, padx=(24, 8), pady=(5, 12), sticky="ew")
        get_resoltion_btn.grid(row=1, column=1, padx=(8, 12), pady=(5, 12), sticky="w")
        
        download_path_frame.grid(row=2, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        download_path_title.grid(row=0, column=0, columnspan=4, padx=8, pady=(10, 6), sticky="w")
        download_path_label.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="e")
        download_path_textbox.grid(row=1, column=1, columnspan=3, padx=(8, 24), pady=5, sticky="ew")
        select_download_path_btn.grid(row=2, column=1, padx=(8, 4), pady=(4, 12), sticky="w")
        open_download_path_btn.grid(row=2, column=2, padx=4, pady=(4, 12))
        set_default_download_path_btn.grid(row=2, column=3, padx=(4, 24), pady=(4, 12), sticky="e")

        downloadselectedsong.grid(row=3, column=0, columnspan=2, padx=20, pady=(16, 8))
        downloadhooklabel.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 10))

        # ══════════ Layout: Advanced Player Settings Tab ══════════

        # ── General Card (includes Speed & Subtitle) ──
        general_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(10, 4), sticky="ew")
        general_header.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        maxresolutionlabel.grid(row=1, column=0, padx=(24, 8), pady=(6, 8), sticky="w")
        maxresolutioncombobox.grid(row=1, column=1, columnspan=2, padx=(8, 24), pady=(6, 8), sticky="ew")
        general_playback_divider.grid(row=2, column=0, columnspan=3, padx=20, pady=(4, 8), sticky="ew")
        playerspeed_title_label.grid(row=3, column=0, padx=(24, 8), pady=6, sticky="w")
        playerspeed_slider.grid(row=3, column=1, padx=8, pady=6, sticky="ew")
        playerspeed_speed_label.grid(row=3, column=2, padx=(4, 24), pady=6, sticky="e")
        subtitle_label.grid(row=4, column=0, padx=(24, 8), pady=6, sticky="w")
        subtitlecombobox.grid(row=4, column=1, columnspan=2, padx=(8, 24), pady=6, sticky="ew")
        autoretry_btn.grid(row=5, column=0, padx=(24, 8), pady=(10, 14), sticky="w")
        audio_only_checkbtn.grid(row=5, column=1, columnspan=2, padx=(8, 24), pady=(10, 14), sticky="w")

        # ── Cache & Buffer Card ──
        cache_buffer_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        cache_buffer_header.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        cache_buffer_note.grid(row=1, column=0, columnspan=3, padx=16, pady=(0, 8), sticky="ew")
        demuxer_max_bytes_label.grid(row=2, column=0, padx=(24, 8), pady=4, sticky="w")
        demuxer_max_bytes_slider.grid(row=2, column=1, padx=8, pady=4, sticky="ew")
        demuxer_max_bytes_value_label.grid(row=2, column=2, padx=(4, 14), pady=4, sticky="w")
        demuxer_max_back_bytes_label.grid(row=3, column=0, padx=(24, 8), pady=4, sticky="w")
        demuxer_max_back_bytes_slider.grid(row=3, column=1, padx=8, pady=4, sticky="ew")
        demuxer_max_back_bytes_value_label.grid(row=3, column=2, padx=(4, 14), pady=4, sticky="w")
        cache_pause_wait_label.grid(row=4, column=0, padx=(24, 8), pady=4, sticky="w")
        cache_pause_wait_slider.grid(row=4, column=1, padx=8, pady=4, sticky="ew")
        cache_pause_wait_value_label.grid(row=4, column=2, padx=(4, 14), pady=4, sticky="w")
        audio_wait_open_label.grid(row=5, column=0, padx=(24, 8), pady=(4, 12), sticky="w")
        audio_wait_open_slider.grid(row=5, column=1, padx=8, pady=(4, 12), sticky="ew")
        audio_wait_open_value_label.grid(row=5, column=2, padx=(4, 14), pady=(4, 12), sticky="w")

        # ── Fullscreen Card ──
        fullscreen_frame.grid(row=2, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        fullscreen_title.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        openwith_fullscreen_btn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        hover_fullscreen_btn.grid(row=1, column=1, padx=8, pady=5, sticky="w")
        fullscreen_mode_label.grid(row=2, column=0, padx=(24, 8), pady=(6, 4), sticky="w")
        fullscreen_mode_normal_btn.grid(row=3, column=0, padx=(24, 8), pady=(2, 12), sticky="w")
        fullscreen_mode_all_widget_btn.grid(row=3, column=1, padx=8, pady=(2, 12), sticky="w")
        fullscreen_mode_window_btn.grid(row=3, column=2, padx=8, pady=(2, 12), sticky="w")

        # ── Advanced Card ──
        advanced_frame.grid(row=3, column=0, columnspan=2, padx=16, pady=(4, 10), sticky="ew")
        advanced_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        show_cache_btn.grid(row=1, column=0, columnspan=2, padx=(24, 8), pady=(4, 8), sticky="w")
        mpvlogbtn.grid(row=2, column=0, padx=(24, 6), pady=(4, 10), sticky="ew")
        force_stop_loading_btn.grid(row=2, column=1, padx=(6, 24), pady=(4, 10), sticky="ew")

        advanced_blur_frame.grid(row=3, column=0, columnspan=2, padx=12, pady=(4, 12), sticky="ew")
        advanced_blur_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(8, 5), sticky="w")
        blurbtn.grid(row=1, column=0, columnspan=2, padx=(16, 8), pady=(4, 8), sticky="w")
        blur_gradient_name_label.grid(row=2, column=0, padx=(16, 8), pady=(5, 5), sticky="w")
        blur_gradient_value_label.grid(row=2, column=1, padx=(8, 16), pady=(5, 5), sticky="ew")
        blur_gradient_choose_btn.grid(row=3, column=0, padx=(16, 8), pady=(5, 10), sticky="ew")
        blur_gradient_default_btn.grid(row=3, column=1, padx=(8, 16), pady=(5, 10), sticky="ew")

        # ══════════ Layout: External Services Tab ══════════
        chrome_extension_frame.grid(row=0, column=0, padx=8, pady=(8, 4), sticky="ew")
        chrome_extension_title.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        chrome_extension_server_checkbtn.grid(row=1, column=0, columnspan=3, padx=(24, 8), pady=5, sticky="w")
        chrome_extension_port_label.grid(row=2, column=0, padx=(24, 8), pady=(4, 12), sticky="w")
        chrome_extension_port_textbox.grid(row=2, column=1, padx=8, pady=(4, 12), sticky="ew")
        chrome_extension_port_set_btn.grid(row=2, column=2, padx=(8, 24), pady=(4, 12), sticky="e")

        discord_presence_frame.grid(row=1, column=0, padx=8, pady=(4, 8), sticky="ew")
        discord_presence_title.grid(row=0, column=0, columnspan=4, padx=8, pady=(10, 6), sticky="w")
        enable_discord_presence_btn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        discord_presence_show_playing_btn.grid(row=1, column=1, columnspan=3, padx=8, pady=5, sticky="w")
        discord_idle_presence_wording_label.grid(row=2, column=0, padx=(24, 8), pady=(4, 12), sticky="w")
        discord_idle_presence_wording_textbox.grid(row=2, column=1, padx=8, pady=(4, 12), sticky="ew")
        discord_idle_presence_wording_set_btn.grid(row=2, column=2, padx=8, pady=(4, 12), sticky="e")
        discord_idle_presence_wording_default_btn.grid(row=2, column=3, padx=(0, 24), pady=(4, 12), sticky="e")
        
        # ══════════ Layout: Version Info Tab ══════════
        ytdlp_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(10, 4), sticky="ew")
        ytdlp_title.grid(row=0, column=0, padx=8, pady=(10, 6), sticky="w")

        ytdlp_current_versions_frame.grid(row=1, column=0, padx=(24, 4), pady=5, sticky="ew")
        ytdlp_latest_versions_frame.grid(row=1, column=1, padx=(4, 24), pady=5, sticky="ew")
        go_ytdlp_web.grid(row=2, column=1, padx=(4, 24), pady=(5, 12), sticky="e")
        auto_update_ytdlp_btn.grid(row=2, column=0, padx=(24, 4), pady=(5, 12), sticky="w")
        ytdlp_use_nightly_build_checkbtn.grid(row=2, column=0, padx=(154, 4), pady=(5, 12), sticky="w")
        
        player_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        player_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        player_current_versions_frame.grid(row=1, column=0, padx=(24, 4), pady=5, sticky="ew")
        player_latest_versions_frame.grid(row=1, column=1, padx=(4, 24), pady=5, sticky="ew")
        go_player_web.grid(row=2, column=1, padx=(4, 24), pady=(5, 12), sticky="e")

        # Version sub-frame layouts
        ytdlp_current_versions_frame_title.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        ytdlp_ver_current_label.grid(row=1, column=0, padx=13, pady=(0, 8), sticky="w")
        ytdlp_latest_versions_frame_title.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        ytdlp_ver_lastest_label.grid(row=1, column=0, padx=13, pady=(0, 8), sticky="w")

        player_current_versions_frame_title.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        player_ver_current_label.grid(row=1, column=0, padx=13, pady=(0, 8), sticky="w")
        player_latest_versions_frame_title.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        player_ver_latest_label.grid(row=1, column=0, padx=13, pady=(0, 8), sticky="w")

        auto_check_ver_btn.grid(row=2, column=0, columnspan=2, padx=20, pady=(8, 10), sticky="w")

        ####### quick init frame #########

        # ── Quick Init Header Card ──
        header_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2B2B2B', corner_radius=8)
        header_frame.grid_columnconfigure(0, weight=1)
        header_title = ctk.CTkLabel(header_frame, text='  \u25b8 Quick Startup', font=('Arial', 15, 'bold'), text_color='#90D080', anchor='w')
        header_title.grid(row=0, column=0, padx=8, pady=(10, 6), sticky="w")
        init_toggle_quickstartup_checkbtn = ctk.CTkCheckBox(header_frame, text='Enable quick startup', variable=init_toggle_quickstartup, command=setting_init_toggle_quickstartup,
                                                              fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 13))
        init_toggle_quickstartup_checkbtn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        init_quick_startup_mode_text = ctk.CTkTextbox(header_frame, font=('Arial', 14), height=25, text_color='#C8C8C8', fg_color='#1a1a1a', corner_radius=6)
        init_quick_startup_mode_text.grid(row=2, column=0, padx=12, pady=(4, 12), sticky="ew")
        init_quick_startup_mode_text.configure(state='disabled')
        header_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(10, 4), sticky="ew")

        # ── Search Card ──
        search_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2B2B2B', corner_radius=8)
        search_frame.grid_columnconfigure((0,1), weight=1)
        init_search_btn = ctk.CTkRadioButton(search_frame, text='  \u25b8 Search', variable=init_quickstartup_mode, value='search', command=init_search_select,
                                              text_color='#E0C48C', text_color_disabled='#E0C48C',
                                              fg_color='#E0C48C', hover_color='#E0C48C', border_color='#E0C48C',
                                              font=('Arial', 15, 'bold'))
        init_search_btn.grid(row=0, column=0, columnspan=2, padx=8, pady=(7, 3), sticky="w")
        init_search_entry = ctk.CTkEntry(search_frame, font=('Arial', 14), width=14, placeholder_text='Quick Startup search query')
        init_search_entry.grid(row=1, column=0, columnspan=2, padx=12, pady=3, sticky="ew")
        init_search_set_btn = ctk.CTkButton(search_frame, text='Set Init Search', command=init_search_set, width=160,
                                              text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        init_search_set_btn.grid(row=2, column=0, columnspan=2, padx=12, pady=(2, 8), sticky="ew")
        search_frame.grid(row=1, column=0, padx=(16, 4), pady=4, sticky="nsew")

        # ── Local Folder Card ──
        local_folder_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2B2B2B', corner_radius=8)
        local_folder_frame.grid_columnconfigure((0,1), weight=1)
        init_local_folder_btn = ctk.CTkRadioButton(local_folder_frame, text='  \u25b8 Local Folder', variable=init_quickstartup_mode, value='local_playlist', command=init_local_playlist,
                                                     text_color='#C0A0E0', text_color_disabled='#C0A0E0',
                                                     fg_color='#C0A0E0', hover_color='#C0A0E0', border_color='#C0A0E0',
                                                     font=('Arial', 15, 'bold'))
        init_local_folder_btn.grid(row=0, column=0, columnspan=2, padx=8, pady=(7, 3), sticky="w")
        init_select_local_folder_btn = ctk.CTkButton(local_folder_frame, text='Select Folder', command=init_select_local_folder, width=160,
                                                       text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        init_select_local_folder_btn.grid(row=1, column=0, columnspan=2, padx=12, pady=(3, 8), sticky="ew")
        local_folder_frame.grid(row=2, column=0, padx=(16, 4), pady=(4, 10), sticky="nsew")

        # ── Playlist Card ──
        playlist_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2B2B2B', corner_radius=8)
        playlist_frame.grid_columnconfigure((0,1), weight=1)
        init_playlist_btn = ctk.CTkRadioButton(playlist_frame, text='  \u25b8 Playlist', variable=init_quickstartup_mode, value='playlist', command=init_playlist_select,
                                                text_color='#80C8E0', text_color_disabled='#80C8E0',
                                                fg_color='#80C8E0', hover_color='#80C8E0', border_color='#80C8E0',
                                                font=('Arial', 15, 'bold'))
        init_playlist_btn.grid(row=0, column=0, columnspan=2, padx=8, pady=(7, 3), sticky="w")

        playlist_options_frame = ctk.CTkFrame(
            playlist_frame,
            fg_color='#242424',
            corner_radius=6,
            border_width=1,
            border_color='#3A3A3A'
        )
        playlist_options_frame.grid_columnconfigure((0,1), weight=1)

        init_yt_playlist_btn = ctk.CTkRadioButton(
            playlist_options_frame,
            text='YouTube Playlist',
            variable=init_quickstartup_playlist_mode,
            value='yt_playlist',
            command=init_yt_playlist_select,
            text_color='#C8C8C8',
            font=('Arial', 13),
            height=18,
            radiobutton_width=16,
            radiobutton_height=16
        )
        init_yt_playlist_btn.grid(row=0, column=0, padx=(12, 4), pady=(7, 3), sticky="w")

        init_playlist_like_btn = ctk.CTkRadioButton(
            playlist_options_frame,
            text='Liked',
            variable=init_quickstartup_playlist_mode,
            value='like',
            command=init_playlist_like_select,
            text_color='#C8C8C8',
            font=('Arial', 13),
            height=18,
            radiobutton_width=16,
            radiobutton_height=16
        )
        init_playlist_like_btn.grid(row=2, column=0, columnspan=2, padx=12, pady=3, sticky="w")

        init_playlist_sub_btn = ctk.CTkRadioButton(
            playlist_options_frame,
            text='Subscriptions',
            variable=init_quickstartup_playlist_mode,
            value='sub',
            command=init_playlist_sub_select,
            text_color='#C8C8C8',
            font=('Arial', 13),
            height=18,
            radiobutton_width=16,
            radiobutton_height=16
        )
        init_playlist_sub_btn.grid(row=3, column=0, columnspan=2, padx=12, pady=3, sticky="w")

        init_playlist_recommendation_btn = ctk.CTkRadioButton(
            playlist_options_frame,
            text='Recommendation',
            variable=init_quickstartup_playlist_mode,
            value='home',
            command=init_playlist_recommendation_select,
            text_color='#C8C8C8',
            font=('Arial', 13),
            height=18,
            radiobutton_width=16,
            radiobutton_height=16
        )
        init_playlist_recommendation_btn.grid(row=4, column=0, columnspan=2, padx=12, pady=(3, 7), sticky="w")

        init_playlist_combobox = ctk.CTkComboBox(playlist_options_frame, font=('Arial', 14), width=14, state='readonly')
        init_playlist_combobox.grid(row=0, column=1, padx=(4, 12), pady=(7, 3), sticky="ew")
        init_get_playlist_btn = ctk.CTkButton(playlist_options_frame, text='Get Playlist', command=init_playlist_get, width=100,
                                               text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        init_get_playlist_btn.grid(row=1, column=0, padx=(12, 4), pady=3, sticky="ew")
        init_playlist_set_btn = ctk.CTkButton(playlist_options_frame, text='Set Playlist', command=init_playlist_set, width=100,
                                               text_color='white', font=('Arial', 14, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        init_playlist_set_btn.grid(row=1, column=1, padx=(4, 12), pady=3, sticky="ew")
        playlist_options_frame.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 8), sticky="nsew")
        playlist_frame.grid(row=1, column=1, rowspan=2, padx=(4, 16), pady=(4, 10), sticky="nsew")


        # ══════════ Layout: Hotkeys Tab ══════════
        hotkey_set_keymem_frame.grid(row=0, column=0, padx=16, pady=(10, 4), sticky="ew")
        hotkey_playback_frame.grid(row=1, column=0, padx=16, pady=4, sticky="ew")
        hotkey_mode_frame.grid(row=2, column=0, padx=16, pady=4, sticky="ew")
        hotkey_volume_frame.grid(row=3, column=0, padx=16, pady=4, sticky="ew")
        hotkey_player_frame.grid(row=4, column=0, padx=16, pady=(4, 10), sticky="ew")

        hotkey_set_keymem_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        hotkey_set_keymem_function_combobox.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        hotkey_set_keymem_startlisten_btn.grid(row=1, column=1, padx=8, pady=5, sticky="e")
        hotkey_set_keymem_set_default_btn.grid(row=2, column=0, columnspan=2, padx=12, pady=(4, 12), sticky="ew")

        hotkey_playback_frame_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        hotkey_playback_play_pause_label.grid(row=1, column=0, padx=(24, 8), pady=4, sticky="w") 
        hotkey_playback_play_pause_textbox.grid(row=1, column=1, padx=(8, 24), pady=4, sticky="e")
        hotkey_playback_stop_label.grid(row=2, column=0, padx=(24, 8), pady=4, sticky="w")
        hotkey_playback_stop_textbox.grid(row=2, column=1, padx=(8, 24), pady=4, sticky="e")
        hotkey_playback_next_label.grid(row=3, column=0, padx=(24, 8), pady=4, sticky="w")
        hotkey_playback_next_textbox.grid(row=3, column=1, padx=(8, 24), pady=4, sticky="e")
        hotkey_playback_prev_label.grid(row=4, column=0, padx=(24, 8), pady=(4, 12), sticky="w")
        hotkey_playback_prev_textbox.grid(row=4, column=1, padx=(8, 24), pady=(4, 12), sticky="e")

        hotkey_mode_frame_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        hotkey_mode_repeat_label.grid(row=1, column=0, padx=(24, 8), pady=4, sticky="w")
        hotkey_mode_repeat_textbox.grid(row=1, column=1, padx=(8, 24), pady=4, sticky="e")
        hotkey_mode_random_label.grid(row=2, column=0, padx=(24, 8), pady=4, sticky="w")
        hotkey_mode_random_textbox.grid(row=2, column=1, padx=(8, 24), pady=4, sticky="e")
        hotkey_mode_continuous_label.grid(row=3, column=0, padx=(24, 8), pady=(4, 12), sticky="w")
        hotkey_mode_continuous_textbox.grid(row=3, column=1, padx=(8, 24), pady=(4, 12), sticky="e")

        hotkey_volume_frame_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        hotkey_volume_up_label.grid(row=1, column=0, padx=(24, 8), pady=4, sticky="w")
        hotkey_volume_up_textbox.grid(row=1, column=1, padx=(8, 24), pady=4, sticky="e")
        hotkey_volume_down_label.grid(row=2, column=0, padx=(24, 8), pady=(4, 12), sticky="w")
        hotkey_volume_down_textbox.grid(row=2, column=1, padx=(8, 24), pady=(4, 12), sticky="e")

        hotkey_player_frame_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        hotkey_toggle_minimize_label.grid(row=1, column=0, padx=(24, 8), pady=(4, 12), sticky="w")
        hotkey_toggle_minimize_textbox.grid(row=1, column=1, padx=(8, 24), pady=(4, 12), sticky="e")





def progressbar_hook(d):
    global downloadhooktext
    try:
        downloadhooktext.set(f'Downloading ... {int((d["downloaded_bytes"]/d["total_bytes"])*100)}%')
    except:downloadhooktext.set(f'Downloading ... ')








def page_control(mode):
    '''
    mode == 1: next page, mode == 2: prev page'''
    if mode == 1:
        nextpageresult = media_list_page_controller.next_page()
    elif mode == 2:
        nextpageresult = media_list_page_controller.prev_page()
    if nextpageresult == -1:
        ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','page still loading, please wait...'))
    elif nextpageresult == -2:
        ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','we got an error while loading the page, please refer to the log for more details'))
    elif nextpageresult == -3:
        ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','your current video list does not support page control!'))


def history_control(mode:int):
    '''
    mode == 1: forward history, mode == 2: backward history
    '''
    
    ui_queue.put(lambda:history_back_btn.configure(state='disabled'))
    ui_queue.put(lambda:history_forward_btn.configure(state='disabled'))

    def _history_thread():
        global media_data_list,loadingplaylist,playing_vid_mode
        try:
            if loadingplaylist:
                messagebox.showinfo(f'JaTubePlayer {ver}','playlist is still loading, please wait...')
                return
            
            if mode == 2:
                if history_page_handler.current_index == 0:
                    record_result = media_list_page_controller._record_history()
                    if record_result:
                        history_page_handler.current_index = 1
                history_template_dict = history_page_handler.read_history_backward()
            else:
                history_template_dict = history_page_handler.read_history_forward()

            
            if history_template_dict:
                insert_textbox(playlist_name_textbox,"⏳loading")
                media_type = history_template_dict.get("media_type")
                match media_type:
                    case MediaType.STARRED_VIDEO:
                        playing_vid_mode = 4
                    case MediaType.DIRECT_URL_DROP:
                        playing_vid_mode = 3
                    case MediaType.FOLDER:
                        playing_vid_mode = 2
                    case _:
                        playing_vid_mode = 0
                    
                media_list_page_controller.history_page_init_and_reload(history_template_dict.get("media_data"),
                                                                        media_type=media_type)
                log_handle(
                    content=f"History page loaded with {history_template_dict.get("media_data", []).vid_url} items",
                    errtype='info',
                    component='history',
                )
                media_data_list = media_list_page_controller.media_data_list
                playing_url = history_template_dict.get("current_playing",None)
                if playing_url:
                    if media_type == 4: # Folder
                        load_thread_queue.put((playing_url,None))
                    else:
                        load_thread_queue.put((None,playing_url))
                insert_textbox(playlist_name_textbox, history_template_dict.get("playlistname",""))
                if playing_url in media_data_list.vid_url:
                    print(f"found playing_url in media_data_list.vid_url: {playing_url} adwiohiopadhwhdwiopahiopwadiophwadh;iowadiohwadhio;awoidhahwiodhiowahouida;uioswdhna;uiobg;ouiadwoual;bsgwd;oulajgbfwd;ouaghwsd;uoAHNWS;RODFULAHW;DPUOHA;/LUODH;OALUHWSDNUOAL;HNWSDOAL;UHS;DJLNA;LJWND\nDWAGUIWUIAGDGWUIADGLUIAWDGYUIWDGLIAGWIDAWUIDUIAWDUILAWUDAWGLUIDGALWIUDGWALIUDGLIAYUGWDLIAUSDIKAGFUIAGHWDUIOA;OWU;EIOFJ;PASJF;OSJEGHIL;ESJFGHI.")
                    global selected_song_number
                    selected_song_number = media_data_list.vid_url.index(playing_url)
                    thumbnail_loader.select_item(selected_song_number)

                if star_vid_handle.search(playing_url):
                    star_btn_ui_functions.star_starred()
                else:
                    star_btn_ui_functions.star_regular()
                            

        except Exception as e:
            log_handle(
                content=f"Error in _history_thread: {e}",
                errtype='error',
                component='history',
            )
        finally:
            ui_queue.put(lambda:history_back_btn.configure(state='normal'))
            ui_queue.put(lambda:history_forward_btn.configure(state='normal'))

    thread = threading.Thread(target=_history_thread)
    thread.start()







@check_internet
def get_user_playlists(forcereload:bool=False):
    '''
    will get the user playlists and update the userplaylistcombobox with the playlist names
    '''
    global user_playlists_name,user_playlists_selected_name
    if not account_handler.check_aes_key():
        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Invalid AES key, please clear account data and restart the app'))
        return
    
    if account_handler.check_cookie_exist() == False:
        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','please set your login first'))
        return

    def _get_user_playlists_thread():
        global user_playlists_name,user_playlists_selected_name
        media_list_page_controller.youtube_init_and_reload(media_data_list=media_data_list, page=playlist_type.PLAYLISTS)
        for playlist_dict in media_list_page_controller.user_playlist_dict_list:
            user_playlists_name.append(playlist_dict['name'])
        ui_queue.put(lambda: userplaylistcombobox.configure(values=user_playlists_name))
        ui_queue.put(lambda: userplaylistcombobox.set(''))
        ui_queue.put(lambda: userplaylistcombobox._open_dropdown_menu())

        ui_queue.put(lambda: enter_playlist_btn.configure(state='normal'))
        ui_queue.put(lambda: playlistlabel.configure(text='📁'))
    
    if (user_playlists_selected_name := userplaylistcombobox.get()) == '' or forcereload:

        ui_queue.put(lambda: playlistlabel.configure(text='⏳'))
        ui_queue.put(lambda: enter_playlist_btn.configure(state='disabled'))
        user_playlists_name.clear()

        thread = threading.Thread(target=_get_user_playlists_thread)
        thread.start()
        

    else:
        sel_idx = user_playlists_name.index(user_playlists_selected_name)
        sel_url = media_list_page_controller.user_playlist_dict_list[sel_idx]['url']
        user_playlists_selected_id = sel_url.split('list=')[1]
        get_youtube_playlists(user_playlists_selected_id,sel_idx)

        

@check_internet
def get_youtube_playlists(playlistID: Literal["sub", "like","home"] | str,
                          sel_idx: int = 0,
                          playlist_name:str=''):
    '''
    will get playlist video with the platlistID, or "sub" for user subscriptions, or "like" for user liked videos
    '''
    if not account_handler.check_aes_key():
        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Invalid AES key, please clear account data and restart the app'))
        return
    if account_handler.check_cookie_exist() == False and playlistID != "home":
        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','please set your login first'))
        return


    global insert_treeview_quene,selected_song_number,playing_vid_mode,loadingplaylist,media_data_list,playlist_type
    selected_song_number = None
    playing_vid_mode = 0
    if loadingplaylist:
        if not messagebox.askokcancel(f'JaTubePlayer {ver}','player is still loading, sure to load again?'):
            return
        
    loadingplaylist = True
    log_handle(
        content=f"start to get playlist videos with playlistID: {playlistID}",
        errtype='info',
        component='playlist',
    )

    if playlistID == 'sub':
        playlistname = 'Subscriptions'
    elif playlistID == 'like':
        playlistname = 'Liked Videos'
    elif playlistID == 'home':
        playlistname = 'Recommend'
    else:

        if not playlist_name:
            playlistname = media_list_page_controller.user_playlist_dict_list[sel_idx]['name']
        else:
            playlistname = playlist_name


    thumbnail_loader.clear_thumbnails()
    _prev_playlistname = playlist_name_textbox.get(0.0,tk.END).strip()

    insert_textbox(playlist_name_textbox, f"⏳loading: {playlistname}")
    ui_queue.put(lambda: page_num_label.configure(text=''))

    def _get_youtube_playlists_thread(playlistID:str):
        global loadingplaylist,media_data_list,media_list_page_controller
        try:
                    
            if playlistID in ['sub','like','home']:
                page_dict = {
                    'sub': playlist_type.SUBSCRIPTIONS,
                    'like': playlist_type.LIKED,
                    'home': playlist_type.HOME
                }
                media_list_page_controller.youtube_init_and_reload(media_data_list=media_data_list,
                                                                page=page_dict[playlistID],
                                                                prev_playlist_name=_prev_playlistname)
            else:
                media_list_page_controller.youtube_init_and_reload(media_data_list=media_data_list,
                                                                page=playlist_type.PLAYLIST,
                                                                playlist_id=playlistID,
                                                                prev_playlist_name=_prev_playlistname)
            media_data_list = media_list_page_controller.media_data_list

            insert_textbox(playlist_name_textbox, f"{playlistname}")
            

        except Exception as e:
            log_handle(
                content=f"Error while getting playlist videos: {e}",
                errtype='error',
                component='playlist',
            )
            ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}', f'Error while getting playlist videos: {err}'))
        finally:
            loadingplaylist = False
    thread = threading.Thread(args=(playlistID,), target=_get_youtube_playlists_thread, daemon=True)
    thread.start()




@check_internet
def youtube_search_thread():
    global playing_vid_mode,loadingplaylist,selected_song_number,media_data_list
    playing_vid_mode = 0
    loadingplaylist = True
    if searchentry.get() != '':
        ui_queue.put(lambda: searchlistlabel.configure(text='⏳'))
        selected_song_number = None
        
        media_list_page_controller.search_init_and_reload(
            media_data_list=media_data_list,
            searchentry=searchentry.get(),
            yt_dlp=yt_dlp,
            ytdlp_log_handle=ytdlp_log_handle,
            cookie=account_handler.get_cookie() if ytdlp_use_cookie.get() else None
        )
        media_data_list = media_list_page_controller.media_data_list

        insert_textbox(playlist_name_textbox, f"Search: {searchentry.get()}")
        star_btn_ui_functions.star_regular()



        
    else:
        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','entry cant be empty!'))
    loadingplaylist = False
    ui_queue.put(lambda: searchlistlabel.configure(text='🔍'))

@check_internet
def youtube_search(event=None):
    if loadingplaylist == False or loadingplaylist == True and messagebox.askokcancel(f'JaTubePlayer {ver}','player is still loading, sure to load again?'):
        threading.Thread(daemon=True,target=youtube_search_thread).start()

@check_internet
def get_starred_vid(event=None):
    global insert_treeview_quene,star_vid_handle,selected_song_number,playing_vid_mode,loadingplaylist,media_data_list
    if loadingplaylist == False or loadingplaylist == True and messagebox.askokcancel(f'JaTubePlayer {ver}','player is still loading, sure to load again?'):
        selected_song_number = None
        playing_vid_mode = 4
        loadingplaylist = True
        log_handle(
            content="start to get starred videos",
            errtype='info',
            component='playlist',
        )
        _prev_playlistname = playlist_name_textbox.get(0.0,tk.END).strip()
        insert_textbox(playlist_name_textbox, "Starred Videos")
        ui_queue.put(lambda: page_num_label.configure(text=''))
        star_btn_ui_functions.star_regular()
        
        loadingplaylist = False
                
        media_list_page_controller.star_video_init_and_reload(
            star_vid_handle,
            prev_playlist_name=_prev_playlistname)
        media_data_list = media_list_page_controller.media_data_list
            

def switch_starred_vid(event=None):
    global star_vid_handle,selected_song_number,playing_vid_mode,playing_vid_info_dict,media_data_list
    
    if playing_vid_mode == 0 or playing_vid_mode == 2 or playing_vid_mode == 4:
        if selected_song_number == None:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please select a video from the playlist first!'))
            return

        
    if playing_vid_mode == 0 or playing_vid_mode == 4:
        url_or_path = media_data_list.vid_url[selected_song_number]
        title = media_data_list.playlisttitles[selected_song_number]
        thumb = media_data_list.playlist_thumbnails[selected_song_number]
        channel = media_data_list.playlist_channel[selected_song_number]
    elif playing_vid_mode == 1:
        url_or_path = playing_title_textbox.get(0.0,tk.END).strip()
        title = os.path.basename(url_or_path)
        thumb = None
        channel = 'local file'
    elif playing_vid_mode == 2:
        url_or_path = media_data_list.vid_url[selected_song_number]
        title = media_data_list.playlisttitles[selected_song_number]
        thumb = None
        channel = 'local file'
    elif playing_vid_mode == 3:
        url_or_path = playing_vid_info_dict['original_url']
        title = playing_vid_info_dict['title']
        try:thumb = playing_vid_info_dict['thumbnails'][-1]['url'] if playing_vid_info_dict['thumbnails'] else None
        except:thumb = playing_vid_info_dict['thumbnail'] if playing_vid_info_dict['thumbnail'] else None
        finally:thumb = thumb if thumb else None
        channel = playing_vid_info_dict['channel']
        
            

    if star_vid_handle.search(url_or_path):
        star_vid_handle.remove(url_or_path)
        star_btn_ui_functions.star_regular()

        ui_queue.put(lambda:ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='Removed from starred videos', duration='short', icon=icondir))

        if playing_vid_mode == 4:
            try:
                item_id = playlisttreebox.get_children()[selected_song_number%50]
                media_list_page_controller.clear_selected(selected_idx=selected_song_number, 
                                                            selected_tree_ID=item_id)
                media_data_list.vid_url.pop(selected_song_number)
                media_data_list.playlisttitles.pop(selected_song_number)
                media_data_list.playlist_thumbnails.pop(selected_song_number)
                media_data_list.playlist_channel.pop(selected_song_number)
                
            except Exception as e:
                log_handle(
                    content=str(e),
                    errtype='error',
                    component='playlist',
                )
                
        
    else:#add
        if "twitch.tv" in url_or_path.lower():
            if "videos" in url_or_path.lower():
                if not messagebox.askyesno(f'JaTubePlayer {ver}','Twitch VOD detected,The VOD might be removed when Twitch expiring the VOD link, do you still want to add it to starred video?'):
                    return
            elif "clip" not in url_or_path.lower():
                if not messagebox.askyesno(f'JaTubePlayer {ver}','This might be a Twitch streamer, if the streamer is not streaming when you try to play the video, it might not work, do you still want to add it to starred video?'):
                    return

                
        res = star_vid_handle.add(url =url_or_path,
                        thumb=thumb,
                        title=title,
                        channel=channel,
                        )
        if res:
            star_btn_ui_functions.star_starred()
            ui_queue.put(lambda:ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='Added to starred videos', duration='short', icon=icondir))
        else:
            ui_queue.put(lambda:ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='Failed to add to starred videos', duration='short', icon=icondir))


    



def update_playing_pos_local_and_chrome():
    global stoped,finish_break, pos_for_label,volume,selected_song_number,stream
    stoped = False
    finish_break = False
    while not stoped:  
        
        try:
            time.sleep(0.1) 
            if player.time_pos != None:
                pos = player.time_pos
            else:
                pos = 0.1


            if player.duration != None:
                length = player.duration
            else:
                length = -1
            ui_queue.put(lambda l=length: player_position_scale.configure(to=l, from_=0.1))
            ui_queue.put(lambda p=pos: player_position_scale.set(p))  ## set pos scale postion
            h_,m_,s_ = lenght_convertor(math.floor(pos))
            h,m,s = lenght_convertor(math.floor(length))
            ui_queue.put(lambda hh=h, mm=m, ss=s: player_song_length_label.configure(text=f' / {hh:02}:{mm:02}:{ss:02}'))
            ui_queue.put(lambda hh_=h_, mm_=m_, ss_=s_: pos_for_label.set(f'{hh_:02}:{mm_:02}:{ss_:02}'))   ### set pos str
            if playing_vid_mode == 3 and stream:

                if show_cache.get():
                    try:
                        cache = player.demuxer_cache_duration
                        if cache:
                            ui_queue.put(lambda c=cache: player_loading_label.configure(text=f'🔴{c:.1f}s', text_color='red'))
                        else:
                            ui_queue.put(lambda: player_loading_label.configure(text="🔴streaming...", text_color='red'))
                    except:
                        ui_queue.put(lambda: player_loading_label.configure(text="🔴streaming...", text_color='red'))
                else:
                    ui_queue.put(lambda: player_loading_label.configure(text="🔴streaming...", text_color='red'))
            else:
                if show_cache.get():
                    try:
                        cache = player.demuxer_cache_duration
                        if cache:
                            ui_queue.put(lambda c=cache: player_loading_label.configure(text=f'cache {c:.1f}s', text_color='#FF6B35'))
                        else:
                            ui_queue.put(lambda: player_loading_label.configure(text="", text_color='#FF6B35'))
                    except:
                        ui_queue.put(lambda: player_loading_label.configure(text="", text_color='#FF6B35'))
                else:
                    ui_queue.put(lambda: player_loading_label.configure(text="", text_color='#FF6B35'))
            if player.eof_reached and length != -1: ## video ends
                if selected_song_number != None:

                    if playing_vid_mode in [1,2,4]:
                        if player_mode_selector.get() =='continue':
                            if playing_vid_mode != 1:
                                playprevnext(1)
                                break
                            
                        elif player_mode_selector.get() =='replay':
                            player.seek(0.1,reference='absolute')
                            root.after(200, lambda: setattr(player, 'pause', False))

                        elif player_mode_selector.get() =='random':
                            player.stop()
                            media_idx = media_list_page_controller.random_media(selected_song_number)
                            if media_idx == -2:
                                ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','The playlist is still loading, please wait and try again'))
                                break
                            elif media_idx == -1:
                                log_handle(
                                    content="Failed to select a random video after playback ended",
                                    errtype="error",
                                    component="player",
                                )
                                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Failed to select a random video, Please refer to log for more details'))
                                break
                            else:
                                selected_song_number = media_idx
                                download_and_play()


                        if star_vid_handle.search(media_data_list.vid_url[selected_song_number]):
                            ui_queue.put(lambda: star_btn_ui_functions.star_starred())
                        else:
                            ui_queue.put(lambda: star_btn_ui_functions.star_regular())

                elif playing_vid_mode in [0,3]:### MPV option keep_open
                    
                    if player_mode_selector.get() =='replay':# =  3 chrome , =0 for chrome but added a video
                        player.seek(0.1,reference='absolute')
                        root.after(200, lambda: setattr(player, 'pause', False))
                    elif player_mode_selector.get() =='continue' and len(media_data_list.vid_url) > 0:
                        stop_playing_video()
                        ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','Please choose a video again!'))
                        
                elif playing_vid_mode == 2:ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer{ver}','Choose a video again'))
            if stoped: 
                finish_break = True
                break
        except:pass



def update_playing_pos_yt():

    try:
        global stoped,finish_break, pos_for_label,volume,selected_song_number, stream, playing_vid_info_dict

        stoped = False
        finish_break = False
 
        while not stoped:

            time.sleep(0.1) 
            if player.time_pos != None:
                pos = player.time_pos
            else:
                pos = 0.1

            if player.duration != None:
                length = player.duration
            else:
                length = -1

            ui_queue.put(lambda l=length: player_position_scale.configure(to=l, from_=0.1))
            ui_queue.put(lambda p=pos: player_position_scale.set(p if player.time_pos != None else 0.1))  ## set pos scale postion
            h_,m_,s_ = lenght_convertor(math.floor(pos))
            h,m,s = lenght_convertor(math.floor(length))
            ui_queue.put(lambda hh=h, mm=m, ss=s: player_song_length_label.configure(text=f' / {hh:02}:{mm:02}:{ss:02}'))
            ui_queue.put(lambda hh_=h_, mm_=m_, ss_=s_: pos_for_label.set(f'{hh_:02}:{mm_:02}:{ss_:02}'))   ### set pos str

            if playing_vid_info_dict == None or playing_vid_info_dict.get('live_status') != 'is_live':
                if show_cache.get():
                    try:
                        cache = player.demuxer_cache_duration
                        if cache:
                            ui_queue.put(lambda c=cache: player_loading_label.configure(text=f'cache {c:.1f}s', text_color='#FF6B35'))
                    except:
                        pass
                else:ui_queue.put(lambda: player_loading_label.configure(text="", text_color='#FF6B35'))
                if player.eof_reached and  length != -1: ## video ends
                    log_handle(
                        content=f'video ended detected in yt thread , now do {player_mode_selector.get()}',
                        errtype='info',
                        component='player',
                    )
                    if selected_song_number != None:

                        if player_mode_selector.get() =='continue':
                            playprevnext(1)()
                            break
                            
                        elif player_mode_selector.get() =='replay':
                            player.seek(0.1,reference='absolute')
                            root.after(200, lambda: setattr(player, 'pause', False))
                        elif player_mode_selector.get() =='random':
                            player.stop()
                            media_idx = media_list_page_controller.random_media(selected_song_number)
                            if media_idx == -2:
                                ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','The playlist is still loading, please wait and try again'))
                                break
                            elif media_idx == -1:
                                log_handle(
                                    content="Failed to select a random video after playback ended",
                                    errtype="error",
                                    component="player",
                                )
                                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Failed to select a random video, Please refer to log for more details'))
                                break
                            else:
                                selected_song_number = media_idx
                                download_and_play()



                            if star_vid_handle.search(media_data_list.vid_url[selected_song_number]):
                                ui_queue.put(lambda: star_btn_ui_functions.star_starred())
                            else:
                                ui_queue.put(lambda: star_btn_ui_functions.star_regular())

                    else:
                        stop_playing_video()
                        ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer{ver}','Choose a video again'))

            else:
                if show_cache.get():
                    try:
                        cache = player.demuxer_cache_duration
                        if cache:
                            ui_queue.put(lambda c=cache: player_loading_label.configure(text=f'🔴cache {c:.1f}s', text_color='red'))
                        else:
                            ui_queue.put(lambda: player_loading_label.configure(text='🔴streaming...', text_color='red'))
                    except:
                        ui_queue.put(lambda: player_loading_label.configure(text='🔴streaming...', text_color='red'))
                else:
                    ui_queue.put(lambda: player_loading_label.configure(text='🔴streaming...', text_color='red'))
                
            if stoped: 
                finish_break = True
                break

    except Exception as e:
        log_handle(
            content=f"Error in update_playing_pos_yt: {e}",
            errtype='error',
            component='player',
        )
        

            


 
def scaler_start_seek(event):
    try:
        player.pause = True
        userposition = math.floor(event)
        player.seek(userposition, reference='absolute+exact')
        log_handle(
            content=f"seek to {userposition}",
            errtype='info',
            component='player',
        )
        pauseStr.set('||')
    except:pass


def scaler_finish_seek(event):
    try:
        player.pause = False
    except:pass


seeking = False
def arrow_release(event):
    global seeking,userposition
    if not seeking:
        userposition = None#####   make it continous

userposition = None
def set_position_keyboard_thread(mode):#1 == backward 2 == forward
    global seeking,userposition
    log_handle(
        content=f"{seeking} {userposition}",
        errtype='info',
        component='player',
    ) 
    try:
        if str(root.focus_get()) != '.!entry' and player.duration != None and not seeking:
            seeking = True
            if mode == 1:
                try:
                    if not userposition :userposition = player.time_pos

                    userposition = max(0, userposition - 5)##not fk it to the negative lol

                    player.seek(userposition, reference='absolute+exact')
                except Exception as e:log_handle(
                                          content=str(e),
                                          errtype='error',
                                          component='player',
                                      )
            elif mode == 2:
                try:
                    if not userposition :userposition = player.time_pos
                    userposition = min(player.duration - 1, userposition + 5)##not fk it to the end
                    player.seek(userposition, reference='absolute+exact')
                except Exception as e:log_handle(
                                          content=str(e),
                                          errtype='error',
                                          component='player',
                                      )
            time.sleep(0.2)
            seeking = False
    except Exception as e:
            log_handle(
                content=str(e),
                errtype='error',
                component='player',
            )
            seeking = False

def set_position_keyboard(mode):
    threading.Thread(daemon=True,target=lambda:set_position_keyboard_thread(mode)).start()    
def pause(mode):#1 == mouse/btn pause 2 == keyboard pause
    try:
        global paused
        if mode == 2 and str(root.focus_get()) == '.!entry':pass
        else:
            if player.duration != None:
                if paused == False:
                    player.pause = True
                    smtc.set_paused()
                    pauseStr.set('▶')
                    pausebutton.update()
                    paused = True
                else:

                    player.pause = False
                    if playing_vid_info_dict:
                        if playing_vid_info_dict.get('live_status') == 'is_live':
                            player.seek(player.duration, reference='absolute+exact')# move to live point
                    pauseStr.set('||')
                    smtc.set_playing()
                    pausebutton.update()
                    paused = False
    except:
        pass


def set_volume(value,mode = 0):
    if mode == 1:player_volume_scale.set(value)
    try:
        global volume
        volume = float(value)
        player.volume =int(max(volume,0))
    except AttributeError:pass
    except Exception as e:log_handle(
                              content=str(e),
                              errtype='error',
                              component='player',
                          )

def set_volume_wheel(event=None):

    if event.delta == 120:set_volume(player_volume_scale.get()+4,1)
    elif event.delta == -120:set_volume(int(player_volume_scale.get())-4,1)




def stop_playing_video():
    global stoped
    stoped = True
    try:discord_presence.idle()
    except:pass
    playing_title_textbox.configure(state='normal')
    playing_title_textbox.delete(1.0,tk.END)
    playing_title_textbox.configure(state='disabled')
    if selected_song_number is not None and playing_vid_mode in [0,2,4]:
        media_list_page_controller.remove_playing_tag()
    try:
        player.stop()
    except:pass

def playprevnext(direction:int)->None:
    '''
    direction:int = 1 -> next,
    direction:int = 2 -> previous
    '''
    global selected_song_number 
    PER_PAGE = 50
    if direction == 1:
        edge_index_per_page = 49
        edge_index_all_page = len(media_data_list.vid_url)-1

        edge_page_count = media_list_page_controller.total_page
        opposite_edge_page_count = 1

        opposite_edge_idx_all_page = 0
        page_direction_val = 1
        '''
        idx after change
        '''
    else:
        edge_index_per_page = 0
        edge_index_all_page = 0

        edge_page_count = 1
        opposite_edge_page_count = media_list_page_controller.total_page

        opposite_edge_idx_all_page = len(media_data_list.vid_url)-1
        page_direction_val = -1
        '''
        idx after change
        '''

    SELECTED_FOLLOW = media_data_list.current_playing_idx_num == selected_song_number 
    try:
        if media_data_list.current_playing_idx_num == -1:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','please select a video first'))
            return
        if loadingvideo == False or loadingvideo==True and messagebox.askokcancel(f'JaTubePlayer {ver}','The video is still loading, sure to load again?'):
            stop_playing_video()
            
            log_handle(
                content=f"[next]selected follow is {SELECTED_FOLLOW}, current playing idx is {media_data_list.current_playing_idx_num}, selected song number is {selected_song_number}",
                errtype='info',
                component='player',
            )
            if media_list_page_controller.total_page > 1:
                if media_data_list.current_playing_idx_num % PER_PAGE == edge_index_per_page or media_data_list.current_playing_idx_num == edge_index_all_page:
                    if direction == 1:
                        pageRes = media_list_page_controller.next_page(select_first_of_next_page=True,
                                                                    selected_follow=SELECTED_FOLLOW)
                    else:
                        pageRes = media_list_page_controller.prev_page(select_last_of_prev_page=True,
                                                                        selected_follow=SELECTED_FOLLOW)

                    if pageRes == 0:
                        log_handle(
                            content="successfully load the next page",
                            errtype='info',
                            component='player',
                        )
                        if media_data_list.current_media_page != 0:
                            
                            if media_data_list.current_media_page == edge_page_count:
                                media_data_list.current_media_page = opposite_edge_page_count
                            else:
                                media_data_list.current_media_page += page_direction_val

                            log_handle(
                                content=f"[next]current media page is {media_data_list.current_media_page}",
                                errtype='info',
                                component='player',
                            )

                    if pageRes == -1:
                        messagebox.showinfo(f'JaTubePlayer {ver}','The next page is still loading')
                        return
                    if pageRes == -2:
                        messagebox.showinfo(f'JaTubePlayer {ver}','Failed to load the next page, see log for more details')
                        return
                    if pageRes == -3:
                        messagebox.showinfo(f'JaTubePlayer {ver}','does not support next page for this source')
                        return

            if media_data_list.current_playing_idx_num == edge_index_all_page:
                media_data_list.current_playing_idx_num = opposite_edge_idx_all_page
                if SELECTED_FOLLOW:
                    selected_song_number = opposite_edge_idx_all_page - page_direction_val 
            else:    
                media_data_list.current_playing_idx_num  += page_direction_val
            
            if SELECTED_FOLLOW:
                cur_page_idx = media_data_list.current_playing_idx_num % 50
                root.after(50, lambda: playlisttreebox.selection_set(playlisttreebox.get_children()[cur_page_idx]))
                root.after(50, lambda: playlisttreebox.see(playlisttreebox.get_children()[cur_page_idx]))
                selected_song_number += page_direction_val
                

            if playing_vid_mode == 0:#classify local file and direct url
                load_thread_queue.put((None,media_data_list.vid_url[media_data_list.current_playing_idx_num]))
            elif playing_vid_mode == 4:
                if media_data_list.vid_url[media_data_list.current_playing_idx_num].startswith(("http://", "https://")) :
                    load_thread_queue.put((None,media_data_list.vid_url[media_data_list.current_playing_idx_num]))
                else:
                    load_thread_queue.put((media_data_list.vid_url[media_data_list.current_playing_idx_num],None))
            else:
                load_thread_queue.put((media_data_list.vid_url[media_data_list.current_playing_idx_num],None))

            if star_vid_handle.search(media_data_list.vid_url[media_data_list.current_playing_idx_num]):
                ui_queue.put(lambda: star_btn_ui_functions.star_starred())
            else:
                ui_queue.put(lambda: star_btn_ui_functions.star_regular())

            log_handle(
                content=f"[next]current playing idx is {media_data_list.current_playing_idx_num}, selected song number is {selected_song_number}",
                errtype='info',
                component='player',
            )
    except Exception as e:
        log_handle(
            content=f"Error in playprevnext(1): {e}",
            errtype='error',
            component='player',
        )
        messagebox.showerror(f'JaTubePlayer {ver}',f'An error occurred: {e}')





def load_thread():  ### add every try except to a new log system for next update
    """
    Note for direct url:for lists, only the top/playing video will be sent inside

    it is a queue based thread, so to load a video, just put the (file_path,direct_url) into the load_thread_queue

    if the the queue has more than 1 item, it will only accept the first item and ignored and remove.

    Note the thread only load ONE 2 args tuple (file_path,direct_url) at once
    
    directl url for youtube + chrome ext
    file_path for folder/file/dnd
    
    """
    global stoped, pos_thread, stream, playing_vid_url, playing_vid_info_dict, loadingvideo, force_stop_loading, subtitle_namelist, subtitle_urllist, subtitlecombobox

    while True:
        while load_thread_queue.empty():
            time.sleep(0.3)  ### wait for loading command
        log_handle(
            content=f"load thread got sth",
            errtype='info',
            component='player',
        )
        # start loading
        chosen_file, direct_url = load_thread_queue.get()

        current_idx = media_data_list.current_playing_idx_num if media_data_list.current_playing_idx_num != -1 else None

        try:
            
            ui_queue.put(lambda: media_list_page_controller.remove_playing_tag())
            
        except Exception as e:
            log_handle(
                content=f"Failed to remove playing tag: {e}",
                errtype='error',
                component='player',
            )

        log_handle(
            content=f"load thread got cmd {chosen_file}, {direct_url}",
            errtype='info',
            component='player',
        )
        force_stop_loading = False  # reset force stop loading bc it is a new load command

        while not load_thread_queue.empty():
            load_thread_queue.get()  # clear the queue

        if direct_url:
            direct_url = direct_url.split('&')[0]

        if (
            loadingvideo == True
            and messagebox.askokcancel(f'JaTubePlayer {ver}', 'The Video is already loading, Sure to load again?')
            or loadingvideo == False
        ):
            if direct_url and "playlist" in direct_url:
                messagebox.showerror(f"Jatubeplayer {ver}",
                                     "this is a playlist, you cannot play it!")
                continue
            create_mpv_player()

            ui_queue.put(lambda: media_list_page_controller.remove_playing_tag())

            if not chosen_file:
                loadingvideo = True

                stop_playing_video()
                ui_queue.put(lambda: player_loading_label.configure(text='⏳ loading...') if player_loading_label.cget('text') != 'retrying...' else None)
                ui_queue.put(lambda: playing_title_textbox.configure(state='normal'))
                ui_queue.put(lambda: playing_title_textbox.delete(1.0, tk.END))
                ui_queue.put(lambda: playing_title_textbox.configure(state='disabled'))
                player.volume = int(player_volume_scale.get())
                
                try:
                    if direct_url and playing_vid_mode == 3:
                        if check_internet_socket():
                            playing_vid_url = direct_url
                            ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg=f'Playing video from chrome\n{direct_url}', duration='short', icon=icondir)
                        else:
                            ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='Internet connection failed, please check your internet connection', duration='short', icon=icondir)
                            loadingvideo = False
                            continue

                    try:
                        final_url, playing_vid_info_dict = get_info(
                            target_url=direct_url,
                            loader=get_info_loader,
                            twitch_handler=twitch_handler
                        )

                        if final_url:
                            requested_formats = playing_vid_info_dict.get("requested_formats",[])
                            if requested_formats:
                                http_headers = dict(requested_formats[0].get("http_headers", {}))
                            else:
                                http_headers = dict(playing_vid_info_dict.get("http_headers", {}))

                            if http_headers:
                               player.http_header_fields = [
                                  f"{name}: {value}"
                                 for name, value in http_headers.items()
                               ]
                            # set mpv req size, with bitwise
                            player.curl_max_request_size = 1 << 20 
                            player.curl_buffer_size = 4 << 20

                            log_handle(
                                content=f"[headers] set {list(http_headers)}",
                                errtype='info',
                                component='player',
                            )
                            player.play(final_url)
                            subtitle_selection_idx.set(0)
                            subtitle_namelist = ['No subtitles']
                            subtitle_urllist = []

                            for sub in playing_vid_info_dict.get('subtitles').values():
                                try:
                                    if len(sub) == 7:
                                        subtitle_namelist.append(sub[6]['name'])
                                        subtitle_urllist.append(sub[6]['url'])
                                    
                                    ui_queue.put(lambda: subtitlecombobox.configure(values=subtitle_namelist))
                                    ui_queue.put(lambda: subtitlecombobox.set(subtitle_namelist[subtitle_selection_idx.get()]))
                                except Exception as e:
                                    log_handle(
                                        content=f"Error processing subtitle: {e}",
                                        errtype='error',
                                        component='player',
                                    )

                            log_handle(
                                content=f"Available subtitles: {subtitle_namelist}",
                                errtype='info',
                                component='player',
                            )

                            try:  ## try to make the vid play info somehow ytdlp fail to get info dict
                                if playing_vid_info_dict.get('live_status') == 'is_live':
                                    global stream
                                    stream = True
                                else:
                                    stream = False
                            except:
                                stream = False
                                log_handle(
                                    content='failed to get live status',
                                    errtype='error',
                                    component='player',
                                )

                        else:
                            force_stop_loading = True
                            log_handle(
                                content="Failed to extract video information",
                                errtype="error",
                                component="player",
                            )
                            messagebox.showerror(f'JaTubePlayer {ver}', 'Failed to extract video information, Please refer to log for more details')
                    except Exception as e:
                        playing_vid_info_dict = None
                        log_handle(
                            content=f"Video information extraction degraded: {e}",
                            errtype="warning",
                            component="player",
                        )
                        threading.Thread(
                            daemon=True,
                            target=lambda: messagebox.showerror(
                                f'JaTubePlayer {ver}',
                                f'we got some problem {e}\n\n we can still play the video, but some information make be missing, and you live streams cannot be played smoothly!'
                            )
                        ).start()
                    except yt_dlp.utils.DownloadError as e:
                        log_handle(
                            content=f'ytdlp error {e}',
                            errtype='error',
                            component='player',
                        )

                    for i in range(31):  ####### for wating mpv to load the vid
                        if force_stop_loading:
                            loadingvideo = False
                            ui_queue.put(lambda: player_loading_label.configure(text=''))
                            force_stop_loading = False
                            succed = False
                            break

                        ui_queue.put(lambda: root.update())
                        log_handle(
                            content=f"loading video {i} times",
                            errtype='info',
                            component='player',
                        )

                        if i % 2 == 0:
                            ui_queue.put(lambda: player_loading_label.configure(text='loading..'))
                        else:
                            ui_queue.put(lambda: player_loading_label.configure(text='loading.'))

                        if i == 15:
                            player.play(direct_url)

                        if i > 29:
                            if autoretry.get() or messagebox.askretrycancel(f'JaTubePlayer {ver}', 'The player encounter some problem while loading, retry?'):
                                loadingvideo = False
                                ui_queue.put(lambda: player_loading_label.configure(text='retrying...'))
                                load_thread_queue.put((chosen_file, direct_url))  #put it back to queue to retry
                                succed = False
                                break
                            else:
                                ui_queue.put(lambda: player_loading_label.configure(text=''))
                                succed = False
                                loadingvideo = False
                                break

                        if player.duration != None:
                            succed = True
                            break

                        time.sleep(0.4)

                    if succed:
                        ui_queue.put(lambda: playing_title_textbox.configure(state='normal'))
                        try:
                            ui_queue.put(lambda: playing_title_textbox.insert(tk.END, playing_vid_info_dict['title']))

                            if fullscreen_status == 0:
                                ui_queue.put(lambda: root.title(f'JaTubePlayer {ver}  '))
                            else:
                                ui_queue.put(lambda: root.title(f'JaTubePlayer {ver}  - {playing_vid_info_dict["title"]}'))
                        except Exception as e:
                            log_handle(
                                content=f"Error inserting title: {e}",
                                errtype='error',
                                component='player',
                            )

                        ui_queue.put(lambda: playing_title_textbox.configure(state='disabled'))
                        ui_queue.put(lambda: smtc.update_media_info(
                            title=playing_vid_info_dict['title'],
                            artist=playing_vid_info_dict['uploader'],
                            album='JaTubePlayer',
                            thumbnail_url=playing_vid_info_dict['thumbnail']
                        ))

                        if enable_discord_presence.get():
                            try:
                                if discord_presence_show_playing.get():
                                    discord_presence.update(song_title=playing_vid_info_dict['title'])
                                else:
                                    discord_presence.idle()
                            except Exception as ex:
                                log_handle(
                                    content=f"Error occurred while updating Discord presence: {ex}",
                                    errtype='error',
                                    component='player',
                                )

                        if current_idx is not None:
                            log_handle(
                                content=f"Setting playing tag for index {current_idx}",
                                errtype='info',
                                component='player',
                            )
                            media_list_page_controller.set_playing_tag(current_idx, 'playing')

                        player.volume = (int(player_volume_scale.get()))

                        if playing_vid_mode == 3:
                            pos_thread = threading.Thread(daemon=True, target=update_playing_pos_local_and_chrome)
                        else:
                            pos_thread = threading.Thread(daemon=True, target=update_playing_pos_yt)

                        pos_thread.start()
                        ui_queue.put(lambda: player_loading_label.configure(text=''))
                        ui_queue.put(lambda: pauseStr.set('||'))
                except Exception as e:
                    log_handle(
                        content=f"Failed to play video: {e}",
                        errtype="error",
                        component="player",
                    )
                    ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}', f"Failed to play video: {str(err)}"))

                    if current_idx is not None:
                        media_list_page_controller.remove_playing_tag()
                        media_data_list.current_playing_idx_num = -1
                        media_data_list.current_media_page = 0

                loadingvideo = False
            else:
                try:
                    stop_playing_video()
                except:
                    pass

                try:
                    if chosen_file:
                        current_idx = media_data_list.current_playing_idx_num if playing_vid_mode == 2 else None  #for MLPC
                        loadingvideo = True
                        succed = False
                        ui_queue.put(lambda: player_loading_label.configure(text='Loading ...'))

                        if os.path.exists(chosen_file):
                            player.play(chosen_file)
                            player.volume = int(player_volume_scale.get())
                            log_handle(
                                content=str(chosen_file),
                                errtype='info',
                                component='player',
                            )
                            time.sleep(0.1)

                            if player.duration == None:
                                for i in range(31):
                                    log_handle(
                                        content='testing point',
                                        errtype='info',
                                        component='player',
                                    )

                                    if force_stop_loading:
                                        loadingvideo = False
                                        ui_queue.put(lambda: player_loading_label.configure(text=''))
                                        force_stop_loading = False
                                        succed = False
                                        break

                                    if player.duration != None:
                                        succed = True
                                        break

                                    log_handle(
                                        content=str(i),
                                        errtype='info',
                                        component='player',
                                    )

                                    if i > 29:
                                        if autoretry.get() or messagebox.askretrycancel(f'JaTubePlayer {ver}', 'The player encounter some problem while loading, retry?'):
                                            loadingvideo = False
                                            ui_queue.put(lambda: player_loading_label.configure(text='retrying...'))
                                            load_thread_queue.put((chosen_file, direct_url))  #put it back to queue to retry
                                            succed = False
                                            break
                                        else:
                                            ui_queue.put(lambda: player_loading_label.configure(text=''))
                                            succed = False
                                            loadingvideo = False
                                            break

                                    log_handle(
                                        content='loading',
                                        errtype='info',
                                        component='player',
                                    )
                                    time.sleep(0.1)
                            else:
                                succed = True

                            if fullscreen_status == 0:
                                ui_queue.put(lambda: root.title(f'JaTubePlayer {ver}  '))
                            else:
                                ui_queue.put(lambda cf=chosen_file: root.title(f'JaTubePlayer {ver}  - {os.path.basename(cf)}'))

                            if succed:
                                ui_queue.put(lambda: playing_title_textbox.configure(state='normal'))
                                log_handle(
                                    content=f"playing mode {playing_vid_mode}",
                                    errtype='info',
                                    component='player',
                                )

                                if playing_vid_mode == 1:
                                    ui_queue.put(lambda cf=chosen_file: playing_title_textbox.insert(tk.END, str(cf)))
                                else:
                                    ui_queue.put(lambda cf=chosen_file: playing_title_textbox.insert(tk.END, os.path.basename(str(cf))))

                                ui_queue.put(lambda: playing_title_textbox.configure(state='disabled'))

                                if fullscreen_status == 0:
                                    ui_queue.put(lambda: root.title(f'JaTubePlayer {ver}  '))
                                else:
                                    ui_queue.put(lambda cf=chosen_file: root.title(f'JaTubePlayer {ver}  - {cf}'))

                                try:
                                    ui_queue.put(lambda cf=chosen_file: smtc.update_media_info(
                                        title=os.path.basename(cf),
                                        artist='-local file',
                                        album='JaTubePlayer',
                                        thumbnail_url=None
                                    ))
                                except Exception as e:
                                    log_handle(
                                        content=f"Error updating media info: {e}",
                                        errtype='error',
                                        component='player',
                                    )

                                if enable_discord_presence.get():
                                    try:
                                        if discord_presence_show_playing.get():
                                            discord_presence.update(song_title="A Local media file :)")
                                        else:
                                            discord_presence.idle()
                                    except:
                                        pass

                                if current_idx is not None:
                                    media_list_page_controller.set_playing_tag(current_idx, 'playing')

                                player.volume = int(player_volume_scale.get())
                                pos_thread = threading.Thread(daemon=True, target=update_playing_pos_local_and_chrome)
                                pos_thread.start()
                                ui_queue.put(lambda: player_loading_label.configure(text=''))
                                ui_queue.put(lambda: pauseStr.set('||'))
                                time.sleep(0.1)
                                playing_vid_info_dict = {"original_url": chosen_file}

                                loadingvideo = False
                        else:
                            log_handle(
                                content=f"Local media file no longer exists: {chosen_file}",
                                errtype="error",
                                component="player",
                            )
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}', 'The file does not exist anymore, please choose another file'))
                            loadingvideo = False
                            ui_queue.put(lambda: player_loading_label.configure(text=''))

                            if current_idx is not None:
                                media_list_page_controller.remove_playing_tag()
                except Exception as e:
                    log_handle(
                        content=f"Failed to play local file: {e}",
                        errtype="error",
                        component="player",
                    )
                    ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}', f"Failed to play local file:  {str(err)}"))
                    loadingvideo = False
                    ui_queue.put(lambda: player_loading_label.configure(text=''))

                    if current_idx is not None:
                        media_list_page_controller.remove_playing_tag()
                        media_data_list.current_playing_idx_num = -1
                        media_data_list.current_media_page = 0



def load_local_files(mode:int,
                     local_folder_path:str=None,):
    '''
    mode 0 == single file mode and dnd single file
    mode 1 == folder mode and dnd folder(must have muti files for better single file control balance)
    mode 2 == dnd multi files
    local_folder_path for quick startup local folder and dnd folder
    dnd_files_path_lists for dnd file list
    // only use kwarg
    '''
    global playing_vid_mode,loadingvideo,selected_song_number,media_data_list


    if mode == 0:playing_vid_mode = 1
    elif mode == 1:playing_vid_mode = 2

    
    result = media_list_page_controller.local_files_init_and_reload(
        media_data_list=media_data_list,
        quick_start_folder_path=local_folder_path,
        mode_for_local_files=mode
    )
    media_data_list = media_list_page_controller.media_data_list
        
    if result is None:
            selected_song_number = None
            ui_queue.put(lambda: star_btn_ui_functions.star_regular())
            stop_playing_video()

            insert_textbox(playlist_name_textbox, "Local File")
    elif result is False:
        messagebox.showerror(f'JaTubePlayer {ver}', 'Failed to load local files, or canceled by user.')
        log_handle(
            content='Failed to load local files, please check the folder or file path and try again',
            errtype='error',
            component='player',
        )
        
            


def download_and_play(event=None):### button and double click event
    '''
    for youtube video, the direct url is needed to make mpv selected , 
    so the load thread will get the direct url and put it in the queue, 
    and the load thread will handle the rest of the process, 
    for local file/folder, the file path is directly put in the queue, 
    and the load thread will handle the rest of the process.
    '''
    try:
        global media_data_list
        media_data_list = media_list_page_controller.media_data_list
    except Exception as e:
        log_handle(
            content=f"Error accessing media_data_list: {e}",
            errtype='error',
            component='player',
        )
        messagebox.showerror(f'JaTubePlayer {ver}', 'An error occurred while accessing the media data list.')

    if playing_vid_mode == 0:
        if check_internet_socket():
            #load from youtube
            if selected_song_number is not None:
                load_thread_queue.put((None,media_data_list.vid_url[selected_song_number]))
                
                    
        
            else: messagebox.showerror(f'JaTubePlayer {ver}','please select a video first')
        else:
            ToastNotification().notify(
                app_id="JaTubePlayer",
                title="JaTubePlayer",
                msg='Internet connection failed, please check your internet connection',
                duration='short',            
            )
    elif playing_vid_mode == 1 or playing_vid_mode == 2:       
        # load local file/folder
        if selected_song_number is not None:
            load_thread_queue.put((media_data_list.vid_url[selected_song_number],None))
            if playing_vid_mode ==2 :
                media_data_list.current_media_page = media_list_page_controller.current_page

        else: messagebox.showerror(f'JaTubePlayer {ver}','please select a video first')

    elif playing_vid_mode == 4:
        if selected_song_number != None:
            url_or_path = media_data_list.vid_url[selected_song_number]
            if url_or_path.startswith(('http://', 'https://')):
                if check_internet_socket():
                    load_thread_queue.put((None,url_or_path))
                    media_data_list.current_media_page = media_list_page_controller.current_page
                else:
                    ToastNotification().notify(
                        app_id="JaTubePlayer",
                        title="JaTubePlayer",
                        msg='Internet connection failed, please check your internet connection',
                        duration='short',            
                    )
            else:
                load_thread_queue.put((url_or_path,None))
        else: messagebox.showerror(f'JaTubePlayer {ver}','please select a video first')
    if playing_vid_mode in [0,2,4]:
        media_data_list.current_playing_idx_num = selected_song_number
        media_data_list.current_media_page = media_list_page_controller.current_page


def onclose():
    stop_playing_video()
    
    if is_downloading.get():
        if not messagebox.askokcancel(f'JaTubePlayer {ver}','A video is still downloading, are you sure to exit?'):
            return
    try:player.stop()
    except:pass
    try:smtc.destroy()
    except:pass
    try:discord_presence.close()
    except:pass
    try:
        thumbnail_loader.close()
    except:pass
    try:
        shortcut_manager.cleanup()
    except:pass
    try:
        dnd_handle.close()
    except:pass
    try:
        twitch_handler.stop_twitch_streamlink()
    except:pass
    try:
        log_handler.flush_log_locally(force_flush_log=True)
    except:pass
    root.destroy()

    
root.protocol('WM_DELETE_WINDOW',onclose)




def fullscreen_widget_change(mode:int=0):
    '''
    passively update/refresh 
    mode = 0, go normal
    mode = 1 go fullscreen , will check [tk.IntVar] fullscreenmode
    '''
    global fullscreen_status, stream, tkinter_scaling,current_ctk_scaling,fullscreen_loading
   
    try:
        
        window_width = round(BASE_WIDTH * effective_scaling)
        window_height = round(BASE_HEIGHT * effective_scaling)
                    
        
        root.update_idletasks()
        if not fullscreen_loading:
            fullscreen_loading = True
        else:
            return
        
        if mode == 0:

            root.geometry(f"{window_width}x{window_height}")
            
            # Tkinter widgets need DPI scaling
            playlisttreebox.configure(height=int(20*effective_scaling))
            if playing_vid_mode in [0,4]:
                playlisttreebox.column("#0", width=int(160*tkinter_scaling), anchor='center')
            else:
                playlisttreebox.column("#0", width=0, anchor='center')
            playlisttreebox.column("title", width=int(1000))
            
            try:
                playlisttreebox.place_configure(relx=0.020, rely=0.135, relwidth=0.925, relheight=0.828)
                Y_scrollbar.place_configure(relx=0.945, rely=0.135, relheight=0.828)
                X_scrollbar.place_configure(relx=0.020, rely=0.963, relwidth=0.925)
                
                # Main frames
                header_frame.place_configure(relx=0, rely=0, relwidth=1, relheight=0.063)
                right_panel_frame.place_configure(relx=0.618, rely=0.070, relwidth=0.377, relheight=0.560)
                playlist_btn_frame.place_configure(relx=0.618, rely=0.630, relwidth=0.377, relheight=0.130)
                video_container.place_configure(relx=0.005, rely=0.070, relwidth=0.607, relheight=0.685)
                controls_frame.place_configure(relx=0.005, rely=0.764, relwidth=0.990, relheight=0.230)
                Frame_for_mpv.place_configure(relx=0.011, rely=0.084, relwidth=0.595, relheight=0.664)
                
                # Sub-frames inside transport bar
                now_playing_frame.place_configure(relx=0.008, rely=0.102, relwidth=0.984, relheight=0.240)
                progress_frame.place_configure(relx=0.008, rely=0.405, relwidth=0.984, relheight=0.230)
                mode_frame.place_configure(relx=0.008, rely=0.585, relwidth=0.132, relheight=0.375)
                playback_frame.place_configure(relx=0.150, rely=0.585, relwidth=0.43, relheight=0.375)
                volume_frame.place_configure(relx=0.595, rely=0.605, relwidth=0.105, relheight=0.350)
                action_btn_frame.place_configure(relx=0.705, rely=0.585, relwidth=0.290, relheight=0.375)
                

                
                # Mode widgets
                mode_label.place_configure(relx=0.06, rely=0.07)
                player_mode_continue.place_configure(relx=0.06, rely=0.45)
                player_mode_replay.place_configure(relx=0.39, rely=0.45)
                player_mode_random.place_configure(relx=0.72, rely=0.45)
                
                # Progress bar
                player_pos_label.place_configure(relx=0, rely=0.03, relwidth=0.050)
                player_position_scale.place_configure(relx=0.055, rely=0.12, relwidth=0.850, relheight=0.45)
                player_song_length_label.place_configure(relx=0.922, rely=0.03, relwidth=0.068)
                
                # Playback controls
                prevsong.place_configure(relx=0.02, rely=0.08, relwidth=0.15, relheight=0.8)
                pausebutton.place_configure(relx=0.18, rely=0.08, relwidth=0.15, relheight=0.8)
                stopbutton.place_configure(relx=0.34, rely=0.08, relwidth=0.15, relheight=0.8)
                nextsong.place_configure(relx=0.50, rely=0.08, relwidth=0.15, relheight=0.8)
                fullscreenbtn.place_configure(relx=0.66, rely=0.08, relwidth=0.13, relheight=0.8)
                player_loading_label.place_configure(relx=0.8, rely=0.25, relwidth=0.18)
                
                # Volume
                player_volume_label.place_configure(relx=0, rely=0.2, relwidth=0.120)
                player_volume_scale.place_configure(relx=0.180, rely=0.35, relwidth=0.780, relheight=0.28)
                
                # Action buttons
                setting_btn.place_configure(relx=0, rely=0.06, relwidth=0.290, relheight=0.88)
                star_btn.place_configure(relx=0.305, rely=0.06, relwidth=0.200, relheight=0.88)
                video_info_btn_frame.place_configure(relx=0.520, rely=0.06, relwidth=0.475, relheight=0.88)
                video_info_title.place_configure(relx=0.04, rely=0.04, relwidth=0.92, relheight=0.34)
                select_info_btn.place_configure(relx=0.04, rely=0.42, relwidth=0.44, relheight=0.47)
                playing_info_btn.place_configure(relx=0.52, rely=0.42, relwidth=0.44, relheight=0.47)
                
                # Now playing
                np_icon.place_configure(relx=0.008, rely=0.14)
                playing_title_textbox.place_configure(relx=0.035, rely=0.10)
            except:
                pass
            
            player_position_scale.configure(height=int(160*0.313*0.5*0.03))
            Frame_for_mpv.lift()
            fullscreenbtn.configure(text='⛶')
            fullscreen_status = 0
            root.title(f'JaTubePlayer {ver} ')
            
        elif mode == 1:
            if fullscreenmode.get() !=1 :
                header_frame.place_forget()
                right_panel_frame.place_forget()
                playlist_btn_frame.place_forget()
                video_container.place_forget()
                action_btn_frame.place_forget()
                now_playing_frame.place_forget()
            

            
            try:
                if fullscreenmode.get() == 0:
                    root.state('zoomed')
                    Frame_for_mpv.place_configure(relx=0, rely=0, relwidth=1, relheight=0.93)
                    controls_frame.place_configure(relx=0.025, rely=0.93, relwidth=0.95, relheight=0.073)

                elif fullscreenmode.get() == 2:
                    Frame_for_mpv.place_configure(relx=0, rely=0, relwidth=1, relheight=0.9)
                    controls_frame.place_configure(relx=0, rely=0.9, relwidth=1, relheight=0.1)
                if fullscreenmode.get() != 1:
                    # Progress
                    progress_frame.place_configure(relx=0.02, rely=0.05, relwidth=0.96, relheight=0.5)
                    player_pos_label.place_configure(relx=0, rely=0.1, relwidth=0.05)
                    player_position_scale.place_configure(relx=0.06, rely=0.2, relwidth=0.83, relheight=0.5)
                    player_song_length_label.place_configure(relx=0.92, rely=0.1, relwidth=0.06)
                    
                    # Playback
                    playback_frame.place_configure(relx=0.35, rely=0.5, relwidth=0.3, relheight=0.45)
                    prevsong.place_configure(relx=0.1, rely=0.1, relwidth=0.13, relheight=0.95)
                    pausebutton.place_configure(relx=0.24, rely=0.1, relwidth=0.13, relheight=0.95)
                    stopbutton.place_configure(relx=0.38, rely=0.1, relwidth=0.13, relheight=0.95)
                    nextsong.place_configure(relx=0.52, rely=0.1, relwidth=0.13, relheight=0.95)
                    fullscreenbtn.place_configure(relx=0.66, rely=0.1, relwidth=0.13, relheight=0.88)
                    player_loading_label.place_configure(relx=0.81, rely=0.07, relwidth=0.18)
                    # Volume
                    volume_frame.place_configure(relx=0.75, rely=0.5, relwidth=0.2, relheight=0.75)
                    player_volume_label.place_configure(relx=0, rely=0.05, relwidth=0.15)
                    player_volume_scale.place_configure(relx=0.18, rely=0.25, relwidth=0.75, relheight=0.4)
                    
                    # Mode
                    mode_frame.place_configure(relx=0.02, rely=0.5, relwidth=0.25, relheight=0.45)
                    mode_label.place_configure(relx=0.02, rely=0.2)
                    player_mode_continue.place_configure(relx=0.25, rely=0.3)
                    player_mode_replay.place_configure(relx=0.5, rely=0.3)
                    player_mode_random.place_configure(relx=0.75, rely=0.3)
                

            except Exception as e:
                log_handle(
                    content=f"Error in fullscreen_widget_change: {e}",
                    errtype='error',
                    component='fullscreen',
                )
            
            player_position_scale.configure(height=int(root.winfo_height()*0.07*0.5*0.5*0.05))
            Frame_for_mpv.lift()
            controls_frame.lift()
            fullscreenbtn.configure(text='↖')
            fullscreen_status = 1
            
            try:
                if playing_title_textbox.get("1.0", "end").strip():
                    root.title(f'JaTubePlayer {ver}   -  {playing_title_textbox.get("1.0", "end").strip()}')
                else:
                    root.title(f'JaTubePlayer {ver} ')
            except Exception as e:
                log_handle(
                    content=f"Error updating title: {e}",
                    errtype='error',
                    component='fullscreen',
                )
        
        
        
        # Refresh sliders after layout is stable
        try:
            vol_value = player_volume_scale.get()
            pos_value = player_position_scale.get()
            player_volume_scale.set(vol_value)
            player_position_scale.set(pos_value)
        except:
            pass
        
    except Exception as e:
        log_handle(
            content=f"Error in fullscreen_widget_change: {e}",
            errtype='error',
            component='fullscreen',
        )
    finally:
        fullscreen_loading = False
       
def full_screen_contorl_hover_thread():
    global hover_fullscreen_last_statue
    hover_fullscreen_last_statue = 1
    while True:
        time.sleep(0.2)
        if fullscreen_status == 1 and hover_fullscreen.get() and not fullscreenmode.get() == 1:
            window_height = root.winfo_height() 
            mouse_y = root.winfo_pointery() 
            if  mouse_y > window_height * 0.93 and mouse_y < window_height +root.winfo_rooty() and root.winfo_rootx() <= root.winfo_pointerx() <= root.winfo_rootx() + root.winfo_width():

                if hover_fullscreen_last_statue == 0:
                    ui_queue.put(lambda:fullscreen_widget_change(mode = 1))
                    log_handle(
                        content='hover control frame removed',
                        errtype='info',
                        component='fullscreen',
                    )
                    hover_fullscreen_last_statue = 1
            else:
                if hover_fullscreen_last_statue == 1:

                    log_handle(
                        content='hover control frame showed',
                        errtype='info',
                        component='fullscreen',
                    )
                    def _place_controls():# Since there will be a delay with the ui queue root .after thus this function is needed to make sure the controls will be placed and mpv frame is placed at the right place after the fullscreen change
                        if fullscreen_status == 1:
                            controls_frame.place_forget()
                            Frame_for_mpv.place_configure(relx=0, rely=0, relwidth=1, relheight=1)
                    ui_queue.put(_place_controls)
                    hover_fullscreen_last_statue = 0
                



def fullscreen_change_state(event=None):## for btn
    if fullscreenmode.get() != 2:
        if root.state() == 'normal':
            root.state('zoomed')
            ui_queue.put(lambda: fullscreen_widget_change(mode = 1))
        elif root.state() == 'zoomed':
            root.state('normal')
            ui_queue.put(lambda: fullscreen_widget_change(mode = 0))
    else:
        if fullscreen_status == 0:
            ui_queue.put(lambda: fullscreen_widget_change(mode = 1))
        elif fullscreen_status == 1:
            ui_queue.put(lambda: fullscreen_widget_change(mode = 0))
        if fullscreen_status == 1 and root.state() == 'zoomed':
            root.state('normal')

    if event:time.sleep(0.05)


def fullscreen_detect_thread():## auto drag
    global hover_fullscreen_last_statue
    time.sleep(0.1)  # Initial delay
    while True:
        try:
            previous = root.state()
            time.sleep(0.01)  
            if previous != root.state():
                ui_queue.put(lambda: fullscreen_widget_change(1 if root.state() == 'zoomed' else 0))
                hover_fullscreen_last_statue = 1
                time.sleep(0.1) 
        except:pass

        
def init_quick_startup(iter:int=0):
    if len(sys.argv) == 1:#if no file opened with
        mode = CONFIG["quickstartup_init"]["mode"]
        if check_internet_socket():
            if yt_dlp:
                if mode == 1:
                    searchentry.insert(tk.END,CONFIG['quickstartup_init']['searchmode_keyword'])
                    youtube_search()
                elif mode == 2:
                    try:
                        playlistID = CONFIG["quickstartup_init"]["playlistmode_playlist_ID"].split("?list=")[1]
                    except IndexError:
                        playlistID = CONFIG["quickstartup_init"]["playlistmode_playlist_ID"]
                    playlistname = CONFIG["quickstartup_init"]["playlistmode_playlist_Name"]
                    insert_textbox(playlist_name_textbox, playlistname)
                    
                    get_youtube_playlists(playlistID=playlistID,
                                          playlist_name=playlistname)
                elif mode == 3:
                    load_local_files(mode=1, local_folder_path=CONFIG["quickstartup_init"]["localfoldermode_folder_Path"])
                
            else:
                log_handle(
                    content="yt_dlp is not loaded, quick startup in youtube related mode is cancelled.",
                    errtype='info',
                    component='startup',
                )
        elif mode == 3:
            load_local_files(mode=1, local_folder_path=CONFIG["quickstartup_init"]["localfoldermode_folder_Path"])
        elif iter < 10:
            root.after(500,lambda: init_quick_startup(iter+1))
            log_handle(
                content=f"quickstartup internet test {iter} times",
                errtype='info',
                component='startup',
            )
        elif iter >= 10:
            try:
                ToastNotification().notify(app_id="JaTubePlayer",
                                        title=f'JaTubePlayer {ver}',
                                        msg='There seems to be no internet connection, quick startup in youtube related mode is cancelled.\nPlease check your internet connection.', 
                                        duration='short', icon=icondir)
                
            except Exception as e:
                log_handle(
                    content="Error in init_quick_startup notification:",
                    errtype='error',
                    component='startup',
                )
                log_handle(
                    content=str(e),
                    errtype='error',
                    component='startup',
                )

def init_openwith_thread():
    global playing_vid_mode
    try:
        if sys.argv[1]:
            playing_vid_mode = 1
            load_thread_queue.put((sys.argv[1],None))
            #no thread here bc we need to wait for the load to finish
            #then we can go to fullscreen

            if CONFIG['open_with_fullscreen']:
                log_handle(
                    content='fullscreen',
                    errtype='info',
                    component='startup',
                )
                fullscreen_widget_change(mode=1)
            
    except:pass














def init_read_dlp():
    global yt_dlp,utils,ytdlpver
    try:
        yt_dlp,utils,ytdlpver = load_yt_dlp(_internal_dir)
        if yt_dlp == None:
            log_handle(
                content=f"Failed to load yt-dlp: {utils}",
                errtype="error",
                component="startup",
            )
            ui_queue.put(lambda u=utils: messagebox.showerror(f'JaTubePlayer {ver}',f'seems to be something wrong with yt_dlp!\n{u}'))
    except Exception as e:
        log_handle(
            content=f"Failed to initialize yt-dlp: {e}",
            errtype="error",
            component="startup",
        )
        ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}',err))
        

def init_read_config():
    global ytdlp_use_cookie,auto_like_refresh,auto_sub_refresh,auto_check_ver,maxresolution,demuxer_max_bytes,demuxer_max_back_bytes,cache_pause_wait,audio_wait_open,blur_hexColor
    global chrome_extension_port,discord_idle_presence_wording

    ytdlp_use_cookie.set(CONFIG['ytdlp_use_cookie'])
    log_handle(
        content=f"ytdlp_use_cookie {ytdlp_use_cookie.get()}",
        errtype='info',
        component='startup',
    )
    try:
        if CONFIG['auto_sub_refresh']:auto_sub_refresh.set(True)
        else:auto_sub_refresh.set(False)
        log_handle(
            content="sub fin",
            errtype='info',
            component='startup',
        )
        if CONFIG['auto_like_refresh']:auto_like_refresh.set(True)
        else:auto_like_refresh.set(False)
        log_handle(
            content="like fin",
            errtype='info',
            component='startup',
        )

        if CONFIG['vercheck']:auto_check_ver.set(True)
        else:auto_check_ver.set(False)
        log_handle(
            content="ver fin",
            errtype='info',
            component='startup',
        )
        
        if CONFIG['open_with_fullscreen']:open_with_fullscreen.set(True)
        else:open_with_fullscreen.set(False)
        log_handle(
            content="open fin",
            errtype='info',
            component='startup',
        )
        
        if CONFIG['show_cache']:show_cache.set(True)
        else:show_cache.set(False)
        log_handle(
            content="cache fin",
            errtype='info',
            component='startup',
        )

        if CONFIG['hover_fullscreen']:hover_fullscreen.set(True)
        else:hover_fullscreen.set(False)

        if CONFIG['ytdlp_use_nightly_build']:
            ytdlp_use_nightly_build.set(True)
        else:
            ytdlp_use_nightly_build.set(False)
        download_path.set(CONFIG['download_path'])
        demuxer_max_bytes.set(CONFIG['cache']['demuxer_max_bytes'])
        demuxer_max_back_bytes.set(CONFIG['cache']['demuxer_max_back_bytes'])
        cache_pause_wait.set(CONFIG['cache']['cache_pause_wait'])
        audio_wait_open.set(CONFIG['cache']['audio_wait_open'])
        fullscreenmode.set(CONFIG['fullscreenmode'])
        blur_hexColor.set(CONFIG.get('blur_hexColor', '#10101000'))
        discord_idle_presence_wording.set(CONFIG['discord_idle_presence_wording'])
        chrome_extension_port.set(CONFIG['chrome_ext_server_port'])

        if CONFIG['enable_discord_presence']:
            enable_discord_presence.set(True)
        else:
            enable_discord_presence.set(False)


        if CONFIG["discord_presence_show_playing"]:discord_presence_show_playing.set(True)
        else:discord_presence_show_playing.set(False)

        max_search_result_count.set(CONFIG["max_result_count"]["search"])
        max_recommendation_result_count.set(CONFIG["max_result_count"]["Recommendations"])
        max_sub_result_count.set(CONFIG["max_result_count"]["sub"])
        max_like_result_count.set(CONFIG["max_result_count"]["like"])

        maxresolution.set(CONFIG["max_resolution"])
        setting_run_chrome_extension_server.set(CONFIG['run_flask'])

        
    except Exception as e:
        log_handle(
            content="Error in init_read_config:",
            errtype='error',
            component='startup',
        )
        log_handle(
            content=str(e),
            errtype='error',
            component='startup',
        )




@check_internet_silent
def init_ver_check():
    def _ver_check():
        if CONFIG['vercheck']:
            latest_dlp = get_latest_dlp_version(ytdlp_use_nightly_build.get())
            if ytdlpver.__version__ != latest_dlp:
                ui_queue.put(lambda ld=latest_dlp: ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg=f'Your yt_dlp is not the newest!\nlatest: {ld}  yours: {ytdlpver.__version__}', duration='short', icon=icondir))
            
            latest_player = get_latest_player_version()
            if ver!= latest_player:
                ui_queue.put(lambda lp=latest_player: ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg=f'Your JaTubePlayer is not the newest!\nlatest: {lp}  yours: {ver}', duration='short', icon=icondir))
    threading.Thread(daemon=True,target=_ver_check).start()







def create_mpv_player():
    global player,deno_exe

    cache_cfg = CONFIG.get("cache", {})
    demuxer_max_bytes_val = int(demuxer_max_bytes.get() or cache_cfg.get("demuxer_max_bytes", 512))
    demuxer_max_back_bytes_val = int(demuxer_max_back_bytes.get() or cache_cfg.get("demuxer_max_back_bytes", 256))
    cache_pause_wait_val = int(cache_pause_wait.get() or cache_cfg.get("cache_pause_wait", 3))
    audio_wait_open_val = float(audio_wait_open.get() or cache_cfg.get("audio_wait_open", 1))

    buf_arg = {
    "cache": "yes",
    "demuxer-max-bytes": f"{demuxer_max_bytes_val}M",
    "demuxer-max-back-bytes": f"{demuxer_max_back_bytes_val}M",
    "cache-pause": "yes",
    "cache-pause-wait": cache_pause_wait_val,
    "cache-pause-initial": "yes",
    "demuxer-thread": "yes",
    "audio-wait-open": audio_wait_open_val,

    }

    sub_arg = {
    "sub_font": "Inter Medium",
    "sub_font_size": 52,
    "sub_color": "1/1/1/1.0",
    "sub_border_color": "0.0/0.35/0.8/0.9",
    "sub_border_size": 5,
    "sub_scale": 0.9,
    }


    log_handle(
        content="create mpv",
        errtype='info',
        component='player',
    )

    if player:
        player.terminate()
        twitch_handler.stop_twitch_streamlink()
        try:
            smtc.destroy()
        except:
            pass
        try:
            discord_presence.idle()
        except:
            pass
        log_handle(
            content="killed",
            errtype='info',
            component='player',
        )


    player = mpv.MPV(
        idle = True,
        hwdec="auto",
        profile="fast",
        wid=Frame_for_mpv.winfo_id(),
        log_handler=log_handler.mpv_log_handler,
        vid="no" if audio_only.get() else "auto",
        keep_open=True,
        curl_enabled=True,
        af='scaletempo',
        msg_level="ytdl_hook=debug,ffmpeg=warn,cplayer=warn",
        script_opts=f"ytdl_hook-ytdl_path={os.path.join(_internal_dir, 'yt-dlp.exe')}",
        **buf_arg,
        **sub_arg
    )




def _init_dnd_on_root_thread():
    global dnd_handle

    dnd_handle = DropHandler(
        media_list_page_control=media_list_page_controller,
        log_handle=log_handle,
        ui_queue=ui_queue,
        selected_song_number_status_changer=dnd_mode_change_status,
        media_data_list=media_data_list,
        playing_vid_mode=playing_vid_mode,
        Chrome_ext_server_ui_functions=Chrome_ext_server_ui_functions,
        messagebox=messagebox,
        root=root
    )

    dnd_handle.init_URL_handler()
    log_handle(
        content="Drag and drop handler initialized on root thread",
        errtype='info',
        component='drag_drop',
    )


def _init_load_extra_objs():
    global dnd_handle,discord_presence,google_control,get_info_loader,star_vid_handle,thumbnail_loader,media_list_page_controller
    global innertube_handler,playlist_retriever
    global account_handler,account_info_handler,history_page_handler,account_innertube_handler,twitch_handler
    global CONFIG

    from utils.Account_token import account_token
    account_token_handle = account_token(
        appdata_dir=appdata_dir,
        log_handle=log_handle
    )
    from history_page.history_page import history_page
    history_page_handler = history_page(log_handle=log_handle,
                                        messagebox=messagebox)

    from account.Account import account_handle
    account_info_handler = AccountInfo()

    from video_media_control.twitch_handle import twitch_handle
    
    discord_presence=DiscordPresence(discord_status_run=discord_status_run,
                                     discord_status_close=discord_status_close,
                                     log_handle=log_handle
                                     )
    discord_presence.discord_idle_presence_wording = CONFIG['discord_idle_presence_wording']
    if enable_discord_presence.get():
        try:discord_presence.idle()
        except Exception as e:
            log_handle(
                content=f"Error initializing Discord presence: {e}",
                errtype='error',
                component='startup',
            )

    get_info_loader = get_info_loader_(yt_dlp = lambda:yt_dlp,
                                      maxresolution = lambda: maxresolution.get(),
                                      deno_exe = lambda: deno_exe,
                                      ytdlp_log_handle = lambda: ytdlp_log_handle,
                                      cookie = lambda: account_handler.get_cookie(),
                                      config_dir=(os.path.join(appdata_dir,'JaTubePlayer','config.json'))
                                      )
    
    media_data_list.vid_url = []
    star_vid_handle = star_vid_handler(appdata_dir=appdata_dir,
                                        get_info_loader=get_info_loader)
    

    thumbnail_loader = ThumbnailLoader(playing_vid_mode=lambda: playing_vid_mode,
                                       insert_treeview_quene=insert_treeview_quene,
                                       playlisttreebox=playlisttreebox,
                                       ui_queue=ui_queue,
                                       tkinter_scaling=lambda: tkinter_scaling,
                                       log_handle=log_handle,
                                       root=root)

    
    
    account_handler = account_handle(current_dir=current_dir,
                                     app_data_dir=appdata_dir,
                                    ctk_messagebox=messagebox,
                                    log_handle=log_handle,
                                    account_info_handler=account_info_handler,
                                    account_token_handle=account_token_handle)
    
            
    innertube_handler = innertube_handle(account_handle=account_handler,
                                         log_handle=log_handle)
    account_innertube_handler = innertube_handle(account_handle=account_handler,
                                                 log_handle=log_handle)
    
    playlist_retriever = playlist_retriever_(innertube_handle=innertube_handler,
                                             log_handle=log_handle)
    
    


    media_list_page_controller = MediaList_PageControl_(
        ui_queue=ui_queue,
        tree_view_queue=insert_treeview_quene,
        log_handle=log_handle,
        thumbnail_loader=thumbnail_loader,
        page_num_label=page_num_label,
        load_thread_queue=load_thread_queue,
        playlist_retriever=playlist_retriever,
        history_page_handler=history_page_handler,
        star_vid_handler=star_vid_handle,
        star_btn_ui_functions=star_btn_ui_functions,
        messagebox=messagebox,
        dnd_ui_functions = dnd_ui_functions,
        Chrome_ext_server_ui_functions=Chrome_ext_server_ui_functions,
        get_cur_playing_url = lambda: playing_vid_info_dict.get("original_url", ''),
        get_cur_playlist_title= lambda: playlist_name_textbox.get(0.0, tk.END).strip()
        )
    twitch_handler = twitch_handle(log_handle,
                                   _internal_dir)
    
    playlist_retriever.maxresults_recommendation = max_recommendation_result_count.get()
    playlist_retriever.maxresults_like = max_like_result_count.get()
    playlist_retriever.maxresults_sub = max_sub_result_count.get()
    media_list_page_controller.max_search_result_count = max_search_result_count.get()
    

    
    root.after(0,_init_dnd_on_root_thread)




def init_set_smtc():
    smtc.next_song_fun = lambda: playprevnext(1)
    smtc.prev_song_fun = lambda: playprevnext(2)
    smtc.pause_fun = pause
    smtc.iconpath = icondir



def init_set_playertray():
    global tray
    tray = Playertray(iconpath=icondir,ver=ver,parent=root,ctk_messagebox=messagebox)                
    tray.run()



def check_keyboard():
    global KeyMemHotkey
    KeyMemHotkey = KeyMemHotkeys_class(keymem_dict={
        'play_pause': CONFIG['keyboard_hotkeys']['play_pause'],
        'next': CONFIG['keyboard_hotkeys']['next'], 
        'previous': CONFIG['keyboard_hotkeys']['previous'],
        'stop': CONFIG['keyboard_hotkeys']['stop'],
        'volume_up': CONFIG['keyboard_hotkeys']['volume_up'],
        'volume_down': CONFIG['keyboard_hotkeys']['volume_down'],
        'mode_random': CONFIG['keyboard_hotkeys']['mode_random'],
        'mode_continuous': CONFIG['keyboard_hotkeys']['mode_continuous'],
        'mode_repeat': CONFIG['keyboard_hotkeys']['mode_repeat'],
        'toggle_minimize': CONFIG['keyboard_hotkeys']['toggle_minimize']


            },command_dict={
        'play_pause': lambda: threading.Thread(target=pause, args=(1,)).start(),
        'next': lambda: threading.Thread(target=playprevnext, args=(1,)).start(), 
        'previous': lambda: threading.Thread(target=playprevnext, args=(2,)).start(),
        'stop': lambda: threading.Thread(target=stop_playing_video).start(),
        'volume_up': lambda: threading.Thread(target=set_volume, args=(player_volume_scale.get()+4,1)).start(),
        'volume_down': lambda: threading.Thread(target=set_volume, args=(player_volume_scale.get()-4,1)).start(),
        'mode_random': lambda: threading.Thread(target=player_mode_selector.set, args=('random',)).start(),
        'mode_continuous': lambda: threading.Thread(target=player_mode_selector.set, args=('continue',)).start(),
        'mode_repeat': lambda: threading.Thread(target=player_mode_selector.set, args=('replay',)).start(),
        'toggle_minimize': lambda: threading.Thread(target=_toggle_minimize).start()
            }, root = root, icondir = icondir)
    
def _init_load_smtc_obj():
    global smtc
    smtc = MediaControlOverlay()
    init_set_smtc()


def _start_up_import():
    """Import heavy modules sequentially with timing"""
    global star_vid_handler,innertube_handle,playlist_retriever_,playlist_type
    global get_latest_player_version,get_latest_dlp_version
    import time
        
    t = time.time()
    
    log_handle(
        content=f"account: {time.time()-t:.3f}s",
        errtype='info',
        component='startup',
    )

    t = time.time()
    from utils.innertube_handle import innertube_handle
    log_handle(
        content=f"innertube: {time.time()-t:.3f}s",
        errtype='info',
        component='startup',
    )

    t = time.time()
    from video_media_control.playlist_retriever import playlist_retriever_,playlist_type
    log_handle(
        content=f"playlist_retriever: {time.time()-t:.3f}s",
        errtype='info',
        component='startup',
    )

    # Version check functions (needed by settings before delayed import)
    t = time.time()
    from utils.get_latest_version import get_latest_dlp_version, get_latest_player_version
    log_handle(
        content=f"version_funcs: {time.time()-t:.3f}s",
        errtype='info',
        component='startup',
    )
    
    t = time.time()
    from video_media_control.star_vid import star_vid_handler
    log_handle(
        content=f"star_vid_handler: {time.time()-t:.3f}s",
        errtype='info',
        component='startup',
    )

    log_handle(
        content=f"Total import time: {time.time()-_TimeStartImport:.3f}s",
        errtype='info',
        component='startup',
    )

    



def _init_account_and_quickstartup():
    '''
    Since the 2 function uses samme lock
    '''
    
    if os.path.exists(account_handler.cookie_dir):
        ui_queue.put(lambda: ToastNotification().notify(app_id="JaTubePlayer",
                                                        title=f'JaTubePlayer {ver}',
                                                        msg='Refreshing login status, please wait...',
                                                        duration='short',
                                                        icon=icondir))
        
        account_info_handler.set_account_avator()
        root.after(0, init_quick_startup)








def _extra_startup_imports():
    global ytdlp_updater
    global MediaControlOverlay,chrome_extension_flask,requests
    global shortcut_manager

    t = time.time()
    
    
    # YT-DLP Update
    t = time.time()
    from utils.ytdlp_update.downloader import ytdlp_update 
    ytdlp_updater = ytdlp_update(
        _internal_dir = _internal_dir,
        root=root,
        appdata_dir=appdata_dir,
        messagebox=messagebox,
        icondir=icondir,
        log_handle=log_handle
    )
    log_handle(
        content=f"ytdlp_update: {time.time()-t:.3f}s",
        errtype='info',
        component='startup',
    )

    # Run version check
    t = time.time()
    init_ver_check()
    log_handle(
        content=f'ver_check: {time.time()-t:.3f}s',
        errtype='info',
        component='startup',
    )

    from system.win_shortcut_control import ShortcutManager
    shortcut_manager = ShortcutManager(app_user_model_id="Jackaopen.JaTubePlayer",
                                       main_path=os.path.abspath(__file__),
                                       icon_path=icondir
    )
    shortcut_manager.create()

    # SMTC
    t = time.time()
    from system.SMTC import MediaControlOverlay
    log_handle(
        content=f"smtc: {time.time()-t:.3f}s",
        errtype='info',
        component='startup',
    )
    _init_load_smtc_obj()
    log_handle(
        content=f'smtc fin',
        errtype='info',
        component='startup',
    )

    # Requests
    t = time.time()
    import requests
    log_handle(
        content=f"requests: {time.time()-t:.3f}s",
        errtype='info',
        component='startup',
    )
    
        # Flask
    t = time.time()
    from chrome_extension.chrome_extension_flask import ChromeExtensionServer
    chrome_extension_flask = ChromeExtensionServer(log_handle=log_handle,
                                                       media_list_page_controller=media_list_page_controller,
                                                       Chrome_ext_server_ui_functions=Chrome_ext_server_ui_functions,
                                                       star_vid_handle=star_vid_handle,
                                                       messagebox=messagebox,
                                                       ui_queue=ui_queue,
                                                       get_info_loader=get_info_loader)
                                                       

    log_handle(
        content=f"flask: {time.time()-t:.3f}s",
        errtype='info',
        component='startup',
    )

    if CONFIG["run_flask"]:
        chrome_extension_flask.server_port = CONFIG["chrome_ext_server_port"]
        _switch_local_server(0)

    


def _start_up():
    """Background thread - ONLY for heavy I/O operations"""
    root.after(0, fullscreen_widget_change)
    _start_up_import()
    log_handle(
        content=f'Import fin',
        errtype='info',
        component='startup',
    )
    
    init_read_dlp()
    log_handle(
        content=f'dlp fin',
        errtype='info',
        component='startup',
    )

    init_read_config()
    log_handle(
        content=f'config fin',
        errtype='info',
        component='startup',
    )

    _init_load_extra_objs()
    log_handle(
        content=f'extra obj fin',
        errtype='info',
        component='startup',
    )

    threading.Thread(target=_init_account_and_quickstartup,daemon=True).start()
    log_handle(
        content=f'account fin',
        errtype='info',
        component='startup',
    ) 
    

       
        
    check_keyboard()
    log_handle(
        content=f'keyboard fin',
        errtype='info',
        component='startup',
    )

    init_openwith_thread()
    log_handle(
        content=f'openwith fin',
        errtype='info',
        component='startup',
    )


    

    
    root.after_idle( _extra_startup_imports)
    log_handle(
        content=f"finish_big_init {time.time()-_TimeStartImport}",
        errtype='info',
        component='startup',
    )
    root.deiconify()
    
    
    
if __name__ == '__main__':
    root.after(100,lambda:threading.Thread(daemon = True,target=load_thread).start())
    root.after(200,lambda:threading.Thread(daemon = True,target=fullscreen_detect_thread).start())
    root.after(850,lambda:threading.Thread(daemon = True,target=init_set_playertray).start())
    root.after(400,lambda:threading.Thread(daemon = True,target=full_screen_contorl_hover_thread).start())
    
    root.after(0,lambda:threading.Thread(daemon = True,target=_start_up).start())

    print("root", root.winfo_id())
    print("Frame_for_mpv", Frame_for_mpv.winfo_id())
    print("FindWindow", hwnd)






sv_ttk.use_dark_theme() ### must be here or will overrider the style
playlisttree_style = ttk.Style()
playlisttree_style.configure("Treeview",
                rowheight=int(80*tkinter_scaling),
                font=("Segoe UI", int(13.5*tkinter_scaling) ),
                fieldbackground="#1e1e1e",
                background="#1e1e1e",
                foreground="#c5c5c5")
playlisttree_style.map("Treeview",
          background=[("selected", "#3e62dc")],
          foreground=[("selected", "#e1e1e1")])

# ══════════════════════════════════════════════════════════════════════════════
# MODERN UI LAYOUT - Organized into logical sections
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# TOP HEADER BAR - Title, Search, Playlist Selection
# ─────────────────────────────────────────────────────────────────────────────
header_frame = ctk.CTkFrame(root, fg_color="#1a1a1a", corner_radius=0)
header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.063)

    
title_icon = ctk.CTkImage(light_image=title_icon_image,
                          dark_image=title_icon_image, size=(28,28))

title_label = ctk.CTkFrame(header_frame,fg_color="transparent",corner_radius=0)

ctk.CTkLabel(title_label,text="",
             image=title_icon,width=0).pack(side="left")

ctk.CTkLabel(title_label,text=" JaTube",width=0,
    font=("Segoe UI", 21.5, "bold", "italic"),text_color="#FF6B35").pack(side="left")

ctk.CTkLabel(title_label,text="Player",width=0,
    font=("Segoe UI", 22.3, "bold", "italic"),text_color="#3e62dc").pack(side="left")

title_label.place(relx=0.012, rely=0.19)

searchlistlabel = ctk.CTkLabel(header_frame, font=('Segoe UI', 14.5), text='🔍',
                               text_color='#888888', anchor="w", bg_color='transparent')
searchlistlabel.place(relx=0.148, rely=0.18)

searchentry = ctk.CTkEntry(header_frame, font=('Segoe UI', 14.5), corner_radius=8,
                           placeholder_text="Search...",
                           border_color="#3e62dc", border_width=1)
searchentry.place(relx=0.170, rely=0.17, relwidth=0.215, relheight=0.66)

search_btn = ctk.CTkButton(header_frame, text='🔎', corner_radius=8,
                           command=youtube_search, fg_color='#3e62dc', hover_color='#4a70f0',
                           font=('Segoe UI', 15.5))
search_btn.place(relx=0.391, rely=0.17, relwidth=0.028, relheight=0.66)

playlistlabel = ctk.CTkLabel(header_frame, font=('Segoe UI', 14.5), text='📁',
                             text_color='#888888', anchor="w", bg_color='transparent')
playlistlabel.place(relx=0.432, rely=0.18)

userplaylistcombobox = ctk.CTkComboBox(header_frame, font=('Segoe UI', 14.5),
                                        values=user_playlists_name, state='readonly', corner_radius=8,
                                        fg_color="#363636", text_color="#c5c5c5",
                                        border_width=0,
                                        button_color="#363636",
                                        button_hover_color="#4a70f0",
                                        dropdown_fg_color="#363636", 
                                        dropdown_hover_color="#3e62dc",
                                        justify="left")
userplaylistcombobox.place(relx=0.455, rely=0.17, relwidth=0.130, relheight=0.66)

enter_playlist_btn = ctk.CTkButton(header_frame, text='▶ Enter', 
                                   command=get_user_playlists, fg_color='#FF6B35', hover_color='#FF8555',
                                   corner_radius=8, font=('Segoe UI', 13.5, 'bold'))
enter_playlist_btn.place(relx=0.591, rely=0.17, relwidth=0.062, relheight=0.66)

searchentry.bind("<Return>", youtube_search)
userplaylistcombobox.bind("<Return>", get_user_playlists)



# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE STATUS PANEL - Combined Chrome Extension & Discord Status
# ═══════════════════════════════════════════════════════════════════════════════
status_panel = ctk.CTkFrame(header_frame, fg_color="#151515", corner_radius=6, 
                            border_width=1, border_color="#3e62dc")
status_panel.place(relx=0.665, rely=0.09, relwidth=0.328, relheight=0.82)

chrome_ext_dot = ctk.CTkLabel(status_panel, text='●', font=('Arial', 15.5),
                               text_color='#333333')
chrome_ext_dot.place(relx=0.031, rely=0.168, relheigh = 0.7)

chrome_ext_text = ctk.CTkLabel(status_panel, text='Chrome Link', 
                                font=('Segoe UI', 14.5), text_color='#777777', anchor="w")
chrome_ext_text.place(relx=0.083, rely=0.158, relheigh = 0.7)



separator = ctk.CTkLabel(status_panel, text='│', font=('Segoe UI', 19.5), text_color='#444444')
separator.place(relx=0.296, rely=0.149, relheigh = 0.7)

discord_status_dot = ctk.CTkLabel(status_panel, text='●', font=('Arial', 15.5),
                                   text_color='#333333')
discord_status_dot.place(relx=0.345, rely=0.168, relheigh = 0.7)

discord_status_text = ctk.CTkLabel(status_panel, text='Discord', 
                                    font=('Segoe UI', 14.5), text_color='#777777', anchor="w")
discord_status_text.place(relx=0.397, rely=0.158, relheigh = 0.7)


separator2 = ctk.CTkLabel(status_panel, text='│', font=('Segoe UI', 19.5), text_color='#444444')
separator2.place(relx=0.540, rely=0.149, relheigh = 0.7)

# Google Profile Container - styled circular frame for profile picture


google_status_profile_pic_label = ctk.CTkLabel(status_panel, text='', font=('Segoe UI', 15.5),
                                               text_color='#555555', fg_color="transparent", 
                                               width=15, height=26, corner_radius=13)
google_status_profile_pic_label.place(relx=0.63, rely=0.5, anchor="center", relheigh = 0.85)
google_status_text = ctk.CTkTextbox(status_panel, 
                                   font=('Segoe UI', 14.5), text_color="#777777", wrap="none",
                                   border_width=0, height=1,fg_color="transparent", activate_scrollbars=False)
google_status_text.place(relx=0.67, rely=0.02, relwidth=0.30, relheigh = 0.9)
google_status_text.configure(state='disabled')

def chrome_ext_status_run():
    chrome_ext_dot.configure(text_color='#00E676')  
    chrome_ext_text.configure(text_color="#34D399") 

def chrome_ext_status_close():
    chrome_ext_dot.configure(text_color='#333333')
    chrome_ext_text.configure(text_color='#777777')

def discord_status_run():
    try:
        discord_status_dot.configure(text_color='#5865F2')  
        discord_status_text.configure(text_color="#5865F2")
    except:pass
def discord_status_close():
    try:
        discord_status_dot.configure(text_color='#333333')
        discord_status_text.configure(text_color='#777777')
    except:pass





# ─────────────────────────────────────────────────────────────────────────────
# RIGHT PANEL - Playlist Treeview & Mode Info
# ─────────────────────────────────────────────────────────────────────────────
right_panel_frame = ctk.CTkFrame(root, fg_color="#1e1e1e", corner_radius=10, border_width=1, border_color="#333333")
right_panel_frame.place(relx=0.618, rely=0.070, relwidth=0.377, relheight=0.560)

mode_header_frame = ctk.CTkFrame(right_panel_frame, fg_color="#252525", corner_radius=8)
mode_header_frame.place(relx=0.020, rely=0.010, relwidth=0.960, relheight=0.115)

current_playlist_frame = ctk.CTkFrame(
    mode_header_frame,
    fg_color='#252525',
    corner_radius=0
)
current_playlist_frame.place(relx=0.010, rely=0.06, relwidth=0.615, relheight=0.88)

current_playlist_caption = ctk.CTkLabel(
    current_playlist_frame,
    text='CURRENT PLAYLIST',
    font=('Segoe UI', 10.5, 'bold'),
    text_color='#777777',
    anchor='w'
)
current_playlist_caption.place(relx=0.025, rely=0.00, relwidth=0.4, relheight=0.32)


playlist_name_textbox = ctk.CTkTextbox(
    current_playlist_frame,
    font=('Segoe UI', 15,"bold"),
    text_color='#c5c5c5',
    fg_color='#252525',
    border_spacing=0,
    border_width=0,
    corner_radius=0,
    wrap='word',
    activate_scrollbars=False,
)
playlist_name_textbox.place(relx=0.01, rely=0.3, relwidth=0.97, relheight=0.7)
insert_textbox(playlist_name_textbox,"Hey! Search, Login or see Recommended")

playlist_history_separator = ctk.CTkLabel(
    mode_header_frame,
    text='│',
    font=('Segoe UI', 27.5),
    text_color='#444444'
)
playlist_history_separator.place(relx=0.630, rely=0.50, anchor='center', relheight=0.96)

history_nav_frame = ctk.CTkFrame(
    mode_header_frame,
    fg_color='#252525',
    corner_radius=0,
    border_width=0
)
history_nav_frame.place(relx=0.635, rely=0.06, relwidth=0.355, relheight=0.88)

history_nav_caption = ctk.CTkLabel(
    history_nav_frame,
    text='PLAYLIST HISTORY',
    font=('Segoe UI', 10.5, 'bold'),
    text_color='#777777'
)
history_nav_caption.place(relx=0.04, rely=0.04, relwidth=0.92, relheight=0.26)

history_back_btn = ctk.CTkButton(
    history_nav_frame,
    text='◀ Back',
    command=lambda: history_control(2),
    fg_color='#2E2E2E',
    hover_color='#404040',
    text_color="#C2C1C1",
    corner_radius=6,
    font=('Segoe UI', 12.5),
    border_width=1,
    border_color='#444444'
)
history_back_btn.place(relx=0.04, rely=0.39, relwidth=0.44, relheight=0.58)

history_forward_btn = ctk.CTkButton(
    history_nav_frame,
    text='Forward ▶',
    command=lambda: history_control(1),
    fg_color='#2E2E2E',
    hover_color='#404040',
    text_color="#C2C1C1",
    corner_radius=6,
    font=('Segoe UI', 12.5),
    border_width=1,
    border_color='#444444'
)
history_forward_btn.place(relx=0.52, rely=0.39, relwidth=0.44, relheight=0.58)



# Playlist Treeview
playlisttreebox = ttk.Treeview(right_panel_frame, columns=("title"), height=4, 
                               selectmode="browse", show='tree')
playlisttreebox.heading("#0", text="")
playlisttreebox.heading("title", text="")
playlisttreebox.column("#0", width=int(170*tkinter_scaling), anchor="w", stretch=False)
playlisttreebox.column("title", width=1000, anchor="w", stretch=False)
playlisttreebox.place(relx=0.020, rely=0.135, relwidth=0.925, relheight=0.828)
playlisttreebox.bind('<Double-1>', download_and_play)
playlisttreebox.bind('<ButtonRelease-1>', get_selected_vid)


Y_scrollbar = ttk.Scrollbar(right_panel_frame)
X_scrollbar = ttk.Scrollbar(right_panel_frame, orient='horizontal')
X_scrollbar.configure(command=playlisttreebox.xview)
Y_scrollbar.configure(command=playlisttreebox.yview)
playlisttreebox.configure(xscrollcommand=X_scrollbar.set, yscrollcommand=Y_scrollbar.set)
Y_scrollbar.place(relx=0.945, rely=0.135, relheight=0.828)
X_scrollbar.place(relx=0.020, rely=0.963, relwidth=0.925)

playlist_btn_frame = ctk.CTkFrame(root, fg_color="#1e1e1e", border_color="#333333", border_width=1, corner_radius=10)
playlist_btn_frame.place(relx=0.618, rely=0.630, relwidth=0.377, relheight=0.130)

# Hero action button
playselectedsong = ctk.CTkButton(playlist_btn_frame, text='▶ Play',
                                  command=lambda: download_and_play(), fg_color='#3e62dc',
                                  hover_color='#4a70f0', corner_radius=8, font=('Segoe UI', 14.5, 'bold'))
playselectedsong.place(relx=0.212, rely=0.54, relwidth=0.19, relheight=0.33)

# Source buttons in a compact row
_src_w = 0.187
_src_gap = 0.008
recommendation_btn = ctk.CTkButton(playlist_btn_frame, text='🏠Recommend',
                                    command=lambda: threading.Thread(daemon=True, target=lambda: get_youtube_playlists("home")).start(),
                                    fg_color='#2E2E2E', hover_color='#404040', corner_radius=6,
                                    font=('Segoe UI', 13), border_width=1, border_color='#444444')
recommendation_btn.place(relx=0.020, rely=0.1, relwidth=_src_w, relheight=0.33)

load_star_btn = ctk.CTkButton(playlist_btn_frame, text='★ Star',
                        command= lambda :threading.Thread(daemon=True, target=get_starred_vid).start(), fg_color='#2E2E2E', hover_color='#404040',
                        corner_radius=6, font=('Segoe UI', 13), border_width=1, border_color='#444444')
load_star_btn.place(relx=0.020, rely=0.54, relwidth=_src_w, relheight=0.33)

sub_btn = ctk.CTkButton(playlist_btn_frame, text='🔔Subcription',
                        command=lambda: get_youtube_playlists("sub"), fg_color='#2E2E2E', hover_color='#404040',
                        corner_radius=6, font=('Segoe UI', 13), border_width=1, border_color='#444444')
sub_btn.place(relx=0.020+(_src_w+_src_gap)*1, rely=0.1, relwidth=_src_w, relheight=0.33)

like_btn = ctk.CTkButton(playlist_btn_frame, text='👍Like',
                         command=lambda: get_youtube_playlists("like"), fg_color='#2E2E2E', hover_color='#404040',
                         corner_radius=6, font=('Segoe UI', 13), border_width=1, border_color='#444444')
like_btn.place(relx=0.020+(_src_w+_src_gap)*2, rely=0.1, relwidth=_src_w, relheight=0.33)

playselectedfile = ctk.CTkButton(playlist_btn_frame, text='📄 File',
                                  command=lambda: load_local_files(mode=0), fg_color='#2E2E2E',
                                  hover_color='#404040', corner_radius=6, font=('Segoe UI', 13),
                                  border_width=1, border_color='#444444')
playselectedfile.place(relx=0.020+(_src_w+_src_gap)*3, rely=0.1, relwidth=_src_w, relheight=0.33)

playselectedfolder = ctk.CTkButton(playlist_btn_frame, text='📁 Folder',
                                    command=lambda: load_local_files(mode=1), fg_color='#2E2E2E',
                                    hover_color='#404040', corner_radius=6, font=('Segoe UI', 13),
                                    border_width=1, border_color='#444444')
playselectedfolder.place(relx=0.020+(_src_w+_src_gap)*4, rely=0.1, relwidth=_src_w, relheight=0.33)

# Page navigation
page_nav_frame = ctk.CTkFrame(playlist_btn_frame, fg_color="#262626", corner_radius=8)
page_nav_frame.place(relx=_src_w*2+_src_gap*2+0.02, rely=0.52, relwidth=_src_w*3+_src_gap*2, relheight=0.38)

prev_page_btn = ctk.CTkButton(page_nav_frame, text='◀ Prev',
                               command=lambda: page_control(2), fg_color='#2E2E2E', hover_color='#404040',
                               corner_radius=8, font=('Segoe UI', 13.5), border_width=1, border_color='#444444')
prev_page_btn.place(relx=0.02, rely=0.116, relwidth=0.28, relheight=0.767)

next_page_btn = ctk.CTkButton(page_nav_frame, text='Next ▶',
                               command=lambda: page_control(1), fg_color='#2E2E2E', hover_color='#404040',
                               corner_radius=8, font=('Segoe UI', 13.5), border_width=1, border_color='#444444')
next_page_btn.place(relx=0.32, rely=0.116, relwidth=0.28, relheight=0.767)

liked_page_label = ctk.CTkLabel(page_nav_frame, font=('Segoe UI', 14.5), text='📄',
                                anchor="w", fg_color="transparent")
liked_page_label.place(relx=0.630 ,rely=0.15)

page_num_label = ctk.CTkLabel(page_nav_frame, font=('Segoe UI', 14.5), text='',
                                     text_color='#888888', anchor="w", fg_color="transparent")
page_num_label.place(relx=0.70, rely=0.15)

# ─────────────────────────────────────────────────────────────────────────────
# LEFT PANEL - Video Player
# ─────────────────────────────────────────────────────────────────────────────
video_container = ctk.CTkFrame(root, fg_color="#0a0a0a", corner_radius=10, border_width=2, border_color="#3e62dc")
video_container.place(relx=0.005, rely=0.070, relwidth=0.607, relheight=0.685)

Frame_for_mpv.place(relx=0.011, rely=0.084, relwidth=0.595, relheight=0.664)
Frame_for_mpv.lift()

# ─────────────────────────────────────────────────────────────────────────────
# TRANSPORT BAR - Full-width bottom bar (Now Playing + Progress + Controls)
# ─────────────────────────────────────────────────────────────────────────────
controls_frame = ctk.CTkFrame(root, fg_color="#141414", corner_radius=10, border_width=1, border_color="#2a2a2a")
controls_frame.place(relx=0.005, rely=0.764, relwidth=0.990, relheight=0.230)

# ── Now Playing Strip ──
now_playing_frame = ctk.CTkFrame(controls_frame, fg_color="#1c1c1c", corner_radius=8)
now_playing_frame.place(relx=0.008, rely=0.102, relwidth=0.984, relheight=0.240)

np_icon = ctk.CTkLabel(now_playing_frame, text='🎶', font=('Segoe UI', 17.5))
np_icon.place(relx=0.008, rely=0.14)

playing_title_textbox = ctk.CTkTextbox(
    now_playing_frame,
    font=('Segoe UI', 18.5, "bold"),
    text_color='#c5c5c5',
    fg_color='#1c1c1c',
    corner_radius=0,
    border_width=0,
    border_spacing=0,
    wrap='word',
    state='disabled',
    activate_scrollbars=False,
)
playing_title_textbox.place(relx=0.035, rely=0.15, relwidth=0.95, relheight=0.9)

# ── Progress Bar ──
progress_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
progress_frame.place(relx=0.008, rely=0.405, relwidth=0.984, relheight=0.230)

player_pos_label = ctk.CTkLabel(progress_frame, font=('Segoe UI Variable Display Semib', 15.5),
                                textvariable=pos_for_label, text_color="#7d9bff", anchor="e")
player_pos_label.place(relx=0, rely=0.03, relwidth=0.050)

player_position_scale = ctk.CTkSlider(progress_frame, from_=0, command=scaler_start_seek,
                                       progress_color='#3e62dc', button_color='#5080ff',
                                       button_hover_color='#6090ff', fg_color='#333333')
player_position_scale.set(0)
player_position_scale.bind('<ButtonRelease-1>', scaler_finish_seek)
player_position_scale.place(relx=0.055, rely=0.12, relwidth=0.850, relheight=0.45)

player_song_length_label = ctk.CTkLabel(progress_frame, font=('Segoe UI Variable Display Semib', 15.5),
                                         text_color="#9E9E9E", anchor="w", text='')
player_song_length_label.place(relx=0.922, rely=0.03, relwidth=0.068)


# ── Transport Row: Mode | Playback | Volume | Actions ──
mode_frame = ctk.CTkFrame(controls_frame, fg_color="#1c1c1c", corner_radius=10)
mode_frame.place(relx=0.008, rely=0.585, relwidth=0.132, relheight=0.375)

mode_label = ctk.CTkLabel(mode_frame, text='Mode', font=('Segoe UI', 14.5), text_color="#6A6969")
mode_label.place(relx=0.06, rely=0.07)

player_mode_continue = ctk.CTkRadioButton(mode_frame, text='▶▶', variable=player_mode_selector,
                                           value='continue', 
                                           font=('Segoe UI', 14.5), radiobutton_width=16, radiobutton_height=16)
player_mode_continue.place(relx=0.06, rely=0.45)

player_mode_replay = ctk.CTkRadioButton(mode_frame, text='🔁', variable=player_mode_selector,
                                         value='replay', 
                                         font=('Segoe UI', 14.5), radiobutton_width=16, radiobutton_height=16)
player_mode_replay.place(relx=0.39, rely=0.45)

player_mode_random = ctk.CTkRadioButton(mode_frame, text='🔀', variable=player_mode_selector,
                                         value='random', 
                                         font=('Segoe UI', 14.5), radiobutton_width=16, radiobutton_height=16)
player_mode_random.place(relx=0.72, rely=0.45)

playback_frame = ctk.CTkFrame(controls_frame, fg_color="#1c1c1c", corner_radius=20)
playback_frame.place(relx=0.150, rely=0.585, relwidth=0.43, relheight=0.375)

prevsong = ctk.CTkButton(playback_frame, text='⏮', command=lambda: playprevnext(2),
                         fg_color='transparent', hover_color='#333333', corner_radius=20,
                         font=('Segoe UI', 18.5))
prevsong.place(relx=0.02, rely=0.08, relwidth=0.15, relheight=0.8)

pausebutton = ctk.CTkButton(playback_frame, textvariable=pauseStr,
                            command=lambda: pause(1), fg_color='#3e62dc', hover_color='#4a70f0',
                            corner_radius=20, font=('Segoe UI', 18.5, 'bold'))
pausebutton.place(relx=0.18, rely=0.08, relwidth=0.15, relheight=0.8)
pauseStr.set('▶')

stopbutton = ctk.CTkButton(playback_frame, text='⏹', command=stop_playing_video,
                           fg_color='transparent', hover_color='#333333', corner_radius=20,
                           font=('Segoe UI', 18.5))
stopbutton.place(relx=0.34, rely=0.08, relwidth=0.15, relheight=0.8)

nextsong = ctk.CTkButton(playback_frame, text='⏭', command=lambda: playprevnext(1),
                         fg_color='transparent', hover_color='#333333', corner_radius=20,
                         font=('Segoe UI', 18.5))
nextsong.place(relx=0.50, rely=0.08, relwidth=0.15, relheight=0.8)

# make fullscreen button match the other transport controls (transparent background, same corner radius/font)
fullscreenbtn = ctk.CTkButton(playback_frame, text='⛶', command=fullscreen_change_state,
                               fg_color='transparent', hover_color='#333333', corner_radius=20,
                               font=('Segoe UI', 18.5))
# slightly narrower so it doesn't crowd the playback buttons
fullscreenbtn.place(relx=0.66, rely=0.08, relwidth=0.15, relheight=0.8)

player_loading_label = ctk.CTkLabel(playback_frame, font=('Segoe UI', 13.5), text='',
                                     text_color='#FF6B35', anchor="center",
                                     fg_color="transparent")
player_loading_label.place(relx=0.81, rely=0.25, relwidth=0.18)

volume_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
volume_frame.place(relx=0.595, rely=0.605, relwidth=0.105, relheight=0.350)

player_volume_label = ctk.CTkLabel(volume_frame, font=('Segoe UI', 17.5), text='🔊',
                                   text_color='#888888', anchor="e")
player_volume_label.place(relx=0, rely=0.2, relwidth=0.120)

player_volume_scale = ctk.CTkSlider(volume_frame, from_=0, to=120, command=set_volume,
                                    progress_color='#FF6B35', button_color='#FF8555',
                                    button_hover_color='#FFA575', fg_color='#333333')
player_volume_scale.set(50)
player_volume_scale.bind('<MouseWheel>', set_volume_wheel)
player_volume_scale.place(relx=0.180, rely=0.35, relwidth=0.780, relheight=0.28)

Frame_for_mpv.bind('<MouseWheel>', set_volume_wheel)


# ── Action Buttons ──
action_btn_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
action_btn_frame.place(relx=0.705, rely=0.585, relwidth=0.290, relheight=0.375)

setting_btn = ctk.CTkButton(action_btn_frame, text='⚙️ Settings', command=setting_frame,
                            fg_color='#FF6B35', hover_color='#FF8555', corner_radius=8,
                            font=('Segoe UI', 14.5, 'bold'))
setting_btn.place(relx=0, rely=0.06, relwidth=0.290, relheight=0.88)

star_btn = ctk.CTkButton(action_btn_frame, text='☆', command=switch_starred_vid,
                            fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0',
                            corner_radius=8, font=('Segoe UI', 14.5, 'bold'))
star_btn.place(relx=0.305, rely=0.06, relwidth=0.200, relheight=0.88)


video_info_btn_frame = ctk.CTkFrame(action_btn_frame, fg_color='#252525',
                                     border_color='#444444', border_width=1,
                                     corner_radius=8)
video_info_btn_frame.place(relx=0.520, rely=0.06, relwidth=0.475, relheight=0.88)

video_info_title = ctk.CTkLabel(video_info_btn_frame, text='ⓘ Video Info',
                                font=('Segoe UI', 13.5, 'bold'), text_color='#D0D0D0',
                                anchor='center')
video_info_title.place(relx=0.04, rely=0.04, relwidth=0.92, relheight=0.34)

select_info_btn = ctk.CTkButton(video_info_btn_frame, text='Selected',
                                 command=lambda: video_info_frame_main(1), fg_color='#303030',
                                 hover_color='#454545', corner_radius=6, font=('Segoe UI', 13),
                                 border_width=1, border_color='#4A4A4A')
select_info_btn.place(relx=0.04, rely=0.42, relwidth=0.44, relheight=0.47)

playing_info_btn = ctk.CTkButton(video_info_btn_frame, text='Playing',
                                  command=lambda: video_info_frame_main(2), fg_color='#303030',
                                  hover_color='#454545', corner_radius=6, font=('Segoe UI', 13),
                                  border_width=1, border_color='#4A4A4A')
playing_info_btn.place(relx=0.52, rely=0.42, relwidth=0.44, relheight=0.47)



motto_label.bind('<MouseWheel>', set_volume_wheel)
motto_label.bind('<Button-1>', lambda event: pause(1))  

root.bind('<Escape>', fullscreen_change_state)
root.bind('<space>', lambda event: pause(2))
root.bind("<KeyPress-Left>", lambda event: set_position_keyboard(1))
root.bind("<KeyPress-Right>", lambda event: set_position_keyboard(2))
root.bind("<KeyRelease-Right>", arrow_release)
root.bind("<KeyRelease-Left>", arrow_release)




root.mainloop()
