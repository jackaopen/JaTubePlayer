import time

from customtkinter.windows.widgets import image
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
import ctypes
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
#print(_internal_dir)


os.environ["PATH"] = _internal_dir + os.pathsep + os.environ["PATH"]
import mpv
#### remember to add yt_dlp.exe from github to _iternal!!!
root = ctk.CTk()
ver='2.0'
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
    root.after(10, _process_ui_queue)
root.after(10, _process_ui_queue)

messagebox = ctk_messagebox(root)

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
    
    
    if errtype == 'error' and 'ytdl_hook' in component.lower():
        error_msg = str(content.lower())
        if "this live event will" in error_msg:
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
Frame_for_mpv.place(relx=0.015, rely=0.096, relwidth=0.587, relheight=0.640)
Frame_for_mpv.bind('<Button-1>',lambda event :pause(1))

# ==== 播放器控制 ====
player = None
stream = False
playing_vid_mode = 0 #0 =youtube 1 = single/openwith 2 = folder 3=chrome
playing_vid_info_dict = ''
selected_song_number = None
yt_dlp = None
youtube = None
playlisttitles = []
playlist_thumbnails = []
playlist_channel = []
user_playlists_name = []
load_thread_queue = queue.Queue()
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
chrome_extension_url = None
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

enable_discord_presence = tk.BooleanVar()
discord_presence_show_playing = tk.BooleanVar()



# ==== 系統相關 ====
credentials = None
cookies_dir = None
client_secret_path = None

# ==== config ====


def save_config():
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
    global selected_song_number
    selected_song_number = playlisttreebox.index(playlisttreebox.selection()[0])


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

        try:
            listen_chromeextension_thread.join()

            res = requests.post('http://localhost:5000/Shutdown',headers={'X-auth':'Jatubeplayerextensionbyjackaopen','X-icon':icondir},timeout=1)
            log_handle(content=str(res.text))
            if res.text == 'ok':
                
                setting_run_chrome_extension_server.set(False)
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
        if playing_vid_mode == 0:
            async with session.get(thumburl) as response:
                imgdata = await response.read()
                img = Image.open(io.BytesIO(imgdata))
                img = img.resize((140, 105), Image.LANCZOS)
                img1 = img.crop((0,14,140,90))
                thumbnailpic = ImageTk.PhotoImage(img1)
                temp.append(thumbnailpic)
                ui_queue.put(lambda id=id, pic=thumbnailpic: playlisttreebox.item(id, image=pic))
    except Exception as e:
        log_handle(content=str(e))



@check_internet
def vid_info_frame(mode):## 1 = selextd ;2 = playing
    global info
    print(f"info frame mode: {info}")
    try:
        if info and info.winfo_exists():
            info.lift()
            info.deiconify()
        else:raise Exception("info window already opened")
    except:
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
            try:
                if playing_vid_mode == 0:
                    
                    if selected_song_number != None:
                        

                        try:
                            opt = {'quiet': True, 
                                   'skip_download':True,
                                   "extract_flat": True,
                                   'ignore_no_formats_error': True} 
                            if cookies_dir:
                                opt['cookiefile'] = cookies_dir
                                
                            with yt_dlp.YoutubeDL(opt) as ydl:
                                ui_queue.put(lambda: title_text.configure(state='normal'))
                                ui_queue.put(lambda: title_text.insert(tk.END,f'loading . . .'))
                                ui_queue.put(lambda: title_text.configure(state='disabled'))


                                info_dict = ydl.extract_info(vid_url[selected_song_number], download=False)

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


                    else:
                        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','please select a video first'))
                        ui_queue.put(lambda: info.destroy())
                else:
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','The function is not available under file selection'))
                    ui_queue.put(lambda: info.destroy())
            except googleapiclient.errors.HttpError as err: ######  handle stupid api
                ui_queue.put(lambda e=err: messagebox.showerror(f'JaTubePlayer {ver}', f"An error occurred: {e}"))
                ui_queue.put(lambda: info.destroy())

        def loadplayinginfo():
            if playing_vid_mode == 0 or playing_vid_mode == 3:
                if playing_vid_info_dict:
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


                else:
                    ui_queue.put(lambda: info.destroy())
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','please play a video first!'))
            else:
                ui_queue.put(lambda: info.destroy())
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','The function is not available under file selection'))
                

        if mode == 1:
            infothread = threading.Thread(daemon = True,target=loadselectedinfo)
            infothread.start()
        elif mode == 2 :
            infothread = threading.Thread(daemon = True,target=loadplayinginfo)
            infothread.start()
        info.mainloop()
        


