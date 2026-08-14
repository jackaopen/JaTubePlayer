import threading
from typing import Callable
import requests,os,time,customtkinter as ctk
from utils.get_latest_version import get_latest_dlp_version
from notification.wintoast_notify import ToastNotification
import hashlib
from utils.ytdlp_update.run_updater import run_as_admin_and_wait
import json
CHUNK_SIZE = 256*1024
class ytdlp_update:
    def __init__(self,
                appdata_dir:str,
                root:ctk.CTkToplevel|ctk.CTk,
                _internal_dir:str,
                icondir:str="",
                log_handle:Callable=print):
        '''
        appdata_dir must be in the form of %APPDATA%
        '''
        self.appdata_dir = appdata_dir
        self.ytdlp_update_dir = os.path.join(appdata_dir,'JaTubePlayer','ytdlp_update')
        self.root = root
        self._internal_dir = _internal_dir
        self.updater_path = os.path.join(self._internal_dir, 'JaTubePlayer_updater.exe')
        self.icondir = icondir
        self.log_handle = log_handle
        self.file_hash_dict = {}
        self.start_updater = False

        self.ytdlpgz_path = os.path.join(self.ytdlp_update_dir, 'yt-dlp.tar.gz')
        self.ytdlpexe_path = os.path.join(self.ytdlp_update_dir, 'new_yt-dlp.exe')
        self.hash_sum_path = os.path.join(self.ytdlp_update_dir, 'SHA2-256SUMS')
        self.hash_sig_path = os.path.join(self.ytdlp_update_dir, 'SHA2-256SUMS.sig')
        self.result_json_path = os.path.join(self.ytdlp_update_dir, 'update_result.json')


    def _build_popup(self,root:ctk.CTkToplevel|ctk.CTk,icondir:str="")->ctk.CTkToplevel:
        popup = ctk.CTkToplevel(root)
        popup.title("JaTubePlayer yt-dlp update")
        popup.attributes("-topmost", True)

        popup.geometry(f"350x150+{root.winfo_screenwidth()//2-350//2}+{root.winfo_screenheight()//2-150//2}")
        popup.resizable(False, False)
        if icondir: root.after(200, lambda: popup.iconbitmap(icondir))

        self.label = ctk.CTkLabel(popup, text="Searching for latest version...", font=('Arial', 14))
        self.label.pack(pady=10)
        self.sizelabel = ctk.CTkLabel(popup, text="", font=('Arial', 12))
        self.sizelabel.pack()

        def _close():
            if self.start_updater:
                self.log_handle(content="cannot cancel update, updater already started",
                                errtype='err',
                                component='download_ytdlp')
                return
            self.is_canceled.set()
            self.cancel_btn.configure(state="disabled")
            while not self._download_stoped.is_set(): 
                root.update()
                popup.update()
                time.sleep(0.1)
            ToastNotification().notify(app_id="JaTubePlayer", title='JaTubePlayer', msg=f'yt-dlp update canceled.', duration='short', icon=icondir)
            popup.destroy()
        
        self.cancel_btn = ctk.CTkButton(popup, text="Cancel", command= _close)
        self.cancel_btn.pack(pady=10, side='bottom')

        bar = ctk.CTkProgressBar(popup, width=250)
        bar.pack(pady=5)
        self.bar = bar
        bar.set(0)
        popup.update()

        self.is_canceled = threading.Event()
        self.is_canceled.clear()
        self._download_stoped = threading.Event()
        self._download_stoped.clear()
        self._download_finished = threading.Event()
        self._download_finished.clear()
        popup.protocol("WM_DELETE_WINDOW", _close)
        return popup

    
    def _verify_hash(self)->None:
        self.log_handle(content=f"verifying hash...",
                        errtype='info',
                        component='download_ytdlp') 
        with open(self.ytdlpexe_path, "rb") as file:
            exe_hash = hashlib.file_digest(file, "sha256").hexdigest()

        with open(self.ytdlpgz_path, "rb") as file:
            tar_hash = hashlib.file_digest(file, "sha256").hexdigest()

        if exe_hash != self.file_hash_dict["yt-dlp.exe"]:
            raise ValueError("yt-dlp.exe hash mismatch")

        if tar_hash != self.file_hash_dict["yt-dlp.tar.gz"]:
            raise ValueError("yt-dlp.tar.gz hash mismatch")
        self.log_handle(content=f"hash are correct",
                        errtype='info',
                        component='download_ytdlp')

    def _process_downloaded_files(self)->bool:
        try:
            self._verify_hash()
            self.log_handle(content=f"hash are correct",
                        errtype='info',
                        component='download_ytdlp')
            exit_code = run_as_admin_and_wait(
                exe_path=self.updater_path,
                app_data_dir=self.appdata_dir
                    )
            if exit_code != 0:
                
                return False
            return True
    
        except Exception as e:
            self.log_handle(content=f"hash verification failed: {e}",
                        errtype='error',
                        component='download_ytdlp')
            return False
        finally:              
            with open(self.result_json_path, 'r') as f:
                result_json = json.load(f)      
                self.log_handle(content=f"updater result: {result_json.get('message','unknown error')}",
                                errtype=result_json.get('status','error'),
                                component='download_ytdlp-result')
        
    def clear_downloaded_files(self):
        if os.path.exists(self.ytdlpgz_path):
            os.remove(self.ytdlpgz_path)
        if os.path.exists(self.ytdlpexe_path):
            os.remove(self.ytdlpexe_path)
        if os.path.exists(self.hash_sum_path):
            os.remove(self.hash_sum_path)
        if os.path.exists(self.hash_sig_path):
            os.remove(self.hash_sig_path)
        

    def download_and_extract_dlp(self)-> bool | str:
        latest_version = get_latest_dlp_version()
        self.start_updater = False
        downloader_popup = self._build_popup(self.root,self.icondir)
        self.clear_downloaded_files()
    
        
        def _download():
            response = None
            try:
                # ytdlp folder
                
                url = f'https://github.com/yt-dlp/yt-dlp/releases/latest/download/SHA2-256SUMS'

                response = requests.get(url, stream=True,timeout=10)
                self.label.configure(text=f"Downloading SHA2-256 - version {latest_version}")

                
                if response.status_code == 200:
                    self.file_hash_dict = {}
                    for line in response.text.splitlines():
                        hash_code, filename = line.split()
                        self.file_hash_dict[filename] = hash_code.lower()
                    with open(self.hash_sum_path, 'wb') as file:
                        file.write(response.content)
                        
                else:
                    raise ConnectionError



                url = f'https://github.com/yt-dlp/yt-dlp/releases/latest/download/SHA2-256SUMS.sig'
                
                response = requests.get(url, stream=True,timeout=10)
                self.label.configure(text=f"Downloading SHA2-256 signature - version {latest_version}")

                
                if response.status_code == 200:
                    with open(self.hash_sig_path, 'wb') as file:
                        if not self.is_canceled.is_set():
                            file.write(response.content)
                            
                else:
                    raise ConnectionError
                
                # ytdlp folder
                url = f'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.tar.gz'
                response = requests.get(url, stream=True,timeout=10)
                self.label.configure(text=f"Downloading yt-dlp.tar.gz - version {latest_version}")

                length = int(response.headers.get('content-length',1))
                current_len = 0
                
                if response.status_code == 200:
                    with open(self.ytdlpgz_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            if self.is_canceled.is_set():
                                self.sizelabel.configure(text="cancelled")
                                raise InterruptedError
                                
                            if chunk:
                                file.write(chunk)
                                current_len += len(chunk)
                                self.bar.set(current_len / length)
                                self.sizelabel.configure(text=f"Downloaded {current_len/1024**2 :.2f} of {length/1024**2 :.2f} MB")
                                downloader_popup.update()
                else:
                    raise ConnectionError
                 
                #ytdlp_exe
  
                self.label.configure(text=f"Downloading yt-dlp.exe - version {latest_version}")
                downloader_popup.update()
                response = requests.get('https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe', stream=True,timeout=10)
                current_len = 0
                length = int(response.headers.get('content-length',1))
                
                if response.status_code == 200:
                    with open(self.ytdlpexe_path,'wb') as file:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            if chunk:
                                if self.is_canceled.is_set():
                                    self.sizelabel.configure(text="cancelled")
                                    raise InterruptedError
                                file.write(chunk)
                                current_len += len(chunk)
                                self.bar.set(current_len / length)
                                self.sizelabel.configure(text=f"Downloaded {current_len/1024**2 :.2f} of {length/1024**2 :.2f} MB")
                                downloader_popup.update()
                                
                else:
                    raise ConnectionError

                
                if self.is_canceled.is_set():
                    raise InterruptedError
                
                
                self.cancel_btn.configure(state="disabled")
                self.start_updater = True

                if self._process_downloaded_files():
                    self.label.configure(text="Done!")
                    self.bar.set(1.0)
                    self.sizelabel.configure(text=f"")
                    downloader_popup.update()
                    time.sleep(1)
                    self.log_handle(content="ytdlp updated",
                                        errtype='info',
                                        component='download_ytdlp')
                    
                    self._download_finished.set()
                else:
                    self.log_handle(content="Failed to process downloaded file, restoring old files",
                                errtype='error',
                                component='download_ytdlp')
                    ToastNotification().notify(
                        app_id="JaTubePlayer",
                        title='JaTubePlayer', 
                        msg='Failed to process downloaded file, restoring old files', 
                        duration='short', 
                        icon=self.icondir
                    )

            except ConnectionError:
                self.log_handle(content=f"connection failed {response.text}",
                        errtype='error',
                        component='download_ytdlp')

            except InterruptedError:
                self.log_handle(content="download cancelled by user,restoring old files",
                            errtype='warning',
                            component='download_ytdlp')

            except Exception as e:
                self.log_handle(content=f"download failed, {e}",
                            errtype='warning',
                            component='download_ytdlp')
            finally:
                self._download_stoped.set()
                downloader_popup.destroy()
                self.clear_downloaded_files()

        
        download_thread = threading.Thread(target=_download,daemon=False)
        download_thread.start()
        
        while download_thread.is_alive():
            self.root.update()
            time.sleep(0.05)
        if self._download_finished.is_set():
            downloader_popup.destroy()
            return latest_version
        else:
            return False