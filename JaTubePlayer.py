import time
from types import NoneType

time1 = time.time()
import tkinter as tk
from tkinter import ttk,filedialog
from tkinter import *
import os,re,ffmpeg,io,json,sys,sv_ttk,threading,webbrowser,sys,time,math,random,queue,asyncio,win32gui
from PIL import Image, ImageTk 
from random import shuffle
import googleapiclient.errors
from concurrent.futures import ThreadPoolExecutor
from copy import *
from datetime import datetime
import customtkinter as ctk
import ctypes
ctk.set_appearance_mode("dark")

from utils.get_scaling import get_window_dpi
from utils.ctk_get_scaling_patch import _apply_google_auth_patch
from utils.load_yt_dlp import *
from utils.get_related_video import *
from utils.download_to_local import download_to_local
from utils.check_internet import *
from utils.check_internet import check_internet
from utils.get_media_info import get_info

from notification.wintoast_notify import ToastNotification
from notification.ctkmessagebox import ctk_messagebox

from ui.blur_for_winsys import blur

from system.tray import Playertray
from system.dnd_winsys import *
from system.keyboard import *
from system.presence import DiscordPresence

_apply_google_auth_patch()
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Jackaopen.JaTubePlayer')





if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)
    icondir = os.path.join(current_dir, '_internal','jtp.ico')
    _internal_dir = os.path.join(current_dir, '_internal')
else:
    icondir = os.path.join(os.path.dirname(__file__), '_internal','jtp.ico')
    current_dir = os.path.dirname(__file__)
    _internal_dir = os.path.join(os.path.dirname(__file__), '_internal')



os.environ["PATH"] = _internal_dir + os.pathsep + os.environ["PATH"]
import mpv
#### remember to add yt_dlp.exe from github to _iternal!!!
root = ctk.CTk()
ver='2.2'
root.title(f'JaTubePlayer {ver} by Jackaopen')
root.geometry('1320x680')
root.iconbitmap(icondir)
hwnd = win32gui.FindWindow(None, root.title())
tkinter_scaling = get_window_dpi(hwnd)/1.25 # 1.25 is 100% scaling




ui_queue = queue.Queue()
def _process_ui_queue():
    try:
        for _ in range(200):
            f = ui_queue.get_nowait()
            try:f()
            except Exception as e:log_handle(e)
    except queue.Empty:pass
    root.after(20, _process_ui_queue)
root.after(20, _process_ui_queue)

messagebox = ctk_messagebox(root,_internal_path=_internal_dir)

mpv_log = []
def _toggle_minimize():
    if root.state() == 'normal':
        root.lift()
        root.iconify()
    else:
        root.deiconify()

def log_handle(errtype="",component="main_system",content="") -> None:
    global force_stop_loading
    '''
    type : error, warn, info, debug
    component : name of the component, not strictly required
    '''
    try:
        errtype = str(errtype)
        component = str(component)
        content = str(content)
    except:
        errtype = 'error'
        component = 'log_handle'
        content = 'Log content conversion to str failed'

    if len(mpv_log) > 2000:mpv_log.pop(0)
    mpv_log.append(f'{datetime.now().strftime("%H:%M:%S")} [{errtype}] <{component}> -- {content}')
    
    
    if errtype == 'error' and component == 'yt-dlp':
        error_msg = str(content.lower())
        if "live event will" in error_msg:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','This live event hasn\'t started yet'))
            force_stop_loading = True
        elif "unavailable" in error_msg:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Video unavailable'))
            force_stop_loading = True
        elif "private" in error_msg:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Video is private'))
            force_stop_loading = True
        elif "members-only" in error_msg or "members" in error_msg:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Video is members-only, try to use or update cookies file'))
            force_stop_loading = True
        elif "Sign in" in error_msg or "not a bot" in error_msg:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Youtube is asking for sign in or captcha verification, please try to use cookies file'))
            force_stop_loading = True
        elif " not currently live" in error_msg:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','The channel is not currently live'))
            force_stop_loading = True
        elif "does not exist" in error_msg:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','The video does not exist'))
            force_stop_loading = True
        elif "No video formats found!" in error_msg:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','No video formats found!'))
            force_stop_loading = True
    if "cookies are no longer valid" in content:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Your cookies file may be invalid or expired'))

    
    try:
        print(f'{datetime.now().strftime("%H:%M:%S")} [{errtype}] <{component}> -- {content}')
        insert_log(content = f"{datetime.now().strftime('%H:%M:%S')} [{errtype}] <{component}> -- {content}\n")
    
    except:pass
class ytdlp_log_handler():
    def debug(self, msg):
        log_handle(errtype='debug',component='yt-dlp',content=msg)
    def info(self, msg):
        log_handle(errtype='info',component='yt-dlp',content=msg)
    def warning(self, msg):
        log_handle(errtype='warn',component='yt-dlp',content=msg)
    def error(self, msg):
        log_handle(errtype='error',component='yt-dlp',content=msg)

log_handle(f'Import JaTubePlayer2.0 modules time: {time.time() - time1:.3f}s')



def dump(filename,content):
    try:
        with open(os.path.join(current_dir,'temp_data',f'{filename}.json'),'w') as f:
            json.dump(content,f,indent=4)
    except:pass



Frame_for_mpv = tk.Frame(root)
Frame_for_mpv.place(relx=0.011, rely=0.084, relwidth=0.595, relheight=0.664)
Frame_for_mpv.bind('<Button-1>',lambda event :pause(1))

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
playing_vid_info_dict = ''
selected_song_number = None
yt_dlp = None
youtube = None
vid_url = []
playlisttitles = []
playlist_thumbnails = []
playlist_channel = []
user_playlists_name = []
load_thread_queue = queue.Queue()
'''
This accept a tuple (chosen_file,direct_url)
'''
playing_vid_info_dict = {}
player_speed = tk.DoubleVar()
player_speed.set(1.0)
deno_exe = os.path.join(_internal_dir,'deno.exe')

subtitle_namelist = ['No subtitles']
subtitle_urllist = [None]

subtitle_selection_idx = tk.IntVar()
subtitle_selection_idx.set(0)



# ==== UI 控制變數 ====

playlistID = tk.StringVar()
autoretry = tk.BooleanVar()
fullscreenwithconsole = tk.BooleanVar()
maxresolution = tk.IntVar()
selected_song_title = tk.StringVar()
downloadhooktext = tk.StringVar()
ytdlp_log_handle = ytdlp_log_handler()
info = None




def _init_load_extra_objs():
    global dnd_handle,discord_presence,google_control,Ferner_encrptor_
    Ferner_encrptor_ = Ferner_encrptor(user_data_dir=os.path.join(current_dir,'user_data'),ctk_messagebox=messagebox)
    
    dnd_handle=DropHandler()
    discord_presence=DiscordPresence(discord_status_run=discord_status_run,discord_status_close=discord_status_close)
    google_control = google_auth_control(ver=ver,youtubeAPI=Ferner_encrptor_.decrypte_api(),current_dir=current_dir,log_handle=log_handle,ctk_messagebox=messagebox)





# ==== 狀態控制 ====

loadingplaylist = False
loadingvideo = False
insert_treeview_quene = queue.Queue()
dnd_path_queue = queue.Queue()
auto_check_ver = tk.BooleanVar()
save_history = tk.BooleanVar()
init_quickstartup_mode = tk.StringVar()
init_toggle_quickstartup = tk.BooleanVar()
auto_sub_refresh = tk.BooleanVar()
auto_like_refresh = tk.BooleanVar()
setting_run_chrome_extension_server = tk.BooleanVar()
audio_only = tk.BooleanVar()
enable_drag_and_drop = tk.BooleanVar()
open_with_fullscreen = tk.BooleanVar()
show_cache = tk.BooleanVar()
youtubeAPI = None
force_stop_loading = False
is_downloading = tk.BooleanVar()
is_downloading.set(False)
hover_fullscreen = tk.BooleanVar()
cache_secs = tk.IntVar()
demuxer_max_bytes = tk.IntVar()
demuxer_max_back_bytes = tk.IntVar()
cache_pause_wait = tk.DoubleVar()
audio_wait_open= tk.IntVar()
download_path = tk.StringVar()
enable_discord_presence = tk.BooleanVar()
discord_presence_show_playing = tk.BooleanVar()
fullscreenmode = tk.IntVar()
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


# ==== 系統相關 ====
credentials = None
cookies_dir = None
client_secret_path = None

# ==== config ====


def save_config():
    '''
    This function saves the current configuration to the config.json file. It gathers the current values of all relevant configuration variables and writes them to the file in JSON format.
    '''
    global CONFIG
    with open(os.path.join(current_dir,'user_data','config.json'),'w') as f:
        json.dump(CONFIG,f,indent=4)
def load_config():
    global CONFIG
    with open(os.path.join(current_dir,'user_data','config.json'),'r') as f:
        CONFIG = json.load(f)
load_config()

# ==== async for thumbnail ====
asyncio_session = None # aiohttp.ClientSession
async_task = [] # task to add thumbnail

# ==== others ====

liked_vid_url = []
page_num = 0

# =====playerinit=====

position = 0
scale_clicked= False
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
blur_window = tk.BooleanVar()
blur_window.set(CONFIG.get('blur'))

if blur_window.get():blur(hwnd, Dark=True, Acrylic=True)  

'''
win32gui.FindWindow(class_name, window_name)
    class_name → we pass None → “I don’t care about the class; match any class.”
    window_name → we pass root.title() → “find the window whose title is exactly this text.”'''


def get_selected_vid(event=None):
    global selected_song_number,star_vid_handle
    try:selected_song_number = playlisttreebox.index(playlisttreebox.selection()[0])
    except:pass
    try:
        if star_vid_handle.search(vid_url[selected_song_number]):
            ui_queue.put(lambda: star_btn.configure(
                text='★',
                fg_color='#D4A017',
                hover_color='#E8B820',
                text_color='#FFFDE7',
                font=('Segoe UI', 13, 'bold')
            ))
        else:
            ui_queue.put(lambda: star_btn.configure(
                text='☆',
                fg_color='#3A3A3A',
                hover_color='#505050',
                text_color='#B0B0B0',
                font=('Segoe UI', 13, 'bold')
            ))
    except:pass


def _extract_file(query):#for threadpool in get sub channel
    try:
        time.sleep(random.uniform(0.1, 2.5))#to prevent being blocked by yt
        ydl_opts = {
                'quiet': True,        
                'extract_flat': True, 
                'skip_download':True,
                "playlistend": 2,
                'logger': ytdlp_log_handle
            }   
    
        if cookies_dir:ydl_opts['cookiefile'] = cookies_dir
        with yt_dlp.YoutubeDL(ydl_opts)as ydl:
            data = ydl.extract_info(query , download=False)
        return data
    except Exception as e:
        log_handle(content=e)
        return None





        
def _switch_local_server(mode:int)->None|str:
    '''
    mode: 0=start ,1=stop

    This function is used to start/stop the local server for chrome extension communication
    This function includes CONFIG and bool var setting_run_chrome_extension_server update
    '''
    global listen_chromeextension_thread,chrome_extension_flask_thread,setting_run_chrome_extension_server
    if mode == 0:


        try:
            listen_chromeextension_thread = threading.Thread(daemon = True,target=init_listen_chromeextension)
            chrome_extension_flask_thread = threading.Thread(daemon = True,target=lambda:chrome_extension_flask.run_flask_app(icondir=icondir))
            listen_chromeextension_thread.start()
            chrome_extension_flask_thread.start()
            setting_run_chrome_extension_server.set(True)
            try:
                root.after(0, chrome_ext_status_run)
            except:pass

            
        except Exception as e:
            return str(e)
        
    elif mode == 1:
        log_handle(content="Shutting down local server for chrome extension communication...")
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
                
        
        

temp = []# to prevent garbage collection of images
async def load_thumbnail_thread(session,id,thumburl):
    try:
        if playing_vid_mode == 0 or playing_vid_mode == 4:
            async with session.get(thumburl) as response:
                imgdata = await response.read()
                img = Image.open(io.BytesIO(imgdata))
                img = img.resize((int(140*tkinter_scaling/1.25), int(105*tkinter_scaling/1.25)), Image.LANCZOS)
                img1 = img.crop((0,int(14*tkinter_scaling/1.25),int(140*tkinter_scaling/1.25),int(90*tkinter_scaling/1.25)))
                thumbnailpic = ImageTk.PhotoImage(img1)
                temp.append(thumbnailpic)
                ui_queue.put(lambda id=id, pic=thumbnailpic: playlisttreebox.item(id, image=pic))
    except Exception as e:
        log_handle(content=str(e))



@check_internet
def vid_info_frame(mode):## 1 = selextd ;2 = playing
    global info
    log_handle(content=f"info frame mode: {info}")
    try:
        if info and info.winfo_exists():
            info.lift()
            info.deiconify()
        else:raise Exception("info window already opened")
    except:
        if mode == 1:
            if playing_vid_mode == 0 or playing_vid_mode == 4 or (playing_vid_mode == 3 and len(vid_url) > 0):
                if selected_song_number == None:
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','No video selected'))
                    return
                if playing_vid_mode == 4 and not vid_url[selected_song_number].startswith(('https://','https://')):
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','The selected video is a local file, video info function is only available for online videos'))
                    ui_queue.put(lambda: info.destroy())
                    return
                
            if playing_vid_mode == 1 or playing_vid_mode == 2:
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','Video info function is only available for YouTube videos'))
                return
        elif mode == 2:
            if playing_vid_mode == 1 or playing_vid_mode == 2:
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','Video info function is only available for YouTube videos'))
                return
            if playing_vid_mode == 4 and not playing_vid_info_dict:
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','Video info is not available for this video'))
                return

        info = ctk.CTkToplevel(root,fg_color='#242424')
        info.title('Video info')
        info.geometry('600x500')
        info.attributes('-topmost','true')
        info.update()
        if blur_window.get():root.after(200,lambda:blur(win32gui.FindWindow(None,info.title()), Dark=True, Acrylic=True))
        
        root.after(200,lambda:info.iconbitmap(icondir))
        def leave():
            root.attributes('-topmost','false')
            info.destroy()
        info.protocol('WM_DELETE_WINDOW',leave)

        # Main container frame with padding
        info_main_frame = ctk.CTkFrame(info, fg_color='transparent')
        info_main_frame.pack(fill='both', expand=True, padx=20, pady=15)

        # Video details frame (title, uploader, date, url)
        details_frame = ctk.CTkFrame(info_main_frame, fg_color='#2E2E2E', corner_radius=10)
        details_frame.pack(fill='x', pady=(0, 10))
        details_frame.grid_columnconfigure(1, weight=1)

        # Title row
        title_label = ctk.CTkLabel(details_frame, text=' Title:', font=('Arial', 13, 'bold'), text_color='#9CA3AF', anchor='w', width=100)
        title_text = ctk.CTkTextbox(details_frame, font=('Arial', 13), height=28, fg_color='#1F1F1F', border_width=1, border_color='#3B3B3B', corner_radius=6, activate_scrollbars=False, wrap="none")
        title_label.grid(row=0, column=0, padx=(15, 5), pady=(15, 8), sticky='w')
        title_text.grid(row=0, column=1, padx=(5, 15), pady=(15, 8), sticky='ew')

        # Uploader row
        uploader_label = ctk.CTkLabel(details_frame, text=' Uploader:', font=('Arial', 13, 'bold'), text_color='#9CA3AF', anchor='w', width=100)
        uploader_text = ctk.CTkTextbox(details_frame, font=('Arial', 13), height=28, fg_color='#1F1F1F', border_width=1, border_color='#3B3B3B', corner_radius=6, activate_scrollbars=False, wrap="none")
        uploader_label.grid(row=1, column=0, padx=(15, 5), pady=8, sticky='w')
        uploader_text.grid(row=1, column=1, padx=(5, 15), pady=8, sticky='ew')

        # Upload date row
        uploaddate_label = ctk.CTkLabel(details_frame, text=' Date:', font=('Arial', 13, 'bold'), text_color='#9CA3AF', anchor='w', width=100)
        uploaddate_text = ctk.CTkTextbox(details_frame, font=('Arial', 13), height=28, fg_color='#1F1F1F', border_width=1, border_color='#3B3B3B', corner_radius=6, activate_scrollbars=False, wrap="none")
        uploaddate_label.grid(row=2, column=0, padx=(15, 5), pady=8, sticky='w')
        uploaddate_text.grid(row=2, column=1, padx=(5, 15), pady=8, sticky='ew')

        # URL row
        url_label = ctk.CTkLabel(details_frame, text=' URL:', font=('Arial', 13, 'bold'), text_color='#9CA3AF', anchor='w', width=100)
        url_text = ctk.CTkTextbox(details_frame, font=('Arial', 13), height=28, fg_color='#1F1F1F', border_width=1, border_color='#3B3B3B', corner_radius=6, activate_scrollbars=False, wrap="none")
        url_label.grid(row=3, column=0, padx=(15, 5), pady=(8, 15), sticky='w')
        url_text.grid(row=3, column=1, padx=(5, 15), pady=(8, 15), sticky='ew')

        # Description frame
        description_frame = ctk.CTkFrame(info_main_frame, fg_color='#2E2E2E', corner_radius=10)
        description_frame.pack(fill='both', expand=True)

        description_label = ctk.CTkLabel(description_frame, text=' Description', font=('Arial', 13, 'bold'), text_color='#9CA3AF', anchor='w')
        description_label.pack(padx=15, pady=(12, 8), anchor='w')
        
        description_text = ctk.CTkTextbox(description_frame, font=('Arial', 13), fg_color='#1F1F1F', border_width=1, border_color='#3B3B3B', corner_radius=6)
        description_text.pack(padx=15, pady=(0, 15), fill='both', expand=True)

        def loadselectedinfo():
            global info
            log_handle(content=f"load selected info, mode: {playing_vid_mode}, url: {vid_url[selected_song_number] if selected_song_number != None and len(vid_url) > 0 else 'N/A'}")
            try:
                
                ui_queue.put(lambda: info.title('loading info...'))
                _,info_dict = get_info(yt_dlp=yt_dlp,
                                    maxres=1080,
                                    target_url=vid_url[selected_song_number],
                                    deno_path=deno_exe,
                                    log_handler=ytdlp_log_handle,
                                    cookie_path=cookies_dir)
                    
                
                ui_queue.put(lambda: info.title('Video info '))
                ui_queue.put(lambda: title_text.configure(state='normal'))
                ui_queue.put(lambda t=info_dict.get('title'): title_text.insert(tk.END, t))
                ui_queue.put(lambda c=info_dict.get('channel'), u=info_dict.get('uploader_id'): uploader_text.insert(tk.END, f"{c}{u}"))
                ui_queue.put(lambda d=info_dict.get('upload_date'): uploaddate_text.insert(tk.END, d))
                ui_queue.put(lambda url=info_dict.get('original_url'): url_text.insert(tk.END, url))
                ui_queue.put(lambda desc=info_dict.get('description'): description_text.insert(tk.END, desc))
                ui_queue.put(lambda: title_text.configure(state='disabled'))
                ui_queue.put(lambda: uploader_text.configure(state='disabled'))
                ui_queue.put(lambda: uploaddate_text.configure(state='disabled'))
                ui_queue.put(lambda: url_text.configure(state='disabled'))
                ui_queue.put(lambda: description_text.configure(state='disabled'))

                ui_queue.put(lambda t=info_dict.get('title'): info.configure(title=f"Selected Video info - {t}"))

            except Exception as e : 
                try:       
                    ui_queue.put(lambda: description_text.configure(state='normal'))
                    ui_queue.put(lambda err=e: description_text.insert(tk.END, f'opps we got some problmes\n{err}'))
                    ui_queue.put(lambda: description_text.configure(state='disabled'))
                except:pass

            except googleapiclient.errors.HttpError as err: ######  handle stupid api
                ui_queue.put(lambda e=err: messagebox.showerror(f'JaTubePlayer {ver}', f"An error occurred: {e}"))
                ui_queue.put(lambda: info.destroy())

        def loadplayinginfo():

            if playing_vid_info_dict == None:
                ui_queue.put(lambda: description_text.configure(state='normal'))
                ui_queue.put(lambda: description_text.insert(tk.END,f"opps we got some problems"))
                ui_queue.put(lambda: description_text.configure(state='disabled'))

            else:
                ui_queue.put(lambda: title_text.configure(state='normal'))
                ui_queue.put(lambda t=playing_vid_info_dict.get('title'): title_text.insert(tk.END, t))
                ui_queue.put(lambda c=playing_vid_info_dict.get('channel'), u=playing_vid_info_dict.get('uploader_id'): uploader_text.insert(tk.END, f"{c}{u}"))
                ui_queue.put(lambda d=playing_vid_info_dict.get('upload_date'): uploaddate_text.insert(tk.END, d))
                ui_queue.put(lambda url=playing_vid_info_dict.get('original_url'): url_text.insert(tk.END, url))
                ui_queue.put(lambda desc=playing_vid_info_dict.get('description'): description_text.insert(tk.END, desc))
                ui_queue.put(lambda: title_text.configure(state='disabled'))
                ui_queue.put(lambda: uploader_text.configure(state='disabled'))
                ui_queue.put(lambda: uploaddate_text.configure(state='disabled'))
                ui_queue.put(lambda: url_text.configure(state='disabled'))
                ui_queue.put(lambda: description_text.configure(state='disabled'))

                ui_queue.put(lambda t=playing_vid_info_dict.get('title'): info.configure(title=f"Playing Video info - {t}"))



        if mode == 1:
            infothread = threading.Thread(daemon = True,target=loadselectedinfo)
            infothread.start()
        elif mode == 2 :
            infothread = threading.Thread(daemon = True,target=loadplayinginfo)
            infothread.start()
        info.mainloop()
        