def setting_frame():
    global setting_api_entry,maxresolutioncombobox,setting,setting_closed,init_playlist_combobox
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
            print('google login setting called')
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
            if playing_vid_mode == 0:
                try:
                    if selected_song_number != None:
                        ui_queue.put(lambda: resolution_title.configure(text='⏳ Loading resolutions...'))
                        res = get_resoltion(vid_url[selected_song_number])
                        ui_queue.put(lambda r=res: resoltion_combox.configure(values=r))
                        ui_queue.put(lambda: resoltion_combox._open_dropdown_menu())
                        ui_queue.put(lambda: resolution_title.configure(text='Video Resolution'))
                    else:
                        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','selected a video first'))

                except Exception as e:log_handle(content=str(e))
            elif playing_vid_mode == 3:
                try:
                    ui_queue.put(lambda: resolution_title.configure(text='⏳ Loading resolutions...'))
                    res = get_resoltion(chrome_extension_url)
                    ui_queue.put(lambda r=res: resoltion_combox.configure(values=r))
                    ui_queue.put(lambda: resoltion_combox._open_dropdown_menu())
                    ui_queue.put(lambda: resolution_title.configure(text='Video Resolution'))

                except Exception as e :log_handle(content=str(e))
                
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
                if playing_vid_mode == 0 or playing_vid_mode == 3:
                    
                    if formats.get() == 0:
                        ui_queue.put(lambda: downloadselectedsong.configure(state = "disabled"))
                        download_to_local(res=0,
                                        mode=formats.get(),
                                        cookies_dir=cookies_dir,
                                        yt_dlp=yt_dlp,
                                        target_vid_url=vid_url[selected_song_number] if playing_vid_mode ==0 else chrome_extension_url,
                                        playing_vid_mode=playing_vid_mode,
                                        target_playlisttitle=playlisttitles[selected_song_number]if playing_vid_mode ==0 else '',
                                        current_dir=current_dir,
                                        icondir=icondir,
                                        info_dict=playing_vid_info_dict,
                                        ver=ver,
                                        chrome_extension_url=chrome_extension_url,
                                        root=root,
                                        ffmpeg=ffmpeg,
                                        ytdlp_log_handle=ytdlp_log_handle,
                                        is_downloading = is_downloading,
                                        deno_path=deno_exe,
                                        ctk_messagebox=messagebox
                                        )
                        ui_queue.put(lambda: is_downloading.set(True))
                        
                        time.sleep(2)
                        ui_queue.put(lambda: downloadselectedsong.configure(state = "normal"))
                    elif formats.get() == 1:
                        if resoltion_combox.get() != '' and resoltion_combox.get().isdigit() and int(resoltion_combox.get()) >=144:
                                ui_queue.put(lambda: downloadselectedsong.configure(state = "disabled"))
                                download_to_local(
                                    res=resoltion_combox.get(),
                                    mode=formats.get(),
                                    cookies_dir=cookies_dir,
                                    yt_dlp=yt_dlp,
                                    target_vid_url=vid_url[selected_song_number] if  playing_vid_mode == 0 else chrome_extension_url,
                                    playing_vid_mode=playing_vid_mode,
                                    target_playlisttitle=playlisttitles[selected_song_number] if playing_vid_mode ==0 else '',
                                    current_dir=current_dir,
                                    icondir=icondir,
                                    info_dict=playing_vid_info_dict,
                                    ver=ver,
                                    chrome_extension_url=chrome_extension_url,
                                    root=root,   
                                    ffmpeg=ffmpeg,
                                    ytdlp_log_handle=ytdlp_log_handle,
                                    is_downloading = is_downloading,
                                    deno_path=deno_exe,
                                    ctk_messagebox=messagebox
                                        )
                                ui_queue.put(lambda: is_downloading.set(True))
                                time.sleep(2)
                                ui_queue.put(lambda: downloadselectedsong.configure(state = "normal"))
                        else:ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please select resolution or enter a valid number\nmust >= 144 '))
                    else:ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','Please select resolution and format first'))
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
                liked_page_num_label.configure(text='')
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

        def subtitle_combobox_callback(event):
            subtitle_selection_idx.set(subtitlecombobox.cget('values').index(subtitlecombobox.get()))
            print(f'selected subtitle idx{subtitle_selection_idx.get()}')
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
                player.speed = player_speed.get()
            except:pass
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


        # Create organized frames for personal playlist settings
        youtube_data_frame = ctk.CTkFrame(personal_playlist_tab, fg_color='#2E2E2E')
        youtube_data_frame.grid_columnconfigure(0, weight=1)
        youtube_data_frame.grid_columnconfigure(1, weight=1)
        
        history_frame = ctk.CTkFrame(personal_playlist_tab, fg_color='#2E2E2E')
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_columnconfigure(1, weight=1)
        
        # YouTube Data Section
        youtube_title = ctk.CTkLabel(youtube_data_frame , text="YouTube Data Management", font=('Arial', 14, 'bold'), text_color='white')
        updatelike_btn = ctk.CTkButton(youtube_data_frame, text='Update Liked Videos', width=160, command=lambda:threading.Thread(daemon=True,target=update_like_list_local).start(), text_color='white', font=('Arial', 13, 'bold'))
        auto_like_refresh_checkbtn = ctk.CTkCheckBox(youtube_data_frame, text='Auto-update liked videos', variable=auto_like_refresh, command=setting_auto_like_refresh, fg_color='#242424', text_color='white')
        
        updatesub_btn = ctk.CTkButton(youtube_data_frame, text='Update Subscriptions', width=160, command=lambda:threading.Thread(daemon=True,target=update_sub_list_local).start(), text_color='white', font=('Arial', 13, 'bold'))
        auto_sub_refresh_checkbtn = ctk.CTkCheckBox(youtube_data_frame, text='Auto-update subscriptions', variable=auto_sub_refresh, command=setting_auto_sub_refresh, fg_color='#242424', text_color='white')
        
        updateuserplaylists_btn = ctk.CTkButton(youtube_data_frame, text='Update Playlists', width=160, command=updateplaylists, text_color='white', font=('Arial', 13, 'bold'))
        
        # History Management Section
        history_title = ctk.CTkLabel(history_frame, text="History Management", font=('Arial', 14, 'bold'), text_color='white')
        record_history_btn = ctk.CTkCheckBox(history_frame, text='Record playback history', variable=save_history, command=save_his_and_rec_option, fg_color='#242424', text_color='white')
        reset_history_btn = ctk.CTkButton(history_frame, text='Reset History', width=160, command=reset_history_setting, text_color='white', font=('Arial', 13, 'bold'))

        auth_scrollable_frame = ctk.CTkScrollableFrame(Authentication_tab, width=680, height=400,fg_color='#242424')
        auth_scrollable_frame.grid(row=0, column=0)

        # Google Frame
        google_frame = ctk.CTkFrame(auth_scrollable_frame, fg_color='#2E2E2E')
        google_frame.grid_columnconfigure(0, weight=1)
        google_frame.grid_columnconfigure(1, weight=1) 
        google_frame.grid(row=0, column=0, pady=5, sticky="ew")

        google_title = ctk.CTkLabel(google_frame, text="Google Account\n*API & Client Secret required", font=('Arial', 14, 'bold'), text_color='white')
        googlelogin_btn = ctk.CTkButton(google_frame,text=f'Login Google',width=200,command=lambda : threading.Thread(daemon=True,target=lambda:google_login_setting(0)).start(),text_color='white', font=('Arial', 13, 'bold'))
        googlelogout_btn = ctk.CTkButton(google_frame,text=f'Logout Google',width=200,command=google_logout_setting,text_color='white', font=('Arial', 13, 'bold'))
        deletesyskey_btn = ctk.CTkButton(google_frame,text='Delete system key',width=200,command=deletesyskey,text_color='white', font=('Arial', 13, 'bold'))
        googleaccountname_text = ctk.CTkTextbox(google_frame,font=('Arial', 13, 'bold'),state='disabled',fg_color='#242424',text_color='white',height=1)

        googleaccountname_text.grid(row=1, column=0, padx=10, pady=10,columnspan=3, sticky="ew")
        googlelogin_btn.grid(row=2, column=0, padx=10, pady=10)
        googlelogout_btn.grid(row=2, column=1, padx=10, pady=10)
        deletesyskey_btn.grid(row=2, column=2, padx=10, pady=10)
        google_title.grid(row=0, column=0, columnspan=3, padx=10, pady=(5,10), sticky="nsew")
        
        # API Frame
        api_frame = ctk.CTkFrame(auth_scrollable_frame, fg_color='#2E2E2E')
        api_frame.grid_columnconfigure(0, weight=1)
        api_frame.grid_columnconfigure(1, weight=1)
        api_frame.grid_columnconfigure(2, weight=1)
        
        api_title = ctk.CTkLabel(api_frame, text="API", font=('Arial', 14, 'bold'), text_color='white')
        deleteapi_btn = ctk.CTkButton(api_frame,text='Delete stored api',width=200,command=deleteapi,text_color='white', font=('Arial', 13, 'bold'))
        setting_api_label = ctk.CTkLabel(api_frame,font=('Arial', 13, 'bold'),text='youtube API:',text_color='white')
        setting_api_entry = ctk.CTkEntry(api_frame,font=('arial 13',13,'bold'),width=160,text_color='lightgray',placeholder_text="Enter API here")
        set_api_btn = ctk.CTkButton(api_frame,text='Enter youtube API',width=200,command=enter_youtube_api,text_color='white', font=('Arial', 13, 'bold'))    
        apilabel = ctk.CTkLabel(api_frame,font=('Arial', 13, 'bold'),text='None',text_color='white')

        api_title.grid(row=0, column=0, columnspan=3, padx=10, pady=(10,5), sticky="nsew")
        setting_api_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        setting_api_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        set_api_btn.grid(row=2, column=2, padx=10, pady=5, sticky="w")
        deleteapi_btn.grid(row=2, column=1, padx=10, pady=(5,10), sticky="ew")
        apilabel.grid(row=1, column=2, padx=10, pady=(5,10), sticky="w")
        api_frame.grid(row=1, column=0, pady=5, sticky="ew")

        # Cookie Frame
        cookie_frame = ctk.CTkFrame(auth_scrollable_frame, fg_color='#2E2E2E')
        cookie_frame.grid_columnconfigure(0, weight=1)
        cookie_frame.grid_columnconfigure(1, weight=1)
        cookie_frame.grid_columnconfigure(2, weight=1)
        
        cookie_title = ctk.CTkLabel(cookie_frame, text="Cookie", font=('Arial', 14, 'bold'), text_color='white')
        setting_cookie_label = ctk.CTkLabel(cookie_frame,font=('Arial', 13, 'bold'),text='Cookie:',text_color='white')
        insert_cookie_btn = ctk.CTkButton(cookie_frame,text='Select cookie',width=200,command=read_cookie_setting,text_color='white', font=('Arial', 13, 'bold'))
        deletecookie_btn = ctk.CTkButton(cookie_frame,text='remove stored cookie',width=200,command=delete_cookie,text_color='white', font=('Arial', 13, 'bold'))
        cookiepath_text = ctk.CTkTextbox(cookie_frame,font=('Arial', 13, 'bold'),height=25,text_color='white')
        cookiepath_text.configure(state='disabled')

        cookie_title.grid(row=0, column=0, columnspan=3, padx=10, pady=(10,5), sticky="nsew")
        setting_cookie_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        cookiepath_text.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        insert_cookie_btn.grid(row=2, column=1, padx=10, pady=(5,10), sticky="ew")
        deletecookie_btn.grid(row=2, column=2, padx=10, pady=(5,10), sticky="w")
        cookie_frame.grid(row=2, column=0, pady=5, sticky="ew")

        # Client Secrets Frame
        client_secrets_frame = ctk.CTkFrame(auth_scrollable_frame, fg_color='#2E2E2E')
        client_secrets_frame.grid_columnconfigure(0, weight=1)
        client_secrets_frame.grid_columnconfigure(1, weight=1)
        client_secrets_frame.grid_columnconfigure(2, weight=1)
    
        client_secrets_title = ctk.CTkLabel(client_secrets_frame, text="Client Secrets", font=('Arial', 14, 'bold'), text_color='white')
        setting_client_secret_label = ctk.CTkLabel(client_secrets_frame,font=('Arial', 13, 'bold'),text='client secrets:',text_color='white')
        insert_client_secrets_btn = ctk.CTkButton(client_secrets_frame,text='Select client secret',width=200,command=read_client_secret_setting,text_color='white', font=('Arial', 13, 'bold'))
        deleteclient_secrets_btn = ctk.CTkButton(client_secrets_frame,text='remove stored client secret',width=200,command=delete_client_secrets,text_color='white', font=('Arial', 13, 'bold'))
        client_secrets_text = ctk.CTkTextbox(client_secrets_frame,font=('Arial', 13, 'bold'),height=1,text_color='white',wrap="none",activate_scrollbars=False)
        client_secrets_text.configure(state='disabled')

        client_secrets_title.grid(row=0, column=0, columnspan=3, padx=10, pady=(10,5), sticky="nsew")
        setting_client_secret_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        client_secrets_text.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        insert_client_secrets_btn.grid(row=2, column=1, padx=10, pady=(5,10), sticky="ew")
        deleteclient_secrets_btn.grid(row=2, column=2, padx=10, pady=(5,10), sticky="w")
        client_secrets_frame.grid(row=3, column=0, pady=5, sticky="ew")


        # Create organized frames for download section
        download_info_frame = ctk.CTkFrame(download_tab, fg_color='#2E2E2E')
        download_info_frame.grid_columnconfigure(0, weight=1)
        
        format_frame = ctk.CTkFrame(download_tab, fg_color='#2E2E2E')
        format_frame.grid_columnconfigure(0, weight=1)
        format_frame.grid_columnconfigure(1, weight=1)
        
        resolution_frame = ctk.CTkFrame(download_tab, fg_color='#2E2E2E')
        resolution_frame.grid_columnconfigure(0, weight=1)
        resolution_frame.grid_columnconfigure(1, weight=1)
        
        # Video Info Section
        info_title = ctk.CTkLabel(download_info_frame, text="Selected Video", font=('Arial', 14, 'bold'), text_color='white')
        download_seleted_title_text = ctk.CTkTextbox(download_info_frame, font=('Arial', 14, 'bold'), width=650, height=60, fg_color='#1a1a1a', text_color='lightgray')
        download_seleted_title_text.configure(state='disabled')
        
        # Format Selection Section
        format_title = ctk.CTkLabel(format_frame, text="Format Selection", font=('Arial', 14, 'bold'), text_color='white')
        download_mp3 = ctk.CTkRadioButton(format_frame, text='Audio (MP3)', variable=formats, value=0, command=lambda:download_select_mode_setting(0), font=('Arial', 12))
        download_mp4 = ctk.CTkRadioButton(format_frame, text='Video (MP4)', variable=formats, value=1, command=lambda:download_select_mode_setting(1), font=('Arial', 12))
        
        # Resolution Section
        resolution_title = ctk.CTkLabel(resolution_frame, text="Video Resolution", font=('Arial', 14, 'bold'), text_color='white')
        resoltion_combox = ctk.CTkComboBox(resolution_frame, font=('Arial', 12), width=200, state='readonly', values=[])
        get_resoltion_btn = ctk.CTkButton(resolution_frame, text='Get Available Resolutions', width=160, command=lambda:threading.Thread(daemon=True,target=get_resolution_setting).start(), text_color='white', font=('Arial', 13, 'bold'))
        
        # Download Section
        downloadselectedsong = ctk.CTkButton(download_tab, text='Download Selected Video', width=400, command=lambda:threading.Thread(daemon=True,target=download_to_loacl_setting).start(), text_color='white', font=('Arial', 13, 'bold'))
        downloadhooklabel = ctk.CTkLabel(download_tab, font=('Arial', 12, 'normal'), textvariable=downloadhooktext, text_color='lightblue')


        # Create scrollable frame for player settings
        player_scrollable_frame = ctk.CTkScrollableFrame(player_tab, width=680, height=400, fg_color='#242424')
        player_scrollable_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        player_scrollable_frame.grid_columnconfigure(0, weight=1)
        player_scrollable_frame.grid_columnconfigure(1, weight=1)

        # Create organized frames for player settings
        playback_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2E2E2E')
        playback_frame.grid_columnconfigure(0, weight=1)
        playback_frame.grid_columnconfigure(1, weight=1)
        
        interface_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2E2E2E')
        interface_frame.grid_columnconfigure(0, weight=1)
        interface_frame.grid_columnconfigure(1, weight=1)
        
        advanced_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2E2E2E')
        advanced_frame.grid_columnconfigure(0, weight=1)
        advanced_frame.grid_columnconfigure(1, weight=1)
        
        external_services_frame = ctk.CTkFrame(player_scrollable_frame, fg_color='#2E2E2E')
        external_services_frame.grid_columnconfigure(0, weight=1)
        external_services_frame.grid_columnconfigure(1, weight=1)
        
        # Playback Settings Section
        playback_title = ctk.CTkLabel(playback_frame, text="Playback Settings", font=('Arial', 14, 'bold'), text_color='white')
        maxresolutionlabel = ctk.CTkLabel(playback_frame, font=('Arial', 12, 'normal'), text='Max Resolution:', text_color='white')
        maxresolutioncombobox = ctk.CTkComboBox(playback_frame, font=('Arial', 12), width=120, state='readonly', values=['480', '720', '1080', '1440', '2160', '4320'])
        maxresolutioncombobox.set(str(maxresolution.get()))
        maxresolutioncombobox.configure(command=max_resolution_select)
        autoretry_btn = ctk.CTkCheckBox(playback_frame, text='Auto retry on error', variable=autoretry, fg_color='#242424', text_color='white')
        audio_only_checkbtn = ctk.CTkCheckBox(playback_frame, text='Audio only mode', variable=audio_only, fg_color='#242424', text_color='white', command=switch_audio_only)
        playerspeed_title_label = ctk.CTkLabel(playback_frame, font=('Arial', 12, 'normal'), text='Player Speed:', text_color='white')
        playerspeed_slider = ctk.CTkSlider(playback_frame,variable=player_speed, from_=0.3, to=3.0, width=200,number_of_steps=27,command=set_player_speed_setting)
        playerspeed_speed_label = ctk.CTkLabel(playback_frame, font=('Arial', 12, 'normal'), text='1.0x', text_color='white')
        
        # Interface Settings Section
        interface_title = ctk.CTkLabel(interface_frame, text="Interface Settings", font=('Arial', 14, 'bold'), text_color='white')
        blurbtn = ctk.CTkCheckBox(interface_frame, text='Acrylic blur effect', variable=blur_window, fg_color='#242424', text_color='white', command=switch_blur_window)
        openwith_fullscreen_btn = ctk.CTkCheckBox(interface_frame, text='Auto fullscreen when opening files', variable=open_with_fullscreen, fg_color='#242424', text_color='white', command=autofullscreen_setting)

        # Advanced Settings Section
        advanced_title = ctk.CTkLabel(advanced_frame, text="Advanced Settings", font=('Arial', 14, 'bold'), text_color='white')
        mpvlogbtn = ctk.CTkButton(advanced_frame, text='Show MPV Log', width=160, command=show_mpv_log, text_color='white', font=('Arial', 13, 'bold'))
        enable_dnd_btn = ctk.CTkCheckBox(advanced_frame, text='Enable Drag and Drop', variable=enable_drag_and_drop, fg_color='#242424', text_color='white', command=switch_drag_and_drop)
        force_stop_loading_btn = ctk.CTkButton(advanced_frame, text='Force Stop Loading Video', width=160, command=set_force_stop_loading, text_color='white', font=('Arial', 13, 'bold'))
        show_cache_btn = ctk.CTkCheckBox(advanced_frame, text='Show Cache Info', variable=show_cache, fg_color='#242424', text_color='white', command=switch_show_cache)
        subtitle_label = ctk.CTkLabel(advanced_frame, text='Subtitle:', font=('Arial', 12), text_color='white')
        subtitlecombobox = ctk.CTkComboBox(advanced_frame, font=('Arial', 12), width=200, state='readonly', values=subtitle_namelist, command=subtitle_combobox_callback)
        
        # External Services Section
        external_services_title = ctk.CTkLabel(external_services_frame, text="External Services Settings", font=('Arial', 14, 'bold'), text_color='white')
        chrome_extension_server_checkbtn = ctk.CTkSwitch(external_services_frame, text='Run Chrome extension server', variable=setting_run_chrome_extension_server, command=switch_flask_server, fg_color='#242424', text_color='white')
        enable_discord_presence_btn = ctk.CTkSwitch(external_services_frame, text='Enable Discord Rich Presence', variable=enable_discord_presence, fg_color='#242424', text_color='white', command=lambda:threading.Thread(daemon=True,target=switch_discord_presence).start())
        discord_presence_show_playing_btn = ctk.CTkCheckBox(external_services_frame, text='Show current playing on Discord', variable=discord_presence_show_playing, fg_color='#242424', text_color='white', command=switch_discord_presence_show_playing)


        # Create frames for better organization
        ytdlp_frame = ctk.CTkFrame(version_info_tab, fg_color='#2E2E2E')
        ytdlp_frame.grid_columnconfigure(0, weight=1)
        ytdlp_frame.grid_columnconfigure(1, weight=1)
        
        player_frame = ctk.CTkFrame(version_info_tab, fg_color='#2E2E2E')
        player_frame.grid_columnconfigure(0, weight=1)
        player_frame.grid_columnconfigure(1, weight=1)

        # YT-DLP Section
        ytdlp_title = ctk.CTkLabel(ytdlp_frame, text="YT-DLP", font=('Arial', 16, 'bold'), text_color='white')
        go_ytdlp_web = ctk.CTkButton(ytdlp_frame,text='Visit Website',width=120,command=lambda:webbrowser.open('https://github.com/yt-dlp/yt-dlp/releases'),text_color='white', font=('Arial', 13, 'bold'))
        auto_update_ytdlp_btn = ctk.CTkButton(ytdlp_frame,text='Update',width=120,command=lambda:threading.Thread(daemon=True,target=update_ytdlp).start(),text_color='white',fg_color="#158258", font=('Arial', 13, 'bold'))


        # JaTubePlayer Section  
        player_title = ctk.CTkLabel(player_frame, text="JaTubePlayer", font=('Arial', 16, 'bold'), text_color='white')
        go_player_web = ctk.CTkButton(player_frame,text='Visit Website',width=120,command=lambda:webbrowser.open('https://github.com/jackaopen/JaTubePlayer/releases'),text_color='white', font=('Arial', 13, 'bold'))
        

        
        # Versions Frame 
        ytdlp_current_versions_frame = ctk.CTkFrame(ytdlp_frame, fg_color='#2E2E2E')
        ytdlp_latest_versions_frame = ctk.CTkFrame(ytdlp_frame, fg_color='#2E2E2E')
        player_current_versions_frame = ctk.CTkFrame(player_frame, fg_color='#2E2E2E')
        player_latest_versions_frame = ctk.CTkFrame(player_frame, fg_color='#2E2E2E')

        ytdlp_current_versions_frame_title = ctk.CTkLabel(ytdlp_current_versions_frame, text="Current Version", font=('Arial', 14, 'bold'), text_color='white')
        ytdlp_latest_versions_frame_title = ctk.CTkLabel(ytdlp_latest_versions_frame, text="Latest Version", font=('Arial', 14, 'bold'), text_color='white')
        player_current_versions_frame_title = ctk.CTkLabel(player_current_versions_frame, text="Current Version", font=('Arial', 14, 'bold'), text_color='white')
        player_latest_versions_frame_title = ctk.CTkLabel(player_latest_versions_frame, text="Latest Version", font=('Arial', 14, 'bold'), text_color='white')

        #ytdlp version frame
        ytdlp_ver_current_label = ctk.CTkLabel(ytdlp_current_versions_frame, font=('Arial', 14, 'normal'), text_color='lightgreen', anchor='w')
        ytdlp_ver_lastest_label = ctk.CTkLabel(ytdlp_latest_versions_frame, font=('Arial', 14, 'normal'), text_color='lightblue', anchor='w')

    
        # player version frame
        player_ver_current_label = ctk.CTkLabel(player_current_versions_frame, font=('Arial', 14, 'normal'), text_color='lightgreen', anchor='w')
        player_ver_latest_label = ctk.CTkLabel(player_latest_versions_frame, font=('Arial', 14, 'normal'), text_color='lightblue', anchor='w')

        # Settings
        auto_check_ver_btn = ctk.CTkCheckBox(version_info_tab,text='Check version at startup',variable=auto_check_ver,command=save_autovercheck_option_ver,fg_color='#242424',text_color='white')





        # Hotkeys Frame
        hotkey_scrollable_frame = ctk.CTkScrollableFrame(hotkey_tab, width=680, height=400,fg_color='#242424')
        hotkey_scrollable_frame.grid(row=0, column=0)
        hotkey_scrollable_frame.grid_columnconfigure(0, weight=1)
        hotkey_playback_frame = ctk.CTkFrame(hotkey_scrollable_frame, fg_color='#2E2E2E')
        hotkey_mode_frame = ctk.CTkFrame(hotkey_scrollable_frame, fg_color='#2E2E2E')
        hotkey_volume_frame = ctk.CTkFrame(hotkey_scrollable_frame, fg_color='#2E2E2E')
        hotkey_player_frame = ctk.CTkFrame(hotkey_scrollable_frame, fg_color='#2E2E2E')
        hotkey_set_keymem_frame = ctk.CTkFrame(hotkey_scrollable_frame, fg_color='#2E2E2E')

        hotkey_set_keymem_title = ctk.CTkLabel(hotkey_set_keymem_frame, text="Set Hotkey", font=('Arial', 14, 'bold'), text_color='white')
        hotkey_set_keymem_function_combobox = ctk.CTkComboBox(hotkey_set_keymem_frame, font=('Arial', 12), width=200, state='readonly', values=['play_pause','next','previous','stop', 'volume_up','volume_down','mode_random','mode_continuous','mode_repeat','toggle_minimize'])
        hotkey_set_keymem_startlisten_btn = ctk.CTkButton(hotkey_set_keymem_frame, text='Set Hotkey', width=160, command=set_keymem_setting_thread, text_color='white', font=('Arial', 13, 'bold'))   
        hotkey_set_keymem_set_default_btn = ctk.CTkButton(hotkey_set_keymem_frame, text='Set Default', width=160, command=set_keymem_default_setting, text_color='white', font=('Arial', 13, 'bold'))
        



        hotkey_playback_frame_title = ctk.CTkLabel(hotkey_playback_frame, text="Playback Hotkeys", font=('Arial', 14, 'bold'), text_color='white')
        hotkey_mode_frame_title = ctk.CTkLabel(hotkey_mode_frame, text="Playback Mode Hotkeys", font=('Arial', 14, 'bold'), text_color='white')
        hotkey_volume_frame_title = ctk.CTkLabel(hotkey_volume_frame, text="Volume Hotkeys", font=('Arial', 14, 'bold'), text_color='white')
        hotkey_player_frame_title = ctk.CTkLabel(hotkey_player_frame, text="Player Hotkeys", font=('Arial', 14, 'bold'), text_color='white')

        hotkey_playback_play_pause_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 12, 'normal'), text='Play/Pause:', text_color='white')
        hotkey_playback_stop_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 12, 'normal'), text='Stop:', text_color='white')
        hotkey_playback_next_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 12, 'normal'), text='Next Video:', text_color='white')
        hotkey_playback_prev_label = ctk.CTkLabel(hotkey_playback_frame, font=('Arial', 12, 'normal'), text='Previous Video:', text_color='white')
    
        hotkey_mode_repeat_label = ctk.CTkLabel(hotkey_mode_frame, font=('Arial', 12, 'normal'), text='Toggle Repeat Mode:', text_color='white')
        hotkey_mode_random_label = ctk.CTkLabel(hotkey_mode_frame, font=('Arial', 12, 'normal'), text='Toggle Random Mode:', text_color='white')
        hotkey_mode_continuous_label = ctk.CTkLabel(hotkey_mode_frame, font=('Arial', 12, 'normal'), text='Toggle Continuous Play Mode:', text_color='white')

        hotkey_volume_up_label = ctk.CTkLabel(hotkey_volume_frame, font=('Arial', 12, 'normal'), text='Volume Up:', text_color='white')
        hotkey_volume_down_label = ctk.CTkLabel(hotkey_volume_frame, font=('Arial', 12, 'normal'), text='Volume Down:', text_color='white')
        hotkey_toggle_minimize_label = ctk.CTkLabel(hotkey_player_frame, font=('Arial', 12, 'normal'), text='Toggle Minimize:', text_color='white')


        hotkey_playback_play_pause_textbox = ctk.CTkTextbox(hotkey_playback_frame, font=('Arial', 12), width=200, height=1, state='disabled')
        hotkey_playback_stop_textbox = ctk.CTkTextbox(hotkey_playback_frame, font=('Arial', 12), width=200, height=1, state='disabled')
        hotkey_playback_next_textbox = ctk.CTkTextbox(hotkey_playback_frame, font=('Arial', 12), width=200, height=1, state='disabled')
        hotkey_playback_prev_textbox = ctk.CTkTextbox(hotkey_playback_frame, font=('Arial', 12), width=200, height=1, state='disabled') 

        hotkey_mode_repeat_textbox = ctk.CTkTextbox(hotkey_mode_frame, font=('Arial', 12), width=200, height=1, state='disabled')
        hotkey_mode_random_textbox = ctk.CTkTextbox(hotkey_mode_frame, font=('Arial', 12), width=200, height=1, state='disabled')
        hotkey_mode_continuous_textbox = ctk.CTkTextbox(hotkey_mode_frame, font=('Arial', 12), width=200, height=1, state='disabled')

        hotkey_volume_up_textbox = ctk.CTkTextbox(hotkey_volume_frame, font=('Arial', 12), width=200, height=1, state='disabled')
        hotkey_volume_down_textbox = ctk.CTkTextbox(hotkey_volume_frame, font=('Arial', 12), width=200, height=1, state='disabled')
        hotkey_toggle_minimize_textbox = ctk.CTkTextbox(hotkey_player_frame, font=('Arial', 12), width=200, height=1, state='disabled')
        
        hotkey_playback_frame.grid_columnconfigure(0, weight=0)
        hotkey_mode_frame.grid_columnconfigure(0, weight=0)
        hotkey_volume_frame.grid_columnconfigure(0, weight=0)
        hotkey_player_frame.grid_columnconfigure(0, weight=0)
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
                #print(setting.winfo_width(),setting.winfo_height())

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

                    if download_seleted_title_text.get(1.0,tk.END).strip() == '':prename_setting = None
                    if selected_song_number != None or playing_vid_mode == 3:
                        if playing_vid_mode ==3 or prename_setting !=playlisttitles[selected_song_number]:
                            ui_queue.put(lambda: download_seleted_title_text.configure(state='normal'))
                            ui_queue.put(lambda: download_seleted_title_text.delete(0.0,tk.END))
                            ui_queue.put(lambda: download_seleted_title_text.insert(tk.END,f'{playlisttitles[selected_song_number] if playing_vid_mode !=3 or not playing_vid_info_dict else playing_vid_info_dict["title"]}'))
                            ui_queue.put(lambda: download_seleted_title_text.configure(state='disabled'))

                    else:
                        ui_queue.put(lambda: download_seleted_title_text.configure(state='normal'))
                        ui_queue.put(lambda: download_seleted_title_text.delete(0.0,tk.END))
                        ui_queue.put(lambda: download_seleted_title_text.insert(tk.END,'Select a video first!'))
                        ui_queue.put(lambda: download_seleted_title_text.configure(state='disabled'))
                    if selected_song_number != None or playing_vid_mode==3 :
                        if playing_vid_mode !=3:prename_setting = playlisttitles[selected_song_number]
                        elif playing_vid_info_dict:prename_setting = playing_vid_info_dict['title']
                    else:prename_setting=None
                    try:
                        if playing_vid_mode == 0 and playing_vid_info_dict.get('live_status') == 'is_live':
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        elif playing_vid_mode ==1 or playing_vid_mode ==2:
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        elif playing_vid_mode ==3 and playing_vid_info_dict.get('live_status') == 'is_live':
                            ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                        else:
                            try:
                                if not is_downloading.get():
                                    ui_queue.put(lambda: downloadselectedsong.configure(state='normal'))
                                else:
                                    ui_queue.put(lambda: downloadselectedsong.configure(state='disabled'))
                            except Exception as e :pass

                    except Exception as e :pass
                    ui_queue.put(lambda:subtitlecombobox.configure(values=subtitle_namelist))
                    ui_queue.put(lambda:subtitlecombobox.set(subtitle_namelist[subtitle_selection_idx.get()]))
                           
                except Exception as e :pass
                time.sleep(1)


        threading.Thread(daemon=True,target=lambda:root.after(200,init_quickstart_data)).start()
        threading.Thread(daemon=True,target=get_version_setting_thread).start()
        threading.Thread(daemon=True,target=get_user_name).start()
        threading.Thread(daemon=True,target=get_hotkey_setting_thread).start()
        threading.Thread(daemon=True,target=setting_frame_listener).start()
        
    
        if youtubeAPI:root.after(0,apilabel.configure(text=f'{youtubeAPI[:10]}{"*" * (len(youtubeAPI)-10)}'))
        update_cookie_path_textbox()
        update_client_secrets_path_textbox()



        # Layout Personal Playlist Tab Frames
        youtube_data_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        youtube_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        updatelike_btn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        auto_like_refresh_checkbtn.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        updatesub_btn.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        auto_sub_refresh_checkbtn.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        updateuserplaylists_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=(5,10), sticky="w")
        
        history_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        history_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        record_history_btn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        reset_history_btn.grid(row=1, column=1, padx=10, pady=(5,10), sticky="w")



        # Layout Download Info Frame
        download_info_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10)
        info_title.grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")
        download_seleted_title_text.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        
        # Layout Format Frame
        format_frame.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        format_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        download_mp3.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        download_mp4.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Layout Resolution Frame  
        resolution_frame.grid(row=1, column=1,  padx=10, pady=10, sticky="w")
        resolution_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        resoltion_combox.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        get_resoltion_btn.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Layout Download Button and Status
        downloadselectedsong.grid(row=2, column=0, columnspan=3, padx=20, pady=20)
        downloadhooklabel.grid(row=3, column=0, columnspan=3, padx=20, pady=(0,10))

        # Layout Player Tab Frames
        playback_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        playback_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        maxresolutionlabel.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        maxresolutioncombobox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        autoretry_btn.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        audio_only_checkbtn.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        playerspeed_title_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        playerspeed_slider.grid(row=4, column=0, columnspan=1, padx=10, pady=5, sticky="ew")
        playerspeed_speed_label.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        interface_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        interface_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        blurbtn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        openwith_fullscreen_btn.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        advanced_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        advanced_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        mpvlogbtn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        enable_dnd_btn.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        force_stop_loading_btn.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        show_cache_btn.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        subtitle_label.grid(row=3, column=0, padx=10, pady=(0,10), sticky="w")
        subtitlecombobox.grid(row=3, column=1, padx=10, pady=(0,10), sticky="w")
        
        # Layout External Services Frame
        external_services_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        external_services_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        chrome_extension_server_checkbtn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        enable_discord_presence_btn.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        discord_presence_show_playing_btn.grid(row=2, column=1, padx=10, pady=(0,10), sticky="w")
        
        # Layout YT-DLP Frame
        ytdlp_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        ytdlp_title.grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")

        ytdlp_current_versions_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ytdlp_latest_versions_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        go_ytdlp_web.grid(row=2, column=1, padx=10, pady=(5,10), sticky="e")
        auto_update_ytdlp_btn.grid(row=2, column=0, padx=10, pady=(5,10), sticky="w")
        
        # Layout Player Frame
        player_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        player_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        player_current_versions_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        player_latest_versions_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        go_player_web.grid(row=2, column=1, padx=10, pady=(5,10), sticky="e")

        #ytdlp version frame layout
        ytdlp_current_versions_frame_title.grid(row=0, column=0, padx=10, pady=(5,5), sticky="w")
        ytdlp_ver_current_label.grid(row=1, column=0, padx=10, pady=(0,10), sticky="w")
        ytdlp_latest_versions_frame_title.grid(row=0, column=0, padx=10, pady=(5,5), sticky="w")
        ytdlp_ver_lastest_label.grid(row=1, column=0, padx=10, pady=(0,10), sticky="w")

        # player version frame layout
        player_current_versions_frame_title.grid(row=0, column=0, padx=10, pady=(5,5), sticky="w")
        player_ver_current_label.grid(row=1, column=0, padx=10, pady=(0,10), sticky="w")
        player_latest_versions_frame_title.grid(row=0, column=0, padx=10, pady=(5,5), sticky="w")
        player_ver_latest_label.grid(row=1, column=0, padx=10, pady=(0,10), sticky="w")


        # Layout Settings
        auto_check_ver_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="w")

