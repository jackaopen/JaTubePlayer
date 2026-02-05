import threading
from typing import Callable
import tarfile,requests,os,shutil,time,customtkinter as ctk
from utils.get_latest_version import get_latest_dlp_version
from notification.wintoast_notify import ToastNotification



def download_and_extract_dlp(_internal_dir : str,root:ctk.CTkToplevel|ctk.CTk,icondir:str="",log:Callable=print)-> bool | str:
    version = get_latest_dlp_version()
    #popup progress bar 
    popup = ctk.CTkToplevel(root)
    popup.title("JaTubePlayer yt-dlp update")
    popup.attributes("-topmost", True)

    popup.geometry(f"350x150+{root.winfo_screenwidth()//2}+{root.winfo_screenheight()//2}")
    popup.resizable(False, False)
    if icondir: root.after(200, lambda: popup.iconbitmap(icondir))

    label = ctk.CTkLabel(popup, text=f"Found newest version {version}", font=('Arial', 14))
    label.pack(pady=10)

    sizelabel = ctk.CTkLabel(popup, text="", font=('Arial', 12))
    sizelabel.pack()

    def _close():
        is_canceled.set()
        while not _download_stoped.is_set(): 
            root.update()
            popup.update()
            time.sleep(0.1)
        ToastNotification().notify(app_id="JaTubePlayer", title='JaTubePlayer', msg=f'yt-dlp update canceled.', duration='short', icon=icondir)
        popup.destroy()

    cancel_btn = ctk.CTkButton(popup, text="Cancel", command= _close)
    cancel_btn.pack(pady=10, side='bottom')

    bar = ctk.CTkProgressBar(popup, width=250)
    bar.pack(pady=5)
    bar.set(0)
    popup.update()
    time.sleep(1)
    is_canceled = threading.Event()
    is_canceled.clear()
    _download_stoped = threading.Event()
    _download_stoped.clear()
    _download_finished = threading.Event()
    _download_finished.clear()
    popup.protocol("WM_DELETE_WINDOW", _close)



    

    def _download():
        
        url = f'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.tar.gz'
        response = requests.get(url, stream=True)
        label.configure(text=f"Downloading yt-dlp.tar.gz - version {version}")

        length = int(response.headers.get('content-length'))
        current_len = 0
        
        if length:
            try:
                with open(os.path.join(_internal_dir, 'yt-dlp.tar.gz'), 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if is_canceled.is_set():
                            break
                        if chunk:
                            file.write(chunk)
                            current_len += len(chunk)
                            bar.set(current_len / length)
                            sizelabel.configure(text=f"Downloaded {current_len/1024**2 :.2f} of {length/1024**2 :.2f} MB")
                            popup.update()

            except Exception as e:
                log(f"Error downloading file: {e}")
            if is_canceled.is_set():
                try:os.remove(os.path.join(_internal_dir, 'yt-dlp.tar.gz'))
                except Exception as e: log(f"Error removing file: {e}")
                finally :
                    _download_stoped.set()
                    return "Download canceled by user."

            with tarfile.open(os.path.join(_internal_dir, 'yt-dlp.tar.gz'), 'r:gz') as tar:
                tar.extractall(path=_internal_dir)
            try:
                os.remove(os.path.join(_internal_dir, 'yt-dlp.tar.gz'))
            except Exception as e:
                log(f"Error removing file: {e}")
            try:
                if os.path.exists(os.path.join(_internal_dir, 'yt_dlp')):
                    shutil.rmtree(os.path.join(_internal_dir, 'yt_dlp'))
                shutil.copytree(os.path.join(_internal_dir,'yt-dlp','yt_dlp'), os.path.join(_internal_dir, 'yt_dlp'))
                
            except Exception as e:log(f"Error copying file: {e}")
            try:
                shutil.rmtree(os.path.join(_internal_dir, 'yt-dlp'))
            except Exception as e:
                log(f"Error removing file: {e}")
            
        #--------------------------------------------------------

            try:os.rename(os.path.join(_internal_dir,'yt-dlp.exe'),os.path.join(_internal_dir,'yt-dlp_old.exe'))
            except Exception as e: log(f"Error rename file: {e}")
            label.configure(text=f"Downloading yt-dlp.exe - version {version}")
            popup.update()
            response = requests.get('https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe', stream=True)
            current_len = 0
            length = int(response.headers.get('content-length'))
            
            if response.status_code == 200:
                try:
                    with open(os.path.join(_internal_dir, 'yt-dlp.exe'), 'wb') as file:
                        
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                if is_canceled.is_set():
                                    break
                                file.write(chunk)
                                bar.set(current_len / length)
                                sizelabel.configure(text=f"Downloaded {current_len/1024**2 :.2f} of {length/1024**2 :.2f} MB")
                                popup.update()
                                current_len += len(chunk)
                                
                except Exception as e:
                    log(f"Error downloading file: {e}")
            if is_canceled.is_set():
                try:os.remove(os.path.join(_internal_dir, 'yt-dlp.exe'))
                except Exception as e: log(f"Error removing file: {e}")
                try:os.rename(os.path.join(_internal_dir,'yt-dlp_old.exe'),os.path.join(_internal_dir,'yt-dlp.exe'))
                except Exception as e: log(f"Error rename file: {e}")
                finally:
                    _download_stoped.set()
                    return "Download canceled by user."

            try:os.remove(os.path.join(_internal_dir,'yt-dlp_old.exe'))
            except Exception as e: log(f"Error removing file: {e}")
            current_len = None
            label.configure(text="Done!")
            sizelabel.configure(text=f"")
            popup.update()
            time.sleep(1)
            popup.destroy()
            ToastNotification().notify(app_id="JaTubePlayer", title='JaTubePlayer', msg=f'yt-dlp updated!\nVersion {version}', duration='short', icon=icondir)
            _download_finished.set()
            return True
    
    download_thread = threading.Thread(target=_download,daemon=False)
    download_thread.start()
    
    while download_thread.is_alive():
        
        root.update()
        time.sleep(0.05)
    if _download_finished.is_set():
        return True
    else:
        return False

    
    
    
if __name__ == "__main__":
    testfolderpath = 'ytdlp_autoupdate_testfolder/'
    root = ctk.CTk()
    root.geometry("1x1")
    print(download_and_extract_dlp(testfolderpath,root,log=print))
    root.mainloop()


        
    