def setting_frame():
    global setting_api_entry,maxresolutioncombobox,setting,setting_closed,init_playlist_combobox,subtitlecombobox
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
        setting.geometry('720x500')
        setting.resizable(False, False)
        formats = tk.IntVar()
        formats.set(-1)
        #setting.resizable(False, False)
        setting_closed = False
        root.after(800, lambda: (setting.lift(), setting.iconbitmap(icondir)))
        if blur_window.get():blur(win32gui.FindWindow(None,setting.title()), Dark=True, Acrylic=True)

        setting_tab = ctk.CTkTabview(setting, width=700, height=500,fg_color='#242424')
        setting_tab.grid(row=0, column=0, padx=0, pady=20, sticky="nsew")

        def update_username_textbox(content="No login yet!"):
            googleaccountname_text.configure(state='normal')
            googleaccountname_text.delete(0.0,tk.END)
            googleaccountname_text.insert(tk.END,content)
            googleaccountname_text.configure(state='disabled')

        def update_cookie_path_textbox():
            cookiepath_text.configure(state='normal')
            cookiepath_text.delete(0.0,tk.END)
            cookiepath_text.insert(tk.END,(cookies_dir if cookies_dir else 'Not selected'))
            cookiepath_text.configure(state='disabled')

        def update_client_secrets_path_textbox():        
            client_secrets_text.configure(state='normal')
            client_secrets_text.delete(0.0,tk.END)
            client_secrets_text.insert(tk.END,(client_secret_path if client_secret_path else 'Not selected'))
            client_secrets_text.configure(state='disabled')
            
        @check_internet
        def google_login_setting(mode):
            global credentials
            log_handle(content='google login setting called')
            if os.path.exists(os.path.join(current_dir,'user_data','sub.json')):
                
                if messagebox.askyesno(f'JaTubePlayer {ver}','The system has detected an existing subscription, do you want to delete it?\n(If you choose No, the subscription will be kept but it may cause some problems if the subscription is not related to the new login account)'):
                    try:os.remove(os.path.join(current_dir,'user_data','sub.json'))
                    except:pass
            if os.path.exists(os.path.join(current_dir,'user_data','liked.json')):
                if messagebox.askyesno(f'JaTubePlayer {ver}','The system has detected an existing liked videos list, do you want to delete it?\n(If you choose No, the liked videos list will be kept but it may cause some problems if the list is not related to the new login account)'):
                    try:os.remove(os.path.join(current_dir,'user_data','liked.json'))
                    except:pass
            credentials = google_control.get_google_cred_and_save()

            log_handle(content='New login attempt finished')
            
            get_user_name()

        def google_logout_setting():
            global credentials,youtube
            google_control.google_logout_clear_data()
            credentials = None
            youtube = None
            update_username_textbox()
            get_user_name()
            
            
        @check_internet
        def get_resolution_setting():
            if playing_vid_mode == 0 or playing_vid_mode == 4:
                if playing_vid_mode == 4 and not vid_url[selected_song_number].startswith(('https://','http://')):
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','The selected video is a local file, downloading is not supported'))
                    return
                try:
                    if selected_song_number != None:
                        ui_queue.put(lambda: resolution_title.configure(text='⏳ Loading resolutions...'))
                        ui_queue.put(lambda: get_resoltion_btn.configure(state='disabled'))
                        res = get_resoltion(vid_url[selected_song_number])
                        ui_queue.put(lambda r=res: resoltion_combox.configure(values=r))
                        ui_queue.put(lambda: resoltion_combox._open_dropdown_menu())
                        ui_queue.put(lambda: resolution_title.configure(text='Video Resolution'))
                    else:
                        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','selected a video first'))

                except Exception as e:log_handle(content=str(e))
                finally:
                    ui_queue.put(lambda: get_resoltion_btn.configure(state='normal'))
            elif playing_vid_mode == 3:
                try:
                    ui_queue.put(lambda: resolution_title.configure(text='⏳ Loading resolutions...'))
                    ui_queue.put(lambda: get_resoltion_btn.configure(state='disabled'))
                    res = get_resoltion(playing_vid_info_dict.get('original_url'))
                    ui_queue.put(lambda r=res: resoltion_combox.configure(values=r))
                    ui_queue.put(lambda: resoltion_combox._open_dropdown_menu())
                    ui_queue.put(lambda: resolution_title.configure(text='Video Resolution'))

                except Exception as e :log_handle(content=str(e))
                finally:
                    ui_queue.put(lambda: get_resoltion_btn.configure(state='normal'))
                
            else:
                   
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','You cant download local file !'))
                
        @check_internet_silent
        def get_user_name():
            userinfo = google_control.get_userinfo(credentials)
            log_handle(content=f'setting frame got userinfo: {userinfo}')
            if userinfo and userinfo.get('name',None):ui_queue.put(lambda n=userinfo.get('name'): update_username_textbox(f"Logged in as  :  {n}"))
            else:ui_queue.put(lambda: update_username_textbox())
            ui_queue.put(lambda: google_status_update())

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
                _vid_url = list(vid_url)
                _playlisttitles = list(playlisttitles)
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
                            _,info_dict = get_info(yt_dlp=yt_dlp,
                                            maxres=1080,
                                            target_url=_vid_url[_selected_idx],
                                            deno_path=deno_exe,
                                            log_handler=ytdlp_log_handle,
                                            cookie_path=cookies_dir)
                            if not info_dict:
                                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Failed to fetch video info, the video may be unavailable or private\nPlease check the log for more details'))
                                is_downloading.set(False)
                                return
                            if info_dict.get('is_live'):
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
                        if resoltion_combox.get() != '' and resoltion_combox.get().isdigit() and int(resoltion_combox.get()) >=144:pass
                        else:
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please select a valid resolution first'))
                            is_downloading.set(False)
                            return
                        if _dict['is_live'] == 'is_live':
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Live video downloading is not supported'))
                            is_downloading.set(False)
                            return
                        else:
                            url = _dict.get('original_url')
                            title = _dict.get('title','unknown_title')
                    if download_path.get() != '[player]/user_data/downloaded_file':
                        if not os.path.exists(download_path.get()):
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','The specified download path does not exist'))
                            is_downloading.set(False)
                            return
                    print(f'title = {title},{playlisttitles}')
                    ui_queue.put(lambda: downloadselectedsong.configure(state = "disabled"))
                    download_to_local(
                        res=resoltion_combox.get(),
                        mode=formats.get(),
                        cookies_dir=cookies_dir,
                        yt_dlp=yt_dlp,
                        target_vid_url=url,
                        title=title,
                        download_path=download_path.get(),
                        current_dir=current_dir,
                        icondir=icondir,
                        ver=ver,
                        root=root,   
                        ffmpeg=ffmpeg,
                        ytdlp_log_handle=ytdlp_log_handle,
                        is_downloading = is_downloading,
                        deno_path=deno_exe,
                        ctk_messagebox=messagebox
                        )
                    log_handle(content=f"downloaded {title  }")
                    
                    time.sleep(2)
                    ui_queue.put(lambda: downloadselectedsong.configure(state = "normal"))
                    ui_queue.put(lambda: downloadhooktext.set(''))
                else:
                    
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','You cant download local file !'))
                    

            
        @check_internet
        def update_sub_list_local():
            if messagebox.askyesno(f'JaTubePlayer {ver}','This might take a while \nProcceed?'):  
                if client_secret_path != 'None':
                    if youtubeAPI:
                        ui_queue.put(lambda: updatesub_btn.configure(text='⏳ loading...'))
                        ui_queue.put(lambda: updatesub_btn.configure(state='disabled'))
                        result = update_sub_list(youtubeAPI,credentials,client_secret_path,current_dir)
                        ui_queue.put(lambda: updatesub_btn.configure(text='update Subscribe channel list'))
                        ui_queue.put(lambda: updatesub_btn.configure(state='normal'))
                        if  result  == True:
                            ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','succeed'))
                            
                        else:
                            
                            ui_queue.put(lambda r=result: messagebox.showinfo(f'JaTubePlayer {ver}',r))
                            
                    else:ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting'))         
                else:ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting'))

        @check_internet
        def update_like_list_local():
            if client_secret_path != 'None':
                if youtubeAPI:
                    ui_queue.put(lambda: updatelike_btn.configure(text='⏳ loading...'))
                    ui_queue.put(lambda: updatelike_btn.configure(state='disabled'))
                    result = update_like_list(youtubeAPI,credentials,client_secret_path,current_dir)
                    ui_queue.put(lambda: updatelike_btn.configure(text='update Liked video list'))
                    ui_queue.put(lambda: updatelike_btn.configure(state='normal'))
                    if  result  == True:
                        ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','succeed'))
                        

                    else:
                        ui_queue.put(lambda r=result: messagebox.showinfo(f'JaTubePlayer {ver}',r))
                        
                else:ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting'))         
            else:ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting'))

        @check_internet
        def updateplaylists():
            updateuserplaylists_btn.configure(text='⏳ loading...')
            get_user_playlists(0)
            updateuserplaylists_btn.configure(text='update Playlist ')


        
        def enter_youtube_api():
            
            global youtubeAPI,credentials
            youtubeAPI = setting_api_entry.get()
            Ferner_encrptor_.encrypt_api(youtubeAPI)
            apilabel.configure(text=f'{youtubeAPI[:10]}{"*" * (len(youtubeAPI)-10)}')
            messagebox.showinfo(f'JaTubePlayer {ver}',f'Your youtube API is now {youtubeAPI}\n ')
            messagebox.showinfo(f'JaTubePlayer {ver}','API changed, you need to relogin your google account \nGo setting -> google login!')
            google_control.youtubeAPI = youtubeAPI
            



        def read_client_secret_setting():
            global client_secret_path,credentials
            
            filetype = [('jsonfile','*.json')]
            client_secret_path = filedialog.askopenfilename(filetypes=filetype)
            if client_secret_path:
                messagebox.showinfo(f'JaTubePlayer {ver}','client secert changed, you need to relogin your google account\n and change your API!')
                messagebox.showinfo(f'JaTubePlayer {ver}',f'your client secret is now at  {client_secret_path}')
                CONFIG['client_secret_path'] = client_secret_path
                save_config()   
                update_client_secrets_path_textbox()
                google_control.client_secret_path = client_secret_path  
            else:messagebox.showwarning(f'JaTubePlayer {ver}','Cancelled!')
            

        def delete_client_secrets():
            global client_secret_path
            
            try:
                if messagebox.askyesno(f'JaTubePlayer {ver}',f'Sure to remove cookie from the player?'):
                    if client_secret_path:
                        messagebox.showinfo(f'JaTubePlayer {ver}','succeed!')
                        client_secret_path = None
                        google_control.client_secret_path = None
                        CONFIG['client_secret_path'] = ''
                        save_config()
                    else:messagebox.showwarning(f'JaTubePlayer {ver}','client secrets not found!')
            except :messagebox.showwarning(f'JaTubePlayer {ver}','client secrets not found!')
            update_client_secrets_path_textbox()

        def read_cookie_setting():
            global cookies_dir
            filetype = [('textfile','*.txt')]
            cookies_dir = filedialog.askopenfilename(filetypes=filetype)
            if cookies_dir:
                messagebox.showinfo(f'JaTubePlayer {ver}',f'your cookie is now at  {cookies_dir}\n Changes will apply to the next video playback.')
                update_cookie_path_textbox()
                CONFIG['cookie_path'] = cookies_dir
                save_config()   
            else:messagebox.showwarning(f'JaTubePlayer {ver}','Cancelled!')
            

        def delete_cookie():
            global cookies_dir
            
            try:
                if  cookies_dir:
                    if messagebox.askyesno(f'JaTubePlayer {ver}',f'Sure to remove cookie from the player?'):
                        messagebox.showinfo(f'JaTubePlayer {ver}','succeed!')
                        CONFIG['cookie_path'] = ''
                        cookies_dir = None
                        save_config()

                else:messagebox.showwarning(f'JaTubePlayer {ver}','cookie not found!')
            except :messagebox.showwarning(f'JaTubePlayer {ver}','cookie not found!')
            
            update_cookie_path_textbox()



        def deletesyskey():
            global credentials,youtubeAPI,youtube
            if messagebox.askokcancel(f'JaTubePlayer {ver}','Sure to delete sys key? \n You will be logged out from google account and stored data will be removed\nNote this will delete both \n1.Creditial and  key for creditial\n 2. stored API and key for API\n Both key will be randomly generated again when the program restarts\nIf you try to login again, they will be generated'):
                try:
                    google_control.google_logout_clear_data()
                    credentials = None
                    youtubeAPI = None
                    youtube = None
                    Ferner_encrptor_.clear_sys_key()
                    google_control.youtubeAPI = None
                    update_username_textbox()
                    apilabel.configure(text='None')
                    messagebox.showinfo(f'JaTubePlayer {ver}','Succeed!')
                except FileNotFoundError:messagebox.showinfo(f'JaTubePlayer {ver}','Key already gone!')
                except Exception as e:messagebox.showerror(f'JaTubePlayer {ver}',e)
            

        def deleteapi():
            global youtubeAPI
            if messagebox.askokcancel(f'JaTubePlayer {ver}','Sure to delete stored API key?'):
                try: 
                    apilabel.configure(text='None')
                    youtubeAPI = None
                    os.remove(os.path.join(current_dir,'user_data','api.enc'))
                    messagebox.showinfo(f'JaTubePlayer {ver}','API deleted!')
                except FileNotFoundError:messagebox.showinfo(f'JaTubePlayer {ver}','API already gone!')
                except Exception as e:messagebox.showerror(f'JaTubePlayer {ver}',e)
                

        def save_his_and_rec_option():
            if save_history.get() :
                if init_toggle_quickstartup.get():init_rec_at_startbtn.configure(state='normal')
                else:init_rec_at_startbtn.configure(state='disabled')
                CONFIG['record_history'] = True
            else:
                log_handle(content=str(init_quickstartup_mode.get()))
                if init_quickstartup_mode.get() =='recommendation':
                    init_quickstartup_mode.set('None')
                    CONFIG['quickstartup_init']['mode'] = 0
                    messagebox.showwarning(f'JaTubePlayer {ver}','You deselected the record history function\nSo the quick startup init is deselected as well\nPlease select a quick startup init function again',)
                init_rec_at_startbtn.configure(state='disabled')
                CONFIG['record_history'] = False
            save_config()
            
        def reset_history_setting(event=None):
            
            if messagebox.askyesno(f'JaTubePlayer {ver}','This will reset the history data and previous will be removed\nProcceed'):
                result,e = init_history(current_dir)
                if result:messagebox.showinfo(f'JaTubePlayer {ver}','Succeed')
                else:messagebox.showerror(f'JaTubePlayer {ver}',f'opps we got some error \n{e}')

        def remove_selected_from_playlist_setting():
            global selected_song_number
            if selected_song_number is None:
                messagebox.showerror(f'JaTubePlayer {ver}', 'No item selected in the playlist!')
                return
            try:
                item_id = playlisttreebox.get_children()[selected_song_number]
                playlisttreebox.delete(item_id)
                vid_url.pop(selected_song_number)
                playlisttitles.pop(selected_song_number)
                playlist_thumbnails.pop(selected_song_number)
                playlist_channel.pop(selected_song_number)
                selected_song_number = None
            except Exception as e:
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
                init_search_entry.configure(state='normal')
                init_playlist_btn.configure(state='normal')
                init_playlist_combobox.configure(state='readonly')
                init_get_playlist_btn.configure(state='normal')
                init_search_set_btn.configure(state='normal')
                init_playlist_set_btn.configure(state='normal')
                init_local_folder_btn.configure(state='normal')
                init_select_local_folder_btn.configure(state='normal')
                if save_history.get():
                    init_rec_at_startbtn.configure(state='normal')
                else: init_rec_at_startbtn.configure(state='disabled')
                
            else:         
                CONFIG["quickstartup_init"]['mode']=0
                save_config()
                init_quickstartup_mode.set(None)
                init_playlist_combobox.set('')
                init_search_entry.delete(0,tk.END)
                init_search_btn.configure(state='disabled')
                init_search_entry.configure(state='disabled')
                init_playlist_btn.configure(state='disabled')
                init_playlist_combobox.configure(state='disabled')
                init_get_playlist_btn.configure(state='disabled')
                init_search_set_btn.configure(state='disabled')
                init_playlist_set_btn.configure(state='disabled')
                init_rec_at_startbtn.configure(state='disabled')
                init_local_folder_btn.configure(state='disabled')
                init_select_local_folder_btn.configure(state='disabled')
                init_select_local_folder_btn.configure(state='disabled')
               
        
        def init_search_select(event=None):
            init_playlist_set_btn.configure(state='disabled')
            init_get_playlist_btn.configure(state='disabled')
            init_playlist_combobox.configure(state='disabled')
            init_select_local_folder_btn.configure(state='disabled')
            init_search_entry.configure(state='normal')
            init_search_set_btn.configure(state='normal')       

        def init_playlist_select(event=None):
            if youtubeAPI:
                if client_secret_path:
                    init_playlist_set_btn.configure(state='normal')
                    init_get_playlist_btn.configure(state='normal')
                    init_playlist_combobox.configure(state='readonly')
                    init_search_entry.configure(state='disabled')
                    init_search_set_btn.configure(state='disabled')
                    init_select_local_folder_btn.configure(state='disabled')
                else:messagebox.showerror(f'JatubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting')
            else:messagebox.showerror(f'JatubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting')

        def setting_init_recommendation_select():
            if save_history.get():
                page_num_label.configure(text='')
                init_quickstartup_mode.set('recommendation')
                messagebox.showinfo(f'JatubePlayer {ver}',f'The quick startup init is now\nRecommendation')
                CONFIG['quickstartup_init']['mode'] = 4
                save_config()   
                init_playlist_set_btn.configure(state='disabled')
                init_get_playlist_btn.configure(state='disabled')
                init_playlist_combobox.configure(state='disabled')
                init_search_entry.configure(state='disabled')
                init_search_set_btn.configure(state='disabled')
                init_select_local_folder_btn.configure(state='disabled')

        def init_search_set():
            if not init_search_entry.get():
                messagebox.showerror(f'JatubePlayer {ver}','Please enter the search query first!')
                init_quickstartup_mode.set(None)
            else:
                CONFIG['quickstartup_init']['mode'] = 1
                CONFIG['quickstartup_init']['entrymode_entry_content'] = init_search_entry.get()
                save_config()
                messagebox.showinfo(f'JaTubePlayer {ver}',f'The quick startup init is now\nSearch : {init_search_entry.get()}')

        @check_internet
        def init_playlist_get():
            if youtubeAPI:
                if client_secret_path:get_user_playlists(1)
                else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting')
            else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting')
            

        def init_playlist_set():    
            global init_playlists_id
            try:
                init_playlists_id = init_playlists_id  
                if not init_playlist_combobox.get():
                    messagebox.showerror(f'JaTubePlayer {ver}','Please select a playlist first!')
                    init_quickstartup_mode.set(None)
                else:
                        CONFIG['quickstartup_init']['mode'] = 2
                        CONFIG['quickstartup_init']['playlistmode_playlist_ID'] = init_playlists_id[init_playlist_combobox.current()]
                        CONFIG['quickstartup_init']['playlistmode_playlist_Name'] = init_playlist_combobox.get()
                        save_config()
                        messagebox.showinfo(f'JaTubePlayer {ver}',f'The quick startup init is now\nPlaylist : {init_playlist_combobox.get()}')
            except NameError:
                if not init_playlist_combobox.get():messagebox.showerror(f'JaTubePlayer {ver}','Please select the playlist again\n-> click get init playlist first!')
                else:messagebox.showerror(f'JaTubePlayer {ver}','Please select the playlist first')
        
        def init_local_playlist(event=None):
            init_playlist_set_btn.configure(state='disabled')
            init_get_playlist_btn.configure(state='disabled')
            init_playlist_combobox.configure(state='disabled')
            init_search_entry.configure(state='disabled')
            init_search_set_btn.configure(state='disabled')
            init_select_local_folder_btn.configure(state='normal')
            
        
        def init_select_local_folder():
            path = filedialog.askdirectory()
            if path:
                    CONFIG['quickstartup_init']['mode'] = 3
                    CONFIG['quickstartup_init']['localfoldermode_folder_Path'] = path
                    save_config()
                    messagebox.showinfo(f'JatubePlayer {ver}',f'The quick startup init is now\nLocal folder : {path}')
            else: messagebox.showinfo(f'JaTubePlayer {ver}','cancelled!')


        def setting_auto_sub_refresh():
            CONFIG['auto_sub_refresh'] = auto_sub_refresh.get()
            save_config()
          
        def setting_auto_like_refresh():
            CONFIG['auto_like_refresh'] = auto_like_refresh.get()
            save_config()

        def switch_flask_server():
            global listen_chromeextension_thread,chrome_extension_flask_thread
            if setting_run_chrome_extension_server.get():
                chrome_extension_server_checkbtn.configure(state='disabled')
                _switch_local_server(0)

                root.after(2000,lambda:chrome_extension_server_checkbtn.configure(state='normal'))
            else:
                chrome_extension_server_checkbtn.configure(state='disabled')
                
                if _switch_local_server(1) :
                    messagebox.showerror(f'JaTubePlayer {ver}','Failed to stop the chrome extension server')
                
                root.after(2000,lambda:chrome_extension_server_checkbtn.configure(state='normal'))
            

        def switch_blur_window():
            global blur_window
            CONFIG['blur'] = blur_window.get()
            save_config()
            try:
                if blur_window.get():
                    blur(hwnd, Dark=True, Acrylic=True) 
                    blur(win32gui.FindWindow(None,setting.title()), Dark=True, Acrylic=True)
                    try:blur(win32gui.FindWindow(None,log_.title()), Dark=True, Acrylic=True)
                    except:pass
                    try:blur(win32gui.FindWindow(None,info.title()), Dark=True, Acrylic=True)
                    except:pass
                else:
                    blur(hwnd,disable=True)
                    blur(win32gui.FindWindow(None,setting.title()), disable=True)
                    try:blur(win32gui.FindWindow(None,log_.title()), disable=True)
                    except:pass
                    try:blur(win32gui.FindWindow(None,info.title()), disable=True)
                    except:pass
            except Exception as e:
                log_handle(content=str(e))    
                
        def max_resolution_select(event=None):
            maxresolution.set(int(maxresolutioncombobox.get()))
            CONFIG["max_resolution"] = maxresolution.get()
            save_config()

        @check_internet
        def update_ytdlp():
            global yt_dlp,utils,ytdlpver
            ui_queue.put(lambda: auto_update_ytdlp_btn.configure(state='disabled'))
            ui_queue.put(lambda: auto_update_ytdlp_btn.configure(text='⏳ updating...'))
            result = download_and_extract_dlp(_internal_dir,root,icondir,log_handle)
            if not result:
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','ytdlp Update failed!, please check log file'))
            else:
                yt_dlp, utils, ytdlpver = reload_yt_dlp(_internal_dir)
                star_vid_handle.yt_dlp = yt_dlp #update yt-dlp reference in star vid handle
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

        def switch_drag_and_drop():
            CONFIG['enable_drag_and_drop'] = enable_drag_and_drop.get()
            ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='Change saved!\nRestart the player will apply the change', duration='short', icon=icondir)
            save_config()

        def switch_show_cache():
            CONFIG['show_cache'] = show_cache.get()
            save_config()

        def switch_hover_fullscreen():
            CONFIG['hover_fullscreen'] = hover_fullscreen.get()
            save_config()

        def _save_cache_settings():
            CONFIG['cache']['cache_secs'] = int(cache_secs.get())
            CONFIG['cache']['demuxer_max_bytes'] = int(demuxer_max_bytes.get())
            CONFIG['cache']['demuxer_max_back_bytes'] = int(demuxer_max_back_bytes.get())
            CONFIG['cache']['cache_pause_wait'] = int(cache_pause_wait.get())
            CONFIG['cache']['audio_wait_open'] = int(audio_wait_open.get())
            save_config()

        def _cache_secs_slider_change(value):
            cache_secs.set(int(float(value)))
            cache_secs_value_label.configure(text=f'{cache_secs.get()}s')

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
            log_handle(f'selected subtitle idx{subtitle_selection_idx.get()}')
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
                    else:raise Exception("No title found")
                except Exception as e:
                    log_handle(content=str(e))
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
                log_handle(content=str(e))
        
        def apply_player_speed_setting(event=None):
            try:
                player.speed = player_speed.get()
            except Exception as e:
                log_handle(content=str(e))

        def select_download_path():
            path =filedialog.askdirectory()
            if path:
                CONFIG['download_path'] = path
                download_path.set(path)
                save_config()
                ui_queue.put(lambda:download_path_textbox.configure(state='normal'))
                ui_queue.put(lambda:download_path_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda:download_path_textbox.insert(tk.END,download_path.get()))
                ui_queue.put(lambda:download_path_textbox.configure(state='disabled'))
                
                messagebox.showinfo(f'JaTubePlayer {ver}',f'Download path set to {path}')
            else:messagebox.showinfo(f'JaTubePlayer {ver}','Cancelled!')
            setting.focus_force()

        def set_default_download_path():
            if messagebox.askyesno(f'JaTubePlayer {ver}','This will reset the download path to default\nProcceed?'):
                CONFIG['download_path'] = "[player]/user_data/downloaded_file" 
                download_path.set("[player]/user_data/downloaded_file")
                save_config()
                ui_queue.put(lambda:download_path_textbox.configure(state='normal'))
                ui_queue.put(lambda:download_path_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda:download_path_textbox.insert(tk.END,download_path.get()))
                ui_queue.put(lambda:download_path_textbox.configure(state='disabled'))
                
                messagebox.showinfo(f'JaTubePlayer {ver}',f'Download path reset to default\n{CONFIG["download_path"]}')
            setting.focus_force()

        def SetFullscreenmode(event=None):
            CONFIG['fullscreenmode'] = fullscreenmode.get()
            save_config()

        player_tab = setting_tab.add("Advanced Player setting")
        personal_playlist_tab = setting_tab.add("Personal playlist")
        download_tab = setting_tab.add("Download")
        quick_init_tab = setting_tab.add("Quick Init")
        Authentication_tab = setting_tab.add("Account & Authentication")
        version_info_tab = setting_tab.add("Version Info")
        hotkey_tab = setting_tab.add("Hotkeys")

        
        '''
        Columns with weight 0 do not expand when the window grows. Columns with weight > 0 get a share of the extra space.
        The actual extra width each weighted
        '''
        personal_playlist_tab.grid_columnconfigure(0, weight=1)
        personal_playlist_tab.grid_columnconfigure(1, weight=1)

        player_tab.grid_columnconfigure(0, weight=1)
        player_tab.grid_columnconfigure(1, weight=1)
    
        
        download_tab.grid_columnconfigure(0, weight=1)
        download_tab.grid_columnconfigure(1, weight=1)

        Authentication_tab.grid_columnconfigure(0, weight=1)
        
        version_info_tab.grid_columnconfigure(0, weight=1)
        version_info_tab.grid_columnconfigure(1, weight=1)

        quick_init_tab.grid_columnconfigure(0, weight=1)  # left spacer
        quick_init_tab.grid_columnconfigure(1, weight=0)  # content column
        quick_init_tab.grid_columnconfigure(2, weight=1)  # right spacer


        # ══════════ Personal Playlist — Card-style sections ══════════
        youtube_data_frame = ctk.CTkFrame(personal_playlist_tab, fg_color='#2B2B2B', corner_radius=8)
        youtube_data_frame.grid_columnconfigure(0, weight=1)
        youtube_data_frame.grid_columnconfigure(1, weight=1)
        
        history_frame = ctk.CTkFrame(personal_playlist_tab, fg_color='#2B2B2B', corner_radius=8)
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_columnconfigure(1, weight=1)
        
        # YouTube Data Section
        youtube_title = ctk.CTkLabel(youtube_data_frame, text='  \u25b8 YouTube Data', font=('Arial', 14, 'bold'), text_color='#FF6B8A', anchor='w')
        updatelike_btn = ctk.CTkButton(youtube_data_frame, text='Update Liked Videos', width=160, command=lambda:threading.Thread(daemon=True,target=update_like_list_local).start(),
                                        text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        auto_like_refresh_checkbtn = ctk.CTkCheckBox(youtube_data_frame, text='Auto-update liked videos', variable=auto_like_refresh, command=setting_auto_like_refresh,
                                                      fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12))
        
        updatesub_btn = ctk.CTkButton(youtube_data_frame, text='Update Subscriptions', width=160, command=lambda:threading.Thread(daemon=True,target=update_sub_list_local).start(),
                                       text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        auto_sub_refresh_checkbtn = ctk.CTkCheckBox(youtube_data_frame, text='Auto-update subscriptions', variable=auto_sub_refresh, command=setting_auto_sub_refresh,
                                                     fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12))
        
        updateuserplaylists_btn = ctk.CTkButton(youtube_data_frame, text='Update Playlists', width=160, command=updateplaylists,
                                                 text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        
        # History Management Section
        history_title = ctk.CTkLabel(history_frame, text='  \u25b8 History', font=('Arial', 14, 'bold'), text_color='#7EDAE0', anchor='w')
        record_history_btn = ctk.CTkCheckBox(history_frame, text='Record playback history', variable=save_history, command=save_his_and_rec_option,
                                              fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12))
        reset_history_btn = ctk.CTkButton(history_frame, text='Reset History', width=160, command=reset_history_setting,
                                           text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')

        # Playlist Item Removal Section
        playlist_remove_frame = ctk.CTkFrame(personal_playlist_tab, fg_color='#2B2B2B', corner_radius=8)
        playlist_remove_frame.grid_columnconfigure(0, weight=1)
        playlist_remove_frame.grid_columnconfigure(1, weight=1)

        playlist_remove_title = ctk.CTkLabel(playlist_remove_frame, text='  \u25b8 Remove from Playlist', font=('Arial', 14, 'bold'), text_color='#E08080', anchor='w')
        playlist_remove_btn = ctk.CTkButton(playlist_remove_frame, text='Remove Selected', width=160,
                                             command=remove_selected_from_playlist_setting,
                                             text_color='white', font=('Arial', 13, 'bold'), fg_color='#B30C00', hover_color='#A52A2A')
        playlist_remove_note = ctk.CTkLabel(playlist_remove_frame,
                                             text='Note: Removing an item only clears it from the current playlist view\nand does not affect the original source (YouTube, local folder, etc.).',
                                             font=('Arial', 13), text_color="#9A9999", anchor='w', justify='left')

        auth_scrollable_frame = ctk.CTkScrollableFrame(Authentication_tab, width=680, height=400, fg_color='#242424')
        auth_scrollable_frame.grid(row=0, column=0)

        # ── Google Account Card ──
        google_frame = ctk.CTkFrame(auth_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        google_frame.grid_columnconfigure(0, weight=1)
        google_frame.grid_columnconfigure(1, weight=1)
        google_frame.grid_columnconfigure(2, weight=1)
        google_frame.grid(row=0, column=0, padx=8, pady=(8, 4), sticky="ew")

        google_title = ctk.CTkLabel(google_frame, text='  \u25b8 Google Account  \u00b7  API & Client Secret required', font=('Arial', 14, 'bold'), text_color='#FFB347', anchor='w')
        googlelogin_btn = ctk.CTkButton(google_frame, text='Login Google', width=200,
                                         command=lambda:threading.Thread(daemon=True,target=lambda:google_login_setting(0)).start(),
                                         text_color='white', font=('Arial', 13, 'bold'), fg_color='#2E7D32', hover_color='#388E3C')
        googlelogout_btn = ctk.CTkButton(google_frame, text='Logout Google', width=200, command=google_logout_setting,
                                          text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        deletesyskey_btn = ctk.CTkButton(google_frame, text='Delete System Key', width=200, command=deletesyskey,
                                          text_color='white', font=('Arial', 13, 'bold'), fg_color='#B30C00', hover_color='#A52A2A')
        googleaccountname_text = ctk.CTkTextbox(google_frame, font=('Arial', 13), state='disabled', fg_color='#1a1a1a', text_color='#C8C8C8', height=1, corner_radius=6)

        google_title.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        googleaccountname_text.grid(row=1, column=0, padx=12, pady=6, columnspan=3, sticky="ew")
        googlelogin_btn.grid(row=2, column=0, padx=(24, 4), pady=(6, 12))
        googlelogout_btn.grid(row=2, column=1, padx=4, pady=(6, 12))
        deletesyskey_btn.grid(row=2, column=2, padx=(4, 24), pady=(6, 12))
        
        # ── API Card ──
        api_frame = ctk.CTkFrame(auth_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        api_frame.grid_columnconfigure(0, weight=0)
        api_frame.grid_columnconfigure(1, weight=1)
        api_frame.grid_columnconfigure(2, weight=0)
        
        api_title = ctk.CTkLabel(api_frame, text='  \u25b8 API Key', font=('Arial', 14, 'bold'), text_color='#7EB8E0', anchor='w')
        deleteapi_btn = ctk.CTkButton(api_frame, text='Delete Stored API', width=160, command=deleteapi,
                                       text_color='white', font=('Arial', 13, 'bold'), fg_color='#B30C00', hover_color='#A52A2A')
        setting_api_label = ctk.CTkLabel(api_frame, font=('Arial', 12), text='YouTube API:', text_color='#B0B0B0')
        setting_api_entry = ctk.CTkEntry(api_frame, font=('Arial', 13), width=160, text_color='#C8C8C8', placeholder_text="Enter API here",
                                          fg_color='#1a1a1a', border_color='#444444')
        set_api_btn = ctk.CTkButton(api_frame, text='Set API', width=120, command=enter_youtube_api,
                                     text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        apilabel = ctk.CTkLabel(api_frame, font=('Arial', 12, 'bold'), text='None', text_color='#7EB8E0')

        api_title.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        setting_api_label.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="e")
        setting_api_entry.grid(row=1, column=1, padx=8, pady=5, sticky="ew")
        apilabel.grid(row=1, column=2, padx=(8, 24), pady=5, sticky="w")
        set_api_btn.grid(row=2, column=1, padx=8, pady=(4, 12), sticky="w")
        deleteapi_btn.grid(row=2, column=2, padx=(8, 24), pady=(4, 12), sticky="e")
        api_frame.grid(row=1, column=0, padx=8, pady=4, sticky="ew")

        # ── Cookie Card ──
        cookie_frame = ctk.CTkFrame(auth_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        cookie_frame.grid_columnconfigure(0, weight=0)
        cookie_frame.grid_columnconfigure(1, weight=1)
        cookie_frame.grid_columnconfigure(2, weight=0)
        
        cookie_title = ctk.CTkLabel(cookie_frame, text='  \u25b8 Cookie', font=('Arial', 14, 'bold'), text_color='#7EE0A8', anchor='w')
        setting_cookie_label = ctk.CTkLabel(cookie_frame, font=('Arial', 12), text='Cookie:', text_color='#B0B0B0')
        insert_cookie_btn = ctk.CTkButton(cookie_frame, text='Select Cookie', width=160, command=read_cookie_setting,
                                           text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        deletecookie_btn = ctk.CTkButton(cookie_frame, text='Remove Cookie', width=160, command=delete_cookie,
                                          text_color='white', font=('Arial', 13, 'bold'), fg_color='#B30C00', hover_color='#A52A2A')
        cookiepath_text = ctk.CTkTextbox(cookie_frame, font=('Arial', 12), height=25, text_color='#C8C8C8', fg_color='#1a1a1a', corner_radius=6)
        cookiepath_text.configure(state='disabled')

        cookie_title.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        setting_cookie_label.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="e")
        cookiepath_text.grid(row=1, column=1, columnspan=2, padx=(8, 24), pady=5, sticky="ew")
        insert_cookie_btn.grid(row=2, column=1, padx=8, pady=(4, 12), sticky="ew")
        deletecookie_btn.grid(row=2, column=2, padx=(8, 24), pady=(4, 12), sticky="w")
        cookie_frame.grid(row=2, column=0, padx=8, pady=4, sticky="ew")

        # ── Client Secrets Card ──
        client_secrets_frame = ctk.CTkFrame(auth_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        client_secrets_frame.grid_columnconfigure(0, weight=0)
        client_secrets_frame.grid_columnconfigure(1, weight=1)
        client_secrets_frame.grid_columnconfigure(2, weight=0)
    
        client_secrets_title = ctk.CTkLabel(client_secrets_frame, text='  \u25b8 Client Secrets', font=('Arial', 14, 'bold'), text_color='#C0A0E0', anchor='w')
        setting_client_secret_label = ctk.CTkLabel(client_secrets_frame, font=('Arial', 12), text='Client Secrets:', text_color='#B0B0B0')
        insert_client_secrets_btn = ctk.CTkButton(client_secrets_frame, text='Select Client Secret', width=160, command=read_client_secret_setting,
                                                    text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        deleteclient_secrets_btn = ctk.CTkButton(client_secrets_frame, text='Remove Client Secret', width=160, command=delete_client_secrets,
                                                   text_color='white', font=('Arial', 13, 'bold'), fg_color='#B30C00', hover_color='#A52A2A')
        client_secrets_text = ctk.CTkTextbox(client_secrets_frame, font=('Arial', 12), height=1, text_color='#C8C8C8', fg_color='#1a1a1a',
                                              wrap="none", activate_scrollbars=False, corner_radius=6)
        client_secrets_text.configure(state='disabled')

        client_secrets_title.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        setting_client_secret_label.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="e")
        client_secrets_text.grid(row=1, column=1, columnspan=2, padx=(8, 24), pady=5, sticky="ew")
        insert_client_secrets_btn.grid(row=2, column=1, padx=8, pady=(4, 12), sticky="ew")
        deleteclient_secrets_btn.grid(row=2, column=2, padx=(8, 24), pady=(4, 12), sticky="w")
        client_secrets_frame.grid(row=3, column=0, padx=8, pady=(4, 8), sticky="ew")


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
        info_title = ctk.CTkLabel(download_info_frame, text='  \u25b8 Selected Video', font=('Arial', 14, 'bold'), text_color='#E0A07E', anchor='w')
        download_seleted_title_text = ctk.CTkTextbox(download_info_frame, font=('Arial', 14), width=650, height=55, fg_color='#1a1a1a', text_color='#C8C8C8', corner_radius=6)
        download_seleted_title_text.configure(state='disabled')
        
        # Format Selection Section
        format_title = ctk.CTkLabel(format_frame, text='  \u25b8 Format', font=('Arial', 14, 'bold'), text_color='#D4A0E0', anchor='w')
        download_mp3 = ctk.CTkRadioButton(format_frame, text='Audio (MP3)', variable=formats, value=0, command=lambda:download_select_mode_setting(0),
                                           font=('Arial', 12), text_color='#C8C8C8')
        download_mp4 = ctk.CTkRadioButton(format_frame, text='Video (MP4)', variable=formats, value=1, command=lambda:download_select_mode_setting(1),
                                           font=('Arial', 12), text_color='#C8C8C8')
        
        # Resolution Section
        resolution_title = ctk.CTkLabel(resolution_frame, text='  \u25b8 Resolution', font=('Arial', 14, 'bold'), text_color='#80C8E0', anchor='w')
        resoltion_combox = ctk.CTkComboBox(resolution_frame, font=('Arial', 12), width=200, state='readonly', values=[],
                                            dropdown_fg_color='#333333', button_color='#444444')
        get_resoltion_btn = ctk.CTkButton(resolution_frame, text='Get Available', width=140,
                                           command=lambda:threading.Thread(daemon=True,target=get_resolution_setting).start(),
                                           text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        
        # ── Download Path Card ──
        download_path_frame = ctk.CTkFrame(download_tab, fg_color='#2B2B2B', corner_radius=8)
        download_path_frame.grid_columnconfigure(0, weight=0)
        download_path_frame.grid_columnconfigure(1, weight=1)
        download_path_frame.grid_columnconfigure(2, weight=0)

        download_path_title = ctk.CTkLabel(download_path_frame, text='  \u25b8 Download Path', font=('Arial', 14, 'bold'), text_color='#A8D8A8', anchor='w')
        download_path_label = ctk.CTkLabel(download_path_frame, font=('Arial', 12), text='Save to:', text_color='#B0B0B0')
        download_path_textbox = ctk.CTkTextbox(download_path_frame, font=('Arial', 12), height=28, text_color='#C8C8C8',
                                               fg_color='#1a1a1a', corner_radius=6, wrap='none', activate_scrollbars=False)
        download_path_textbox.configure(state='disabled')
        select_download_path_btn = ctk.CTkButton(download_path_frame, text='Select Path', width=130,
                                                  command=select_download_path,
                                                  text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        set_default_download_path_btn = ctk.CTkButton(download_path_frame, text='Set Default', width=130,
                                                       command=set_default_download_path,
                                                       text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')

        # Download Action
        downloadselectedsong = ctk.CTkButton(download_tab, text='Download Selected Video', width=400,
                                              command=lambda:threading.Thread(daemon=True,target=download_to_loacl_setting).start(),
                                              text_color='white', font=('Arial', 14, 'bold'), fg_color='#2E7D32', hover_color='#388E3C', corner_radius=8)
        downloadhooklabel = ctk.CTkLabel(download_tab, font=('Arial', 12), textvariable=downloadhooktext, text_color='#80C8E0')


        # Create scrollable frame for player settings
        player_scrollable_frame = ctk.CTkScrollableFrame(player_tab, width=680, height=400, fg_color='#242424')
        player_scrollable_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        player_scrollable_frame.grid_columnconfigure(0, weight=1)
        player_scrollable_frame.grid_columnconfigure(1, weight=1)

        # ══════════════════════════════════════════════════════
        # PLAYER SETTINGS — Card-style organized sections
        # ══════════════════════════════════════════════════════

        # ── General Playback Card ──
        general_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        general_frame.grid_columnconfigure(0, weight=0, minsize=180)
        general_frame.grid_columnconfigure(1, weight=1)

        general_header = ctk.CTkLabel(general_frame, text='  ▸ General', font=('Arial', 14, 'bold'), text_color='#7EB8E0', anchor='w')
        maxresolutionlabel = ctk.CTkLabel(general_frame, font=('Arial', 12), text='Max Resolution', text_color='#B0B0B0')
        maxresolutioncombobox = ctk.CTkComboBox(general_frame, font=('Arial', 12), width=130, state='readonly',
                                                 values=['480', '720', '1080', '1440', '2160', '4320'],
                                                 dropdown_fg_color='#333333', button_color='#444444')
        maxresolutioncombobox.set(str(maxresolution.get()))
        maxresolutioncombobox.configure(command=max_resolution_select)
        autoretry_btn = ctk.CTkCheckBox(general_frame, text='Auto retry on error', variable=autoretry,
                                         fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12))
        audio_only_checkbtn = ctk.CTkCheckBox(general_frame, text='Audio only mode', variable=audio_only,
                                               fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12), command=switch_audio_only)

        # ── Speed & Subtitle Card ──
        speed_subtitle_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        speed_subtitle_frame.grid_columnconfigure(0, weight=0, minsize=180)
        speed_subtitle_frame.grid_columnconfigure(1, weight=1)
        speed_subtitle_frame.grid_columnconfigure(2, weight=0, minsize=50)

        speed_subtitle_header = ctk.CTkLabel(speed_subtitle_frame, text='  ▸ Speed & Subtitle', font=('Arial', 14, 'bold'), text_color='#7EE0A8', anchor='w')
        playerspeed_title_label = ctk.CTkLabel(speed_subtitle_frame, font=('Arial', 12), text='Playback Speed', text_color='#B0B0B0')
        playerspeed_slider = ctk.CTkSlider(speed_subtitle_frame, variable=player_speed, from_=0.3, to=3.0, width=200,
                                            number_of_steps=27, command=set_player_speed_setting,
                                            progress_color='#4A9E6E', button_color='#7EE0A8', button_hover_color='#98F0C0')
        playerspeed_slider.bind('<ButtonRelease-1>', apply_player_speed_setting)
        playerspeed_speed_label = ctk.CTkLabel(speed_subtitle_frame, font=('Arial', 12, 'bold'), text='1.0x', text_color='#7EE0A8')
        subtitle_label = ctk.CTkLabel(speed_subtitle_frame, text='Subtitle', font=('Arial', 12), text_color='#B0B0B0')
        subtitlecombobox = ctk.CTkComboBox(speed_subtitle_frame, font=('Arial', 12), width=220, state='readonly',
                                            values=subtitle_namelist, command=subtitle_combobox_callback,
                                            dropdown_fg_color='#333333', button_color='#444444')

        # ── Cache & Buffer Card ──
        cache_buffer_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        cache_buffer_frame.grid_columnconfigure(0, weight=0, minsize=180)
        cache_buffer_frame.grid_columnconfigure(1, weight=1)
        cache_buffer_frame.grid_columnconfigure(2, weight=0, minsize=50)

        _slider_kw = dict(progress_color='#8E7A4A', button_color='#E0C48C', button_hover_color='#F0D8A0')
        cache_buffer_header = ctk.CTkLabel(cache_buffer_frame, text='  ▸ Cache & Buffer', font=('Arial', 14, 'bold'), text_color='#E0C48C', anchor='w')

        cache_secs_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12), text='Cache Duration', text_color='#B0B0B0')
        cache_secs_slider = ctk.CTkSlider(cache_buffer_frame, variable=cache_secs, from_=10, to=300, width=200,
                                           number_of_steps=290, command=_cache_secs_slider_change, **_slider_kw)
        cache_secs_slider.bind('<ButtonRelease-1>', _apply_cache_slider_settings)
        cache_secs_value_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12, 'bold'), text=f'{cache_secs.get()}s', text_color='#E0C48C')

        demuxer_max_bytes_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12), text='Max Buffer Size', text_color='#B0B0B0')
        demuxer_max_bytes_slider = ctk.CTkSlider(cache_buffer_frame, variable=demuxer_max_bytes, from_=16, to=2048, width=200,
                                                  number_of_steps=2032, command=_demuxer_max_bytes_slider_change, **_slider_kw)
        demuxer_max_bytes_slider.bind('<ButtonRelease-1>', _apply_cache_slider_settings)
        demuxer_max_bytes_value_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12, 'bold'), text=f'{demuxer_max_bytes.get()}M', text_color='#E0C48C')

        demuxer_max_back_bytes_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12), text='Max Back Buffer', text_color='#B0B0B0')
        demuxer_max_back_bytes_slider = ctk.CTkSlider(cache_buffer_frame, variable=demuxer_max_back_bytes, from_=16, to=2048, width=200,
                                                       number_of_steps=2032, command=_demuxer_max_back_bytes_slider_change, **_slider_kw)
        demuxer_max_back_bytes_slider.bind('<ButtonRelease-1>', _apply_cache_slider_settings)
        demuxer_max_back_bytes_value_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12, 'bold'), text=f'{demuxer_max_back_bytes.get()}M', text_color='#E0C48C')

        cache_pause_wait_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12), text='Cache Pause Wait', text_color='#B0B0B0')
        cache_pause_wait_slider = ctk.CTkSlider(cache_buffer_frame, variable=cache_pause_wait, from_=0.1, to=20.0, width=200,
                                                       number_of_steps=199, command=_cache_pause_wait_slider_change, **_slider_kw)
        cache_pause_wait_slider.bind('<ButtonRelease-1>', _apply_cache_slider_settings)
        cache_pause_wait_value_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12, 'bold'), text=f'{cache_pause_wait.get():.1f}s', text_color='#E0C48C')

        audio_wait_open_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12), text='Audio Wait Open', text_color='#B0B0B0')
        audio_wait_open_slider = ctk.CTkSlider(cache_buffer_frame, variable=audio_wait_open, from_=1, to=10, width=200,
                                                number_of_steps=9, command=_audio_wait_open_slider_change, **_slider_kw)
        audio_wait_open_slider.bind('<ButtonRelease-1>', _apply_cache_slider_settings)
        audio_wait_open_value_label = ctk.CTkLabel(cache_buffer_frame, font=('Arial', 12, 'bold'), text=f'{audio_wait_open.get()}s', text_color='#E0C48C')

        # ── Fullscreen Settings Card ──
        fullscreen_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        fullscreen_frame.grid_columnconfigure(0, weight=1)
        fullscreen_frame.grid_columnconfigure(1, weight=1)
        fullscreen_frame.grid_columnconfigure(2, weight=1)

        fullscreen_title = ctk.CTkLabel(fullscreen_frame, text='  ▸ Fullscreen', font=('Arial', 14, 'bold'), text_color='#C0A0E0', anchor='w')
        openwith_fullscreen_btn = ctk.CTkCheckBox(fullscreen_frame, text='Auto fullscreen on open', variable=open_with_fullscreen,
                                                    fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12), command=autofullscreen_setting)
        hover_fullscreen_btn = ctk.CTkCheckBox(fullscreen_frame, text='Hover Fullscreen', variable=hover_fullscreen,
                                                fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12), command=lambda:switch_hover_fullscreen)
        fullscreen_mode_label = ctk.CTkLabel(fullscreen_frame, text='Fullscreen Mode:', font=('Arial', 12), text_color='#B0B0B0', anchor='w')
        fullscreen_mode_normal_btn = ctk.CTkRadioButton(fullscreen_frame, text='Normal', variable=fullscreenmode, value=0,
                                                         text_color='#C8C8C8', font=('Arial', 12),command=SetFullscreenmode)
        fullscreen_mode_all_widget_btn = ctk.CTkRadioButton(fullscreen_frame, text='Fullscreen (all widgets)', variable=fullscreenmode, value=1,
                                                              text_color='#C8C8C8', font=('Arial', 12),command=SetFullscreenmode)
        fullscreen_mode_window_btn = ctk.CTkRadioButton(fullscreen_frame, text='Fullscreen to window', variable=fullscreenmode, value=2,
                                                         text_color='#C8C8C8', font=('Arial', 12),command=SetFullscreenmode )

        # ── Advanced Settings Card ──
        advanced_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        advanced_frame.grid_columnconfigure(0, weight=1)
        advanced_frame.grid_columnconfigure(1, weight=1)

        advanced_title = ctk.CTkLabel(advanced_frame, text='  ▸ Advanced', font=('Arial', 14, 'bold'), text_color='#E08080', anchor='w')
        blurbtn = ctk.CTkCheckBox(advanced_frame, text='Acrylic blur effect', variable=blur_window,
                                   fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12), command=switch_blur_window)
        mpvlogbtn = ctk.CTkButton(advanced_frame, text='Show MPV Log', width=160, command=show_mpv_log,
                                   text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        enable_dnd_btn = ctk.CTkCheckBox(advanced_frame, text='Enable Drag and Drop', variable=enable_drag_and_drop,
                                          fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12), command=switch_drag_and_drop)
        force_stop_loading_btn = ctk.CTkButton(advanced_frame, text='Force Stop Loading', width=160, command=set_force_stop_loading,
                                                text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        show_cache_btn = ctk.CTkCheckBox(advanced_frame, text='Show Cache Info', variable=show_cache,
                                          fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12), command=switch_show_cache)

        # ── External Services Card ──
        external_services_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2B2B2B', corner_radius=8)
        external_services_frame.grid_columnconfigure(0, weight=1)
        external_services_frame.grid_columnconfigure(1, weight=1)

        external_services_title = ctk.CTkLabel(external_services_frame, text='  ▸ External Services', font=('Arial', 14, 'bold'), text_color='#80C0E0', anchor='w')
        chrome_extension_server_checkbtn = ctk.CTkSwitch(external_services_frame, text='Chrome extension server', variable=setting_run_chrome_extension_server,
                                                          command=switch_flask_server, text_color='#C8C8C8', font=('Arial', 12))
        enable_discord_presence_btn = ctk.CTkSwitch(external_services_frame, text='Discord Rich Presence', variable=enable_discord_presence,
                                                     text_color='#C8C8C8', font=('Arial', 12),
                                                     command=lambda:threading.Thread(daemon=True,target=switch_discord_presence).start())
        discord_presence_show_playing_btn = ctk.CTkCheckBox(external_services_frame, text='Show playing on Discord', variable=discord_presence_show_playing,
                                                             fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12), command=switch_discord_presence_show_playing)


        # ══════════ Version Info — Card-style sections ══════════
        ytdlp_frame = ctk.CTkFrame(version_info_tab, fg_color='#2B2B2B', corner_radius=8)
        ytdlp_frame.grid_columnconfigure(0, weight=1)
        ytdlp_frame.grid_columnconfigure(1, weight=1)
        
        player_frame = ctk.CTkFrame(version_info_tab, fg_color='#2B2B2B', corner_radius=8)
        player_frame.grid_columnconfigure(0, weight=1)
        player_frame.grid_columnconfigure(1, weight=1)

        # YT-DLP Section
        ytdlp_title = ctk.CTkLabel(ytdlp_frame, text='  \u25b8 YT-DLP', font=('Arial', 14, 'bold'), text_color='#7EE0A8', anchor='w')
        go_ytdlp_web = ctk.CTkButton(ytdlp_frame, text='Visit Website', width=120,
                                      command=lambda:webbrowser.open('https://github.com/yt-dlp/yt-dlp/releases'),
                                      text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        auto_update_ytdlp_btn = ctk.CTkButton(ytdlp_frame, text='Update', width=120,
                                               command=lambda:threading.Thread(daemon=True,target=update_ytdlp).start(),
                                               text_color='white', font=('Arial', 13, 'bold'), fg_color='#2E7D32', hover_color='#388E3C')

        # JaTubePlayer Section
        player_title = ctk.CTkLabel(player_frame, text='  \u25b8 JaTubePlayer', font=('Arial', 14, 'bold'), text_color='#7EB8E0', anchor='w')
        go_player_web = ctk.CTkButton(player_frame, text='Visit Website', width=120,
                                       command=lambda:webbrowser.open('https://github.com/jackaopen/JaTubePlayer/releases'),
                                       text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')

        # Version Sub-frames
        ytdlp_current_versions_frame = ctk.CTkFrame(ytdlp_frame, fg_color='#1a1a1a', corner_radius=6)
        ytdlp_latest_versions_frame = ctk.CTkFrame(ytdlp_frame, fg_color='#1a1a1a', corner_radius=6)
        player_current_versions_frame = ctk.CTkFrame(player_frame, fg_color='#1a1a1a', corner_radius=6)
        player_latest_versions_frame = ctk.CTkFrame(player_frame, fg_color='#1a1a1a', corner_radius=6)

        ytdlp_current_versions_frame_title = ctk.CTkLabel(ytdlp_current_versions_frame, text='Current', font=('Arial', 12, 'bold'), text_color='#B0B0B0')
        ytdlp_latest_versions_frame_title = ctk.CTkLabel(ytdlp_latest_versions_frame, text='Latest', font=('Arial', 12, 'bold'), text_color='#B0B0B0')
        player_current_versions_frame_title = ctk.CTkLabel(player_current_versions_frame, text='Current', font=('Arial', 12, 'bold'), text_color='#B0B0B0')
        player_latest_versions_frame_title = ctk.CTkLabel(player_latest_versions_frame, text='Latest', font=('Arial', 12, 'bold'), text_color='#B0B0B0')

        ytdlp_ver_current_label = ctk.CTkLabel(ytdlp_current_versions_frame, font=('Arial', 14), text_color='#7EE0A8', anchor='w')
        ytdlp_ver_lastest_label = ctk.CTkLabel(ytdlp_latest_versions_frame, font=('Arial', 14), text_color='#80C8E0', anchor='w')

        player_ver_current_label = ctk.CTkLabel(player_current_versions_frame, font=('Arial', 14), text_color='#7EE0A8', anchor='w')
        player_ver_latest_label = ctk.CTkLabel(player_latest_versions_frame, font=('Arial', 14), text_color='#80C8E0', anchor='w')

        # Settings
        auto_check_ver_btn = ctk.CTkCheckBox(version_info_tab, text='Check version at startup', variable=auto_check_ver, command=save_autovercheck_option_ver,
                                              fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12))





        # ══════════ Hotkeys — Card-style sections ══════════
        hotkey_scrollable_frame = ctk.CTkScrollableFrame(hotkey_tab, width=680, height=400, fg_color='#242424')
        hotkey_scrollable_frame.grid(row=0, column=0)
        hotkey_scrollable_frame.grid_columnconfigure(0, weight=1)

        _hk_card_kw = dict(fg_color='#2B2B2B', corner_radius=8)
        _hk_textbox_kw = dict(font=('Arial', 12), width=200, height=1, state='disabled', fg_color='#1a1a1a', text_color='#C8C8C8', corner_radius=6)

        hotkey_playback_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)
        hotkey_mode_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)
        hotkey_volume_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)
        hotkey_player_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)
        hotkey_set_keymem_frame = ctk.CTkFrame(hotkey_scrollable_frame, **_hk_card_kw)

        hotkey_set_keymem_title = ctk.CTkLabel(hotkey_set_keymem_frame, text='  \u25b8 Set Hotkey', font=('Arial', 14, 'bold'), text_color='#E0C48C', anchor='w')
        hotkey_set_keymem_function_combobox = ctk.CTkComboBox(hotkey_set_keymem_frame, font=('Arial', 12), width=200, state='readonly',
                                                               values=['play_pause','next','previous','stop', 'volume_up','volume_down','mode_random','mode_continuous','mode_repeat','toggle_minimize'],
                                                               dropdown_fg_color='#333333', button_color='#444444')
        hotkey_set_keymem_startlisten_btn = ctk.CTkButton(hotkey_set_keymem_frame, text='Set Hotkey', width=160, command=set_keymem_setting_thread,
                                                            text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        hotkey_set_keymem_set_default_btn = ctk.CTkButton(hotkey_set_keymem_frame, text='Reset All to Default', width=160, command=set_keymem_default_setting,
                                                            text_color='white', font=('Arial', 13, 'bold'), fg_color='#B30C00', hover_color='#A52A2A')

        hotkey_playback_frame_title = ctk.CTkLabel(hotkey_playback_frame, text='  \u25b8 Playback', font=('Arial', 14, 'bold'), text_color='#FF6B8A', anchor='w')
        hotkey_mode_frame_title = ctk.CTkLabel(hotkey_mode_frame, text='  \u25b8 Playback Mode', font=('Arial', 14, 'bold'), text_color='#7EE0A8', anchor='w')
        hotkey_volume_frame_title = ctk.CTkLabel(hotkey_volume_frame, text='  \u25b8 Volume', font=('Arial', 14, 'bold'), text_color='#80C8E0', anchor='w')
        hotkey_player_frame_title = ctk.CTkLabel(hotkey_player_frame, text='  \u25b8 Player', font=('Arial', 14, 'bold'), text_color='#C0A0E0', anchor='w')

        hotkey_playback_play_pause_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 12), text='Play / Pause', text_color='#B0B0B0')
        hotkey_playback_stop_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 12), text='Stop', text_color='#B0B0B0')
        hotkey_playback_next_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 12), text='Next Video', text_color='#B0B0B0')
        hotkey_playback_prev_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 12), text='Previous Video', text_color='#B0B0B0')
    
        hotkey_mode_repeat_label = ctk.CTkLabel(hotkey_mode_frame, font=('Arial', 12), text='Repeat Mode', text_color='#B0B0B0')
        hotkey_mode_random_label = ctk.CTkLabel(hotkey_mode_frame, font=('Arial', 12), text='Random Mode', text_color='#B0B0B0')
        hotkey_mode_continuous_label = ctk.CTkLabel(hotkey_mode_frame, font=('Arial', 12), text='Continuous Play', text_color='#B0B0B0')

        hotkey_volume_up_label = ctk.CTkLabel(hotkey_volume_frame, font=('Arial', 12), text='Volume Up', text_color='#B0B0B0')
        hotkey_volume_down_label = ctk.CTkLabel(hotkey_volume_frame, font=('Arial', 12), text='Volume Down', text_color='#B0B0B0')
        hotkey_toggle_minimize_label = ctk.CTkLabel(hotkey_player_frame, font=('Arial', 12), text='Toggle Minimize', text_color='#B0B0B0')

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
                if mode == 1:
                    init_quickstartup_mode.set('search')
                    init_search_entry.delete(0,tk.END)
                    init_search_entry.insert(tk.END,quickstartconfig['entrymode_entry_content'])
                    init_search_select()
                elif mode == 2:
                    if client_secret_path and os.path.exists(client_secret_path) and youtubeAPI:
                        init_quickstartup_mode.set('playlist')
                        init_playlist_combobox.set(quickstartconfig['playlistmode_playlist_Name'])
                        init_playlist_select()


                elif mode == 3:
                    init_quickstartup_mode.set('local_playlist')
                    
                elif mode == 4 and save_history.get():
                    init_quickstartup_mode.set('recommedation')
                    setting_init_recommendation_select()
                
                if not save_history.get():init_rec_at_startbtn.configure(state='disabled')


        def get_hotkey_setting_thread():
            try:
                ui_queue.put(lambda: hotkey_playback_play_pause_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_playback_play_pause_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('play_pause', 'Not set'): hotkey_playback_play_pause_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_playback_play_pause_textbox.configure(state='disabled'))

                ui_queue.put(lambda: hotkey_playback_stop_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_playback_stop_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('stop', 'Not set'): hotkey_playback_stop_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_playback_stop_textbox.configure(state='disabled'))

                ui_queue.put(lambda: hotkey_playback_next_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_playback_next_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('next', 'Not set'): hotkey_playback_next_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_playback_next_textbox.configure(state='disabled'))

                ui_queue.put(lambda: hotkey_playback_prev_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_playback_prev_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('previous', 'Not set'): hotkey_playback_prev_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_playback_prev_textbox.configure(state='disabled'))

                ui_queue.put(lambda: hotkey_mode_repeat_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_mode_repeat_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('mode_repeat', 'Not set'): hotkey_mode_repeat_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_mode_repeat_textbox.configure(state='disabled'))

                ui_queue.put(lambda: hotkey_mode_random_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_mode_random_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('mode_random', 'Not set'): hotkey_mode_random_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_mode_random_textbox.configure(state='disabled'))

                ui_queue.put(lambda: hotkey_mode_continuous_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_mode_continuous_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('mode_continuous', 'Not set'): hotkey_mode_continuous_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_mode_continuous_textbox.configure(state='disabled'))

                ui_queue.put(lambda: hotkey_volume_up_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_volume_up_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('volume_up', 'Not set'): hotkey_volume_up_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_volume_up_textbox.configure(state='disabled'))

                ui_queue.put(lambda: hotkey_volume_down_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_volume_down_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('volume_down', 'Not set'): hotkey_volume_down_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_volume_down_textbox.configure(state='disabled'))
            
            
                ui_queue.put(lambda: hotkey_toggle_minimize_textbox.configure(state='normal'))
                ui_queue.put(lambda: hotkey_toggle_minimize_textbox.delete(0.0,tk.END))
                ui_queue.put(lambda v=CONFIG['keyboard_hotkeys'].get('toggle_minimize', 'Not set'): hotkey_toggle_minimize_textbox.insert(tk.END,v))
                ui_queue.put(lambda: hotkey_toggle_minimize_textbox.configure(state='disabled'))
            except Exception as e:
                log_handle(content=f"Error loading hotkey settings: {e}")
                
        
        def get_version_setting_thread():
            try:
                if check_internet_socket():
                    
                    ui_queue.put(lambda: ytdlp_ver_current_label.configure(text=f'{ytdlpver.__version__}'))
                    ui_queue.put(lambda: player_ver_current_label.configure(text=f'{ver}'))
                    ui_queue.put(lambda v=get_latest_player_version(): player_ver_latest_label.configure(text=f'{v}'))
                    ui_queue.put(lambda v=get_latest_dlp_version(): ytdlp_ver_lastest_label.configure(text=f'{v}'))
                else:
                    ui_queue.put(lambda: ytdlp_ver_lastest_label.configure(text=f'No internet'))
                    ui_queue.put(lambda: ytdlp_ver_current_label.configure(text=f'{ytdlpver.__version__}'))
                    ui_queue.put(lambda: player_ver_current_label.configure(text=f'{ver}'))
                    ui_queue.put(lambda: player_ver_latest_label.configure(text=f'No internet'))
            except Exception as e:log_handle(content=str(e))








        def setting_frame_listener():#looping thread to check selected video and quick startup mode
            '''
            looping thread to check selected video and quick startup mode
            check downloadability of the selected video
            '''
            
            
            global prename_setting
            while not setting_closed:

                try:
                    ui_queue.put(lambda: init_quick_startup_mode_text.configure(state='normal'))
                    ui_queue.put(lambda: init_quick_startup_mode_text.delete(0.0,tk.END))
                    try:
                        quickstartconfig = CONFIG['quickstartup_init']
                        mode = quickstartconfig['mode']
                        if mode == 0:ui_queue.put(lambda: init_quick_startup_mode_text.insert(tk.END,f'Not selected'))
                        elif mode == 1:ui_queue.put(lambda: init_quick_startup_mode_text.insert(tk.END,f'search : {CONFIG["quickstartup_init"]["entrymode_entry_content"]}'))
                        elif mode == 2:
                            if client_secret_path and os.path.exists(client_secret_path) and youtubeAPI:
                                ui_queue.put(lambda: init_quick_startup_mode_text.insert(tk.END,f'playlist : {CONFIG["quickstartup_init"]["playlistmode_playlist_Name"]}'))
                            else:
                                ui_queue.put(lambda: messagebox.showerror(f'JatubePlayer {ver}','you need client secret and youtube API!\nThe quick startup mode has deselected'))
                                CONFIG['quickstartup_init']['mode'] = 0
                                save_config()

                        elif mode == 3:ui_queue.put(lambda: init_quick_startup_mode_text.insert(tk.END,f'Local folder : {CONFIG["quickstartup_init"]["localfoldermode_folder_Path"]}'))
                        elif mode == 4:ui_queue.put(lambda: init_quick_startup_mode_text.insert(tk.END,f'recommmendation'))


                    except Exception as e:log_handle(content=str(e))
                    ui_queue.put(lambda: init_quick_startup_mode_text.configure(state='disabled'))

                    
                    ui_queue.put(lambda: download_seleted_title_text.configure(state='normal'))
                    ui_queue.put(lambda: download_seleted_title_text.delete(0.0,tk.END))
                    
                    if playing_vid_mode ==3 and playing_vid_info_dict:ui_queue.put(lambda: download_seleted_title_text.insert(tk.END,f'{playing_vid_info_dict["title"]}'))
                    elif selected_song_number != None and playlisttitles:ui_queue.put(lambda: download_seleted_title_text.insert(tk.END,f'{playlisttitles[selected_song_number]}'))
                    else:ui_queue.put(lambda: download_seleted_title_text.insert(tk.END,'Select a video first!'))
                    
                    ui_queue.put(lambda: download_seleted_title_text.configure(state='disabled'))
                        
                    
                        
                    
                    try:
                        _info_dict = playing_vid_info_dict if playing_vid_info_dict else {}
                        if playing_vid_mode == 0 and _info_dict.get('live_status') == 'is_live':
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        elif playing_vid_mode ==1 or playing_vid_mode ==2:
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        elif playing_vid_mode ==3 and _info_dict.get('live_status') == 'is_live':
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        elif playing_vid_mode ==4 and not vid_url[selected_song_number].startswith(('http://','https://')):
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
        threading.Thread(daemon=True,target=get_user_name).start()
        threading.Thread(daemon=True,target=get_hotkey_setting_thread).start()
        threading.Thread(daemon=True,target=setting_frame_listener).start()

        ui_queue.put(lambda:subtitlecombobox.configure(values=subtitle_namelist))
        ui_queue.put(lambda:subtitlecombobox.set(subtitle_namelist[subtitle_selection_idx.get()]))

        ui_queue.put(lambda:download_path_textbox.configure(state='normal'))
        ui_queue.put(lambda:download_path_textbox.delete(0.0,tk.END))
        ui_queue.put(lambda:download_path_textbox.insert(tk.END,download_path.get()))
        ui_queue.put(lambda:download_path_textbox.configure(state='disabled'))
        
    
        if youtubeAPI:root.after(0,apilabel.configure(text=f'{youtubeAPI[:10]}{"*" * (len(youtubeAPI)-10)}'))
        update_cookie_path_textbox()
        update_client_secrets_path_textbox()



        # ══════════ Layout: Personal Playlist Tab ══════════
        youtube_data_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(10, 4), sticky="ew")
        youtube_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        updatelike_btn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        auto_like_refresh_checkbtn.grid(row=1, column=1, padx=8, pady=5, sticky="w")
        updatesub_btn.grid(row=2, column=0, padx=(24, 8), pady=5, sticky="w")
        auto_sub_refresh_checkbtn.grid(row=2, column=1, padx=8, pady=5, sticky="w")
        updateuserplaylists_btn.grid(row=3, column=0, columnspan=2, padx=(24, 8), pady=(5, 12), sticky="w")
        
        history_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        history_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        record_history_btn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        reset_history_btn.grid(row=1, column=1, padx=8, pady=(5, 12), sticky="w")

        playlist_remove_frame.grid(row=2, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        playlist_remove_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        playlist_remove_btn.grid(row=1, column=0, padx=(24, 8), pady=(5, 4), sticky="w")
        playlist_remove_note.grid(row=1, column=1, columnspan=2, padx=(24, 8), pady=(2, 12), sticky="w")



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
        download_path_title.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        download_path_label.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="e")
        download_path_textbox.grid(row=1, column=1, padx=(8, 8), pady=5, sticky="ew")
        select_download_path_btn.grid(row=2, column=1, padx=(8, 4), pady=(4, 12), sticky="w")
        set_default_download_path_btn.grid(row=2, column=2, padx=(4, 24), pady=(4, 12), sticky="e")

        downloadselectedsong.grid(row=3, column=0, columnspan=2, padx=20, pady=(16, 8))
        downloadhooklabel.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 10))

        # ══════════ Layout: Advanced Player Settings Tab ══════════

        # ── General Card ──
        general_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(10, 4), sticky="ew")
        general_header.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        maxresolutionlabel.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        maxresolutioncombobox.grid(row=1, column=1, padx=8, pady=5, sticky="w")
        autoretry_btn.grid(row=2, column=0, padx=(24, 8), pady=5, sticky="w")
        audio_only_checkbtn.grid(row=2, column=1, padx=8, pady=(5, 12), sticky="w")

        # ── Speed & Subtitle Card ──
        speed_subtitle_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        speed_subtitle_header.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        playerspeed_title_label.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        playerspeed_slider.grid(row=1, column=1, padx=8, pady=5, sticky="ew")
        playerspeed_speed_label.grid(row=1, column=2, padx=(4, 14), pady=5, sticky="w")
        subtitle_label.grid(row=2, column=0, padx=(24, 8), pady=(5, 12), sticky="w")
        subtitlecombobox.grid(row=2, column=1, padx=8, pady=(5, 12), sticky="w")

        # ── Cache & Buffer Card ──
        cache_buffer_frame.grid(row=2, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        cache_buffer_header.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        cache_secs_label.grid(row=1, column=0, padx=(24, 8), pady=4, sticky="w")
        cache_secs_slider.grid(row=1, column=1, padx=8, pady=4, sticky="ew")
        cache_secs_value_label.grid(row=1, column=2, padx=(4, 14), pady=4, sticky="w")
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
        fullscreen_frame.grid(row=3, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        fullscreen_title.grid(row=0, column=0, columnspan=3, padx=8, pady=(10, 6), sticky="w")
        openwith_fullscreen_btn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        hover_fullscreen_btn.grid(row=1, column=1, padx=8, pady=5, sticky="w")
        fullscreen_mode_label.grid(row=2, column=0, padx=(24, 8), pady=(6, 4), sticky="w")
        fullscreen_mode_normal_btn.grid(row=3, column=0, padx=(24, 8), pady=(2, 12), sticky="w")
        fullscreen_mode_all_widget_btn.grid(row=3, column=1, padx=8, pady=(2, 12), sticky="w")
        fullscreen_mode_window_btn.grid(row=3, column=2, padx=8, pady=(2, 12), sticky="w")

        # ── Advanced Card ──
        advanced_frame.grid(row=4, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        advanced_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        blurbtn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        mpvlogbtn.grid(row=2, column=0, padx=(24, 8), pady=5, sticky="w")
        enable_dnd_btn.grid(row=2, column=1, padx=8, pady=5, sticky="w")
        force_stop_loading_btn.grid(row=3, column=0, padx=(24, 8), pady=5, sticky="w")
        show_cache_btn.grid(row=3, column=1, padx=8, pady=(5, 12), sticky="w")

        # ── External Services Card ──
        external_services_frame.grid(row=5, column=0, columnspan=2, padx=16, pady=(4, 10), sticky="ew")
        external_services_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        chrome_extension_server_checkbtn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        enable_discord_presence_btn.grid(row=1, column=1, padx=8, pady=5, sticky="w")
        discord_presence_show_playing_btn.grid(row=2, column=1, padx=8, pady=(0, 12), sticky="w")
        
        # ══════════ Layout: Version Info Tab ══════════
        ytdlp_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(10, 4), sticky="ew")
        ytdlp_title.grid(row=0, column=0, padx=8, pady=(10, 6), sticky="w")

        ytdlp_current_versions_frame.grid(row=1, column=0, padx=(24, 4), pady=5, sticky="ew")
        ytdlp_latest_versions_frame.grid(row=1, column=1, padx=(4, 24), pady=5, sticky="ew")
        go_ytdlp_web.grid(row=2, column=1, padx=(4, 24), pady=(5, 12), sticky="e")
        auto_update_ytdlp_btn.grid(row=2, column=0, padx=(24, 4), pady=(5, 12), sticky="w")
        
        player_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        player_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        player_current_versions_frame.grid(row=1, column=0, padx=(24, 4), pady=5, sticky="ew")
        player_latest_versions_frame.grid(row=1, column=1, padx=(4, 24), pady=5, sticky="ew")
        go_player_web.grid(row=2, column=1, padx=(4, 24), pady=(5, 12), sticky="e")

        # Version sub-frame layouts
        ytdlp_current_versions_frame_title.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        ytdlp_ver_current_label.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")
        ytdlp_latest_versions_frame_title.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        ytdlp_ver_lastest_label.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")

        player_current_versions_frame_title.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        player_ver_current_label.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")
        player_latest_versions_frame_title.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        player_ver_latest_label.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")

        auto_check_ver_btn.grid(row=2, column=0, columnspan=2, padx=20, pady=(8, 10), sticky="w")

####### quick init frame #########

        # ── Quick Init Header Card ──
        header_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2B2B2B', corner_radius=8)
        header_frame.grid_columnconfigure(0, weight=1)
        header_title = ctk.CTkLabel(header_frame, text='  \u25b8 Quick Startup', font=('Arial', 14, 'bold'), text_color='#90D080', anchor='w')
        header_title.grid(row=0, column=0, padx=8, pady=(10, 6), sticky="w")
        init_toggle_quickstartup_checkbtn = ctk.CTkCheckBox(header_frame, text='Enable quick startup', variable=init_toggle_quickstartup, command=setting_init_toggle_quickstartup,
                                                              fg_color='#3A3A3A', hover_color='#505050', text_color='#C8C8C8', font=('Arial', 12))
        init_toggle_quickstartup_checkbtn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        init_quick_startup_mode_text = ctk.CTkTextbox(header_frame, font=('Arial', 13), height=25, text_color='#C8C8C8', fg_color='#1a1a1a', corner_radius=6)
        init_quick_startup_mode_text.grid(row=2, column=0, padx=12, pady=(4, 12), sticky="ew")
        init_quick_startup_mode_text.configure(state='disabled')
        header_frame.grid(row=0, column=0, columnspan=2, padx=16, pady=(10, 4), sticky="ew")

        # ── Search Card ──
        search_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2B2B2B', corner_radius=8)
        search_frame.grid_columnconfigure((0,1), weight=1)
        search_title = ctk.CTkLabel(search_frame, text='  \u25b8 Search', font=('Arial', 14, 'bold'), text_color='#E0C48C', anchor='w')
        search_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        init_search_btn = ctk.CTkRadioButton(search_frame, text='Init search', variable=init_quickstartup_mode, value='search', command=init_search_select,
                                              text_color='#C8C8C8', font=('Arial', 12))
        init_search_btn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        init_search_entry = ttk.Entry(search_frame, font=('Arial', 13), width=14)
        init_search_entry.grid(row=1, column=1, padx=(8, 12), pady=5, sticky="ew")
        init_search_set_btn = ctk.CTkButton(search_frame, text='Set Init Search', command=init_search_set, width=160,
                                              text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        init_search_set_btn.grid(row=2, column=0, columnspan=2, padx=12, pady=(4, 12), sticky="ew")
        search_frame.grid(row=1, column=0, padx=(16, 4), pady=4, sticky="nsew")
        
        # ── Playlist Card ──
        playlist_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2B2B2B', corner_radius=8)
        playlist_frame.grid_columnconfigure((0,1), weight=1)
        playlist_title = ctk.CTkLabel(playlist_frame, text='  \u25b8 Playlist', font=('Arial', 14, 'bold'), text_color='#80C8E0', anchor='w')
        playlist_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        init_playlist_btn = ctk.CTkRadioButton(playlist_frame, text='Init playlist', variable=init_quickstartup_mode, value='playlist', command=init_playlist_select,
                                                text_color='#C8C8C8', font=('Arial', 12))
        init_playlist_btn.grid(row=1, column=0, padx=(24, 4), pady=5, sticky="w")
        init_playlist_combobox = ttk.Combobox(playlist_frame, font=('Arial', 13), width=14, state='readonly')
        init_playlist_combobox.grid(row=1, column=1, padx=(4, 12), pady=5, sticky="ew")
        init_get_playlist_btn = ctk.CTkButton(playlist_frame, text='Get Playlist', command=init_playlist_get, width=100,
                                               text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        init_get_playlist_btn.grid(row=2, column=0, padx=(24, 4), pady=(4, 12), sticky="ew")
        init_playlist_set_btn = ctk.CTkButton(playlist_frame, text='Set Playlist', command=init_playlist_set, width=100,
                                               text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        init_playlist_set_btn.grid(row=2, column=1, padx=(4, 12), pady=(4, 12), sticky="ew")
        playlist_frame.grid(row=1, column=1, padx=(4, 16), pady=4, sticky="nsew")

        # ── Local Folder Card ──
        local_folder_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2B2B2B', corner_radius=8)
        local_folder_frame.grid_columnconfigure((0,1), weight=1)
        local_folder_title = ctk.CTkLabel(local_folder_frame, text='  \u25b8 Local Folder', font=('Arial', 14, 'bold'), text_color='#C0A0E0', anchor='w')
        local_folder_title.grid(row=0, column=0, columnspan=2, padx=8, pady=(10, 6), sticky="w")
        init_local_folder_btn = ctk.CTkRadioButton(local_folder_frame, text='Init local folder', variable=init_quickstartup_mode, value='local_playlist', command=init_local_playlist,
                                                     text_color='#C8C8C8', font=('Arial', 12))
        init_local_folder_btn.grid(row=1, column=0, padx=(24, 8), pady=5, sticky="w")
        init_select_local_folder_btn = ctk.CTkButton(local_folder_frame, text='Select Folder', command=init_select_local_folder, width=160,
                                                       text_color='white', font=('Arial', 13, 'bold'), fg_color='#3A3A3A', hover_color='#505050')
        init_select_local_folder_btn.grid(row=1, column=1, padx=(8, 12), pady=(5, 12), sticky="ew")
        local_folder_frame.grid(row=2, column=0, padx=(16, 4), pady=4, sticky="nsew")
        
        # ── Recommendation Card ──
        rec_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2B2B2B', corner_radius=8)
        rec_frame.grid_columnconfigure(0, weight=1)
        rec_title = ctk.CTkLabel(rec_frame, text='  \u25b8 Recommendation', font=('Arial', 14, 'bold'), text_color='#E08080', anchor='w')
        rec_title.grid(row=0, column=0, padx=8, pady=(10, 6), sticky="w")
        init_rec_at_startbtn = ctk.CTkRadioButton(rec_frame, text='Init recommendation', variable=init_quickstartup_mode, value='recommendation', command=setting_init_recommendation_select,
                                                    text_color='#C8C8C8', font=('Arial', 12))
        init_rec_at_startbtn.grid(row=1, column=0, padx=(24, 8), pady=(5, 12), sticky="w")
        rec_frame.grid(row=2, column=1, padx=(4, 16), pady=4, sticky="nsew")


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
        setting.mainloop()

def lenght_convertor(length):
    
    hour = math.floor(length// 3600)
    min = math.floor(length%3600//60)
    sec = math.floor(length%60)
    return hour,min,sec

def show_mpv_log():
    global log_,log_text,insert_log
    try:
        log_.deiconify()
        log_.lift()
        # Refresh log content
        log_text.configure(state='normal')
        log_text.delete(1.0, tk.END)
        for entry in mpv_log:
            log_text.insert(tk.END, entry + '\n')
        log_text.configure(state='disabled')
        log_text.see(tk.END)
    except:
        log_ = tk.Toplevel(root, bg='#1a1a1a')
        log_.title('JaTubePlayer Log Viewer')
        log_.resizable(True, True)
        log_.geometry('800x400')
        log_.minsize(400, 200)
        log_.iconbitmap(icondir)
        log_.attributes('-topmost', 'true')

        if blur_window.get():
            root.after(200, lambda: blur(win32gui.FindWindow(None, log_.title()), Dark=True, Acrylic=True))

        def leave():
            root.attributes('-topmost', 'false')
            log_.destroy()
        log_.protocol('WM_DELETE_WINDOW', leave)

        # Main frame
        main_frame = tk.Frame(log_, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Title label
        title_label = tk.Label(main_frame, text='📋 JaTubePlayer Log Viewer', font=('Segoe UI', 12, 'bold'), 
                               bg='#1a1a1a', fg='#ffffff')
        title_label.pack(anchor='w', pady=(0, 8))

        # Text frame with scrollbar
        text_frame = tk.Frame(main_frame, bg='#2d2d2d')
        text_frame.pack(fill='both', expand=True)

        scrollbar = ctk.CTkScrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        log_text = tk.Text(text_frame, font=('Consolas', 10), bg='#2d2d2d', fg='#e0e0e0',
                           insertbackground='white', selectbackground='#4a4a4a',
                           relief='flat', padx=8, pady=8, wrap='word',
                           yscrollcommand=scrollbar.set)
        log_text.pack(side='left', fill='both', expand=True)
        scrollbar.configure(command=log_text.yview)

        # Insert log entries
        for entry in mpv_log:
            log_text.insert(tk.END, entry + '\n')
        log_text.configure(state='disabled')
        log_text.see(tk.END)

        # Button frame
        btn_frame = tk.Frame(main_frame, bg='#1a1a1a')
        btn_frame.pack(fill='x', pady=(8, 0))



        def refresh_log():
            log_text.configure(state='normal')
            log_text.delete(1.0, tk.END)
            for entry in mpv_log:
                log_text.insert(tk.END, entry + '\n')
            log_text.configure(state='disabled')
            log_text.see(tk.END)
        def insert_log(content:str):
            log_text.configure(state='normal')
            log_text.insert(tk.END, content + '\n')
            log_text.configure(state='disabled')
            log_text.see(tk.END)    





def progressbar_hook(d):
    global downloadhooktext
    try:
        downloadhooktext.set(f'Downloading ... {int((d["downloaded_bytes"]/d["total_bytes"])*100)}%')
    except:downloadhooktext.set(f'Downloading ... ')


@check_internet
def enterplaylist(event=None):
    '''
    The bth event
    if there is no playlist selected, it will get the user playlists first
    else it will set and enter the playlist selected and update the mode textbox , playlistID variable and get the youtube playlist videos
   
    '''
    log_handle(content=str(userplaylistcombobox.get()))
    if userplaylistcombobox.get() == '':
        try:get_user_playlists(0)
        except:
            messagebox.showerror(f'JaTubePlayer {ver}','login or select a playlist first!')
    else:
        index = userplaylistcombobox.cget("values").index(userplaylistcombobox.get())
        playlistID.set(user_playlists_id[index])
        modetextbox.configure(state='normal')
        modetextbox.delete(1.0,tk.END)
        modetextbox.insert(tk.END,f"Playlist\n{user_playlists_name[index]}")
        modetextbox.configure(state='disabled')
        get_youtube_playlists()





def page_control(mode):
    log_handle(content=str(modetextbox.get(0.0,tk.END).strip()))
    if modetextbox.get(0.0,tk.END).strip() == 'Subscribed':get_sub_channel(mode)
    elif modetextbox.get(0.0,tk.END).strip() == 'Liked':get_liked_vid(mode)
    else:
        if 'loading' in modetextbox.get(0.0,tk.END).strip() or 'updating' in modetextbox.get(0.0,tk.END).strip():
            messagebox.showinfo(f'JaTubePlayer {ver}','still loading, please wait!')
        else:messagebox.showerror(f'JaTubePlayer {ver}','Please init subsciption or like page first!')


def get_sub_channel_thread(mode):
        global loadingplaylist,user_playlists_name,youtube,user_playlists_id,vid_url,selected_song_number,youtubeAPI,page_num
        loadingplaylist = True
        usestoreddata = False
        stop = False## for auto sub update and check if list is empty or not
        if mode !=0 and page_num == 0:# check if inited first
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please init the like page first'))
        else:  
            if mode == 0:
                usestoreddata = messagebox.askyesno(f'JaTubePlayer {ver}','login with stored data?')
                if not usestoreddata:
                    stop = True
                    ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','please go to "setting > Personal playlist" to login the desired account\n then go to "setting > Personal playlist" to update the list\n then try again!'))

            if usestoreddata and mode == 0 or mode != 0:#init or page change
                if auto_sub_refresh.get() and mode == 0:#auto update sub list, if required, only when init
                    ui_queue.put(lambda: modetextbox.configure(state='normal'))
                    ui_queue.put(lambda: modetextbox.delete(1.0, tk.END))
                    ui_queue.put(lambda: modetextbox.insert(tk.END, f"Subscribed\n⏳ updating..."))
                    ui_queue.put(lambda: modetextbox.configure(state='disabled'))
                    ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='Auto updating subscription list...', duration='short', icon=icondir)
                    res = update_sub_list(youtubeAPI,credentials,client_secret_path,current_dir)
                    if res != True:
                        failres = messagebox.askokcancel(f'JaTubePlayer {ver}','failed to update the subscription list!')
                        if not failres:stop = True

                #start to load sub list
                selected_song_number = None
                channel = sub_channel(current_dir)
                if channel != False and channel != 'NONE':
                    channel_temp = channel
                elif channel == 'NONE':
                    ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','There seems to be no stored data\n please go to "setting > update subscription list" to update the list\n then try again!'))
                    stop = True
                else:
                    stop = True
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','opps something went wrong'))
            try:
                if not stop:
                    if mode == 0:
                        page_num = 1
                    elif mode == 1:
                        if page_num == len(channel)//50+1:page_num = 1
                        else:page_num += 1
                    elif mode == 2:
                        if page_num == 1: page_num = len(channel)//50+1
                        else:page_num -= 1

                    ui_queue.put(lambda pn=page_num, ct=channel_temp: page_num_label.configure(text=f'page {pn}/{len(ct)//50+1}'))
                    
                    if channel_temp != False and channel_temp != 'NONE':
                        channel_ids = []
                        for i in range((page_num-1)*50,page_num*50):
                            try:channel_ids.append(channel_temp[i])
                            except Exception as e :log_handle(content=str(e))




                        ui_queue.put(lambda: modetextbox.configure(state='normal'))
                        ui_queue.put(lambda: modetextbox.delete(1.0, tk.END))
                        ui_queue.put(lambda: modetextbox.insert(tk.END, f"Subscribed\n⏳ loading..."))
                        ui_queue.put(lambda: modetextbox.configure(state='disabled'))

                        vid_url = []
                        playlisttitles.clear()
                        playlist_thumbnails.clear()
                        playlist_channel.clear()
                        ui_queue.put(lambda: playlisttreebox.delete(*playlisttreebox.get_children()))
                        ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
                        ydl_opts = {
                                'quiet': True,
                                'extract_flat': True,
                                'skip_download': True,
                                'playlistend': 1,  # Only get the latest video
                                'ignoreerrors': True,
                                'no_warnings': True,
                            }
                        
                        if cookies_dir:
                            ydl_opts['cookiefile'] = cookies_dir 
                            
                        index_for_tree = 1
                        channel_ids = [x.replace("UC", "UU", 1) for x in channel_ids]## UC for cahnnel ID, UU for uploaded video playlist ID
                        
                        with ThreadPoolExecutor() as executor:
                            futures = [executor.submit(_extract_file,f"https://www.youtube.com/playlist?list={url}") for url in channel_ids]
                            for future in futures:
                                
                                info = future.result()                        
                                
                                if info != None:
                                    response = info['entries'][0]
                                    vid_url.append(response['url'])## get vid info url
                                    playlisttitles.append(response["title"])
                                    playlist_channel.append(info['uploader'])
                                    playlist_thumbnails.append(response['thumbnails'][0]['url'])
                                    try:
                                        insert_treeview_quene.put((response['thumbnails'][0]['url'],
                                                                f'🛑LIVE {response["title"]}' if response['live_status'] == 'is_live' else response['title'],
                                                                info['uploader']))
                                    except:insert_treeview_quene.put((response['thumbnails'][0]['url'],
                                                                response["title"],
                                                                info['uploader']))
                                    index_for_tree +=1

                        # Update status box once (instead of every loop)
                        ui_queue.put(lambda: modetextbox.configure(state='normal'))
                        ui_queue.put(lambda: modetextbox.delete(1.0, tk.END))
                        ui_queue.put(lambda: modetextbox.insert(tk.END, f"Subscribed"))
                        ui_queue.put(lambda: modetextbox.configure(state='disabled'))
                        

            except Exception as e :log_handle(content=str(e))
            loadingplaylist = False

@check_internet
def get_sub_channel(mode,parent=root):
    global playing_vid_mode,credentials
    if client_secret_path :
        log_handle(content=str(client_secret_path))
        if os.path.exists(client_secret_path):
            if youtubeAPI != None:
                if  not credentials or not credentials.valid:
                    if messagebox.askokcancel(title=f"JaTubePlayer {ver}", message="This function requires login. Do you want to log in?"):
                        credentials = google_control.get_cred()
                        google_status_update()
                    else:return
                if loadingplaylist == False or loadingplaylist == True and messagebox.askokcancel(f'JaTubePlayer {ver}','player is still loading, sure to load again?'):
                    playing_vid_mode = 0
                    thread = threading.Thread(daemon = True,target=lambda:get_sub_channel_thread(mode))
                    thread.start()
        
            else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting')
        else:messagebox.showerror(f'JaTubePlayer {ver}','The client secrets does not exist or is invalid.\nPlease set up the youtube client secrets in setting')
    else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube client secrets in setting')



def get_liked_vid_thread(mode):
        global youtubeAPI,credentials,page_num,liked_vid_url,vid_url,selected_song_number,nextpagetoken,loadingplaylist,youtube
        if mode !=0 and page_num == 0:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please init the like page first'))
        else:
            selected_song_number = None
            loadingplaylist = True
            try:
                if not youtube:youtube = build('youtube','V3',developerKey=youtubeAPI,static_discovery = False,credentials=credentials)
                playlisttitles.clear()
                playlist_thumbnails.clear()
                vid_url = []
                ui_queue.put(lambda: playlisttreebox.delete(*playlisttreebox.get_children()))
                ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
                playlist_channel.clear()
                stop = False#for updating the like list , both auto and user cancel auto load
                
                if mode == 0:#mode 0 init, mode 1 next page, mode 2 previous page
                    log_handle(content=str(auto_like_refresh.get()))
                    if auto_like_refresh.get():
                        ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver} Liked', msg='Auto updating liked videos, please wait...', duration='short', icon=icondir)

                        ui_queue.put(lambda: modetextbox.configure(state='normal'))
                        ui_queue.put(lambda: modetextbox.delete(1.0, tk.END))
                        ui_queue.put(lambda: modetextbox.insert(tk.END, f"Liked\n⏳ updating..."))
                        ui_queue.put(lambda: modetextbox.configure(state='disabled'))
                        res = update_like_list(youtubeAPI,credentials,client_secret_path,current_dir)
                        if res != True:
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','failed to update the subscription list!\ntry to Login in google and update the list manually?'))
                            stop = True 
                               
                    elif not messagebox.askyesno(f'JaTubePlayer {ver}','login with stored data?'):
                        stop = True
                        ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','please go to "setting > Personal playlist" to login the desired account\n then go to "setting > Personal playlist" to update the list\n then try again!'))

                    if not stop:

                        url = liked_channel(current_dir)
                        if url != False and url != 'NONE':
                            liked_vid_url = url
                        elif url == 'NONE':
                            if messagebox.askokcancel(f'JaTubePlayer {ver}','There seems to be no stored data, load the data now?'):
                                result = update_like_list(youtubeAPI,credentials,client_secret_path,current_dir)
                                if result:
                                    ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}','succeed'))
                                    loadingplaylist = False
                                    get_liked_vid(0)
                                else:
                                    stop = True
                                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','opps something went wrong'))
                        else:
                            stop = True
                            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','opps something went wrong'))



                
                if not stop:
                    if mode == 0:page_num = 1
                    elif mode == 1 and page_num != 0:
                        if page_num != len(liked_vid_url)//50+1:
                            page_num += 1
                        else: page_num = 1
                    elif mode == 2 and page_num != 0:
                        if page_num != 1:
                            page_num -= 1
                        else: page_num = len(liked_vid_url)//50+1

                    ui_queue.put(lambda pn=page_num, lvu=liked_vid_url: page_num_label.configure(text=f'page {pn}/{len(lvu)//50+1}'))

                    if page_num != 0:
                        for i in range(50*(page_num-1),50*page_num):#######use len of vid url
                            try:
                                item = liked_vid_url[i]
                                vid_url.append(item)
                            except IndexError:break
                            
                            try:
                                ui_queue.put(lambda: modetextbox.configure(state='normal'))
                                ui_queue.put(lambda: modetextbox.delete(1.0, tk.END))
                                ui_queue.put(lambda: modetextbox.insert(tk.END, f"Liked\n⏳ loading... "))
                                ui_queue.put(lambda: modetextbox.configure(state='disabled'))
                                                        
                                title_response = youtube.videos().list(
                                    part='snippet',
                                    id=item.split('watch?v=')[1]
                                    ).execute()
                                if title_response != None:
                                    try:
                                        vid_info = title_response['items'][0]['snippet']
                                        if vid_info:
                                            try:
                                                title = f'🛑LIVE {vid_info["title"]}' if vid_info['live_status'] == 'is_live' else vid_info['title']
                                            except:title = vid_info["title"]
                                            playlisttitles.append(title)
                                            playlist_thumbnails.append(vid_info['thumbnails']['high']['url'])
                                            playlist_channel.append(vid_info['channelTitle'])
                                            insert_treeview_quene.put((vid_info['thumbnails']['high']['url'],title,vid_info['channelTitle']))
                                            ui_queue.put(lambda: root.update())
                                        else:
                                            ui_queue.put(lambda: ToastNotification().notify(app_id="JaTubePlayer", 
                                                                                            title=f'JaTubePlayer {ver}',
                                                                                            msg='Skipped a unavailable video', 
                                                                                            duration='short', 
                                                                                            icon=icondir))
                                    except:pass
                                else:pass
                            except Exception as e : ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}',err))

                        # Check if there are any videos returned
                
                    # Update status box once (instead of every loop)
                    ui_queue.put(lambda: modetextbox.configure(state='normal'))
                    ui_queue.put(lambda: modetextbox.delete(1.0, tk.END))
                    ui_queue.put(lambda: modetextbox.insert(tk.END, f"Liked"))
                    ui_queue.put(lambda: modetextbox.configure(state='disabled'))
                else:loadingplaylist = False
            except Exception as e:ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}',err))
            loadingplaylist = False

@check_internet
def get_liked_vid(mode):
    global playing_vid_mode,credentials
    if client_secret_path :
        if os.path.exists(client_secret_path):
            if youtubeAPI != None:
                if  not credentials or not credentials.valid:
                    if messagebox.askokcancel(title=f"JaTubePlayer {ver}", message="This function requires login. Do you want to log in?"):
                        credentials = google_control.get_cred()
                        google_status_update()
                    else:return
                if loadingplaylist == False or loadingplaylist == True and messagebox.askokcancel(f'JaTubePlayer {ver}','player is still loading, sure to load again?'):
                    playing_vid_mode = 0
                    thread = threading.Thread(daemon = True,target=lambda:get_liked_vid_thread(mode))
                    thread.start()
        
            else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting')
        else:messagebox.showerror(f'JaTubePlayer {ver}','The client secrets does not exist or is invalid.\nPlease set up the youtube client secrets in setting')
    else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube client secrets in setting')





nextpagetoken = None





@check_internet
def get_user_playlists_thread(mode):#0 = normal fun, 1 = init fun
    '''
    To get wat playlist do user have
    mode 0 = normal fun, 1 = init fun
    '''
    global user_playlists_name,youtube,user_playlists_id,init_playlists_id,credentials
    user_playlists_name = []
    user_playlists_id = []

    ui_queue.put(lambda: playlistlabel.configure(text='⏳'))
    try:
        if not youtube:youtube = build('youtube','V3',developerKey=youtubeAPI,static_discovery = False,credentials=credentials)
    except Exception as e:ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}',err))
    try:
        global playlists
        playlists = youtube.playlists().list(part='snippet', mine=True).execute()
    except:
        try:
            if not youtube:youtube = build('youtube','V3',developerKey=youtubeAPI,static_discovery = False,credentials=credentials)
            playlists = youtube.playlists().list(part='snippet', mine=True).execute()
        except Exception as e:ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}',err))

    try:
        for playlist in playlists['items']:
            user_playlists_id.append(f"{playlist['id']}")
            user_playlists_name.append(f"{playlist['snippet']['title']}")
        if mode == 0:
            ui_queue.put(lambda: userplaylistcombobox.configure(values=user_playlists_name))
            ui_queue.put(lambda: userplaylistcombobox._open_dropdown_menu())
        elif mode == 1:
            try:
                ui_queue.put(lambda: init_playlist_combobox.configure(values=user_playlists_name))
                ui_queue.put(lambda: init_playlist_combobox.event_generate('<Button-1>'))
                init_playlists_id = user_playlists_id
            except:pass

    except Exception as e:log_handle(content=str(e))

    ui_queue.put(lambda: playlistlabel.configure(text="📁"))
    
@check_internet
def get_user_playlists(mode):
    '''
    mode 0 = normal fun, 1 = init fun
    
    '''
    global credentials
    if client_secret_path :
        if os.path.exists(client_secret_path):
            if youtubeAPI != None:
                if  not credentials or not credentials.valid:
                    if messagebox.askokcancel(title=f"JaTubePlayer {ver}", message="This function requires login. Do you want to log in?"):
                        credentials = google_control.get_cred()
                        google_status_update()
                    else:return
                thread = threading.Thread(daemon = True,target=lambda:get_user_playlists_thread(mode))
                thread.start()
        
            else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting')
        else:messagebox.showerror(f'JaTubePlayer {ver}','The client secrets does not exist or is invalid.\nPlease set up the youtube client secrets in setting')
    else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube client secrets in setting')


@check_internet
def get_youtube_playlist_thread(playlistid_input = None): ###### get specifc info from the playlist that user choose
    global loadingplaylist,vid_url,selected_song_number,nextpagetoken,playlistID
    loadingplaylist = True
    try:
        selected_song_number = None
        playlistsongs =  []
        playlisttitles.clear()
        playlist_channel.clear()
        playlist_thumbnails.clear()
        vid_url.clear()

        ui_queue.put(lambda: playlisttreebox.delete(*playlisttreebox.get_children()))
        ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
        if youtube == None:
            google_control.get_cred()
            ui_queue.put(lambda: google_status_update())
            get_user_playlists(0)
        elif playlistID.get() or playlistid_input:
            ui_queue.put(lambda: playlistlabel.configure(text='⏳'))
            while True:
                playlist_response = youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlistID.get() if not playlistid_input else playlistid_input,
                    maxResults=100,
                    pageToken=nextpagetoken
                ).execute()
                playlistsongs.extend(playlist_response['items'])
                nextpagetoken = playlist_response.get('nextPageToken')
                if not nextpagetoken:
                    break
            tree_index = 1
            for item in playlistsongs:
                try:
                    video_id = item['contentDetails']['videoId']
                    title_response = youtube.videos().list(
                        part='snippet',
                        id=video_id
                    ).execute()
                    vid_url.append(f"https://www.youtube.com/watch?v={video_id}")
                    vid_info = title_response['items'][0]['snippet']
                    playlist_channel.append(vid_info['channelTitle'])
                    playlisttitles.append(vid_info['title'])
                    playlist_thumbnails.append(vid_info['thumbnails']['high']['url'])
                    insert_treeview_quene.put((vid_info['thumbnails']['high']['url'],vid_info['title'],vid_info['channelTitle']))
                    tree_index += 1
                except Exception as e:
                    log_handle(content=str(e))

        

    except googleapiclient.errors.HttpError as err: ######  handle stupid api
            ui_queue.put(lambda e=err: messagebox.showerror(f'JaTubePlayer {ver}', f"An error occurred: {e}"))
    except Exception as e:
            ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}', err))
    ui_queue.put(lambda: playlistlabel.configure(text='📁'))
    ui_queue.put(lambda: page_num_label.configure(text=''))
    loadingplaylist = False

