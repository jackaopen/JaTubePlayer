from utils.check_internet import check_internet
from effect.blur_for_client import blur
from utils.get_media_info import get_info
from loader.get_info_loader import get_info_loader_
import tkinter as tk
import customtkinter as ctk
import queue
import win32gui
import threading


@check_internet
def vid_info_frame(mode,
                   log_handle:object,
                   playing_vid_mode:int,
                   selected_song_number:int,
                   ui_queue:queue.Queue,
                   ver:str,
                   messagebox:object,
                   root:object,
                   icondir:str,
                   playing_vid_info_dict:dict,
                   get_info_loader:get_info_loader_,
                   vid_url:list,
                   blur_window:bool,
                   blur_hexColor:str
                   )->ctk:
    '''
    mode: 1 for selected video, 2 for currently playing video
    '''
    global info
    log_handle(
        content=f"info frame mode: {mode}",
        errtype='info',
        component='video_info',
    )
    try:
        if info and info.winfo_exists():
            info.lift()
            info.deiconify()
        else:
            raise Exception("info window already opened")
    except:
        if mode == 1:
            if playing_vid_mode == 0 or playing_vid_mode == 4 or (playing_vid_mode == 3 and len(vid_url) > 0):
                if selected_song_number is None:
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','No video selected'))
                    return
                if playing_vid_mode == 4 and not vid_url[selected_song_number].startswith(('https://','http://')):
                    ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','The selected video is a local file, video info function is only available for online videos'))
                    ui_queue.put(lambda: info.destroy())
                    return

            if playing_vid_mode in (1, 2):
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer{ver}','Video info function is only available for YouTube videos'))
                return
        elif mode == 2:
            if playing_vid_mode in (1, 2):
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
        if blur_window.get():
            root.after(200,lambda:blur(win32gui.FindWindow(None,info.title()),  hexColor=blur_hexColor.get()))

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
            log_handle(
                content=f"load selected info, mode: {playing_vid_mode}, url: {vid_url[selected_song_number] if selected_song_number is not None and len(vid_url) > 0 else 'N/A'}",
                errtype='info',
                component='video_info',
            )
            try:
                if selected_song_number is not None:

                    ui_queue.put(lambda: info.title('loading info...'))
                    _,info_dict = get_info(
                                        loader=get_info_loader,
                                        target_url=vid_url[selected_song_number]
                                    )
                        
                    
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
                else:
                    ui_queue.put(lambda: messagebox.showwarning(f'JaTubePlayer {ver}','No video selected'))
                    return

            except Exception as e : 
                log_handle(
                    content=f"Failed to populate selected video information: {e}",
                    errtype="error",
                    component="video_info",
                )
                try:       
                    ui_queue.put(lambda: description_text.configure(state='normal'))
                    ui_queue.put(lambda err=e: description_text.insert(tk.END, f'opps we got some problmes\n{err}'))
                    ui_queue.put(lambda: description_text.configure(state='disabled'))
                except:pass

        def loadplayinginfo():

            if not playing_vid_info_dict:
                ui_queue.put(lambda: messagebox.showerror(f'JaTubePlayer {ver}', 'No video is currently playing'))
                ui_queue.put(lambda: info.destroy())
                return
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
            infothread = threading.Thread(daemon=True, target=loadselectedinfo)
            infothread.start()
        elif mode == 2:
            infothread = threading.Thread(daemon=True, target=loadplayinginfo)
            infothread.start()
        return info
