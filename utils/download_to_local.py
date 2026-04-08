import re,os
from notification.wintoast_notify import ToastNotification
from tkinter import BooleanVar
from tkinter import messagebox
import time,threading
import customtkinter as ctk
import queue

cancel_download = threading.Event()
ytdlp_killed = threading.Event()
file_deletion_queue = queue.Queue()
def download_to_local(res:str,
                      mode:int,
                      cookies_dir:str,
                      yt_dlp:object,
                      target_vid_url:str,
                      title:str,
                      download_path:str,
                      current_dir:str,
                      icondir:str,
                      ver:str,
                      root:ctk.CTkToplevel,
                      ffmpeg:object,
                      ytdlp_log_handle:object,
                      deno_path:str,
                      is_downloading:BooleanVar,
                      ctk_messagebox:object,
                      ):
    
    '''
    pass the URL and title 
    Note the vid should not be a live stream, the function will NOT check  if it is live
    mode 0: audio only
    mode 1: video + audio
    '''
    try:is_downloading.set(True)
    except:pass
    
    def _pre_download_cleanup():
        if not os.path.exists(os.path.join(current_dir,'user_data','downloaded_file')):
            os.makedirs(os.path.join(current_dir,'user_data','downloaded_file'))
            
        try:os.remove(os.path.join(current_dir,'user_data','downloaded_file','tempvid.mp4'))
        except:pass
        try:os.remove(os.path.join(current_dir,'user_data','downloaded_file','tempaud.webm'))
        except:pass
        try:os.remove(os.path.join(current_dir,'user_data','downloaded_file','tempaud.webm.part'))
        except:pass
        try:os.remove(os.path.join(current_dir,'user_data','downloaded_file','tempvid.mp4.part'))
        except:pass

    def progress_hook(d):
        global cancel_download,ytdlp_killed
        # Check for cancellation on each progress update
        print("hook")
        if cancel_download.is_set():
            print("Download cancelled by user via progress hook.")
            ytdlp_killed.set()
            raise yt_dlp.utils.DownloadCancelled("Download cancelled by user[progress hook].")
            
        else:
            try:
                if d['status'] == 'downloading':

                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    
                    fragment_index = d.get('downloaded_bytes', 0) 
                    fragment_count = d.get('total_bytes', 1)  
                    
                    if fragment_index and fragment_count:
                        progress = int(fragment_index) / int(fragment_count)
                        root.after(0,lambda:bar.set(progress))
                
                    eta = d.get('eta') or 0
                    speed = d.get('speed') or 0
                    
                    downloaded_mb = downloaded_bytes / 1024**2
                    speed_mb = speed / 1024**2
                    
                    root.after(0,lambda:sub_info_label.configure(
                        text=f"Downloaded {downloaded_mb:.1f} MB\n"
                            f"ETA: {eta:.1f}s at {speed_mb:.1f} MB/s"))
                elif d['status'] == 'finished':
                    root.after(0,lambda:bar.set(1.0))
                    root.after(0,lambda:sub_info_label.configure(text=""))
            except Exception as e:print(e)
                    
        
            

        
    def _start_download():
        global cancel_download,ytdlp_killed
        nonlocal download_path
        cancel_download.clear()
        ytdlp_killed.clear()

        

        
        try:
            better_name = re.sub(r'[\\/:*?"<>|#]', ' ', title)
            main_label.configure(state='normal')
            main_label.delete('0.0', 'end')
            main_label.insert('0.0', f"Downloading: {title}")
            main_label.configure(state='disabled')
            if mode == 0:
                if download_path == '[player]/user_data/downloaded_file':
                    download_path = os.path.join(current_dir,'user_data','downloaded_file',f'{better_name}')
                else:download_path = os.path.join(download_path,f'{better_name}')
                down_tdl_opt = {
                            'outtmpl':download_path,
                            'format' : 'bestaudio/best',
                            'progress_hooks': [progress_hook],
                            'logger': ytdlp_log_handle,
                            'postprocessors': [{
                            'key': 'FFmpegExtractAudio',  # Extract audio after download
                            'preferredcodec': 'mp3',  
                            'preferredquality': '192'  
                            }],'ignore_no_formats_error': True,
                            'js-runtimes':f'deno:{deno_path}'    
    
                            }  
                if cookies_dir:
                    down_tdl_opt['cookiefile'] = cookies_dir 
                with yt_dlp.YoutubeDL(down_tdl_opt) as ydl:ydl.download(target_vid_url)

                main_label.configure(state='normal')
                main_label.delete('0.0', 'end')
                main_label.insert('0.0', f"processing video and audio...")
                main_label.configure(state='disabled')
                
            else:

                if os.path.exists(os.path.join(current_dir,'user_data','downloaded_file','tempvid.mp4')):os.remove(os.path.join(current_dir,'user_data','downloaded_file','tempvid.mp4'))
                if os.path.exists(os.path.join(current_dir,'user_data','downloaded_file','tempaud.webm')):os.remove(os.path.join(current_dir,'user_data','downloaded_file','tempaud.webm'))
                down_tdl_opt = {
                            'outtmpl':os.path.join(current_dir,'user_data','downloaded_file','tempvid.mp4'),
                            'format' : f'bestvideo[height<={res}]',
                            'progress_hooks': [progress_hook],
                            'ignore_no_formats_error': True,
                            'logger': ytdlp_log_handle,
                            'js-runtimes':f'deno:{deno_path}'
        

                            }
                
                if cookies_dir:
                    down_tdl_opt['cookiefile'] = cookies_dir 
                with yt_dlp.YoutubeDL(down_tdl_opt) as ydl:ydl.download(target_vid_url)
                down_tdl_opt = {
                            'outtmpl':os.path.join(current_dir,'user_data','downloaded_file','tempaud.webm'),
                            'format' : 'bestaudio',
                            'progress_hooks': [progress_hook],
                            'ignore_no_formats_error': True,
                            'logger': ytdlp_log_handle,
                            'js-runtimes':f'deno:{deno_path}'
                            }    
                if cookies_dir:
                    down_tdl_opt['cookiefile'] = cookies_dir   
                if cancel_download.is_set():return
                with yt_dlp.YoutubeDL(down_tdl_opt) as ydl:ydl.download(target_vid_url)
                vid = ffmpeg.input(os.path.join(current_dir,'user_data','downloaded_file','tempvid.mp4'))
                aud = ffmpeg.input(os.path.join(current_dir,'user_data','downloaded_file','tempaud.webm'))

                try:
                    try:os.remove(os.path.join(current_dir,'user_data','downloaded_file',f'{better_name}.mp4'))
                    except:pass
                    bar.place_forget()
                    main_label.configure(state='normal')
                    main_label.delete('0.0', 'end')
                    main_label.insert('0.0', f"processing video and audio...")
                    main_label.configure(state='disabled')

                    download_frame.update()

                    if download_path == '[player]/user_data/downloaded_file':
                        download_path = os.path.join(current_dir,'user_data','downloaded_file',f'{better_name}.mp4')
                    else:
                        download_path = os.path.join(download_path,f'{better_name}.mp4')
                    ffmpeg.output(vid,aud,
                                download_path,
                                vcodec='copy', 
                                acodec='aac',
                                audio_bitrate='192k',
                                ).run()
                    
                except Exception as e:messagebox.showerror(f'JaTubePlayer {ver}',e)
                os.remove(os.path.join(current_dir,'user_data','downloaded_file','tempvid.mp4'))
                os.remove(os.path.join(current_dir,'user_data','downloaded_file','tempaud.webm'))

            main_label.configure(state='normal')
            main_label.delete('0.0', 'end')
            main_label.insert('0.0', f"finished! you can close this window if it dont close automatically")
            main_label.configure(state='disabled')

            ToastNotification().notify(app_id="JaTubePlayer", 
                title=f'JaTubePlayer {ver} Download', 
                msg=f'Downloaded : {better_name}', 
                duration='short', 
                icon = icondir)
        except yt_dlp.utils.DownloadCancelled:
            ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver} Download', msg=f'Download cancelled : {better_name}', duration='short', icon=icondir)
        except Exception as e:
            print(e)
            ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver} Download', msg=f'Download failed : {better_name}\n{e}', duration='short', icon=icondir)
        except yt_dlp.utils.DownloadError as de:
            print(de)
            ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {ver} Download', msg=f'Download failed : {better_name}\n{de}', duration='short', icon=icondir)

        time.sleep(1)
        try:is_downloading.set(False)
        except:pass
        try:
            download_frame.destroy()
        except:pass





    _pre_download_cleanup()
    downloadthread = threading.Thread(target=_start_download,daemon=False)# daemon False to keep thread alive until done

    def _on_close():
        global cancel_download
        if ctk_messagebox.askyesno(title="JaTubePlayer Download",
                                   message="Are you sure you want to cancel the download?"):
            print("Download cancelled by user.")
            
            cancel_download.set()
            
            t1 = time.time()
            while ytdlp_killed.is_set() == False and time.time() - t1 < 5:
                ytdlp_log_handle.info("Waiting for yt-dlp to acknowledge cancellation...")
                time.sleep(1)
            
            file_deletion_queue.put(os.path.join(current_dir,'user_data','downloaded_file','tempvid.mp4'))
            file_deletion_queue.put(os.path.join(current_dir,'user_data','downloaded_file','tempaud.webm'))
            file_deletion_queue.put(os.path.join(current_dir,'user_data','downloaded_file',"tempaud.webm.part"))
            file_deletion_queue.put(os.path.join(current_dir,'user_data','downloaded_file',"tempvid.mp4.part"))
            
            # Prevent infinite loop - max 10 retries per file
            retry_count = 0
            max_total_retries = 5
            
            while not file_deletion_queue.empty() and retry_count < max_total_retries:
                time.sleep(0.5)
                file_path = file_deletion_queue.get()
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        ytdlp_log_handle.info(f"Removed file: {file_path}")
                except FileNotFoundError:
                    pass
                except PermissionError:
                    retry_count += 1
                    if retry_count < max_total_retries:
                        print(f"File locked, retry {retry_count}/{max_total_retries}: {file_path}")
                        file_deletion_queue.put(file_path)    
                    else:
                        print(f"Could not remove {file_path}: Still locked after {max_total_retries} retries")
                except Exception as e:
                    print(f"Could not remove {file_path}: {e}")
            is_downloading.set(False)
            try:download_frame.destroy()
            except:pass

    

    # build download frame
    download_frame = ctk.CTkToplevel(root) 
    download_frame.title(f'JaTubePlayer {ver} Download')
    download_frame.geometry(f"500x210+{root.winfo_screenwidth()/2}+{root.winfo_screenheight()/2}")
    download_frame.resizable(False, False)
    download_frame.attributes("-topmost", True)
    download_frame.protocol("WM_DELETE_WINDOW", _on_close)  # Disable close button
    

    if icondir: root.after(200, lambda: download_frame.iconbitmap(icondir))

    main_label = ctk.CTkTextbox(download_frame, font=('Arial', 14),height=50, width=480)
    main_label.delete('0.0', 'end')
    main_label.insert('0.0', f"Preparing to download...")
    main_label.configure(state='disabled')
    main_label.pack(pady=10)

    
    bar = ctk.CTkProgressBar(download_frame, width=250)
    bar.pack(pady=5)
    bar.set(0)

    sub_info_label = ctk.CTkLabel(download_frame, text=f"", font=('Arial', 12))
    sub_info_label.pack(pady=10)

    cancel_btn = ctk.CTkButton(download_frame, text="Cancel Download", command=lambda: threading.Thread(target=_on_close).start())
    cancel_btn.pack(pady=5)

    download_frame.update()
    time.sleep(1)

    downloadthread.start()           


if __name__ == "__main__":
    import yt_dlp
    import yt_dlp.version
    import ffmpeg
    import logging
    class ytdlp_log_handler():
        def debug(self, msg):print(msg)
        def info(self, msg):print(msg)
        def warning(self, msg):print(msg)
        def error(self, msg):print(msg)
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create main window
    test_root = ctk.CTk()
    test_root.withdraw()  # Hide main window for test
    
    # Test parameters
    test_url = "https://www.youtube.com/watch?v=Xc9Y7Dw3ffw8"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(yt_dlp.version.__version__)

    
    # Test with video download (mode=1)
    download_to_local(
        res="1080",
        mode=1,  # Video + Audio
        cookies_dir="",
        yt_dlp=yt_dlp,
        target_vid_url=test_url,
        playing_vid_mode=0,  # YouTube video mode
        target_playlisttitle="Test Download",
        current_dir=current_dir,
        icondir="",
        title="Test Video",
        ver="Test",
        chrome_extension_url="",
        root=test_root,
        ffmpeg=ffmpeg,
        ytdlp_log_handle=ytdlp_log_handler(),
        is_downloading=BooleanVar(value=False)
    )
    
    test_root.mainloop()
    