@check_internet
def get_youtube_playlists(playlistID = None):
    '''
    If no playlistID is provided, it will use the global playlistID variable, which is set when user select a playlist from the combobox

    If playlistID is provided, it will use that playlistID to get the playlist videos, which is used for quick init function
    '''
    global playing_vid_mode,youtube,credentials
    if playlistID:
        if not youtube:youtube = build('youtube','V3',developerKey=youtubeAPI,static_discovery = False,credentials=credentials)#### make youtube init for quick startup bc it wont go through get user playlist so yt wont be created
    if client_secret_path :
        if os.path.exists(client_secret_path):
            if youtubeAPI != None:
                if  not credentials or not credentials.valid:
                    if messagebox.askokcancel(title=f"JaTubePlayer {ver}", message="This function requires login. Do you want to log in?"):
                        credentials = google_control.get_cred()
                        google_status_update()
                    else:return
                if loadingplaylist == False or loadingplaylist == True and messagebox.askokcancel(f'JaTubePlayer {ver}','player is still loading, sure to load again?'):
                    log_handle(content="start to get playlist videos")
                    playing_vid_mode = 0
                    thread = threading.Thread(daemon = True,target=lambda:get_youtube_playlist_thread(playlistID))
                    thread.start()
        
            else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube api key in setting')
        else:messagebox.showerror(f'JaTubePlayer {ver}','The client secrets does not exist or is invalid.\nPlease set up the youtube client secrets in setting')
    else:messagebox.showerror(f'JaTubePlayer {ver}','This function requires login.\nPlease set up the youtube client secrets in setting')




