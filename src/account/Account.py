import subprocess
import os 
import sys
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from notification.ctkmessagebox import ctk_messagebox
import win32crypt
import pywintypes
import threading
from utils.Account_token import account_token
from notification.wintoast_notify import ToastNotification



class account_handle:
    def __init__(self,
                 current_dir: str,
                 app_data_dir: str,
                 ctk_messagebox: ctk_messagebox,
                 log_handle:object,
                 account_info_handler:object,
                 account_token_handle:account_token):
        
        self.current_dir = current_dir
        self.ctk_messagebox = ctk_messagebox
        self.log_handle = log_handle
        self.account_info_handler = account_info_handler
        self.account_token_handle = account_token_handle
        self.appdata_dir = app_data_dir

        self.account_dir = os.path.join(self.current_dir, "account")
        print(f"account_dir: {self.account_dir}")
        self.user_data_dir = os.path.join(app_data_dir, "JaTubePlayer")
        self.project_path = os.path.join(self.account_dir, "WebView2Host.csproj")
        self.host_exe_path = os.path.join(self.account_dir, "WebView2Host.exe")

        self.aes_key_path = os.path.join(self.user_data_dir, "AES_key.enc")
        self.cookie_dir = os.path.join(self.user_data_dir, "cookie_key.enc")
        self.account_token_dir = os.path.join(self.user_data_dir,"account_token.enc")

        self._encfile_lock = threading.Lock()
        self.check_and_create_aes_key()
        self.process_log_reader_thread = None
        
    
    def _process_log_reader(self, process:subprocess.Popen):
        '''
        read the log from the process and print it to the console
        '''
        for line in process.stderr:
            try:self.log_handle(
                    content=line.strip(),
                    errtype='err',
                    component='account',
                )
            except:pass

        for line in process.stdout:
            try:self.log_handle(
                    content=line.strip(), 
                    errtype='info',
                    component='account',
                )
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
            self.log_handle(
                content="Log reader thread is already running, skipping start.",
                errtype='info',
                component='account',
            )
    
    def Start_wv_process(self,
                      option:int,
                      should_update_avator:bool=True,
                      _force_no_lock:bool=False
                      )->bool:
        '''
        login, retrun 
        option: 0 = login, 1 = refresh, 2 = clear profile
        should_update_avator: if True, update the account avator after refresh, for login, it will always update the avator
        _force_no_lock : if True, do not acquire the lock, for internal use only
        '''
        if not _force_no_lock and not self._encfile_lock.acquire(blocking=False):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message="Another login/refresh operation is in progress. Please wait."
            )
            return False

        command = ""
        WV_handle = None
        try:

            if option not in [0, 1,2]:
                self.log_handle(
                    content=f"Invalid option: {option}. Must be 0 (login), 1 (refresh), or 2 (clear profile).",
                    errtype='error',
                    component='account',
                )
                return False

            WV_hash_result,WV_handle = self.account_token_handle.verify_WV_hash(self.host_exe_path)
            if not WV_hash_result:
                self.ctk_messagebox.showerror_and_wait(
                    title="JaTubePlayer",
                    message="The account handling executable is incorrect, please check the file!"
                )
                self.log_handle(
                        content=f"The account handling executable is incorrect",
                        errtype='error',
                        component='account',
                    )
                return False

            self.account_token_handle.clear_token_file()
            self.account_token_handle.gen_and_encrypt()
            encoded_token = None
            with open(self.account_token_dir,"rb") as f:
                encoded_token = f.read()

            match option:
                case 0:
                    command = "login"
                case 1:
                    command = "refresh"
                case 2:
                    command = "clear"
                    should_update_avator = False # cannot update avator after clear profile

            if option == 0 and not self.check_aes_key():
                self.log_handle(
                    content="No aes key found!",
                    errtype='error',
                    component='account',
                )
                self.ctk_messagebox.showerror(
                    title="JaTubePlayer",
                    message=f"No AES key found!\n Try to restart the app to recreate one",
                )
                return False
            
            if not os.path.exists(self.host_exe_path):
                self.log_handle(
                    content="WebView2 host not found",
                    errtype='warning',
                    component='account',
                )
                self.ctk_messagebox.showerror_and_wait(
                    title="JaTubePlayer",
                    message=f" WebView2 host : {self.host_exe_path} not found!\n "
                )
                return False
            
            
            
            if command == "refresh" and os.path.exists(self.cookie_dir):
                ToastNotification().notify(
                    title="JaTubePlayer",
                    msg="Refreshing login session...\nPlease wait.",
                )                
                
            if getattr(sys, "frozen", False):
                resource_root = self.current_dir
            else:
                resource_root = os.path.dirname(self.current_dir)

            WV_host_result = subprocess.Popen(
                [str(self.host_exe_path), resource_root, str(self.appdata_dir), command],
                text=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW                
            )

            token = win32crypt.CryptUnprotectData(encoded_token)[1]
            encoded = base64.b64encode(token).decode("ascii")

            WV_host_result.stdin.write(encoded+'\n')
            WV_host_result.stdin.flush()
            self._start_process_log_reader(WV_host_result)
            
            

            exit_code = WV_host_result.wait()
            self.process_log_reader_thread.join() 
            

            if exit_code != 0:
                self.log_handle(
                    content=f"WebView2 host exited with code {exit_code}",
                    errtype='error',
                    component='account',
                )
                self.ctk_messagebox.showerror_and_wait(
                    title="JaTubePlayer",
                    message=f"WebView2 host exited with code {exit_code}\nPlease check the log for more details."
                )
                return False
            
            if should_update_avator and command == "refresh" or command == "login":
                self.account_info_handler.set_account_avator(force=True)
            return True

        except Exception as e:
            self.log_handle(
                content=f"Failed to {command} login: {e}",
                errtype='error',
                component='account',
            )
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"Failed to {command} login: {e}"
            )
            return False
        finally:
            if not _force_no_lock:
                self._encfile_lock.release()
            self.account_token_handle.clear_token_file()

            if WV_handle is not None:
                WV_handle.Close()
        
    
    def get_cookie(self,force:bool=False)->str|None:
        '''
        get the cookie from the cookie file
        return the cookie string
        force: True ONLY for login get avator 
        '''
        
        if not self.check_cookie_exist():
            return None
        _lock = None
        if not force:
            _lock = self._encfile_lock.acquire(blocking=False)
            if not _lock:
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
            self.log_handle(
                content=f"Failed to retrieve cookie: {e}",
                errtype='error',
                component='account',
            )
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=(f"Failed to retrieve cookie: {e}"
                         "\nPlease try to login again.")
            )
            return None
        finally:
            if _lock:
                self._encfile_lock.release()

    def check_cookie_exist(self)->bool:
        '''
        check if the cookie file exists
        '''
        if not os.path.exists(self.aes_key_path):
            self.log_handle(
                content=f"AES key file is missing: {self.aes_key_path}",
                errtype="warning",
                component="account",
            )
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"AES key file : {self.aes_key_path} not found!\n "
            )
            return False
                
        if not os.path.exists(self.cookie_dir):
            self.log_handle(
                content=f"Cookie file is missing: {self.cookie_dir}",
                errtype="warning",
                component="account",
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
            clear_result = False
            if os.path.exists(self.cookie_dir):
                os.remove(self.cookie_dir)
            if os.path.exists(self.aes_key_path) and not cookie_only:
                os.remove(self.aes_key_path)
            if not cookie_only:
                clear_result = self.Start_wv_process(
                    option=2,
                    should_update_avator=False,
                    _force_no_lock=True
                )


            
                if not clear_result:
                    self.log_handle(
                        content=f"Failed to clear profile data",
                        errtype='error',
                        component='account',
                    )
                    self.ctk_messagebox.showerror(
                        title="JaTubePlayer",
                        message=f"Failed to clear profile data"
                    )
                    return False
            return True
            
        except Exception as e:
            self.log_handle(
                content=f"Failed to clear login data: {e}",
                errtype='error',
                component='account',
            )
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"Failed to clear login data: {e}"
            )
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
            self.log_handle(
                content="AES key is missing; the stored login session will be cleared",
                errtype="warning",
                component="account",
            )
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
            self.log_handle(
                content=f"AES key file is missing: {self.aes_key_path}",
                errtype="warning",
                component="account",
            )
            
            return False
        with open(self.aes_key_path, "rb") as f:
            bolb = f.read()
        try:
            win32crypt.CryptUnprotectData(bolb)[1]

        except pywintypes.error as e:           # different user or machine.
            self.log_handle(
                content=f"Failed to decrypt the credential key: {e.strerror}",
                errtype="error",
                component="account",
            )
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"FATAL ERROR: \nget credential key failed: {e.strerror}\nPlease delete the file .enc and restart the app")                
            return False
        
        except Exception as e:
            self.log_handle(
                content=f"Failed to validate the credential key: {e}",
                errtype="error",
                component="account",
            )
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
            self.log_handle(
                content=f"{self.aes_key_path} AES key file exists, checking validity...",
                errtype='info',
                component='account',
            )
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
            self.log_handle(
                content="AES key is missing; creating a replacement key",
                errtype="warning",
                component="account",
            )
            self.ctk_messagebox.showwarning(title="JaTubePlayer",
                message="The AES key seems to be missing, recreate one will also delete the stored cookie , please login again afterward!")
            self._create_AES_key()
