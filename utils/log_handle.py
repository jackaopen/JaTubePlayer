from collections import deque
from datetime import datetime
import queue
import tkinter as tk
import customtkinter as ctk
from notification.ctkmessagebox import ctk_messagebox 
from typing import Callable
from effect.blur_for_client import blur
import win32gui

YTDLP_ERROR_MESSAGES = (
        (("live event will",), "This live event hasn't started yet"),
        (("members-only", "members only"), "This video is members-only"),
        (("private video", "video is private"), "This video is private"),
        (("sign in", "not a bot"), "YouTube is requesting account verification"),
        (("not currently live",), "The channel is not currently live"),
        (("does not exist",), "The video does not exist"),
        (("no video formats found",), "No video formats were found"),
        (("unavailable",), "Video unavailable"),
        (("cookies are no longer valid",), "Your account cookies may be invalid or expired"),
        (("premieres","premieres in",), "This is a premiere video, and it hasn't started yet"),
        (("age-restricted",), "This video is age-restricted"),
        (("geo-restricted",), "This video is geo-restricted"),
    )

class log_handler_:
    def __init__(self,
                ui_queue:queue.Queue,
                ver:str,
                mpv_log:deque,
                messagebox:ctk_messagebox,
                force_stop_loading:Callable[[], None],
                root:tk.Tk,
                icondir:str,
                blur_callable:Callable[[],tuple[str,bool]]
                ):
        '''
        blur_callable should retrun tuple of (hexColor,blur_window:bool)
        '''
        self.log_handle_frame = log_handle_frame(
            root=root,
            mpv_log=mpv_log,
            icondir=icondir,
            blur_callable=blur_callable
        )
        self.ytdlp_log_handler = ytdlp_log_handler(log_handle=self.log_handle)
        
        self.ui_queue = ui_queue
        self.ver = ver
        self.mpv_log = mpv_log
        self.messagebox = messagebox
        self.force_stop_loading = force_stop_loading
    mpv_log = deque(maxlen=2000)

    

    def _show_ytdlp_error(self, content: str) -> None:
        normalized = content.casefold()
        
        for patterns, message in YTDLP_ERROR_MESSAGES:
            if any(pattern in normalized for pattern in patterns):
                self.force_stop_loading()
                self.ui_queue.put(
                    lambda message=message:
                    self.messagebox.showerror(f"JaTubePlayer {self.ver}", message)
                )
                return

    def log_handle(self,
                   content:str,
                   errtype: str = "info",
                   component: str = "main_system")-> None:
        
        level = str(errtype or "info").strip().lower()
        component = str(component or "main_system").strip()
        content = str(content)

        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"{timestamp} | {level.upper():<7} | {component:<12} | {content}"

        self.mpv_log.append(line)
        print(line)

        # Tk operations remain on the UI thread
        if self.log_handle_frame.log_frame is not None and self.log_handle_frame.log_frame.winfo_exists():
            self.ui_queue.put(lambda line=line: self.log_handle_frame.insert_log(line))

        if level == "error" and component == "yt-dlp":
            self._show_ytdlp_error(content)


class ytdlp_log_handler:
    def __init__(self,
                 log_handle: Callable):
        self.log_handle = log_handle
        
    def debug(self, msg):
        self.log_handle(errtype='debug',component='yt-dlp',content=msg)
    def info(self, msg):
        self.log_handle(errtype='info',component='yt-dlp',content=msg)
    def warning(self, msg):
        self.log_handle(errtype='warn',component='yt-dlp',content=msg)
    def error(self, msg):
        self.log_handle(errtype='error',component='yt-dlp',content=msg)


class log_handle_frame:
    def __init__(self,
                 root,
                 mpv_log: deque,
                 blur_callable: Callable[[], tuple[str, bool]],
                 icondir: str = "",
                 
                 ):

        self.root = root
        self.mpv_log = mpv_log
        self.icondir = icondir
        self.blur_callable = blur_callable
        self.log_frame = None
        self.log_text = None

    def show_mpv_log(self):
        if self.log_frame is not None and self.log_frame.winfo_exists():
            self.log_frame.deiconify()
            self.log_frame.lift()
            self.refresh_log()
            return

        self.log_frame = tk.Toplevel(self.root, bg='#1a1a1a')
        self.log_frame.title('JaTubePlayer Log Viewer')
        self.log_frame.resizable(True, True)
        self.log_frame.geometry('800x400')
        self.log_frame.minsize(400, 200)
        self.log_frame.attributes('-topmost', True)
        if self.icondir:
            try:
                self.log_frame.iconbitmap(self.icondir)
            except Exception:
                pass
        self.log_frame.protocol('WM_DELETE_WINDOW', self.close)

        main_frame = tk.Frame(self.log_frame, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        title_label = tk.Label(main_frame, text='📋 JaTubePlayer Log Viewer', font=('Segoe UI', 12, 'bold'),
                               bg='#1a1a1a', fg='#ffffff')
        title_label.pack(anchor='w', pady=(0, 8))

        text_frame = tk.Frame(main_frame, bg='#2d2d2d')
        text_frame.pack(fill='both', expand=True)

        scrollbar = ctk.CTkScrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        self.log_text = tk.Text(text_frame, font=('Consolas', 10), bg='#2d2d2d', fg='#e0e0e0',
                                insertbackground='white', selectbackground='#4a4a4a',
                                relief='flat', padx=8, pady=8, wrap='word',
                                yscrollcommand=scrollbar.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.configure(command=self.log_text.yview)

        btn_frame = tk.Frame(main_frame, bg='#1a1a1a')
        btn_frame.pack(fill='x', pady=(8, 0))
        ctk.CTkButton(btn_frame, text='Refresh', width=100, command=self.refresh_log).pack(side='left')
        ctk.CTkButton(btn_frame, text='Close', width=100, command=self.close).pack(side='right')

        self.refresh_log()
        hexcolor , blur_window = self.blur_callable()
        if blur_window:
            blur(win32gui.FindWindow(None, self.log_frame.title()),
                 hexColor=hexcolor)

    def refresh_log(self):
        if self.log_text is None or not self.log_text.winfo_exists():
            return
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        for entry in self.mpv_log:
            self.log_text.insert(tk.END, entry + '\n')
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)

    def insert_log(self, content: str):
        if self.log_text is None or not self.log_text.winfo_exists():
            return
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, content + '\n')
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)

    def close(self):
        if self.log_frame is not None and self.log_frame.winfo_exists():
            self.log_frame.destroy()
        self.log_frame = None
        self.log_text = None