@check_internet
def youtube_search_thread():
    global playing_vid_mode,loadingplaylist,vid_url,selected_song_number,playlisttitles,playlist_thumbnails,playlist_channel
    playing_vid_mode = 0
    loadingplaylist = True
    if searchentry.get() != '':
        ui_queue.put(lambda: searchlistlabel.configure(text='⏳'))
        selected_song_number = None
        search_url_vid = f"https://www.youtube.com/results?search_query={searchentry.get()}&sp=EgIQAQ%253D%253D "  
        search_url_stream = f"https://www.youtube.com/results?search_query={searchentry.get()}&sp=EgJAAQ%253D%253D "  
        ydl_opts = {
            'quiet': True,        
            'extract_flat': True,  # Get video list without downloading
            'force_generic_extractor': True,
            'skip_download':True,
            'playlistend':39,

            
        }

        if cookies_dir:
            ydl_opts['cookiefile'] = cookies_dir 
        ydl_opts['logger'] = ytdlp_log_handle

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            vid_search_results = ydl.extract_info(search_url_vid, download=False)
            stream_search_results = ydl.extract_info(search_url_stream, download=False)
        
        playlisttreebox.delete(*playlisttreebox.get_children()) #########      start to process thumnail and title
        ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
        vid_url = []
        playlisttitles.clear()
        playlist_thumbnails.clear()
        playlist_channel.clear()
        index_for_tree = 1

        for item in stream_search_results['entries']:
            if item and  'url' in item:
                if item['url'].split('youtube.com/')[1].split('/')[0] != 'channel':
                    try:
                        thumbnail_url = f"https://i.ytimg.com/vi/{item['url'].split('v=')[1]}/hqdefault.jpg"
                    except IndexError:
                        thumbnail_url = f"https://i.ytimg.com/vi/{item['url'].split('shorts/')[1]}/hqdefault.jpg"

                    vid_url.append(item['url'])
                    playlisttitles.append(item['title'])
                    playlist_thumbnails.append(thumbnail_url)
                    playlist_channel.append(item['channel'])
                    insert_treeview_quene.put((thumbnail_url,f"🛑LIVE {item['title']}",item['channel']))
                    index_for_tree +=1 



        for item in vid_search_results['entries']:
            if item and  'url' in item:
                if item['url'].split('youtube.com/')[1].split('/')[0] != 'channel':
                    try:
                        thumbnail_url = f"https://i.ytimg.com/vi/{item['url'].split('v=')[1]}/hqdefault.jpg"
                    except IndexError:
                        thumbnail_url = f"https://i.ytimg.com/vi/{item['url'].split('shorts/')[1]}/hqdefault.jpg"

                    vid_url.append(item['url'])
                    playlisttitles.append(item['title'])
                    playlist_thumbnails.append(thumbnail_url)
                    playlist_channel.append(item['channel'])
                    insert_treeview_quene.put((thumbnail_url,item['title'],item['channel']))
                    index_for_tree +=1 

        ui_queue.put(lambda: modetextbox.configure(state='normal'))
        ui_queue.put(lambda: modetextbox.delete(1.0,tk.END))
        ui_queue.put(lambda: modetextbox.insert(tk.END,f"Search\n{searchentry.get()}"))
        ui_queue.put(lambda: modetextbox.configure(state='disabled'))
        ui_queue.put(lambda: page_num_label.configure(text=''))

        
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
    global vid_url,playlisttitles,playlist_channel,playlist_thumbnails,insert_treeview_quene,star_vid_handle,selected_song_number,playing_vid_mode
    selected_song_number = None
    playing_vid_mode = 4
    log_handle(content="start to get starred videos")
    ui_queue.put(lambda: modetextbox.configure(state='normal'))
    ui_queue.put(lambda: modetextbox.delete(1.0,tk.END))
    ui_queue.put(lambda: modetextbox.insert(tk.END,f"Starred Videos"))
    ui_queue.put(lambda: modetextbox.configure(state='disabled'))
    ui_queue.put(lambda: page_num_label.configure(text=''))
    ui_queue.put(lambda: playlisttreebox.delete(*playlisttreebox.get_children()))
    ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
    ui_queue.put(lambda:star_vid_handle.list_all(
      
            treeview_queue=insert_treeview_quene,
            vid_url=vid_url,
            playlisttitles=playlisttitles,
            playlist_channel=playlist_channel,
            playlist_thumbnails=playlist_thumbnails))
          