####### quick init frame #########

        # Header Frame
        header_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2E2E2E')
        header_frame.grid_columnconfigure(0, weight=1)
        header_title = ctk.CTkLabel(header_frame, text="Quick Startup Settings", font=('Arial', 14, 'bold'), text_color='white')
        header_title.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        init_toggle_quickstartup_checkbtn = ctk.CTkCheckBox(header_frame,text='toggle quick startup init',variable=init_toggle_quickstartup,command=setting_init_toggle_quickstartup,fg_color='#242424',text_color='white')
        init_toggle_quickstartup_checkbtn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        init_quick_startup_mode_text = ctk.CTkTextbox(header_frame, font=('Arial', 13), height=25, text_color='white')
        init_quick_startup_mode_text.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        init_quick_startup_mode_text.configure(state='disabled')
        header_frame.grid(row=0, column=0,columnspan=2, padx=10, pady=5, sticky="ew")

        # Search Frame
        search_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2E2E2E')
        search_frame.grid_columnconfigure((0,1), weight=1)
        search_title = ctk.CTkLabel(search_frame, text="Search", font=('Arial', 14, 'bold'), text_color='white')
        search_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="ew")
        init_search_btn = ctk.CTkRadioButton(search_frame,text='init search',variable=init_quickstartup_mode,value='search',command=init_search_select)
        init_search_btn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        init_search_entry = ttk.Entry(search_frame,font=('arial 12',14,'bold'),width=14)
        init_search_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        init_search_set_btn = ctk.CTkButton(search_frame,text='set init search',command=init_search_set,width=160,text_color='white', font=('Arial', 13, 'bold'))
        init_search_set_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        search_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Playlist Frame
        playlist_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2E2E2E')
        playlist_frame.grid_columnconfigure((0,1), weight=1)
        playlist_title = ctk.CTkLabel(playlist_frame, text="Playlist", font=('Arial', 14, 'bold'), text_color='white')
        playlist_title.grid(row=0, column=0, columnspan=2, padx=5, pady=(5,5), sticky="ew")
        init_playlist_btn = ctk.CTkRadioButton(playlist_frame,text='init playlist',variable=init_quickstartup_mode,value='playlist',command=init_playlist_select)
        init_playlist_btn.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        init_playlist_combobox = ttk.Combobox(playlist_frame,font=('arial 12',14,'bold'),width=14,state='readonly')
        init_playlist_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        init_get_playlist_btn = ctk.CTkButton(playlist_frame,text='get init playlist',command=init_playlist_get,width=144,text_color='white', font=('Arial', 13, 'bold'))
        init_get_playlist_btn.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        init_playlist_set_btn = ctk.CTkButton(playlist_frame,text='set init playlist',command=init_playlist_set,width=144,text_color='white', font=('Arial', 13, 'bold'))
        init_playlist_set_btn.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        playlist_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Local Folder Frame
        local_folder_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2E2E2E')
        local_folder_frame.grid_columnconfigure((0,1), weight=1)
        local_folder_title = ctk.CTkLabel(local_folder_frame, text="Local Folder", font=('Arial', 14, 'bold'), text_color='white')
        local_folder_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="ew")
        init_local_folder_btn = ctk.CTkRadioButton(local_folder_frame,text='init local folder',variable=init_quickstartup_mode,value='local_playlist',command=init_local_playlist)
        init_local_folder_btn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        init_select_local_folder_btn = ctk.CTkButton(local_folder_frame,text='select local folder',command=init_select_local_folder,width=160,text_color='white', font=('Arial', 13, 'bold'))
        init_select_local_folder_btn.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        local_folder_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # Recommendation Frame
        rec_frame = ctk.CTkFrame(quick_init_tab, fg_color='#2E2E2E')
        rec_frame.grid_columnconfigure(0, weight=1)
        rec_title = ctk.CTkLabel(rec_frame, text="Recommendation", font=('Arial', 14, 'bold'), text_color='white')
        rec_title.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        init_rec_at_startbtn = ctk.CTkRadioButton(rec_frame,text='init Recommendation',variable=init_quickstartup_mode,value='recommendation',command=setting_init_recommendation_select)
        init_rec_at_startbtn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        rec_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")


        #hotkey tab layout
        hotkey_playback_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        hotkey_mode_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        hotkey_volume_frame.grid(row=3, column=0,  padx=20, pady=10, sticky="ew")
        hotkey_set_keymem_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        hotkey_player_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        hotkey_set_keymem_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        hotkey_set_keymem_function_combobox.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        hotkey_set_keymem_startlisten_btn.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        hotkey_set_keymem_set_default_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=(5,10), sticky="ew")

        hotkey_playback_frame_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        hotkey_playback_play_pause_label.grid(row=1, column=0, padx=10, pady=5, sticky="w") 
        hotkey_playback_play_pause_textbox.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        hotkey_playback_stop_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        hotkey_playback_stop_textbox.grid(row=2, column=1, padx=10, pady=5, sticky="e")
        hotkey_playback_next_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        hotkey_playback_next_textbox.grid(row=3, column=1, padx=10, pady=5, sticky="e")
        hotkey_playback_prev_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        hotkey_playback_prev_textbox.grid(row=4, column=1, padx=10, pady=5, sticky="e")
        hotkey_mode_frame_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        hotkey_mode_repeat_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        hotkey_mode_repeat_textbox.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        hotkey_mode_random_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        hotkey_mode_random_textbox.grid(row=2, column=1, padx=10, pady=5, sticky="e")
        hotkey_mode_continuous_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        hotkey_mode_continuous_textbox.grid(row=3, column=1, padx=10, pady=5, sticky="e")
        hotkey_volume_frame_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        hotkey_volume_up_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        hotkey_volume_up_textbox.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        hotkey_volume_down_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        hotkey_volume_down_textbox.grid(row=2, column=1, padx=10, pady=5, sticky="e")
        hotkey_player_frame_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        hotkey_toggle_minimize_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        hotkey_toggle_minimize_textbox.grid(row=1, column=1, padx=10, pady=5, sticky="e")
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

                    ui_queue.put(lambda pn=page_num, ct=channel_temp: liked_page_num_label.configure(text=f'sub page {pn}/{len(ct)//50+1}'))
                    
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

                    ui_queue.put(lambda pn=page_num, lvu=liked_vid_url: liked_page_num_label.configure(text=f'like page {pn}/{len(lvu)//50+1}'))

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
                                        try:
                                            title = f'🛑LIVE {vid_info["title"]}' if vid_info['live_status'] == 'is_live' else vid_info['title']
                                        except:title = vid_info["title"]
                                        playlisttitles.append(title)
                                        playlist_thumbnails.append(vid_info['thumbnails']['high']['url'])
                                        playlist_channel.append(vid_info['channelTitle'])
                                        insert_treeview_quene.put((vid_info['thumbnails']['high']['url'],title,vid_info['channelTitle']))
                                        ui_queue.put(lambda: root.update())
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

    ui_queue.put(lambda: playlistlabel.configure(text='⏳ loading...'))
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

    # #print out the private playlist titles and IDs
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

    ui_queue.put(lambda: playlistlabel.configure(text='Select playlist:'))
    
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

        ui_queue.put(lambda: playlisttreebox.delete(*playlisttreebox.get_children()))
        if youtube == None:
            google_control.get_cred()
            ui_queue.put(lambda: google_status_update())
            get_user_playlists(0)
        elif playlistID.get() or playlistid_input:
            ui_queue.put(lambda: playlistlabel.configure(text='⏳Loading...'))
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
            vid_url = [f"https://www.youtube.com/watch?v={item['contentDetails']['videoId']}" for item in playlistsongs]
            for item in playlistsongs:
                video_id = item['contentDetails']['videoId']
                title_response = youtube.videos().list(
                    part='snippet',
                    id=video_id
                ).execute()
                vid_info = title_response['items'][0]['snippet']
                playlist_channel.append(vid_info['channelTitle'])
                playlisttitles.append(vid_info['title'])
                playlist_thumbnails.append(vid_info['thumbnails']['high']['url'])
                insert_treeview_quene.put((vid_info['thumbnails']['high']['url'],vid_info['title'],vid_info['channelTitle']))
                tree_index += 1
        

    except googleapiclient.errors.HttpError as err: ######  handle stupid api
            ui_queue.put(lambda e=err: messagebox.showerror(f'JaTubePlayer {ver}', f"An error occurred: {e}"))
    except Exception as e:
            ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}', err))
    ui_queue.put(lambda: playlistlabel.configure(text='select playlist:'))
    ui_queue.put(lambda: liked_page_num_label.configure(text=''))
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
        ui_queue.put(lambda: searchlistlabel.configure(text='⏳ loading...'))
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
        
        ui_queue.put(lambda: playlisttreebox.delete(*playlisttreebox.get_children())) #########      start to process thumnail and title
        
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
        ui_queue.put(lambda: liked_page_num_label.configure(text=''))

        
    else:
        ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}','entry cant be empty!'))
    loadingplaylist = False
    ui_queue.put(lambda: searchlistlabel.configure(text='Search:'))

