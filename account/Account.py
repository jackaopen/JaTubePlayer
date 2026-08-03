import subprocess
import os 
import sys
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from notification.ctkmessagebox import ctk_messagebox
import win32crypt
import pywintypes
import threading

from notification.wintoast_notify import ToastNotification



class account_handle:
    def __init__(self,
                 current_dir: str,
                 ctk_messagebox: ctk_messagebox,
                 log_handle:object,
                 account_info_handler:object):
        
        self.current_dir = current_dir
        self.ctk_messagebox = ctk_messagebox
        self.log_handle = log_handle
        self.account_info_handler = account_info_handler

        self.account_dir = os.path.join(self.current_dir, "account")
        self.user_data_dir = os.path.join(self.current_dir, "user_data")
        self.project_path = os.path.join(self.account_dir, "WebView2Host.csproj")
        self.host_exe_path = os.path.join(self.account_dir, "WebView2Host.exe")

        self.aes_key_path = os.path.join(self.user_data_dir, "AES_key.enc")
        self.cookie_dir = os.path.join(self.user_data_dir, "cookie_key.enc")

        self._encfile_lock = threading.Lock()
        self.check_and_create_aes_key()
        self.process_log_reader_thread = None
        
    
    def _process_log_reader(self, process:subprocess.Popen):
        '''
        read the log from the process and print it to the console
        '''
        for line in process.stderr:
            try:self.log_handle(line.strip())
            except:pass

    def _start_process_log_reader(self, process:subprocess.Popen):
        '''
        start a thread to read the log from the process and print it to the console
        '''
        if not self.process_log_reader_thread or not self.process_log_reader_thread.is_alive():
            self.process_log_reader_thread = threading.Thread(target=self._process_log_reader, args=(process,))
            self.process_log_reader_thread.daemon = True
            self.process_log_reader_thread.start()
        else:
            self.log_handle("Log reader thread is already running, skipping start.")
    
    def login_refresh(self,
                      option:int,
                      should_update_avator:bool=True)->bool:
        '''
        login, retrun 
        option: 0 = login, 1 = refresh
        should_update_avator: if True, update the account avator after refresh, for login, it will always update the avator
        '''
        if not self._encfile_lock.acquire(blocking=False):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message="Another login/refresh operation is in progress. Please wait."
            )
            return False
            
        try:
            if option not in [0, 1]:
                self.log_handle(f"Invalid option: {option}. Must be 0 (login) or 1 (refresh).", "error")
                return False
            
            if not os.path.exists(self.host_exe_path):
                self.log_handle("WebView2 host not found")
                self.ctk_messagebox.showerror_and_wait(
                    title="JaTubePlayer",
                    message=f" WebView2 host : {self.host_exe_path} not found!\n "
                )
                return False   
            command = "login" if option == 0 else "refresh"

            if command == "refresh" and os.path.exists(self.cookie_dir):
                ToastNotification().notify(
                    title="JaTubePlayer",
                    msg="Refreshing login session...\nPlease wait.",
                )                

            WV_host_result = subprocess.Popen(
                [str(self.host_exe_path), str(self.current_dir), command],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
            )
            self._start_process_log_reader(WV_host_result)
            

            exit_code = WV_host_result.wait()
            self.process_log_reader_thread.join()  
            if exit_code != 0:
                self.log_handle(f"WebView2 host exited with code {exit_code}","error")
                self.ctk_messagebox.showerror_and_wait(
                    title="JaTubePlayer",
                    message=f"WebView2 host exited with code {exit_code}\nPlease check the log for more details."
                )
                return False
            
            if should_update_avator and command == "refresh" or command == "login":
                self.account_info_handler.set_account_avator()
            return True

        except Exception as e:
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"Failed to {command} login: {e}"
            )
            self.log_handle(f"Failed to {command} login: {e}", "error")
            return False
        finally:
            self._encfile_lock.release()
        
        
    def get_cookie(self)->str|None:
        '''
        get the cookie from the cookie file
        return the cookie string
        '''
        
        if not self.check_cookie_exist():
            return None
        if not self._encfile_lock.acquire(blocking=False):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message="Another login/refresh operation is in progress. Please wait."
            )
            return None
        try:

            with open(self.aes_key_path, "rb") as f:
                bolb = f.read()
                
                aeskey = win32crypt.CryptUnprotectData(bolb)[1]

                with open(self.cookie_dir, "rb") as f:
                    bolb = f.read()
                    nonce = bolb[:12]
                    tag = bolb[12:28]
                    ciphertext = bolb[28:]
                cipher = AES.new(aeskey, AES.MODE_GCM, nonce=nonce)

                # Decrypt the ciphertext and verify its authenticity using the tag
                cookie = cipher.decrypt_and_verify(ciphertext, tag)
                return cookie.decode("utf-8")
        except Exception as e:
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=(f"Failed to retrieve cookie: {e}"
                         "\nPlease try to login again.")
            )
            self.log_handle(f"Failed to retrieve cookie: {e}", "error")
            return None
        finally:
            self._encfile_lock.release()

    def check_cookie_exist(self)->bool:
        '''
        check if the cookie file exists
        '''
        if not os.path.exists(self.aes_key_path):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"AES key file : {self.aes_key_path} not found!\n "
            )
            return False
                
        if not os.path.exists(self.cookie_dir):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"Cookie file : {self.cookie_dir} not found!\n "
            )
            return False
        return True

    def clear_login_data(self,
                         cookie_only:bool=False)->bool:
        '''
        remove the cookie file and AES key file
        if cookie_only is True, only remove the cookie file
        '''
        if not self._encfile_lock.acquire(blocking=False):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message="Another login/refresh operation is in progress. Please wait."
            )
            return False
        try:
            if os.path.exists(self.cookie_dir):
                os.remove(self.cookie_dir)
            if os.path.exists(self.aes_key_path) and not cookie_only:
                os.remove(self.aes_key_path)
            return True
        except Exception as e:
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"Failed to clear login data: {e}"
            )
            self.log_handle(f"Failed to clear login data: {e}", "error")
            return False
        finally:
            self._encfile_lock.release()


    def _create_AES_key(self):
        '''
        Create a new AES key and store it in the user_data directory.
        If the cookie file exists, delete it and show a warning message.
        will need to re-login after this operation

        use AES 256
        '''
        if os.path.exists(self.cookie_dir):
            self.ctk_messagebox.showwarning(
                title="JaTubePlayer",
                message="The AES key seems to be missing, recreate one will also delete the stored login session.\n Please login again afterward!")
            os.remove(self.cookie_dir)
        
        os.makedirs(self.user_data_dir, exist_ok=True)
        bolb = win32crypt.CryptProtectData(get_random_bytes(32))
        with open(self.aes_key_path, "wb") as f:
            f.write(bolb)
        
    def check_aes_key(self)->bool:
        '''
        try to read the AES key with DPAPI
        
        '''
        if not os.path.exists(self.aes_key_path):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"AES key file : {self.aes_key_path} not found!\n "
            )
            return False
        with open(self.aes_key_path, "rb") as f:
            bolb = f.read()
        try:
            win32crypt.CryptUnprotectData(bolb)[1]

        except pywintypes.error as e:           # different user or machine.
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"FATAL ERROR: \nget credential key failed: {e.strerror}\nPlease delete the file .enc and restart the app")                
            return False
        
        except Exception as e:
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"ERROR: \nget credential key failed: {str(e)}\n")                
            return False
        return True
    
    def check_and_create_aes_key(self):
        '''
        Check for the fernet key file existence.
        if not present create one.
        retrun false for invalid key, true for valid key/created new key
        '''
        print("check_and_create_aes_key")
        if os.path.exists(self.aes_key_path):
            self.log_handle(f"{self.aes_key_path} AES key file exists, checking validity...")
            if not self.check_aes_key():
                self.ctk_messagebox.showerror_and_wait(
                    title="JaTubePlayer",
                    message="The AES key is invalid. A new one will be created.\nAlso, the login state will be cleared, please login again afterward!")
                if not self.clear_login_data():
                    self.ctk_messagebox.showerror_and_wait(
                        title="JaTubePlayer",
                        message="Failed to clear login data. Please check the log for more details.")
                    return
                self._create_AES_key()
        else:
            self.ctk_messagebox.showwarning(title="JaTubePlayer",
                message="The AES key seems to be missing, recreate one will also delete the stored cookie , please login again afterward!")
            self._create_AES_key()