def switch_starred_vid(event=None):
    global star_vid_handle,selected_song_number,playing_vid_mode,vid_url,playlist_thumbnails,playlisttitles,playlist_channel,cookies_dir,playing_vid_info_dict
    
    if playing_vid_mode == 0 or playing_vid_mode == 2 or playing_vid_mode == 4:
        if selected_song_number == None:
            ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please select a video from the playlist first!'))
            return

        
    if playing_vid_mode == 0 or playing_vid_mode == 4:
        url_or_path = vid_url[selected_song_number]
        title = playlisttitles[selected_song_number]
        thumb = playlist_thumbnails[selected_song_number]
        channel = playlist_channel[selected_song_number]
    elif playing_vid_mode == 1:
        url_or_path = playing_title_textbox.get(0.0,tk.END).strip()
        title = os.path.basename(url_or_path)
        thumb = None
        channel = 'local file'
    elif playing_vid_mode == 2:
        url_or_path = vid_url[selected_song_number]
        title = playlisttitles[selected_song_number]
        thumb = None
        channel = 'local file'
    elif playing_vid_mode == 3:
        url_or_path = playing_vid_info_dict['original_url']
        title = playing_vid_info_dict['title']
        try:thumb = playing_vid_info_dict['thumbnails'][0]['url'] if playing_vid_info_dict['thumbnails'] else None
        except:thumb = playing_vid_info_dict['thumbnail'] if playing_vid_info_dict['thumbnail'] else None
        finally:thumb = thumb if thumb else None
        channel = playing_vid_info_dict['channel']
        
            

    if star_vid_handle.search(url_or_path):
        star_vid_handle.remove(url_or_path)
        ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
        ui_queue.put(lambda:ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='Removed from starred videos', duration='short', icon=icondir))

        if playing_vid_mode == 4:
            try:
                vid_url.pop(selected_song_number)
                playlisttitles.pop(selected_song_number)
                playlist_thumbnails.pop(selected_song_number)
                playlist_channel.pop(selected_song_number)
                ui_queue.put(lambda i=selected_song_number: playlisttreebox.delete(playlisttreebox.get_children()[i]))
            except Exception as e:
                log_handle(content=str(e))
                
        
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
                        cookie_path=cookies_dir)
        if res:
            ui_queue.put(lambda: star_btn.configure(text='★', fg_color='#D4A017', hover_color='#E8B820', text_color='#FFFDE7', font=('Segoe UI', 13, 'bold')))
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
                    ui_queue.put(lambda: playlisttreebox.selection_remove(playlisttreebox.selection()))
                    if playing_vid_mode == 2 or playing_vid_mode == 4:
                        ui_queue.put(lambda: playlisttreebox.selection_remove(playlisttreebox.selection()))
                        if player_mode_selector.get() =='continue':
                            if selected_song_number == len(vid_url) -1:
                                selected_song_number = 0
                            else:    
                                selected_song_number  = selected_song_number + 1
                        elif player_mode_selector.get() =='replay':
                            player.seek(0.1,reference='absolute')
                            root.after(200, lambda: setattr(player, 'pause', False))
                        elif player_mode_selector.get() =='random':
                            selected_song_number = random.randint(0,len(vid_url))
                        download_and_play()
                        ui_queue.put(lambda s=selected_song_number: playlisttreebox.selection_set(playlisttreebox.get_children()[s]))
                        if star_vid_handle.search(vid_url[selected_song_number]):
                            ui_queue.put(lambda: star_btn.configure(text='★', fg_color='#D4A017', hover_color='#E8B820', text_color='#FFFDE7', font=('Segoe UI', 13, 'bold')))
                        else:
                            ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
                        break

                elif playing_vid_mode == 1 or playing_vid_mode == 3 or playing_vid_mode == 0:### MPV option keep_open
                    
                    if player_mode_selector.get() =='replay':# =  3 chrome , =0 for chrome but added a video
                        player.seek(0.1,reference='absolute')
                        root.after(200, lambda: setattr(player, 'pause', False))
                    elif player_mode_selector.get() =='continue' and len(vid_url) > 0:
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
                    log_handle(content=f'video ended detected in yt thread , now do {player_mode_selector.get()}')
                    if selected_song_number != None:
                        if player_mode_selector.get() !='replay':
                            ui_queue.put(lambda: playlisttreebox.selection_remove(playlisttreebox.selection())) ## remove selection

                        if player_mode_selector.get() =='continue':
                            player.stop()
                            if selected_song_number == len(vid_url) -1:
                                selected_song_number = 0
                            else:    
                                selected_song_number  = selected_song_number + 1

                        elif player_mode_selector.get() =='replay':
                            player.seek(0.1,reference='absolute')
                            root.after(200, lambda: setattr(player, 'pause', False))
                        elif player_mode_selector.get() =='random':
                            player.stop()
                            selected_song_number = random.randint(0,len(vid_url))
                        
                        if player_mode_selector.get() !='replay':
                            ui_queue.put(lambda s=selected_song_number: playlisttreebox.selection_set(playlisttreebox.get_children()[s])) ## get selection
                            finish_break = True  ### so set it before enfter d.a.p fun
                            download_and_play() ### will stuck here bc of watiing while loop
                            if star_vid_handle.search(vid_url[selected_song_number]):
                                ui_queue.put(lambda: star_btn.configure(text='★', fg_color='#D4A017', hover_color='#E8B820', text_color='#FFFDE7', font=('Segoe UI', 13, 'bold')))
                            else:
                                ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
                            break
                            
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
        log_handle(content=f"Error in update_playing_pos_yt: {e}")
        

            


 