@check_internet
def youtube_search(event=None):
    if loadingplaylist == False or loadingplaylist == True and messagebox.askokcancel(f'JaTubePlayer {ver}','player is still loading, sure to load again?'):
        threading.Thread(daemon=True,target=youtube_search_thread).start()





def update_playing_pos_local_and_chrome():
    global stoped,finish_break, pos_for_label,volume,selected_song_number,stream
    stoped = False
    finish_break = False

    while not stoped:  
        
        try:
            time.sleep(0.1) 
            #print(player_file.get_position()*length , player_file.get_length()/1000 ,player_file.is_playing(),resolution.get(),vid_aud_prior.get(),cache)
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
            if abs(pos - length ) <= 0.4 and length != -1: ## video ends
                
                if selected_song_number != None:
                    ui_queue.put(lambda: playlisttreebox.selection_remove(playlisttreebox.selection()))
                    if playing_vid_mode == 2:
                        ui_queue.put(lambda: playlisttreebox.selection_remove(playlisttreebox.selection()))
                        if player_mode_selector.get() =='continue':
                            if selected_song_number == len(vid_url) -1:
                                selected_song_number = 0
                            else:    
                                selected_song_number  = selected_song_number + 1
                        elif player_mode_selector.get() =='replay':player.seek(0,reference='absolute')
                        elif player_mode_selector.get() =='random':
                            selected_song_number = random.randint(0,len(vid_url))
                        download_and_play()
                        ui_queue.put(lambda s=selected_song_number: playlisttreebox.selection_set(playlisttreebox.get_children()[s]))

                        break

                elif playing_vid_mode == 1 or playing_vid_mode == 3:### MPV option keep_open
                    if player_mode_selector.get() =='replay':
                        player.seek(0,reference='absolute')
                elif playing_vid_mode == 2:ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer{ver}','Choose a video again'))
            if stoped: 
                #print('ajksdbasjd')
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
                if abs(pos - length ) <= 0.2 and length != -1: ## video ends
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
                            player.seek(0,reference='absolute')#### go back instead of recreate mpv obj via dap

                        elif player_mode_selector.get() =='random':
                            player.stop()
                            selected_song_number = random.randint(0,len(vid_url))
                        
                        if player_mode_selector.get() !='replay':
                            ui_queue.put(lambda s=selected_song_number: playlisttreebox.selection_set(playlisttreebox.get_children()[s])) ## get selection
                            finish_break = True  ### so set it before enfter d.a.p fun
                            download_and_play() ### will stuck here bc of watiing while loop
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
                #print('ajksdbasjd')
                finish_break = True
                break

    except Exception as e:
        log_handle(content=f"Error in update_playing_pos_yt: {e}")
        import traceback
        traceback.print_exc()

            


 
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
    global stoped, pos_thread , stream ,playing_vid_url,playing_vid_info_dict,loadingvideo,force_stop_loading,subtitle_namelist,subtitle_urllist
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


            if playing_vid_mode == 0 or playing_vid_mode == 2:

                vid_url_in = vid_url.copy()
                playlisttitles_in = playlisttitles.copy()

                playing_vid_url = vid_url_in[selected_song_number]
                selected_song_number_in = int(selected_song_number)

            if not chosen_file:  
                
                    loadingvideo = True
                    
                    stop_playing_video()  
                    ui_queue.put(lambda: player_loading_label.configure(text='⏳ loading...') if player_loading_label.cget('text') != 'retrying...' else None)
                    ui_queue.put(lambda: playing_title_textbox.configure(state='normal'))
                    ui_queue.put(lambda: playing_title_textbox.delete(1.0,tk.END))
                    ui_queue.put(lambda: playing_title_textbox.configure(state='disabled'))
                    player.volume =int(player_volume_scale.get())
                    
                    try:    
                            if direct_url:
                                if check_internet_socket():
                                    playing_vid_url = direct_url
                                    ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg=f'Playing video from chrome\n{direct_url}', duration='short', icon=icondir)
                                else:
                                    ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver}', msg='Internet connection failed, please check your internet connection', duration='short', icon=icondir)
                                    loadingvideo = False
                                    return None #### return if no internet
                                    #the def actually dont need to return anything but just to make sure it wont go futher
                            try:
                                vid_only_url, audio_only_url,playing_vid_info_dict = get_info(yt_dlp=yt_dlp,
                                                                                                        maxres=maxresolution.get(),
                                                                                                        target_url=vid_url_in[selected_song_number_in] if not direct_url else direct_url,
                                                                                                        deno_path=deno_exe,
                                                                                                        log_handler=ytdlp_log_handle,
                                                                                                        cookie_path=cookies_dir)
                                if not vid_only_url and not audio_only_url:
                                    messagebox.showerror(f'JaTubePlayer {ver}','Failed to extract video info, maybe because of network problem or the video is private or age restricted.\nYou can try to play the video again or check the log for more details.')
                                    force_stop_loading = True 

                                player.loadfile(vid_only_url, audio_file=audio_only_url)
                                subtitle_selection_idx.set(0)
                                subtitle_namelist = ['No subtitles']
                                subtitle_urllist = []

                                for sub in playing_vid_info_dict.get('subtitles').values():
                                    try:
                                        if len(sub) == 7:
                                            subtitle_namelist.append(sub[6]['name'])
                                            subtitle_urllist.append(sub[6]['url'])
                                        
                                    except Exception as e:
                                        print(f"Error processing subtitle: {e}")
                                print(f"Available subtitles: {subtitle_namelist}")
            
                                try:## try to make the vid play info somehow ytdlp fail to get info dict
                                    if playing_vid_info_dict.get('live_status') == 'is_live':
                                        global stream
                                        stream = True
           
                                    else:
                                        stream = False
                                except:
                                    stream = False
                                    log_handle(type='error',content='failed to get live status')




                                try:## try to make the vid play info somehow ytdlp fail to get info dict
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
                                if i == 10 or i==20:

                                    mpv_log.append('calling')
                                    player.play(vid_url_in[selected_song_number_in] if not direct_url else direct_url)
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
                                    ui_queue.put(lambda: playing_title_textbox.insert(tk.END, playlisttitles_in[selected_song_number_in] if not direct_url else playing_vid_info_dict['title']))
                                    if modeforfullscreen == 0:ui_queue.put(lambda: root.title(f'JaTubePlayer {ver} by Jackaopen '))
                                    else:ui_queue.put(lambda: root.title(f'JaTubePlayer {ver} by Jackaopen - {playlisttitles_in[selected_song_number_in] if not direct_url else playing_vid_info_dict["title"]}')) 

                                except Exception as e:
                                    log_handle(content=f"Error inserting title: {e}")
                                ui_queue.put(lambda: playing_title_textbox.configure(state='disabled'))
                                
                                ui_queue.put(lambda: smtc.update_media_info(
                                    title = playlisttitles_in[selected_song_number_in] if not direct_url else playing_vid_info_dict['title'],
                                    artist = playlist_channel[selected_song_number_in] if not direct_url else playing_vid_info_dict['uploader'],
                                    album = 'JaTubePlayer',
                                    thumbnail_url = playlist_thumbnails[selected_song_number_in] if not direct_url else playing_vid_info_dict['thumbnail']
                                ))
                                if enable_discord_presence.get():
                                    try:
                                        if discord_presence_show_playing.get():
                                            discord_presence.update(song_title=playlisttitles_in[selected_song_number_in] if not direct_url else playing_vid_info_dict['title'])
                                        else:discord_presence.idle()
                                    except:pass

                                player.volume = (int(player_volume_scale.get()))
                                if playing_vid_mode == 0:pos_thread = threading.Thread(daemon = True,target=update_playing_pos_yt)
                                else:pos_thread = threading.Thread(daemon = True,target=update_playing_pos_local_and_chrome)
                                
                                pos_thread.start()
                                ui_queue.put(lambda: player_loading_label.configure(text=''))
                            
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

                                if modeforfullscreen == 0:ui_queue.put(lambda: root.title(f'JaTubePlayer {ver} by Jackaopen '))
                                else:ui_queue.put(lambda cf=chosen_file: root.title(f'JaTubePlayer {ver} by Jackaopen - {os.path.basename(cf)}')) 
                                                                   

                                if succed:
                                    ui_queue.put(lambda: playing_title_textbox.configure(state='normal'))
                                    log_handle(content=f"playing mode {playing_vid_mode}")
                                    if playing_vid_mode == 1:
                                        ui_queue.put(lambda cf=chosen_file: playing_title_textbox.insert(tk.END, str(cf)))  
                                    else:
                                        ui_queue.put(lambda cf=chosen_file: playing_title_textbox.insert(tk.END, os.path.basename(str(cf))))
                                    ui_queue.put(lambda: playing_title_textbox.configure(state='disabled'))
                                    


                                    if modeforfullscreen == 0:ui_queue.put(lambda: root.title(f'JaTubePlayer {ver} by Jackaopen '))
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
                                   
                                    time.sleep(0.1)
                                    loadingvideo = False
                    except Exception as e:
                        ui_queue.put(lambda err=e: messagebox.showerror(f'JaTubePlayer {ver}', f"Failed to play local file:  {str(err)}"))
                        loadingvideo = False