def scale_click(event):
    try:
        player.pause = True
        log_handle(content=str(event))
        userposition = math.floor(event)
        player.seek(userposition, reference='absolute')
        pauseStr.set('||')
    except:pass


def scale_release(event):
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
    log_handle(content=f"{seeking} {userposition}") 
    try:
        if str(root.focus_get()) != '.!entry' and player.duration != None and not seeking:
            seeking = True
            if mode == 1:
                try:
                    if not userposition :userposition = player.time_pos

                    userposition = max(0, userposition - 5)##not fk it to the negative lol

                    player.seek(userposition, reference='absolute')
                except Exception as e:log_handle(content=str(e))
            elif mode == 2:
                try:
                    if not userposition :userposition = player.time_pos
                    userposition = min(player.duration - 1, userposition + 5)##not fk it to the end
                    player.seek(userposition, reference='absolute')
                except Exception as e:log_handle(content=str(e))
            time.sleep(0.2)
            seeking = False
    except Exception as e:
            log_handle(content=str(e))
            seeking = False

def set_position_keyboard(mode):threading.Thread(daemon=True,target=lambda:set_position_keyboard_thread(mode)).start()    
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
                            player.seek(player.duration, reference='absolute')# move to live point
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
        player.volume =int(volume)
    except AttributeError:pass
    except Exception as e:log_handle(content=str(e))

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
    try:
        player.stop()
    except:pass

def playnextsong():
    global selected_song_number
    if playing_vid_mode != 1:
        if selected_song_number != None:
            if loadingvideo == False or loadingvideo==True and messagebox.askokcancel(f'JaTubePlayer {ver}','The video is still loading, sure to load again?'):
                stop_playing_video()
                
                playlisttreebox.selection_remove(playlisttreebox.selection())
                if selected_song_number == len(vid_url)-1:
                    selected_song_number = 0
                else:    
                    selected_song_number  +=1 
                playlisttreebox.selection_set(playlisttreebox.get_children()[selected_song_number])
                time.sleep(0.5)
                download_and_play()
                if star_vid_handle.search(vid_url[selected_song_number]):
                            ui_queue.put(lambda: star_btn.configure(text='★', fg_color='#D4A017', hover_color='#E8B820', text_color='#FFFDE7', font=('Segoe UI', 13, 'bold')))
                else:
                    ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
        else:messagebox.showerror(f'JaTubePlayer {ver}','please select a video first')
    else:messagebox.showerror(f'JaTubePlayer {ver}','You cant use the function with file playing mode')



def playprevsong():
    global selected_song_number
    if playing_vid_mode != 1:
        if selected_song_number != None:
            if loadingvideo == False or loadingvideo==True and messagebox.askokcancel(f'JaTubePlayer {ver}','The video is still loading, sure to load again?'):
                playlisttreebox.selection_remove(playlisttreebox.selection())
                stop_playing_video()
                
                if selected_song_number == 0: 
                    selected_song_number = len(vid_url) -1
                else: 
                    selected_song_number  = selected_song_number - 1
                time.sleep(0.5)
                download_and_play()
                if star_vid_handle.search(vid_url[selected_song_number]):
                            ui_queue.put(lambda: star_btn.configure(text='★', fg_color='#D4A017', hover_color='#E8B820', text_color='#FFFDE7', font=('Segoe UI', 13, 'bold')))
                else:
                    ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
                
                playlisttreebox.selection_set(playlisttreebox.get_children()[selected_song_number])
        else:messagebox.showerror(f'JaTubePlayer {ver}','please select a video first')
    else:messagebox.showerror(f'JaTubePlayer {ver}','You cant use the function with file playing mode')





def load_thread():  ### add every try except to a new log system for next update

    """

    Note for direct url:for lists, only the top/playing video will be sent inside

    it is a queue based thread, so to load a video, just put the (file_path,direct_url) into the load_thread_queue

    if the the queue has more than 1 item, it will only accept the first item and ignored and remove.

    Note the thread only load ONE 2 args tuple (file_path,direct_url) at once
    
    directl url for youtube + chrome ext
    file_path for folder/file/dnd
    
    """
    global stoped, pos_thread , stream ,playing_vid_url,playing_vid_info_dict,loadingvideo,force_stop_loading,subtitle_namelist,subtitle_urllist,subtitlecombobox
    while True:
        while load_thread_queue.empty():
                time.sleep(0.3)  ### wait for loading command
        # start loading
        chosen_file,direct_url = load_thread_queue.get()
        log_handle(content=f"load thread got cmd {chosen_file} {direct_url}")
        force_stop_loading = False # reset force stop loading bc it is a new load command
        while not load_thread_queue.empty():load_thread_queue.get() # clear the queue

        if direct_url:direct_url = direct_url.split('&')[0]
        if loadingvideo == True and messagebox.askokcancel(f'JaTubePlayer {ver}','The Video is already loading, Sure to load again?') or loadingvideo == False:
            create_mpv_player()


            if not chosen_file:  
                
                    loadingvideo = True
                    
                    stop_playing_video()  
                    ui_queue.put(lambda: player_loading_label.configure(text='⏳ loading...') if player_loading_label.cget('text') != 'retrying...' else None)
                    ui_queue.put(lambda: playing_title_textbox.configure(state='normal'))
                    ui_queue.put(lambda: playing_title_textbox.delete(1.0,tk.END))
                    ui_queue.put(lambda: playing_title_textbox.configure(state='disabled'))
                    player.volume =int(player_volume_scale.get())
                    
                    try:    
                            if direct_url and playing_vid_mode == 3:
                                if check_internet_socket():
                                    playing_vid_url = direct_url
                                    ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg=f'Playing video from chrome\n{direct_url}', duration='short', icon=icondir)
                                else:
                                    ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='Internet connection failed, please check your internet connection', duration='short', icon=icondir)
                                    loadingvideo = False
                                    return None #### return if no internet
                                    #the def actually dont need to return anything but just to make sure it wont go futher
                            try:
                                final_url,playing_vid_info_dict = get_info(yt_dlp=yt_dlp,
                                                                        maxres=maxresolution.get(),
                                                                        target_url=direct_url,
                                                                        deno_path=deno_exe,
                                                                        log_handler=ytdlp_log_handle,
                                                                        cookie_path=cookies_dir)
                                
                                if final_url:
                                    player.play(final_url)
                                    subtitle_selection_idx.set(0)
                                    subtitle_namelist = ['No subtitles']
                                    subtitle_urllist = []

                                    for sub in playing_vid_info_dict.get('subtitles').values():
                                        try:
                                            if len(sub) == 7:
                                                subtitle_namelist.append(sub[6]['name'])
                                                subtitle_urllist.append(sub[6]['url'])
                                            ui_queue.put(lambda:subtitlecombobox.configure(values=subtitle_namelist))
                                            ui_queue.put(lambda:subtitlecombobox.set(subtitle_namelist[subtitle_selection_idx.get()]))
                                        except Exception as e:
                                            log_handle(type='error',content=f"Error processing subtitle: {e}")

                                    log_handle(content=f"Available subtitles: {subtitle_namelist}")
                
                                    try:## try to make the vid play info somehow ytdlp fail to get info dict
                                        if playing_vid_info_dict.get('live_status') == 'is_live':
                                            global stream
                                            stream = True
            
                                        else:
                                            stream = False
                                    except:
                                        stream = False
                                        log_handle(type='error',content='failed to get live status')




                                    try:# save to history
                                        if save_history.get():
                                            desc = playing_vid_info_dict.get('description')
                                            infotags = playing_vid_info_dict.get('tags')
                                            channel_url = playing_vid_info_dict.get('channel_id')
                                            taglist = re.findall(r"[#＃](\w+)", f"{desc}")
                                            tag = ''
                                            if taglist != []:
                                                for i in range(len(taglist)):
                                                    tag = tag +''.join(taglist[i]) + ' '
                                                    if i >=2:break
                                            else :
                                                for i in range(len(infotags)):
                                                    tag = tag +''.join(infotags[i]) + ' '
                                                    if i >=2:break
                                            log_handle(content=f"{tag} {channel_url}")
                                            save_recent_vid_info(tag,channel_url,current_dir)
                                    except:pass
                                else:force_stop_loading = True   
                            except Exception as e :
                                playing_vid_info_dict = None
                                threading.Thread(daemon= True,target=lambda:messagebox.showerror(f'JaTubePlayer {ver}',f'we got some problem {e}\n\n we can still play the video, but some information make be missing, and you live streams cannot be played smoothly!')).start()
                            
                            except yt_dlp.utils.DownloadError as e:
                                log_handle(type='[error]',msg=f'ytdlp error {e}')
                            
                            for i in range(31):####### for wating mpv to load the vid

                                if force_stop_loading:
                                    loadingvideo = False
                                    ui_queue.put(lambda: player_loading_label.configure(text=''))
                                    force_stop_loading = False
                                    succed = False
                                    break


                                ui_queue.put(lambda: root.update())
                                mpv_log.append(f'loading_thread {i} ')
                                
                                if i %2 ==0:
                                    ui_queue.put(lambda: player_loading_label.configure(text='loading..'))
                                else:ui_queue.put(lambda: player_loading_label.configure(text='loading.'))


                                if i > 29:
                                    if autoretry.get() or messagebox.askretrycancel(f'JaTubePlayer {ver}','The player encounter some problem while loading, retry?'):
                                        loadingvideo = False
                                        ui_queue.put(lambda: player_loading_label.configure(text='retrying...'))
                                        load_thread_queue.put((chosen_file,direct_url)) #put it back to queue to retry
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
                                    if fullscreen_status == 0:ui_queue.put(lambda: root.title(f'JaTubePlayer {ver} by Jackaopen '))
                                    else:ui_queue.put(lambda: root.title(f'JaTubePlayer {ver} by Jackaopen - {playing_vid_info_dict["title"]}')) 

                                except Exception as e:
                                    log_handle(content=f"Error inserting title: {e}")
                                ui_queue.put(lambda: playing_title_textbox.configure(state='disabled'))
                                
                                ui_queue.put(lambda: smtc.update_media_info(
                                    title = playing_vid_info_dict['title'],
                                    artist = playing_vid_info_dict['uploader'],
                                    album = 'JaTubePlayer',
                                    thumbnail_url = playing_vid_info_dict['thumbnail']
                                ))
                                if enable_discord_presence.get():
                                    try:
                                        if discord_presence_show_playing.get():
                                            discord_presence.update(song_title=playing_vid_info_dict['title'])
                                        else:discord_presence.idle()
                                    except:pass

                                player.volume = (int(player_volume_scale.get()))
                                if playing_vid_mode == 3:pos_thread = threading.Thread(daemon = True,target=update_playing_pos_local_and_chrome)
                                else :pos_thread = threading.Thread(daemon = True,target=update_playing_pos_yt)
                                
                                pos_thread.start()
                                ui_queue.put(lambda: player_loading_label.configure(text=''))
                                ui_queue.put(lambda: pauseStr.set('||'))
                            
                    except Exception as e:
                        ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}', f"Failed to play video: {str(err)}"))
                    loadingvideo = False
                        
            else:
                    try:
                        stop_playing_video()
                    except: pass
                    try:
                        if chosen_file:
                                
                                loadingvideo = True
                                succed = False
                                ui_queue.put(lambda: player_loading_label.configure(text='Loading ...'))
                                if os.path.exists(chosen_file):
                                    
                                    player.play(chosen_file)
                                    player.volume =int(player_volume_scale.get())
                                    log_handle(content=str(chosen_file))
                                    time.sleep(0.1)
                                    
                                    if player.duration == None:
                                        for i in range(31):
                                            log_handle(content='testing point')
                                            if force_stop_loading:
                                                loadingvideo = False
                                                ui_queue.put(lambda: player_loading_label.configure(text=''))
                                                force_stop_loading = False
                                                succed = False
                                                break
                                            if player.duration != None:
                                                succed = True
                                                break
                                            log_handle(content=str(i))
                                            if i > 29:
                                                if autoretry.get() or messagebox.askretrycancel(f'JaTubePlayer {ver}','The player encounter some problem while loading, retry?'):
                                                    loadingvideo = False
                                                    ui_queue.put(lambda: player_loading_label.configure(text='retrying...'))
                                                    load_thread_queue.put((chosen_file,direct_url)) #put it back to queue to retry
                                                    succed = False
                                                    break
                                                else:
                                                    ui_queue.put(lambda: player_loading_label.configure(text=''))
                                                    succed = False
                                                    loadingvideo = False
                                                    break
                                            log_handle(content='loading')
                                            time.sleep(0.1)

                                            
                                    else:succed = True   

                                    if fullscreen_status == 0:ui_queue.put(lambda: root.title(f'JaTubePlayer {ver} by Jackaopen '))
                                    else:ui_queue.put(lambda cf=chosen_file: root.title(f'JaTubePlayer {ver} by Jackaopen - {os.path.basename(cf)}')) 
                                                                    

                                    if succed:
                                        ui_queue.put(lambda: playing_title_textbox.configure(state='normal'))
                                        log_handle(content=f"playing mode {playing_vid_mode}")
                                        if playing_vid_mode == 1:
                                            ui_queue.put(lambda cf=chosen_file: playing_title_textbox.insert(tk.END, str(cf)))  
                                        else:
                                            ui_queue.put(lambda cf=chosen_file: playing_title_textbox.insert(tk.END, os.path.basename(str(cf))))
                                        ui_queue.put(lambda: playing_title_textbox.configure(state='disabled'))
                                        


                                        if fullscreen_status == 0:ui_queue.put(lambda: root.title(f'JaTubePlayer {ver} by Jackaopen '))
                                        else:ui_queue.put(lambda cf=chosen_file: root.title(f'JaTubePlayer {ver} by Jackaopen - {cf}')) 
                                        try:
                                            ui_queue.put(lambda cf=chosen_file: smtc.update_media_info(
                                                title = os.path.basename(cf),
                                                artist = '-local file',
                                                album = 'JaTubePlayer',
                                                thumbnail_url = None

                                            ))
                                        except Exception as e:
                                            log_handle(content=f"Error updating media info: {e}")    

                                        if enable_discord_presence.get():
                                            try:
                                                if discord_presence_show_playing.get():
                                                    discord_presence.update(song_title="A Local media file :)")
                                                else:discord_presence.idle()
                                            except:pass
                                        
                                        
                                        player.volume = int(player_volume_scale.get())
                                        pos_thread = threading.Thread(daemon = True,target=update_playing_pos_local_and_chrome)
                                        pos_thread.start()
                                        ui_queue.put(lambda: player_loading_label.configure(text=''))
                                        ui_queue.put(lambda: pauseStr.set('||'))
                                        time.sleep(0.1)
                                        playing_vid_info_dict = {}
                                        loadingvideo = False
                                else:
                                    ui_queue.put(lambda:messagebox.showerror(f'JaTubePlayer {ver}', 'The file does not exist anymore, please choose another file'))
                                    loadingvideo = False
                                    ui_queue.put(lambda: player_loading_label.configure(text=''))
                    except Exception as e:
                        ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}', f"Failed to play local file:  {str(err)}"))
                        loadingvideo = False
                        ui_queue.put(lambda: player_loading_label.configure(text=''))




def load_local_files(mode,dnd_single_file_path=None,local_folder_path=None,dnd_files_path_lists:list=None):
    '''
    mode 0 == single file mode and dnd single file
    mode 1 == folder mode and dnd folder(must have muti files for better single file control balance)
    mode 2 == dnd multi files
    local_folder_path for quick startup local folder and dnd folder
    dnd_files_path_lists for dnd file list
    // only use kwarg
    '''
    global playing_vid_mode,vid_url,local_single_filepath,loadingvideo,selected_song_number
    
    if mode == 0:
        
        filetype = [
            ("All Supported Files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.mpeg *.mpg *.3gp *.webm *.ogv *.ts *.mts *.vob *.mp3 *.wav *.flac *.aac *.ogg *.wma *.m4a *.aiff *.opus *.amr"),
            ("Video Files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.mpeg *.mpg *.3gp *.webm *.ogv *.ts *.mts *.vob"),
            ("Audio Files", "*.mp3 *.wav *.flac *.aac *.ogg *.wma *.m4a *.aiff *.opus *.amr"),
            ]
        if not dnd_single_file_path:local_single_filepath = filedialog.askopenfilename(filetypes= filetype)
        else:local_single_filepath = dnd_single_file_path
        
        if local_single_filepath:
            playing_vid_mode = 1
            selected_song_number = None
            playlisttitles.clear()
            playlist_thumbnails.clear()
            vid_url = []
            playlisttreebox.delete(*playlisttreebox.get_children())
            ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))

            stop_playing_video()

            modetextbox.configure(state='normal')
            modetextbox.delete(1.0, tk.END)
            modetextbox.insert(tk.END, f"Local File")
            modetextbox.configure(state='disabled')
            
            load_thread_queue.put((local_single_filepath,None))
    if mode == 1:
        

        filetype = (
            ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".mpeg", ".mpg", ".3gp", ".webm", ".ogv",
            ".ts", ".mts", ".vob", ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", ".opus", ".amr"
        )
            
        

        if not local_folder_path:folder_path = filedialog.askdirectory()
        else:folder_path = local_folder_path
        
        log_handle(content=str(folder_path))
        if folder_path:
            playing_vid_mode = 2
            selected_song_number = None
            playlisttitles.clear()
            playlist_thumbnails.clear()
            vid_url = []
            playlisttreebox.delete(*playlisttreebox.get_children())
            folder_items = [file for file in os.listdir(folder_path) if file.endswith(filetype)]

            modetextbox.configure(state='normal')
            modetextbox.delete(1.0, tk.END)
            modetextbox.insert(tk.END, f"Local Folder\n{folder_path}")
            modetextbox.configure(state='disabled')

            index_for_tree = 1
            for item in folder_items:
                vid_url.append(os.path.join(folder_path,item))
                insert_treeview_quene.put((None,item,'Local files-'))
                playlisttitles.append(item)
                index_for_tree += 1
        
    if mode == 2 and dnd_files_path_lists:
            playing_vid_mode = 2
            selected_song_number = None
            playlisttitles.clear()
            playlist_thumbnails.clear()
            vid_url = []
            playlisttreebox.delete(*playlisttreebox.get_children())

            modetextbox.configure(state='normal')
            modetextbox.delete(1.0, tk.END)
            modetextbox.insert(tk.END, f"Local Folder\n{os.path.dirname(dnd_files_path_lists[0])}")
            modetextbox.configure(state='disabled')

            index_for_tree = 1
            for item in dnd_files_path_lists:
                vid_url.append(item)
                try:
                    base = os.path.basename(item)
                    insert_treeview_quene.put((None,base,'Local files-'))
                except:
                    pass
                playlisttitles.append(item)
                index_for_tree += 1




def download_and_play(event=None):### button and double click event
    '''
    for youtube video, the direct url is needed to make mpv play it, 
    so the load thread will get the direct url and put it in the queue, 
    and the load thread will handle the rest of the process, 
    for local file/folder, the file path is directly put in the queue, 
    and the load thread will handle the rest of the process.
    '''
    
    if playing_vid_mode == 0:
        if check_internet_socket():
            #load from youtube
            if selected_song_number != None:
                load_thread_queue.put((None,vid_url[selected_song_number]))
        
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
        if selected_song_number != None:
            load_thread_queue.put((vid_url[selected_song_number],None))
        else: messagebox.showerror(f'JaTubePlayer {ver}','please select a video first')

    elif playing_vid_mode == 4:
        if selected_song_number != None:
            url_or_path = vid_url[selected_song_number]
            if url_or_path.startswith(('http://', 'https://')):
                if check_internet_socket():
                    load_thread_queue.put((None,url_or_path))
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
        asyncio.run_coroutine_threadsafe(asyncio_session.close(),asynceventloop)
    except:pass
    try:
        shortcut_manager.cleanup()
    except:pass
    root.destroy()

    