def load_local_files(mode,dnd_single_file_path=None,local_folder_path=None,dnd_files_path_lists:list=None):
    '''
    mode 0 == single file mode
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
    
    if playing_vid_mode == 0:
        if check_internet_socket():
            #load from youtube
            if selected_song_number != None:
                load_thread_queue.put((None,None))
        
            else: messagebox.showerror(f'JaTubePlayer {ver}','please select a video first')
        else:
            ToastNotification().notify(
                app_id="JaTubePlayer",
                title="JaTubePlayer",
                msg='Internet connection failed, please check your internet connection',
                duration='short',            
            )
    else:       
        # load local file/folder
        if selected_song_number != None:
            load_thread_queue.put((vid_url[selected_song_number],None))
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




def fullscreen_widget_change(event=None):
    global modeforfullscreen, stream, tkinter_scaling
   
    try:
        window_dpi = copy(get_window_dpi(hwnd))
        tkinter_scaling = window_dpi
        
        # Force geometry update before making changes
        root.update_idletasks()
        
        if root.state() == 'normal':
            root.geometry('1320x680')
            
            # Tkinter widgets need DPI scaling
            playlisttreebox.configure(height=int(20*window_dpi))
            if playing_vid_mode == 0:
                playlisttreebox.column("#0", width=180, anchor='center')
            else:
                playlisttreebox.column("#0", width=0, anchor='center')
            playlisttreebox.column("title", width=int(1000))
            
            try:
                playlisttreebox.place_configure(relx=0.020, rely=0.161, relwidth=0.925, relheight=0.796)
                Y_scrollbar.place_configure(relx=0.945, rely=0.161, relheight=0.796)
                X_scrollbar.place_configure(relx=0.020, rely=0.957, relwidth=0.925)
                
                # Main frames
                header_frame.place_configure(relx=0, rely=0, relwidth=1, relheight=0.0735)
                right_panel_frame.place_configure(relx=0.617, rely=0.081, relwidth=0.375, relheight=0.684)
                playlist_btn_frame.place_configure(relx=0.617, rely=0.765, relwidth=0.375, relheight=0.213)
                video_container.place_configure(relx=0.008, rely=0.081, relwidth=0.602, relheight=0.669)
                controls_frame.place_configure(relx=0.008, rely=0.757, relwidth=0.602, relheight=0.235)
                Frame_for_mpv.place_configure(relx=0.015, rely=0.096, relwidth=0.587, relheight=0.640)
                
                # Sub-frames
                progress_frame.place_configure(relx=0.019, rely=0.031, relwidth=0.962, relheight=0.313)
                playback_frame.place_configure(relx=0.252, rely=0.219, relwidth=0.503, relheight=0.313)
                volume_frame.place_configure(relx=0.780, rely=0.219, relwidth=0.208, relheight=0.30)
                mode_frame.place_configure(relx=0.019, rely=0.225, relwidth=0.289, relheight=0.188)
                now_playing_frame.place_configure(relx=0.019, rely=0.5, relwidth=0.629, relheight=0.438)
                action_btn_frame.place_configure(relx=0.654, rely=0.469, relwidth=0.340, relheight=0.469)
                
                # Mode widgets
                mode_label.place_configure(relx=0.035, rely=0.1)
                player_mode_continue.place_configure(relx=0.261, rely=0.267)
                player_mode_replay.place_configure(relx=0.487, rely=0.267)
                player_mode_random.place_configure(relx=0.748, rely=0.267)
                
                # Progress bar
                player_pos_label.place_configure(relx=0, rely=0.06, relwidth=0.092)
                player_position_scale.place_configure(relx=0.105, rely=0.1, relwidth=0.784, relheight=0.32)
                player_song_length_label.place_configure(relx=0.902, rely=0.06, relwidth=0.092)
                
                # Playback controls
                prevsong.place_configure(relx=0.12, rely=0, relwidth=0.16, relheight=0.7)
                pausebutton.place_configure(relx=0.29, rely=0, relwidth=0.16, relheight=0.7)
                stopbutton.place_configure(relx=0.45, rely=0, relwidth=0.16, relheight=0.7)
                nextsong.place_configure(relx=0.62, rely=0, relwidth=0.16, relheight=0.7)
                player_loading_label.place_configure(relx=0.79, rely=0.1, relwidth=0.25)
                
                # Volume
                player_volume_label.place_configure(relx=0, rely=0.125, relwidth=0.182)
                player_volume_scale.place_configure(relx=0.212, rely=0.25, relwidth=0.727, relheight=0.3)
                
                # Action buttons
                setting_btn.place_configure(relx=0, rely=0.067, relwidth=0.778, relheight=0.467)
                select_info_btn.place_configure(relx=0, rely=0.6, relwidth=0.400, relheight=0.4)
                playing_info_btn.place_configure(relx=0.426, rely=0.6, relwidth=0.370, relheight=0.4)
                fullscreenbtn.place_configure(relx=0.815, rely=0.6, relwidth=0.148, relheight=0.4)
                
                # Now playing
                np_icon.place_configure(relx=0.016, rely=0.171)
                playing_title_textbox.place_configure(relx=0.07, rely=0.086)
            except:
                pass
            
            player_position_scale.configure(height=int(160*0.313*0.5*0.03))
            Frame_for_mpv.lift()
            fullscreenbtn.configure(text='⛶')
            modeforfullscreen = 0
            root.title(f'JaTubePlayer {ver} by Jackaopen')
            
        elif root.state() == 'zoomed':
            header_frame.place_forget()
            right_panel_frame.place_forget()
            playlist_btn_frame.place_forget()
            video_container.place_forget()
            action_btn_frame.place_forget()
            now_playing_frame.place_forget()
            
            try:
                Frame_for_mpv.place_configure(relx=0, rely=0, relwidth=1, relheight=0.93)
                controls_frame.place_configure(relx=0.025, rely=0.93, relwidth=0.95, relheight=0.073)
                
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
                
                # Fullscreen button
                fullscreenbtn.place_forget()
                fullscreenbtn.place(relx=0.96, rely=-0.8, relwidth=0.03, relheight=0.714)
            except:
                pass
            
            player_position_scale.configure(height=int(root.winfo_height()*0.07*0.5*0.5*0.05))
            Frame_for_mpv.lift()
            controls_frame.lift()
            fullscreenbtn.lift()
            fullscreenbtn.configure(text='↖')
            modeforfullscreen = 1
            
            try:
                if playing_title_textbox.get():root.title(f'JaTubePlayer {ver} by Jackaopen  -  {playing_title_textbox.get(1.0, "end").strip()}')
                else:root.title(f'JaTubePlayer {ver} by Jackaopen')
            except:
                pass
        
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
       



def fullscreen_change_state(event=None):## for btn
    if root.state() == 'normal':root.state('zoomed')
    elif root.state() == 'zoomed':root.state('normal')
    if event:time.sleep(0.1)


def fullscreen_detect_thread():## auto drag
    time.sleep(0.1)  # Initial delay
    while True:
        try:
            previous = root.state()
            time.sleep(0.01)  
            if previous != root.state():
                time.sleep(0.1) 
                ui_queue.put(lambda: fullscreen_widget_change())
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
            log_handle(content=f"inter {iter}")
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
                fullscreen_change_state()
            
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
                                selected_song_number = 0
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
    global cookies_dir,client_secret_path,auto_like_refresh,auto_sub_refresh,auto_check_ver,save_history,maxresolution,listen_chromeextension_thread,enable_drag_and_drop
    cookies_dir= CONFIG['cookie_path']
    client_secret_path = CONFIG['client_secret_path']
    log_handle(content=f"cookie {cookies_dir}")
    log_handle(content=f"client {client_secret_path}")  
    try:
        if CONFIG['auto_sub_refresh']:auto_sub_refresh.set(True)
        else:auto_sub_refresh.set(False)
        print("sub fin")
        if CONFIG['auto_like_refresh']:auto_like_refresh.set(True)
        else:auto_like_refresh.set(False)
        print("like fin")

        if CONFIG['vercheck']:auto_check_ver.set(True)
        else:auto_check_ver.set(False)
        print("ver fin")

        if CONFIG['record_history']:save_history.set(True)
        else:save_history.set(False)
        print("history fin")
        
        if CONFIG['open_with_fullscreen']:open_with_fullscreen.set(True)
        else:open_with_fullscreen.set(False)
        print("open fin")
        
        if CONFIG['enable_drag_and_drop']:enable_drag_and_drop.set(True)
        else:enable_drag_and_drop.set(False)
        print("dnd fin")

        if CONFIG['show_cache']:show_cache.set(True)
        else:show_cache.set(False)
        print("cache fin")


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

    buf_arg = {
        "cache": True,
        "cache-secs": 90,
        "demuxer-max-bytes": "1024MiB",
        "demuxer-max-back-bytes": "256MiB",
        "demuxer_readahead_secs": 60.0,
        "cache-pause": "yes",
        "cache-pause-wait": 2,
        "demuxer_thread": True,
        "audio_wait_open": 5.0,  
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
        wid=Frame_for_mpv.winfo_id(),
        log_handler=log_handle,
        vid="no" if audio_only.get() else "auto",
        keep_open=True,
        msg_level="ytdl_hook=debug,ffmpeg=warn,cplayer=warn",
        **buf_arg,
        **sub_arg
    )

    log_handle(content=str(True if playing_vid_mode == 1 else False))




    
def init_set_smtc():
    smtc.next_song_fun = playnextsong
    smtc.prev_song_fun = playprevsong
    smtc.pause_fun = pause
    smtc.iconpath = icondir

def init_set_dnd_handle():
    print("init dnd ... ")
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
            if playing_vid_mode == 0 :
                async_task.append(load_thumbnail_thread(asyncio_session,id,thumb))

            #adjust column width in playlisttreebox insert thread
            if playing_vid_mode ==0:
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
    global playing_vid_mode,selected_song_number,chrome_extension_url
    if setting_run_chrome_extension_server.get():
        if chrome_extension_flask.chrome_extension_url:
            log_handle(content=str(chrome_extension_flask.chrome_extension_url))
            chrome_extension_url = chrome_extension_flask.chrome_extension_url.split("&")[0]
            load_thread_queue.put((None,chrome_extension_url))
            playing_vid_mode = 3
            selected_song_number = None
            playlisttreebox.delete(*playlisttreebox.get_children())
            modetextbox.configure(state="normal")
            modetextbox.delete(0.0,tk.END)
            modetextbox.insert(tk.END,"Chrome extension video")
            modetextbox.configure(state="disabled")



            chrome_extension_flask.chrome_extension_url = None
        root.after(500,init_listen_chromeextension)

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
    global aiohttp,build, Credentials,google_auth_control,Ferner_encrptor
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
    
    log_handle(content=f"Total import time: {time.time()-time1:.3f}s")



def _extra_startup_imports():
    global update_sub_list, update_like_list, liked_channel, sub_channel,download_and_extract_dlp
    global MediaControlOverlay,chrome_extension_flask,requests

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
    import chrome_extension.chrome_extension_flask as chrome_extension_flask
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
    root.after(120,lambda:threading.Thread(daemon = True,target=dnd_path_listener).start())
    root.after(150,lambda:threading.Thread(daemon = True,target=load_thread).start())
    root.after(100,lambda:threading.Thread(daemon = True,target=start_async_eventloop).start())
    root.after(200,lambda:threading.Thread(daemon = True,target=fullscreen_detect_thread).start())
    root.after(850,lambda:threading.Thread(daemon = True,target=init_set_playertray).start())
    

    root.after(0,lambda:threading.Thread(daemon = True,target=_start_up).start())
    








sv_ttk.use_dark_theme() ### must be here or will overrider the style
style = ttk.Style()
style.configure("Treeview",
                rowheight=int(108*tkinter_scaling),
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
header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.0735)

title = ctk.CTkLabel(header_frame, text='🎵 JaTubePlayer', font=('Segoe UI', 20, 'bold'), 
                     text_color='#FF6B35', anchor="w")
title.place(relx=0.015, rely=0.2)

searchlistlabel = ctk.CTkLabel(header_frame, font=('Segoe UI', 13), text='🔍 Search:',
                               text_color='#888888', anchor="w", bg_color='transparent')
searchlistlabel.place(relx=0.1515, rely=0.28)

searchentry = ctk.CTkEntry(header_frame, font=('Segoe UI', 13), corner_radius=8,
                           placeholder_text="Search...",
                           border_color="#3e62dc", border_width=1)
searchentry.place(relx=0.2121, rely=0.18, relwidth=0.197, relheight=0.64)

search_btn = ctk.CTkButton(header_frame, text='🔎', corner_radius=8,
                           command=youtube_search, fg_color='#3e62dc', hover_color='#4a70f0',
                           font=('Segoe UI', 14))
search_btn.place(relx=0.415, rely=0.18, relwidth=0.0303, relheight=0.64)

playlistlabel = ctk.CTkLabel(header_frame, font=('Segoe UI', 13), text='📁 Playlist:',
                             text_color='#888888', anchor="w", bg_color='transparent')
playlistlabel.place(relx=0.462, rely=0.28)

userplaylistcombobox = ctk.CTkComboBox(header_frame, font=('Segoe UI', 13),
                                        values=user_playlists_name, state='readonly', corner_radius=8,
                                        fg_color="#363636", text_color="#c5c5c5",
                                        border_width=0,
                                        button_color="#363636",
                                        button_hover_color="#4a70f0",
                                        dropdown_fg_color="#363636", 
                                        dropdown_hover_color="#3e62dc",
                                        justify="left")
userplaylistcombobox.place(relx=0.530, rely=0.18, relwidth=0.121, relheight=0.64)

enter_playlist_btn = ctk.CTkButton(header_frame, text='▶ Enter', 
                                   command=enterplaylist, fg_color='#FF6B35', hover_color='#FF8555',
                                   corner_radius=8, font=('Segoe UI', 12, 'bold'))
enter_playlist_btn.place(relx=0.659, rely=0.18, relwidth=0.066, relheight=0.64)

searchentry.bind("<Return>", youtube_search)
userplaylistcombobox.bind("<Return>", enterplaylist)



# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE STATUS PANEL - Combined Chrome Extension & Discord Status
# ═══════════════════════════════════════════════════════════════════════════════
status_panel = ctk.CTkFrame(header_frame, fg_color="#151515", corner_radius=6, 
                            border_width=1, border_color="#3e62dc")
status_panel.place(relx=0.738, rely=0.10, relwidth=0.256, relheight=0.80)

chrome_ext_dot = ctk.CTkLabel(status_panel, text='●', font=('Arial', 14),
                               text_color='#333333')
chrome_ext_dot.place(relx=0.031, rely=0.168)

chrome_ext_text = ctk.CTkLabel(status_panel, text='Chrome Link', 
                                font=('Segoe UI', 12), text_color='#777777', anchor="w")
chrome_ext_text.place(relx=0.083, rely=0.198)



separator = ctk.CTkLabel(status_panel, text='│', font=('Segoe UI', 18), text_color='#444444')
separator.place(relx=0.296, rely=0.149)

discord_status_dot = ctk.CTkLabel(status_panel, text='●', font=('Arial', 14),
                                   text_color='#333333')
discord_status_dot.place(relx=0.345, rely=0.168)

discord_status_text = ctk.CTkLabel(status_panel, text='Discord', 
                                    font=('Segoe UI', 12), text_color='#777777', anchor="w")
discord_status_text.place(relx=0.397, rely=0.198)


separator2 = ctk.CTkLabel(status_panel, text='│', font=('Segoe UI', 18), text_color='#444444')
separator2.place(relx=0.540, rely=0.149)

# Google Profile Container - styled circular frame for profile picture


google_status_profile_pic_label = ctk.CTkLabel(status_panel, text='X', font=('Segoe UI', 14),
                                               text_color='#555555', fg_color="transparent", 
                                               width=15, height=26, corner_radius=13)
google_status_profile_pic_label.place(relx=0.66, rely=0.5, anchor="center")

google_status_text = ctk.CTkTextbox(status_panel, 
                                   font=('Segoe UI', 12), text_color='#888888', wrap="none",
                                   border_width=0, height=1,fg_color="transparent")
google_status_text.place(relx=0.715, rely=0.13, relwidth=0.27)
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
                    profile_pic = profile_pic.resize((26, 26), Image.LANCZOS)
                    ctk_image = ctk.CTkImage(profile_pic, size=(26, 26))
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
right_panel_frame.place(relx=0.617, rely=0.081, relwidth=0.375, relheight=0.684)

mode_header_frame = ctk.CTkFrame(right_panel_frame, fg_color="#252525", corner_radius=8)
mode_header_frame.place(relx=0.020, rely=0.017, relwidth=0.960, relheight=0.129)

mode_icon_label = ctk.CTkLabel(mode_header_frame, text='📋', font=('Segoe UI', 20))
mode_icon_label.place(relx=0.021, rely=0.25)

modetextbox = tk.Text(mode_header_frame, font=('Segoe UI', 11), width=65, fg='#c5c5c5',
                      bg='#252525', relief='flat', height=2, wrap='char', borderwidth=0)
modetextbox.place(relx=0.095, rely=0.167)
modetextbox.insert(tk.END, 'Please login or search something')
modetextbox.configure(state='disabled')



# Playlist Treeview
playlisttreebox = ttk.Treeview(right_panel_frame, columns=("title"), height=5, 
                               selectmode="browse", show='tree headings')
playlisttreebox.heading("#0", text="")
playlisttreebox.heading("title", text="")
playlisttreebox.column("#0", width=180, anchor="w", stretch=False)
playlisttreebox.column("title", width=1000, anchor="w", stretch=False)
playlisttreebox.place(relx=0.020, rely=0.161, relwidth=0.925, relheight=0.796)
playlisttreebox.bind('<Double-1>', download_and_play)
playlisttreebox.bind('<ButtonRelease-1>', get_selected_vid)

Y_scrollbar = ttk.Scrollbar(right_panel_frame)
X_scrollbar = ttk.Scrollbar(right_panel_frame, orient='horizontal')
X_scrollbar.configure(command=playlisttreebox.xview)
Y_scrollbar.configure(command=playlisttreebox.yview)
playlisttreebox.configure(xscrollcommand=X_scrollbar.set, yscrollcommand=Y_scrollbar.set)
Y_scrollbar.place(relx=0.945, rely=0.161, relheight=0.796)
X_scrollbar.place(relx=0.020, rely=0.957, relwidth=0.925)

playlist_btn_frame = ctk.CTkFrame(root, fg_color="#1e1e1e", border_color="#333333", border_width=1, corner_radius=10)
playlist_btn_frame.place(relx=0.617, rely=0.765, relwidth=0.375, relheight=0.213)

recommendation_btn = ctk.CTkButton(playlist_btn_frame, text='✨ Recommend',
                                    command=lambda: threading.Thread(daemon=True, target=init_get_recommendation).start(),
                                    fg_color='#2E2E2E', hover_color='#404040', corner_radius=8,
                                    font=('Segoe UI', 13), border_width=1, border_color='#444444')
recommendation_btn.place(relx=0.020, rely=0.069, relwidth=0.303, relheight=0.241)

sub_btn = ctk.CTkButton(playlist_btn_frame, text='📺 Subscriptions',
                        command=lambda: get_sub_channel(0), fg_color='#2E2E2E', hover_color='#404040',
                        corner_radius=8, font=('Segoe UI', 13), border_width=1, border_color='#444444')
sub_btn.place(relx=0.343, rely=0.069, relwidth=0.303, relheight=0.241)

like_btn = ctk.CTkButton(playlist_btn_frame, text='❤️Liked',
                         command=lambda: get_liked_vid(0), fg_color='#2E2E2E', hover_color='#404040',
                         corner_radius=8, font=('Segoe UI', 13), border_width=1, border_color='#444444')
like_btn.place(relx=0.667, rely=0.069, relwidth=0.303, relheight=0.241)

playselectedfile = ctk.CTkButton(playlist_btn_frame, text='📄 File',
                                  command=lambda: load_local_files(0), fg_color='#2E2E2E',
                                  hover_color='#404040', corner_radius=8, font=('Segoe UI', 13),
                                  border_width=1, border_color='#444444')
playselectedfile.place(relx=0.020, rely=0.359, relwidth=0.303, relheight=0.207)

playselectedfolder = ctk.CTkButton(playlist_btn_frame, text='📁 Folder',
                                    command=lambda: load_local_files(1), fg_color='#2E2E2E',
                                    hover_color='#404040', corner_radius=8, font=('Segoe UI', 13),
                                    border_width=1, border_color='#444444')
playselectedfolder.place(relx=0.343, rely=0.359, relwidth=0.303, relheight=0.207)

playselectedsong = ctk.CTkButton(playlist_btn_frame, text='▶ Play Selected',
                                  command=lambda: download_and_play(), fg_color='#3e62dc',
                                  hover_color='#4a70f0', corner_radius=8, font=('Segoe UI', 12, 'bold'))
playselectedsong.place(relx=0.667, rely=0.359, relwidth=0.303, relheight=0.241)

page_nav_frame = ctk.CTkFrame(playlist_btn_frame, fg_color="#262626", corner_radius=8)
page_nav_frame.place(relx=0.020, rely=0.634, relwidth=0.949, relheight=0.310)

prev_page_btn = ctk.CTkButton(page_nav_frame, text='◀ Prev',
                               command=lambda: page_control(2), fg_color='#2E2E2E', hover_color='#404040',
                               corner_radius=8, font=('Segoe UI', 13), border_width=1, border_color='#444444')
prev_page_btn.place(relx=0.017, rely=0.133, relwidth=0.298, relheight=0.711)

next_page_btn = ctk.CTkButton(page_nav_frame, text='Next ▶',
                               command=lambda: page_control(1), fg_color='#2E2E2E', hover_color='#404040',
                               corner_radius=8, font=('Segoe UI', 13), border_width=1, border_color='#444444')
next_page_btn.place(relx=0.336, rely=0.133, relwidth=0.298, relheight=0.711)

liked_page_label = ctk.CTkLabel(page_nav_frame, font=('Segoe UI', 13), text='📄',
                                anchor="w", fg_color="transparent")
liked_page_label.place(relx=0.681, rely=0.222)

liked_page_num_label = ctk.CTkLabel(page_nav_frame, font=('Segoe UI', 13), text='',
                                     text_color='#888888', anchor="w", fg_color="transparent")
liked_page_num_label.place(relx=0.745, rely=0.222)

# ─────────────────────────────────────────────────────────────────────────────
# LEFT PANEL - Video Player & Controls
# ─────────────────────────────────────────────────────────────────────────────
video_container = ctk.CTkFrame(root, fg_color="#0a0a0a", corner_radius=10, border_width=2, border_color="#333333")
video_container.place(relx=0.008, rely=0.081, relwidth=0.602, relheight=0.669)

Frame_for_mpv.place(relx=0.015, rely=0.096, relwidth=0.587, relheight=0.640)
Frame_for_mpv.lift()

# ─────────────────────────────────────────────────────────────────────────────
# PLAYER CONTROLS - Below video
# ─────────────────────────────────────────────────────────────────────────────
controls_frame = ctk.CTkFrame(root, fg_color="#1a1a1a", corner_radius=10, border_width=1, border_color="#333333")
controls_frame.place(relx=0.008, rely=0.757, relwidth=0.602, relheight=0.235)

progress_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
progress_frame.place(relx=0.019, rely=0.031, relwidth=0.962, relheight=0.313)

player_pos_label = ctk.CTkLabel(progress_frame, font=('Segoe UI Mono', 14),
                                textvariable=pos_for_label, text_color="#7d9bff", anchor="e")
player_pos_label.place(relx=0, rely=0.06, relwidth=0.092)

player_position_scale = ctk.CTkSlider(progress_frame, from_=0, command=scale_click,
                                       progress_color='#3e62dc', button_color='#5080ff',
                                       button_hover_color='#6090ff', fg_color='#333333')
player_position_scale.set(0)
player_position_scale.bind('<ButtonRelease-1>', scale_release)
player_position_scale.place(relx=0.105, rely=0.1, relwidth=0.784, relheight=0.32)

player_song_length_label = ctk.CTkLabel(progress_frame, font=('Segoe UI Mono', 14),
                                         text_color="#9E9E9E", anchor="w", text='')
player_song_length_label.place(relx=0.902, rely=0.06, relwidth=0.092)

playback_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
playback_frame.place(relx=0.252, rely=0.219, relwidth=0.503, relheight=0.313)

prevsong = ctk.CTkButton(playback_frame, text='⏮', command=playprevsong,
                         fg_color='#2E2E2E', hover_color='#404040', corner_radius=25,
                         font=('Segoe UI', 15))
prevsong.place(relx=0.05, rely=0, relwidth=0.18, relheight=0.7)

pausebutton = ctk.CTkButton(playback_frame, textvariable=pauseStr,
                            command=lambda: pause(1), fg_color='#3e62dc', hover_color='#4a70f0',
                            corner_radius=25, font=('Segoe UI', 15, 'bold'))
pausebutton.place(relx=0.28, rely=0, relwidth=0.18, relheight=0.7)
pauseStr.set('▶')

stopbutton = ctk.CTkButton(playback_frame, text='⏹', command=stop_playing_video,
                           fg_color='#2E2E2E', hover_color='#404040', corner_radius=25,
                           font=('Segoe UI', 15))
stopbutton.place(relx=0.51, rely=0, relwidth=0.18, relheight=0.7)

nextsong = ctk.CTkButton(playback_frame, text='⏭', command=playnextsong,
                         fg_color='#2E2E2E', hover_color='#404040', corner_radius=25,
                         font=('Segoe UI', 15))
nextsong.place(relx=0.74, rely=0, relwidth=0.18, relheight=0.7)

player_loading_label = ctk.CTkLabel(playback_frame, font=('Segoe UI', 13), text='',
                                     text_color='#FF6B35', anchor="w")
player_loading_label.place(relx=0.775, rely=0.1, relwidth=0.25)

volume_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
volume_frame.place(relx=0.780, rely=0.219, relwidth=0.208, relheight=0.30)

player_volume_label = ctk.CTkLabel(volume_frame, font=('Segoe UI', 16), text='🔊',
                                   text_color='#888888', anchor="e")
player_volume_label.place(relx=0, rely=0.125, relwidth=0.182)

player_volume_scale = ctk.CTkSlider(volume_frame, from_=0, to=120, command=set_volume,
                                    progress_color='#FF6B35', button_color='#FF8555',
                                    button_hover_color='#FFA575', fg_color='#333333')
player_volume_scale.set(50)
player_volume_scale.bind('<MouseWheel>', set_volume_wheel)
player_volume_scale.place(relx=0.212, rely=0.25, relwidth=0.727, relheight=0.30)

Frame_for_mpv.bind('<MouseWheel>', set_volume_wheel)

mode_frame = ctk.CTkFrame(controls_frame, fg_color="#252525", corner_radius=8)
mode_frame.place(relx=0.019, rely=0.225, relwidth=0.289, relheight=0.188)

mode_label = ctk.CTkLabel(mode_frame, text='Mode:', font=('Segoe UI', 14), text_color="#6A6969")
mode_label.place(relx=0.035, rely=0.1)

player_mode_continue = ctk.CTkRadioButton(mode_frame, text='▶▶', variable=player_mode_selector,
                                           value='continue', 
                                           font=('Segoe UI', 11), radiobutton_width=16, radiobutton_height=16)
player_mode_continue.place(relx=0.261, rely=0.267)

player_mode_replay = ctk.CTkRadioButton(mode_frame, text='🔁', variable=player_mode_selector,
                                         value='replay', 
                                         font=('Segoe UI', 11), radiobutton_width=16, radiobutton_height=16)
player_mode_replay.place(relx=0.487, rely=0.267)

player_mode_random = ctk.CTkRadioButton(mode_frame, text='🔀', variable=player_mode_selector,
                                         value='random', 
                                         font=('Segoe UI', 11), radiobutton_width=16, radiobutton_height=16)
player_mode_random.place(relx=0.748, rely=0.267)

now_playing_frame = ctk.CTkFrame(controls_frame, fg_color="#252525", corner_radius=8)
now_playing_frame.place(relx=0.019, rely=0.5, relwidth=0.629, relheight=0.438)

np_icon = ctk.CTkLabel(now_playing_frame, text='🎶', font=('Segoe UI', 16))
np_icon.place(relx=0.016, rely=0.171)

playing_title_textbox = tk.Text(now_playing_frame, font=('Segoe UI', 14), width=45, fg='#c5c5c5',
                                bg='#252525', relief='flat', wrap='word', state='disabled',
                                height=2, borderwidth=0)
playing_title_textbox.place(relx=0.07, rely=0.086)



action_btn_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
action_btn_frame.place(relx=0.654, rely=0.469, relwidth=0.340, relheight=0.469)

setting_btn = ctk.CTkButton(action_btn_frame, text='⚙️ settings', command=setting_frame,
                            fg_color='#FF6B35', hover_color='#FF8555', corner_radius=8,
                            font=('Segoe UI', 14))
setting_btn.place(relx=0, rely=0.067, relwidth=0.778, relheight=0.467)

select_info_btn = ctk.CTkButton(action_btn_frame, text='ℹ️selected info',
                                 command=lambda: vid_info_frame(1), fg_color='#2E2E2E',
                                 hover_color='#404040', corner_radius=8, font=('Segoe UI', 12),
                                 border_width=1, border_color='#444444')
select_info_btn.place(relx=0, rely=0.6, relwidth=0.380, relheight=0.4)

playing_info_btn = ctk.CTkButton(action_btn_frame, text='📊 playing info',
                                  command=lambda: vid_info_frame(2), fg_color='#2E2E2E',
                                  hover_color='#404040', corner_radius=8, font=('Segoe UI', 11),
                                  border_width=1, border_color='#444444')
playing_info_btn.place(relx=0.426, rely=0.6, relwidth=0.370, relheight=0.4)

fullscreenbtn = ctk.CTkButton(action_btn_frame, text='⛶', command=fullscreen_change_state,
                               fg_color='#2E2E2E', hover_color='#404040', corner_radius=10,
                               border_color='#444444', border_width=1,
                               font=('Segoe UI', 15))
fullscreenbtn.place(relx=0.815, rely=0.6, relwidth=0.148, relheight=0.4)



root.bind('<Escape>', fullscreen_change_state)
root.bind('<space>', lambda event: pause(2))
root.bind("<KeyPress-Left>", lambda event: set_position_keyboard(1))
root.bind("<KeyPress-Right>", lambda event: set_position_keyboard(2))
root.bind("<KeyRelease-Right>", arrow_release)
root.bind("<KeyRelease-Left>", arrow_release)

modeforfullscreen = 0


root.mainloop()