root.protocol('WM_DELETE_WINDOW',onclose)

@check_internet
def get_resoltion(url) -> list[str]:
    try:
        opt = {'quiet': True,
               'skip_download':True,
               "extract_flat": True,
               'ignore_no_formats_error': True,
               'logger': ytdlp_log_handle,
               'js-runtimes':f'deno:{deno_exe}' 
               } 
        if cookies_dir:opt['cookiefile'] = cookies_dir

        with yt_dlp.YoutubeDL(opt) as ydl:
            info = ydl.extract_info(url, download=False)
            
        res = []
        for format_info in info['formats']:
            # Check for video formats only
            if format_info.get('vcodec', 'none') != 'none':
                height = format_info.get('height')
                if height and isinstance(height, int):
                    res.append(str(height))
                elif format_info.get('format_note'):
                    # Parse resolution from format_note
                    try:
                        note = format_info.get('format_note', '')
                        if 'p' in note:
                            res_str = note.split('p')[0]
                            if res_str.isdigit():
                                res.append(str(res_str))
                    except (ValueError, IndexError):
                        continue
        
        # Remove duplicates and sort
        res = sorted(list(set(res)))
        
        # Return default if no resolutions found
        if not res:
            log_handle(content="No valid resolutions found, returning defaults")
            return ["480", "720", "1080", "1440", "2160"]
        
        return res
    except Exception as e:
        log_handle(content=f"Error in get_resoltion: {e}")
        # Return default resolutions on any error
        return ["480", "720", "1080", "1440", "2160"]




def fullscreen_widget_change(mode:int=0):
    '''
    passively update/refresh 
    mode = 0, go normal
    mode = 1 go fullscreen , will check [tk.IntVar] fullscreenmode
    '''
    global fullscreen_status, stream, tkinter_scaling
   
    try:
        window_dpi = copy(get_window_dpi(hwnd))
        tkinter_scaling = window_dpi
        
        # Force geometry update before making changes
        root.update_idletasks()
        
        if mode == 0:
            
            root.geometry('1320x680')
            
            # Tkinter widgets need DPI scaling
            playlisttreebox.configure(height=int(20*window_dpi))
            if playing_vid_mode == 0 or playing_vid_mode == 4:
                playlisttreebox.column("#0", width=180, anchor='center')
            else:
                playlisttreebox.column("#0", width=0, anchor='center')
            playlisttreebox.column("title", width=int(1000))
            
            try:
                playlisttreebox.place_configure(relx=0.020, rely=0.125, relwidth=0.925, relheight=0.838)
                Y_scrollbar.place_configure(relx=0.945, rely=0.125, relheight=0.838)
                X_scrollbar.place_configure(relx=0.020, rely=0.963, relwidth=0.925)
                
                # Main frames
                header_frame.place_configure(relx=0, rely=0, relwidth=1, relheight=0.063)
                right_panel_frame.place_configure(relx=0.618, rely=0.070, relwidth=0.377, relheight=0.560)
                playlist_btn_frame.place_configure(relx=0.618, rely=0.63, relwidth=0.377, relheight=0.13)
                video_container.place_configure(relx=0.005, rely=0.070, relwidth=0.607, relheight=0.685)
                controls_frame.place_configure(relx=0.005, rely=0.764, relwidth=0.990, relheight=0.230)
                Frame_for_mpv.place_configure(relx=0.011, rely=0.084, relwidth=0.595, relheight=0.664)
                
                # Sub-frames inside transport bar
                now_playing_frame.place_configure(relx=0.008, rely=0.102, relwidth=0.984, relheight=0.240)
                progress_frame.place_configure(relx=0.008, rely=0.405, relwidth=0.984, relheight=0.230)
                mode_frame.place_configure(relx=0.008, rely=0.585, relwidth=0.132, relheight=0.375)
                playback_frame.place_configure(relx=0.150, rely=0.585, relwidth=0.43, relheight=0.375)
                volume_frame.place_configure(relx=0.635, rely=0.605, relwidth=0.105, relheight=0.350)
                action_btn_frame.place_configure(relx=0.745, rely=0.585, relwidth=0.300, relheight=0.375)
                

                
                # Mode widgets
                mode_label.place_configure(relx=0.06, rely=0.07)
                player_mode_continue.place_configure(relx=0.06, rely=0.45)
                player_mode_replay.place_configure(relx=0.39, rely=0.45)
                player_mode_random.place_configure(relx=0.72, rely=0.45)
                
                # Progress bar
                player_pos_label.place_configure(relx=0, rely=0.03, relwidth=0.050)
                player_position_scale.place_configure(relx=0.055, rely=0.12, relwidth=0.850, relheight=0.50)
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
                player_volume_scale.place_configure(relx=0.180, rely=0.35, relwidth=0.780, relheight=0.3)
                
                # Action buttons
                setting_btn.place_configure(relx=0, rely=0.06, relwidth=0.255, relheight=0.88)
                star_btn.place_configure(relx=0.270, rely=0.06, relwidth=0.175, relheight=0.88)
                select_info_btn.place_configure(relx=0.460, rely=0.06, relwidth=0.175, relheight=0.88)
                playing_info_btn.place_configure(relx=0.650, rely=0.06, relwidth=0.175, relheight=0.88)
                
                # Now playing
                np_icon.place_configure(relx=0.008, rely=0.14)
                playing_title_textbox.place_configure(relx=0.035, rely=0.10)
            except:
                pass
            
            player_position_scale.configure(height=int(160*0.313*0.5*0.03))
            Frame_for_mpv.lift()
            fullscreenbtn.configure(text='⛶')
            fullscreen_status = 0
            root.title(f'JaTubePlayer {ver} by Jackaopen')
            
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
                log_handle(content=f"Error in fullscreen_widget_change: {e}"    )
            
            player_position_scale.configure(height=int(root.winfo_height()*0.07*0.5*0.5*0.05))
            Frame_for_mpv.lift()
            controls_frame.lift()
            fullscreenbtn.configure(text='↖')
            fullscreen_status = 1
            
            try:
                if playing_title_textbox.get("1.0", "end").strip():
                    root.title(f'JaTubePlayer {ver} by Jackaopen  -  {playing_title_textbox.get("1.0", "end").strip()}')
                else:
                    root.title(f'JaTubePlayer {ver} by Jackaopen')
            except Exception as e:
                log_handle(content=f"Error updating title: {e}")
        
        root.update_idletasks()
        
        # Refresh sliders after layout is stable
        try:
            vol_value = player_volume_scale.get()
            pos_value = player_position_scale.get()
            player_volume_scale.set(vol_value)
            player_position_scale.set(pos_value)
        except:
            pass
        
    except Exception as e:
        log_handle(content=f"Error in fullscreen_widget_change: {e}")
       
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
                    log_handle('hover control frame removed')
                    hover_fullscreen_last_statue = 1
            else:
                if hover_fullscreen_last_statue == 1:

                    log_handle('hover control frame showed')
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
            if credentials and yt_dlp:
                if mode == 1:
                    searchentry.insert(tk.END,CONFIG['quickstartup_init']['entrymode_entry_content'])
                    youtube_search()
                elif mode == 2:
                    modetextbox.configure(state='normal')
                    modetextbox.delete(1.0,tk.END)
                    modetextbox.insert(tk.END,f"Playlist\n{CONFIG["quickstartup_init"]["playlistmode_playlist_Name"]}")
                    modetextbox.configure(state='disabled')
                    get_youtube_playlists(CONFIG["quickstartup_init"]["playlistmode_playlist_ID"])
                elif mode == 3:
                    load_local_files(1,local_folder_path=CONFIG["quickstartup_init"]["localfoldermode_folder_Path"])
                elif mode == 4:
                    init_get_recommendation()
            else:
                pass


        elif mode == 3:
            load_local_files(1,CONFIG["quickstartup_init"]["localfoldermode_folder_Path"])
        elif iter < 10:
            root.after(500,lambda: init_quick_startup(iter+1))
            log_handle(content=f"quickstartup internet test {iter} times")
        elif iter >= 10:
            try:
                ToastNotification().notify(app_id="JaTubePlayer",
                                        title=f'JaTubePlayer {ver}',
                                        msg='There seems to be no internet connection, quick startup in youtube related mode is cancelled.\nPlease check your internet connection.', 
                                        duration='short', icon=icondir)
                
            except Exception as e:
                log_handle(content="Error in init_quick_startup notification:")
                log_handle(content=str(e))

def init_openwith_thread():
    global playing_vid_mode
    try:
        if sys.argv[1]:
            playing_vid_mode = 1
            load_thread_queue.put((sys.argv[1],None))
            #no thread here bc we need to wait for the load to finish
            #then we can go to fullscreen

            if CONFIG['open_with_fullscreen']:
                log_handle(content='fullscreen')
                fullscreen_widget_change(mode=1)
            
    except:pass




def read_and_check_creditial():
    global credentials
    credentials = google_control.load_token_from_env()#better way to load token,since we cant force user to login at first time




def dnd_path_listener():       
        global selected_song_number 

        '''
        if the dropped file is valid, return the list of file paths
        valid file: return a single folder or multiple files
        
        '''
        while True:
            file_paths = dnd_path_queue.get()
            if file_paths:
                try:
                    valid_type = True
                    log_handle(content=f"Files dropped: {file_paths}")
                    for i in range(len(file_paths)):# check every file type if its valid
                        if os.path.isdir(file_paths[i]) and len(file_paths)> 1 :
                            ui_queue.put(lambda: messagebox.showerror("Jatubeplater drag&drop", "You can only drop a single folder or multiple files at once."))
                            valid_type = False
                            break
                        elif os.path.isfile(file_paths[i]):
                            _,ext = os.path.splitext(file_paths[i])
                            if ext.lower() not in ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.mpeg', '.mpg', '.3gp', '.webm', '.ogv', '.ts', '.mts', '.vob', '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.opus', '.amr']:
                                _file_path = file_paths[i]  # Capture for lambda
                                ui_queue.put(lambda fp=_file_path: messagebox.showerror("Jatubeplater drag&drop", f"The file '{fp}' is not contain valid media file."))
                                valid_type = False
                                break
                    #call thing to add to playlist
                    
                    if valid_type:
                        if len(file_paths) == 1:
                            if os.path.isfile(file_paths[0]):
                                load_local_files(mode=0,dnd_single_file_path=file_paths[0])#still put a file into it
                                selected_song_number = None
                                load_thread_queue.put((file_paths[0],None))#play the first file
                            elif os.path.isdir(file_paths[0]):
                                load_local_files(mode=1,local_folder_path=file_paths[0])
                        elif len(file_paths) > 0:
                            load_local_files(mode=2,dnd_files_path_lists=file_paths)
                finally:
                    time.sleep(0.5)
            else:time.sleep(1)


@check_internet
def init_get_recommendation():
    global playlisttitles,vid_url,playlist_channel,playlist_thumbnails,cookies_dir,loadingplaylist,playing_vid_mode
    if not loadingplaylist or loadingplaylist and messagebox.askokcancel(f'JaTubePlayer {ver}','Player is already loading, sure to load again?'):
        loadingplaylist = True
        playing_vid_mode = 0
        ui_queue.put(lambda: playlisttreebox.delete(*playlisttreebox.get_children()))
        time.sleep(1)
        while not yt_dlp:
            time.sleep(1)
            log_handle(content='wating for dlp...')
        ui_queue.put(lambda: modetextbox.configure(state='normal'))
        ui_queue.put(lambda: modetextbox.delete(1.0,tk.END))
        ui_queue.put(lambda: modetextbox.insert(tk.END,"Recommendation\n⏳Loading..."))
        ui_queue.put(lambda: modetextbox.configure(state='disabled'))
        playlisttitles,vid_url,playlist_channel,playlist_thumbnails = get_related_video(yt_dlp.YoutubeDL,current_dir,cookies_dir)
        zipped = list(zip(playlisttitles,vid_url,playlist_channel,playlist_thumbnails))
        shuffle(zipped)
        playlisttitles,vid_url,playlist_channel,playlist_thumbnails = map(list, zip(*zipped))
        for i in range(len(playlisttitles)):
            insert_treeview_quene.put((playlist_thumbnails[i],playlisttitles[i],playlist_channel[i]))
        ui_queue.put(lambda: modetextbox.configure(state='normal'))
        ui_queue.put(lambda: modetextbox.delete(1.0,tk.END))
        ui_queue.put(lambda: modetextbox.insert(tk.END,"Recommendation"))
        ui_queue.put(lambda: modetextbox.configure(state='disabled'))
        loadingplaylist = False


def init_read_api():
    global youtubeAPI
    youtubeAPI = Ferner_encrptor_.decrypte_api()


def init_read_dlp():
    global yt_dlp,utils,ytdlpver
    try:
        yt_dlp,utils,ytdlpver = load_yt_dlp(_internal_dir)
        if yt_dlp == None:
            ui_queue.put(lambda u=utils: messagebox.showerror(f'JaTubePlayer {ver}',f'seems to be something wrong with yt_dlp!\n{u}'))
    except Exception as e :ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}',err))
        

def init_read_config():
    global cookies_dir,client_secret_path,auto_like_refresh,auto_sub_refresh,auto_check_ver,save_history,maxresolution,listen_chromeextension_thread,enable_drag_and_drop,cache_secs,demuxer_max_bytes,demuxer_max_back_bytes,cache_pause_wait,audio_wait_open
    cookies_dir= CONFIG['cookie_path']
    client_secret_path = CONFIG['client_secret_path']
    log_handle(content=f"cookie {cookies_dir}")
    log_handle(content=f"client {client_secret_path}")  
    try:
        if CONFIG['auto_sub_refresh']:auto_sub_refresh.set(True)
        else:auto_sub_refresh.set(False)
        log_handle(content="sub fin")
        if CONFIG['auto_like_refresh']:auto_like_refresh.set(True)
        else:auto_like_refresh.set(False)
        log_handle(content="like fin")

        if CONFIG['vercheck']:auto_check_ver.set(True)
        else:auto_check_ver.set(False)
        log_handle(content="ver fin")

        if CONFIG['record_history']:save_history.set(True)
        else:save_history.set(False)
        log_handle(content="history fin")
        
        if CONFIG['open_with_fullscreen']:open_with_fullscreen.set(True)
        else:open_with_fullscreen.set(False)
        log_handle(content="open fin")
        
        if CONFIG['enable_drag_and_drop']:enable_drag_and_drop.set(True)
        else:enable_drag_and_drop.set(False)
        log_handle(content="dnd fin")

        if CONFIG['show_cache']:show_cache.set(True)
        else:show_cache.set(False)
        log_handle(content="cache fin")

        if CONFIG['hover_fullscreen']:hover_fullscreen.set(True)
        else:hover_fullscreen.set(False)

        
        download_path.set(CONFIG['download_path'])
        cache_secs.set(CONFIG['cache']['cache_secs'])
        demuxer_max_bytes.set(CONFIG['cache']['demuxer_max_bytes'])
        demuxer_max_back_bytes.set(CONFIG['cache']['demuxer_max_back_bytes'])
        cache_pause_wait.set(CONFIG['cache']['cache_pause_wait'])
        audio_wait_open.set(CONFIG['cache']['audio_wait_open'])
        fullscreenmode.set(CONFIG['fullscreenmode'])

        if CONFIG['enable_discord_presence']:
            enable_discord_presence.set(True)
            try:discord_presence.idle()
            except:pass
        else:
            enable_discord_presence.set(False)


        if CONFIG["discord_presence_show_playing"]:discord_presence_show_playing.set(True)
        else:discord_presence_show_playing.set(False)

        


        maxresolution.set(CONFIG["max_resolution"])
        setting_run_chrome_extension_server.set(CONFIG['run_flask'])

        
    except Exception as e:
        log_handle(content="Error in init_read_config:")
        log_handle(str(e))




@check_internet_silent
def init_ver_check():
    if CONFIG['vercheck']:
        latest_dlp = get_latest_dlp_version()
        if ytdlpver.__version__ != latest_dlp:
            ui_queue.put(lambda ld=latest_dlp: ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg=f'Your yt_dlp is not the newest!\nlatest: {ld}  yours: {ytdlpver.__version__}', duration='short', icon=icondir))
        
        latest_player = get_latest_player_version()
        if ver!= latest_player:
            ui_queue.put(lambda lp=latest_player: ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg=f'Your JaTubePlayer is not the newest!\nlatest: {lp}  yours: {ver}', duration='short', icon=icondir))







def create_mpv_player():
    global player,deno_exe

    cache_cfg = CONFIG.get("cache", {})
    cache_secs_val = int(cache_secs.get() or cache_cfg.get("cache_secs", 80))
    demuxer_max_bytes_val = int(demuxer_max_bytes.get() or cache_cfg.get("demuxer_max_bytes", 512))
    demuxer_max_back_bytes_val = int(demuxer_max_back_bytes.get() or cache_cfg.get("demuxer_max_back_bytes", 256))
    cache_pause_wait_val = int(cache_pause_wait.get() or cache_cfg.get("cache_pause_wait", 3))
    audio_wait_open_val = float(audio_wait_open.get() or cache_cfg.get("audio_wait_open", 1))

    buf_arg = {
    "cache": "yes",
    "cache-secs": cache_secs_val,
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


    log_handle("create mpv")
    log_handle(content=f"cookie dir: {cookies_dir}")

    if player:
        player.terminate()
        try:
            smtc.destroy()
        except:
            pass
        try:
            discord_presence.idle()
        except:
            pass
        log_handle(content="killed")


    player = mpv.MPV(
        idle = True,
        hwdec="auto",
        profile="fast",
        wid=Frame_for_mpv.winfo_id(),
        log_handler=log_handle,
        vid="no" if audio_only.get() else "auto",
        keep_open=True,
        af='scaletempo',
        msg_level="ytdl_hook=debug,ffmpeg=warn,cplayer=warn",
        **buf_arg,
        **sub_arg
    )

    log_handle(content=str(True if playing_vid_mode == 1 else False))




    

def init_star_vid_instance():
    global star_vid_handle
    star_vid_handle = star_vid_handler(current_dir=current_dir,
                                        yt_dlp=yt_dlp,
                                        deno_path=os.path.join(current_dir,'_internal','deno'),
                                        yt_dlp_log_handler=ytdlp_log_handler())

def init_set_smtc():
    smtc.next_song_fun = playnextsong
    smtc.prev_song_fun = playprevsong
    smtc.pause_fun = pause
    smtc.iconpath = icondir

def init_set_dnd_handle():
    log_handle(content="init dnd ... ")
    global dnd_handle
    log_handle(content=f"dnd {enable_drag_and_drop.get()}")
    dnd_handle.enable_drop(hwnd, enable_drag_and_drop.get())
    dnd_handle.dnd_path_queue = dnd_path_queue
    dnd_handle.root = root

def init_set_playertray():
    global tray
    tray = Playertray(iconpath=icondir,ver=ver,parent=root,ctk_messagebox=messagebox)                
    tray.run()


async def async_thumb():
    global asyncio_session,async_task
    try:
        if not asyncio_session:asyncio_session = aiohttp.ClientSession()##needs in async def ,in order to use the same session repeatedly
        if async_task:
            task_temp = async_task.copy()
            await asyncio.gather(*task_temp)
            async_task.remove(item for item in task_temp)
    except:pass
    await asyncio.sleep(0.25)  # Use asyncio.sleep instead of root.after
    asyncio.create_task(async_thumb())

def init_tree_view_quene():
    global async_task,asyncio_session
    try:
        while not insert_treeview_quene.empty():
            thumb, title, ch = insert_treeview_quene.get_nowait()
            id = playlisttreebox.insert('', 'end', values=(f'{title}\n{ch}',))
            if playing_vid_mode == 0 or playing_vid_mode == 4:
                async_task.append(load_thumbnail_thread(asyncio_session,id,thumb))

            #adjust column width in playlisttreebox insert thread
            if playing_vid_mode ==0 or playing_vid_mode == 4:
                playlisttreebox.column("#0", width=180,anchor='center')
            else:
                playlisttreebox.column("#0", width=0,anchor='center')



    except Exception as e:log_handle(content=str(e))
    root.after(20,init_tree_view_quene)

asynceventloop = asyncio.new_event_loop()
def start_async_eventloop():
    asyncio.set_event_loop(asynceventloop)
    asynceventloop.call_soon_threadsafe(lambda: asynceventloop.create_task(async_thumb()))
    asynceventloop.run_forever()

def init_listen_chromeextension():
    global playing_vid_mode,selected_song_number,star_vid_handle
    while setting_run_chrome_extension_server.get():
        if chrome_extension_flask.chrome_extension_url:
            log_handle(content=f"chrome extension url: {chrome_extension_flask.chrome_extension_url}")
            chrome_extension_url = chrome_extension_flask.chrome_extension_url.split("&")[0]
            playing_vid_mode = 3
            load_thread_queue.put((None,chrome_extension_url))
            selected_song_number = None

            vid_url.clear()
            playlisttitles.clear()
            playlist_thumbnails.clear()
            playlist_channel.clear()
            if star_vid_handle.search(chrome_extension_url):
                ui_queue.put(lambda: star_btn.configure(text='★', fg_color='#D4A017', hover_color='#E8B820', text_color='#FFFDE7', font=('Segoe UI', 13, 'bold')))
            else:
                ui_queue.put(lambda: star_btn.configure(text='☆', fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0', font=('Segoe UI', 13, 'bold')))
            
            ui_queue.put(lambda: playlisttreebox.delete(*playlisttreebox.get_children()))
            ui_queue.put(lambda: modetextbox.configure(state="normal"))
            ui_queue.put(lambda: modetextbox.delete(0.0, tk.END))
            ui_queue.put(lambda: modetextbox.insert(tk.END, "Chrome extension video"))
            ui_queue.put(lambda: modetextbox.configure(state="disabled"))
            chrome_extension_flask.chrome_extension_url = None

        elif chrome_extension_flask.chrome_extension_star_video:
            url = chrome_extension_flask.chrome_extension_star_video.split("&")[0]
            log_handle(content=f"chrome extension star video url: {url}")
            if not star_vid_handle.search(url):
                res = star_vid_handle.add(url)
                if res:ToastNotification().notify(app_id="JaTubePlayer", 
                                                   title=f'JaTubePlayer {ver}', 
                                                   msg='Added starred video to playlist\nFetching data...', 
                                                   duration='short', 
                                                   icon=icondir)
                else:
                    log_handle(content=f"Failed to add starred video from chrome extension, error in adding: {res}")
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}', "Failed to add starred video to playlist.\nError in adding video."))
                if playing_vid_mode == 4:
                    get_starred_vid()
                        

            else:
                ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}', "This video is already in your starred list."))
            chrome_extension_flask.chrome_extension_star_video = None
        elif chrome_extension_flask.chrome_extension_add_to_end:
            if playing_vid_mode ==0 or playing_vid_mode == 3 or playing_vid_mode == 4:
                url = chrome_extension_flask.chrome_extension_add_to_end.split("&")[0]
                log_handle(content=f"Adding video to playlist from chrome extension: {url}")
                try:
                    modetitle = modetextbox.get("1.0", "end").strip()

                    ui_queue.put(lambda: modetextbox.configure(state="normal"))
                    if "[with added video]" not in modetitle:
                        ui_queue.put(lambda mt=modetitle: (
                            modetextbox.delete(1.0, tk.END),
                            modetextbox.insert(tk.END, f"{mt} [with added video]")
                        ))
                    ui_queue.put(lambda: modetextbox.configure(state="disabled"))



                    if playing_vid_mode == 3:
                        playing_vid_mode = 0
                        selected_song_number = None

                    ToastNotification().notify(app_id="JaTubePlayer", 
                                               title=f'JaTubePlayer {ver}', 
                                               msg='Added video to playlist\nFetching data...', 
                                               duration='short', 
                                               icon=icondir)
                    _,info = get_info(
                        yt_dlp=yt_dlp,
                        maxres=1080,
                        target_url=url,
                        deno_path=deno_exe,
                        log_handler=ytdlp_log_handler()
                    )
                    try:thumb = info['thumbnails'][0]['url']
                    except:thumb = info['thumbnail']
                    finally:thumb = thumb if thumb else None 
                    log_handle(content=f"Added video to playlist: {info['title']} thumbnail: {thumb}")
                    insert_treeview_quene.put((thumb,f"[ADDED]{info['title']}",info['uploader']))
                    vid_url.append(url)
                    playlisttitles.append(info['title'])
                    playlist_channel.append(info['uploader'])
                    playlist_thumbnails.append(thumb)
                    ToastNotification().notify(app_id="JaTubePlayer",
                                               title=f'JaTubePlayer {ver}',
                                               msg='Added video to playlist',
                                               duration='short',
                                               icon=icondir)
                except Exception as e:
                    log_handle(content=f"Error adding video to playlist: {e}")
                    messagebox.showerror(f'JaTubePlayer {ver}', f"Failed to add video to playlist.\nError: {e}")    
                finally:
                    chrome_extension_flask.chrome_extension_add_to_end = None
            else:
                ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer {ver}', "You are in local media mode, cannot add video to playlist.\nYou can star the video to add it to the starred list, then go to starred mode to watch it."))
        
        
        
        time.sleep(0.5)

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
        'next': lambda: threading.Thread(target=playnextsong).start(), 
        'previous': lambda: threading.Thread(target=playprevsong).start(),
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
    global aiohttp,build, Credentials,google_auth_control,Ferner_encrptor,star_vid_handler
    global get_latest_player_version,get_latest_dlp_version
    import time
    

    t = time.time()
    import aiohttp
    log_handle(content=f"aiohttp: {time.time()-t:.3f}s")
    
    # Google API
    t = time.time()
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    log_handle(content=f"google_api: {time.time()-t:.3f}s")
    
    # Auth
    t = time.time()
    from account.google_login import google_auth_control
    log_handle(content=f"auth: {time.time()-t:.3f}s")
    
    # Fernet
    t = time.time()
    from account.fernet_pubnew_class import Ferner_encrptor
    log_handle(content=f"fernet: {time.time()-t:.3f}s")
    
    # Version check functions (needed by settings before delayed import)
    t = time.time()
    from utils.get_latest_version import get_latest_dlp_version, get_latest_player_version
    log_handle(content=f"version_funcs: {time.time()-t:.3f}s")
    
    t = time.time()
    from utils.star_vid import star_vid_handler
    log_handle(content=f"version_funcs: {time.time()-t:.3f}s")

    log_handle(content=f"Total import time: {time.time()-time1:.3f}s")





def _extra_startup_imports():
    global update_sub_list, update_like_list, liked_channel, sub_channel,download_and_extract_dlp
    global MediaControlOverlay,chrome_extension_flask,requests
    global shortcut_manager

    t = time.time()
    from utils.sub_and_like_public import update_sub_list, update_like_list, liked_channel, sub_channel
    log_handle(content=f"sub_and_like: {time.time()-t:.3f}s")
    
    # YT-DLP Update
    t = time.time()
    from utils.auto_ytdlp_update import download_and_extract_dlp
    log_handle(content=f"ytdlp_update: {time.time()-t:.3f}s")

    # Run version check
    t = time.time()
    init_ver_check()
    log_handle(content=f'ver_check: {time.time()-t:.3f}s')

    from system.win_shortcut_control import ShortcutManager
    shortcut_manager = ShortcutManager(app_user_model_id="Jackaopen.JaTubePlayer", main_path=os.path.abspath(__file__))
    shortcut_manager.create()

    # SMTC
    t = time.time()
    from system.SMTC import MediaControlOverlay
    log_handle(content=f"smtc: {time.time()-t:.3f}s")
    _init_load_smtc_obj()
    log_handle(content=f'smtc fin')

    # Requests
    t = time.time()
    import requests
    log_handle(content=f"requests: {time.time()-t:.3f}s")
    
        # Flask
    t = time.time()
    import chrome_extension.chrome_extension_flask as cef
    chrome_extension_flask = cef.ChromeExtensionServer(log_handle=log_handle)
    log_handle(content=f"flask: {time.time()-t:.3f}s")

    if CONFIG["run_flask"]:_switch_local_server(0)
    root.after(100, google_status_update)

    


def _start_up():
    """Background thread - ONLY for heavy I/O operations"""
    root.after(0, fullscreen_widget_change)
    _start_up_import()
    log_handle(content=f'Import fin')
    
    init_read_dlp()
    log_handle(content=f'dlp fin')

    init_star_vid_instance()
    log_handle(content=f'star vid fin')

    _init_load_extra_objs()
    log_handle(content=f'extra obj fin')
    
    init_read_api()
    log_handle(content=f'api fin')
    

    read_and_check_creditial()
    log_handle(content=f'creditial fin')

    init_read_config()
    log_handle(content=f'config fin')
    
    init_tree_view_quene()
    log_handle(content=f'treeview quene fin')
    
    check_keyboard()
    log_handle(content=f'keyboard fin')

    init_openwith_thread()
    log_handle(content=f'openwith fin')

   
    init_set_dnd_handle()
    log_handle(content=f'dnd fin')
    
    root.after(0, init_quick_startup)
    root.after_idle( _extra_startup_imports)
    log_handle(f"finish_big_init {time.time()-time1}")
    
    
    
if __name__ == '__main__':
    root.after(200,lambda:threading.Thread(daemon = True,target=dnd_path_listener).start())
    root.after(100,lambda:threading.Thread(daemon = True,target=load_thread).start())
    root.after(50,lambda:threading.Thread(daemon = True,target=start_async_eventloop).start())
    root.after(200,lambda:threading.Thread(daemon = True,target=fullscreen_detect_thread).start())
    root.after(850,lambda:threading.Thread(daemon = True,target=init_set_playertray).start())
    root.after(400,lambda:threading.Thread(daemon = True,target=full_screen_contorl_hover_thread).start())
    

    root.after(0,lambda:threading.Thread(daemon = True,target=_start_up).start())
    








sv_ttk.use_dark_theme() ### must be here or will overrider the style
style = ttk.Style()
style.configure("Treeview",
                rowheight=int(95*tkinter_scaling),
                font=("Arial", 12),
                fieldbackground="#1e1e1e",
                background="#1e1e1e",
                foreground="#c5c5c5")
style.map("Treeview",
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

title = ctk.CTkLabel(header_frame, text='🎵 JaTubePlayer', font=('Segoe UI', 20, 'bold'), 
                     text_color='#FF6B35', anchor="w")
title.place(relx=0.012, rely=0.19)

searchlistlabel = ctk.CTkLabel(header_frame, font=('Segoe UI', 13), text='🔍',
                               text_color='#888888', anchor="w", bg_color='transparent')
searchlistlabel.place(relx=0.148, rely=0.18)

searchentry = ctk.CTkEntry(header_frame, font=('Segoe UI', 13), corner_radius=8,
                           placeholder_text="Search YouTube...",
                           border_color="#3e62dc", border_width=1)
searchentry.place(relx=0.170, rely=0.17, relwidth=0.215, relheight=0.66)

search_btn = ctk.CTkButton(header_frame, text='🔎', corner_radius=8,
                           command=youtube_search, fg_color='#3e62dc', hover_color='#4a70f0',
                           font=('Segoe UI', 14))
search_btn.place(relx=0.391, rely=0.17, relwidth=0.028, relheight=0.66)

playlistlabel = ctk.CTkLabel(header_frame, font=('Segoe UI', 13), text='📁',
                             text_color='#888888', anchor="w", bg_color='transparent')
playlistlabel.place(relx=0.432, rely=0.18)

userplaylistcombobox = ctk.CTkComboBox(header_frame, font=('Segoe UI', 13),
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
                                   command=enterplaylist, fg_color='#FF6B35', hover_color='#FF8555',
                                   corner_radius=8, font=('Segoe UI', 12, 'bold'))
enter_playlist_btn.place(relx=0.591, rely=0.17, relwidth=0.062, relheight=0.66)

searchentry.bind("<Return>", youtube_search)
userplaylistcombobox.bind("<Return>", enterplaylist)



# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE STATUS PANEL - Combined Chrome Extension & Discord Status
# ═══════════════════════════════════════════════════════════════════════════════
status_panel = ctk.CTkFrame(header_frame, fg_color="#151515", corner_radius=6, 
                            border_width=1, border_color="#3e62dc")
status_panel.place(relx=0.665, rely=0.09, relwidth=0.328, relheight=0.82)

chrome_ext_dot = ctk.CTkLabel(status_panel, text='●', font=('Arial', 14),
                               text_color='#333333')
chrome_ext_dot.place(relx=0.031, rely=0.168, relheigh = 0.7)

chrome_ext_text = ctk.CTkLabel(status_panel, text='Chrome Link', 
                                font=('Segoe UI', 12), text_color='#777777', anchor="w")
chrome_ext_text.place(relx=0.083, rely=0.158, relheigh = 0.7)



separator = ctk.CTkLabel(status_panel, text='│', font=('Segoe UI', 18), text_color='#444444')
separator.place(relx=0.296, rely=0.149, relheigh = 0.7)

discord_status_dot = ctk.CTkLabel(status_panel, text='●', font=('Arial', 14),
                                   text_color='#333333')
discord_status_dot.place(relx=0.345, rely=0.168, relheigh = 0.7)

discord_status_text = ctk.CTkLabel(status_panel, text='Discord', 
                                    font=('Segoe UI', 12), text_color='#777777', anchor="w")
discord_status_text.place(relx=0.397, rely=0.158, relheigh = 0.7)


separator2 = ctk.CTkLabel(status_panel, text='│', font=('Segoe UI', 18), text_color='#444444')
separator2.place(relx=0.540, rely=0.149, relheigh = 0.7)

# Google Profile Container - styled circular frame for profile picture


google_status_profile_pic_label = ctk.CTkLabel(status_panel, text='X', font=('Segoe UI', 14),
                                               text_color='#555555', fg_color="transparent", 
                                               width=15, height=26, corner_radius=13)
google_status_profile_pic_label.place(relx=0.66, rely=0.5, anchor="center", relheigh = 0.85)

google_status_text = ctk.CTkTextbox(status_panel, 
                                   font=('Segoe UI', 12), text_color='#888888', wrap="none",
                                   border_width=0, height=1,fg_color="transparent", activate_scrollbars=False)
google_status_text.place(relx=0.715, rely=0.05, relwidth=0.27, relheigh = 0.85)
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

@check_internet_silent
def google_status_update():
    def _google_status_update():
        try:
            ui_queue.put(lambda: google_status_text.configure(state='normal'))
            ui_queue.put(lambda: google_status_text.delete(1.0, tk.END))
            if credentials:
                acc_info = google_control.get_userinfo(credentials)

                if acc_info and 'picture' in acc_info:
                    pic_url = acc_info['picture']
                    response = requests.get(pic_url)
                    profile_pic = Image.open(io.BytesIO(response.content))
                    profile_pic = profile_pic.resize((34,34), Image.LANCZOS)
                    ctk_image = ctk.CTkImage(profile_pic, size=(34, 34))
                    ui_queue.put(lambda img=ctk_image: google_status_profile_pic_label.configure(
                        image=img, 
                        text=''
                    ))
                    # Update container border to green for logged in(
                    ui_queue.put(lambda n=acc_info.get('name','Unknown'): google_status_text.insert(tk.END, f"{n}"))
                    ui_queue.put(lambda: google_status_text.configure(text_color='#C79842'))
                else:
                    ui_queue.put(lambda: google_status_profile_pic_label.configure(text='', text_color='#555555'))
                    ui_queue.put(lambda: google_status_text.insert(tk.END, 'No info'))
                    ui_queue.put(lambda: google_status_text.configure(text_color='#AAAAAA'))
            else:
                ui_queue.put(lambda: google_status_profile_pic_label.configure(text='✕', text_color='#555555', font=('Segoe UI', 16, 'bold'),image=None))
                ui_queue.put(lambda: google_status_text.insert(tk.END, 'Not logged in'))
                ui_queue.put(lambda: google_status_text.configure(text_color='#AAAAAA'))
        except Exception as e:
            log_handle(f"Google status update error: {e}")
            ui_queue.put(lambda: google_status_profile_pic_label.configure(text='⚠', text_color='#FFB347'))
            ui_queue.put(lambda: google_status_text.insert(tk.END, 'Error'))
            ui_queue.put(lambda: google_status_text.configure(text_color='#FFB347'))
        finally:ui_queue.put(lambda: google_status_text.configure(state='disabled'))

    
    threading.Thread(target=_google_status_update, daemon=True).start()

# ─────────────────────────────────────────────────────────────────────────────
# RIGHT PANEL - Playlist Treeview & Mode Info
# ─────────────────────────────────────────────────────────────────────────────
right_panel_frame = ctk.CTkFrame(root, fg_color="#1e1e1e", corner_radius=10, border_width=1, border_color="#333333")
right_panel_frame.place(relx=0.618, rely=0.070, relwidth=0.377, relheight=0.560)

mode_header_frame = ctk.CTkFrame(right_panel_frame, fg_color="#252525", corner_radius=8)
mode_header_frame.place(relx=0.020, rely=0.010, relwidth=0.960, relheight=0.105)

mode_icon_label = ctk.CTkLabel(mode_header_frame, text='📋', font=('Segoe UI', 18))
mode_icon_label.place(relx=0.021, rely=0.18)

modetextbox = tk.Text(mode_header_frame, font=('Segoe UI', 11), width=65, fg='#c5c5c5',
                      bg='#252525', relief='flat', height=2, wrap='char', borderwidth=0)
modetextbox.place(relx=0.095, rely=0)
modetextbox.insert(tk.END, 'Please login or search something')
modetextbox.configure(state='disabled')



# Playlist Treeview
playlisttreebox = ttk.Treeview(right_panel_frame, columns=("title"), height=4, 
                               selectmode="browse", show='tree')
playlisttreebox.heading("#0", text="")
playlisttreebox.heading("title", text="")
playlisttreebox.column("#0", width=180, anchor="w", stretch=False)
playlisttreebox.column("title", width=1000, anchor="w", stretch=False)
playlisttreebox.place(relx=0.020, rely=0.125, relwidth=0.925, relheight=0.838)
playlisttreebox.bind('<Double-1>', download_and_play)
playlisttreebox.bind('<ButtonRelease-1>', get_selected_vid)

Y_scrollbar = ttk.Scrollbar(right_panel_frame)
X_scrollbar = ttk.Scrollbar(right_panel_frame, orient='horizontal')
X_scrollbar.configure(command=playlisttreebox.xview)
Y_scrollbar.configure(command=playlisttreebox.yview)
playlisttreebox.configure(xscrollcommand=X_scrollbar.set, yscrollcommand=Y_scrollbar.set)
Y_scrollbar.place(relx=0.945, rely=0.125, relheight=0.838)
X_scrollbar.place(relx=0.020, rely=0.963, relwidth=0.925)

playlist_btn_frame = ctk.CTkFrame(root, fg_color="#1e1e1e", border_color="#333333", border_width=1, corner_radius=10)
playlist_btn_frame.place(relx=0.618, rely=0.63, relwidth=0.377, relheight=0.13)

# Hero action button
playselectedsong = ctk.CTkButton(playlist_btn_frame, text='▶ Play',
                                  command=lambda: download_and_play(), fg_color='#3e62dc',
                                  hover_color='#4a70f0', corner_radius=8, font=('Segoe UI', 13, 'bold'))
playselectedsong.place(relx=0.212, rely=0.54, relwidth=0.19, relheight=0.33)

# Source buttons in a compact row
_src_w = 0.187
_src_gap = 0.008
recommendation_btn = ctk.CTkButton(playlist_btn_frame, text='✨Recommed',
                                    command=lambda: threading.Thread(daemon=True, target=init_get_recommendation).start(),
                                    fg_color='#2E2E2E', hover_color='#404040', corner_radius=6,
                                    font=('Segoe UI', 11), border_width=1, border_color='#444444')
recommendation_btn.place(relx=0.020, rely=0.1, relwidth=_src_w, relheight=0.33)

load_star_btn = ctk.CTkButton(playlist_btn_frame, text='★ Star',
                        command= lambda :threading.Thread(daemon=True, target=get_starred_vid).start(), fg_color='#2E2E2E', hover_color='#404040',
                        corner_radius=6, font=('Segoe UI', 11), border_width=1, border_color='#444444')
load_star_btn.place(relx=0.020, rely=0.54, relwidth=_src_w, relheight=0.33)

sub_btn = ctk.CTkButton(playlist_btn_frame, text='📺Subcription',
                        command=lambda: get_sub_channel(0), fg_color='#2E2E2E', hover_color='#404040',
                        corner_radius=6, font=('Segoe UI', 11), border_width=1, border_color='#444444')
sub_btn.place(relx=0.020+(_src_w+_src_gap)*1, rely=0.1, relwidth=_src_w, relheight=0.33)

like_btn = ctk.CTkButton(playlist_btn_frame, text='❤ Like',
                         command=lambda: get_liked_vid(0), fg_color='#2E2E2E', hover_color='#404040',
                         corner_radius=6, font=('Segoe UI', 11), border_width=1, border_color='#444444')
like_btn.place(relx=0.020+(_src_w+_src_gap)*2, rely=0.1, relwidth=_src_w, relheight=0.33)

playselectedfile = ctk.CTkButton(playlist_btn_frame, text='📄 File',
                                  command=lambda: load_local_files(0), fg_color='#2E2E2E',
                                  hover_color='#404040', corner_radius=6, font=('Segoe UI', 11),
                                  border_width=1, border_color='#444444')
playselectedfile.place(relx=0.020+(_src_w+_src_gap)*3, rely=0.1, relwidth=_src_w, relheight=0.33)

playselectedfolder = ctk.CTkButton(playlist_btn_frame, text='📁 Folder',
                                    command=lambda: load_local_files(1), fg_color='#2E2E2E',
                                    hover_color='#404040', corner_radius=6, font=('Segoe UI', 11),
                                    border_width=1, border_color='#444444')
playselectedfolder.place(relx=0.020+(_src_w+_src_gap)*4, rely=0.1, relwidth=_src_w, relheight=0.33)

# Page navigation
page_nav_frame = ctk.CTkFrame(playlist_btn_frame, fg_color="#262626", corner_radius=8)
page_nav_frame.place(relx=_src_w*2+_src_gap*2+0.02, rely=0.52, relwidth=_src_w*3+_src_gap*2, relheight=0.38)

prev_page_btn = ctk.CTkButton(page_nav_frame, text='◀ Prev',
                               command=lambda: page_control(2), fg_color='#2E2E2E', hover_color='#404040',
                               corner_radius=8, font=('Segoe UI', 12), border_width=1, border_color='#444444')
prev_page_btn.place(relx=0.02, rely=0.116, relwidth=0.28, relheight=0.767)

next_page_btn = ctk.CTkButton(page_nav_frame, text='Next ▶',
                               command=lambda: page_control(1), fg_color='#2E2E2E', hover_color='#404040',
                               corner_radius=8, font=('Segoe UI', 12), border_width=1, border_color='#444444')
next_page_btn.place(relx=0.32, rely=0.116, relwidth=0.28, relheight=0.767)

liked_page_label = ctk.CTkLabel(page_nav_frame, font=('Segoe UI', 13), text='📄',
                                anchor="w", fg_color="transparent")
liked_page_label.place(relx=0.630 ,rely=0.15)

page_num_label = ctk.CTkLabel(page_nav_frame, font=('Segoe UI', 13), text='',
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

np_icon = ctk.CTkLabel(now_playing_frame, text='🎶', font=('Segoe UI', 16))
np_icon.place(relx=0.008, rely=0.14)

playing_title_textbox = tk.Text(now_playing_frame, font=('Segoe UI Semibold', 14), width=130, fg='#c5c5c5',
                                bg='#1c1c1c', relief='flat', wrap='word', state='disabled',
                                height=1, borderwidth=0)
playing_title_textbox.place(relx=0.035, rely=0.15)

# ── Progress Bar ──
progress_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
progress_frame.place(relx=0.008, rely=0.405, relwidth=0.984, relheight=0.230)

player_pos_label = ctk.CTkLabel(progress_frame, font=('Segoe UI Variable Display Semib', 14),
                                textvariable=pos_for_label, text_color="#7d9bff", anchor="e")
player_pos_label.place(relx=0, rely=0.03, relwidth=0.050)

player_position_scale = ctk.CTkSlider(progress_frame, from_=0, command=scale_click,
                                       progress_color='#3e62dc', button_color='#5080ff',
                                       button_hover_color='#6090ff', fg_color='#333333')
player_position_scale.set(0)
player_position_scale.bind('<ButtonRelease-1>', scale_release)
player_position_scale.place(relx=0.055, rely=0.12, relwidth=0.850, relheight=0.50)

player_song_length_label = ctk.CTkLabel(progress_frame, font=('Segoe UI Variable Display Semib', 14),
                                         text_color="#9E9E9E", anchor="w", text='')
player_song_length_label.place(relx=0.922, rely=0.03, relwidth=0.068)


# ── Transport Row: Mode | Playback | Volume | Actions ──
mode_frame = ctk.CTkFrame(controls_frame, fg_color="#1c1c1c", corner_radius=10)
mode_frame.place(relx=0.008, rely=0.585, relwidth=0.132, relheight=0.375)

mode_label = ctk.CTkLabel(mode_frame, text='Mode', font=('Segoe UI', 12), text_color="#6A6969")
mode_label.place(relx=0.06, rely=0.07)

player_mode_continue = ctk.CTkRadioButton(mode_frame, text='▶▶', variable=player_mode_selector,
                                           value='continue', 
                                           font=('Segoe UI', 11), radiobutton_width=16, radiobutton_height=16)
player_mode_continue.place(relx=0.06, rely=0.45)

player_mode_replay = ctk.CTkRadioButton(mode_frame, text='🔁', variable=player_mode_selector,
                                         value='replay', 
                                         font=('Segoe UI', 11), radiobutton_width=16, radiobutton_height=16)
player_mode_replay.place(relx=0.39, rely=0.45)

player_mode_random = ctk.CTkRadioButton(mode_frame, text='🔀', variable=player_mode_selector,
                                         value='random', 
                                         font=('Segoe UI', 11), radiobutton_width=16, radiobutton_height=16)
player_mode_random.place(relx=0.72, rely=0.45)

playback_frame = ctk.CTkFrame(controls_frame, fg_color="#1c1c1c", corner_radius=20)
playback_frame.place(relx=0.150, rely=0.585, relwidth=0.43, relheight=0.375)

prevsong = ctk.CTkButton(playback_frame, text='⏮', command=playprevsong,
                         fg_color='transparent', hover_color='#333333', corner_radius=20,
                         font=('Segoe UI', 17))
prevsong.place(relx=0.02, rely=0.08, relwidth=0.15, relheight=0.8)

pausebutton = ctk.CTkButton(playback_frame, textvariable=pauseStr,
                            command=lambda: pause(1), fg_color='#3e62dc', hover_color='#4a70f0',
                            corner_radius=20, font=('Segoe UI', 17, 'bold'))
pausebutton.place(relx=0.18, rely=0.08, relwidth=0.15, relheight=0.8)
pauseStr.set('▶')

stopbutton = ctk.CTkButton(playback_frame, text='⏹', command=stop_playing_video,
                           fg_color='transparent', hover_color='#333333', corner_radius=20,
                           font=('Segoe UI', 17))
stopbutton.place(relx=0.34, rely=0.08, relwidth=0.15, relheight=0.8)

nextsong = ctk.CTkButton(playback_frame, text='⏭', command=playnextsong,
                         fg_color='transparent', hover_color='#333333', corner_radius=20,
                         font=('Segoe UI', 17))
nextsong.place(relx=0.50, rely=0.08, relwidth=0.15, relheight=0.8)

# make fullscreen button match the other transport controls (transparent background, same corner radius/font)
fullscreenbtn = ctk.CTkButton(playback_frame, text='⛶', command=fullscreen_change_state,
                               fg_color='transparent', hover_color='#333333', corner_radius=20,
                               font=('Segoe UI', 17))
# slightly narrower so it doesn't crowd the playback buttons
fullscreenbtn.place(relx=0.66, rely=0.08, relwidth=0.15, relheight=0.8)

player_loading_label = ctk.CTkLabel(playback_frame, font=('Segoe UI', 12), text='',
                                     text_color='#FF6B35', anchor="center",
                                     fg_color="transparent")
player_loading_label.place(relx=0.81, rely=0.25, relwidth=0.18)

volume_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
volume_frame.place(relx=0.635, rely=0.605, relwidth=0.105, relheight=0.350)

player_volume_label = ctk.CTkLabel(volume_frame, font=('Segoe UI', 16), text='🔊',
                                   text_color='#888888', anchor="e")
player_volume_label.place(relx=0, rely=0.2, relwidth=0.120)

player_volume_scale = ctk.CTkSlider(volume_frame, from_=0, to=120, command=set_volume,
                                    progress_color='#FF6B35', button_color='#FF8555',
                                    button_hover_color='#FFA575', fg_color='#333333')
player_volume_scale.set(50)
player_volume_scale.bind('<MouseWheel>', set_volume_wheel)
player_volume_scale.place(relx=0.180, rely=0.35, relwidth=0.780, relheight=0.3)

Frame_for_mpv.bind('<MouseWheel>', set_volume_wheel)

# ── Action Buttons ──
action_btn_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
action_btn_frame.place(relx=0.745, rely=0.585, relwidth=0.300, relheight=0.375)

setting_btn = ctk.CTkButton(action_btn_frame, text='⚙️ Settings', command=setting_frame,
                            fg_color='#FF6B35', hover_color='#FF8555', corner_radius=8,
                            font=('Segoe UI', 13, 'bold'))
setting_btn.place(relx=0, rely=0.06, relwidth=0.255, relheight=0.88)

star_btn = ctk.CTkButton(action_btn_frame, text='☆', command=switch_starred_vid,
                            fg_color='#3A3A3A', hover_color='#505050', text_color='#B0B0B0',
                            corner_radius=8, font=('Segoe UI', 13, 'bold'))
star_btn.place(relx=0.270, rely=0.06, relwidth=0.175, relheight=0.88)


select_info_btn = ctk.CTkButton(action_btn_frame, text='ℹ️ Sel',
                                 command=lambda: vid_info_frame(1), fg_color='#2E2E2E',
                                 hover_color='#404040', corner_radius=8, font=('Segoe UI', 11),
                                 border_width=1, border_color='#444444')
select_info_btn.place(relx=0.460, rely=0.06, relwidth=0.175, relheight=0.88)

playing_info_btn = ctk.CTkButton(action_btn_frame, text='📊 Now',
                                  command=lambda: vid_info_frame(2), fg_color='#2E2E2E',
                                  hover_color='#404040', corner_radius=8, font=('Segoe UI', 11),
                                  border_width=1, border_color='#444444')
playing_info_btn.place(relx=0.650, rely=0.06, relwidth=0.175, relheight=0.88)





root.bind('<Escape>', fullscreen_change_state)
root.bind('<space>', lambda event: pause(2))
root.bind("<KeyPress-Left>", lambda event: set_position_keyboard(1))
root.bind("<KeyPress-Right>", lambda event: set_position_keyboard(2))
root.bind("<KeyRelease-Right>", arrow_release)
root.bind("<KeyRelease-Left>", arrow_release)




root.mainloop()
