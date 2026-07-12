import subprocess
import os 
import sys
import argparse
import hashlib
import json
import re
import time

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from notification.ctkmessagebox import ctk_messagebox
import win32crypt
import pywintypes
import requests






class account_handle:
    def __init__(self,
                 current_dir: str,
                 ctk_messagebox: ctk_messagebox,
                 log_handle:object):
        
        self.current_dir = current_dir
        self.ctk_messagebox = ctk_messagebox
        self.log_handle = log_handle

        self.account_dev_dir = os.path.join(self.current_dir, "account_dev")
        self.account_dir = os.path.join(self.current_dir, "account")
        self.user_data_dir = os.path.join(self.current_dir, "user_data")
        self.project_path = os.path.join(self.account_dev_dir, "WebView2Host.csproj")
        self.host_exe_path = os.path.join(self.account_dev_dir, "WebView2Host.exe")

        self.aes_key_path = os.path.join(self.user_data_dir, "AES_key.enc")
        self.cookie_dir = os.path.join(self.user_data_dir, "cookie_key.enc")


        self.check_and_create_aes_key()

    

    
    def login_refresh(self,
                      option:int)->bool|tuple[str,str]:
        '''
        login, retrun 
        option: 0 = login, 1 = refresh
        '''
        if not os.path.exists(self.host_exe_path):
            self.log_handle("WebView2 host not found")
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f" WebView2 host : {self.host_exe_path} not found!\n "
            )
            return None
        command = "login" if option == 0 else "refresh"
        result = subprocess.run(
            [str(self.host_exe_path), str(self.current_dir), command],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.stderr.strip():
            self.log_handle(result.stderr.strip())
        if result.stdout.strip():
            account_info = json.loads(result.stdout.strip().splitlines()[0])
            if (isinstance(account_info, list) and len(account_info) == 2 and
                    all(isinstance(value, str) for value in account_info)):
                return tuple(account_info)
            raise ValueError("WebView2 returned invalid account information")
        
    def get_cookie(self)->str|None:
        '''
        get the cookie from the cookie file
        return the cookie string
        '''

        if not os.path.exists(self.aes_key_path):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"AES key file : {self.aes_key_path} not found!\n "
            )
            return None
        
        if not os.path.exists(self.cookie_dir):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"Cookie file : {self.cookie_dir} not found!\n "
            )
            return None
        

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
        

    def clear_login_data(self,
                         cookie_only:bool=False):
        '''
        remove the cookie file and AES key file
        if cookie_only is True, only remove the cookie file
        '''
        if os.path.exists(self.cookie_dir):
            os.remove(self.cookie_dir)
        if os.path.exists(self.aes_key_path) and not cookie_only:
            os.remove(self.aes_key_path)


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
        
    def check_aes_key(self):
        '''
        try to read the AES key with DPAPI
        if failed, raise an exception
        if success, do nothing
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
        except pywintypes.error as e:
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"FATAL ERROR: \nget credential key failed: {e.strerror}\nPlease delete the file .enc and restart the app")                
            os._exit(1)
        return True
    
    def check_and_create_aes_key(self):
        '''
        Check for the fernet key file existence.
        if not present create one.
        '''
        if os.path.exists(self.aes_key_path):
            self.check_aes_key()
        else:
            self.ctk_messagebox.showwarning(title="JaTubePlayer",
                message="The AES key seems to be missing, recreate one will also delete the stored cookie , please login again afterward!")
            self._create_AES_key()

    def _encrypt_cookie(self, cookie:str):
        '''
        encrypt the cookie with AES GCM and store it in the user_data directory.
        '''
        if not os.path.exists(self.aes_key_path):
            self.ctk_messagebox.showerror_and_wait(
                title="JaTubePlayer",
                message=f"AES key file : {self.aes_key_path} not found!\n "
            )
            return None
        
        with open(self.aes_key_path, "rb") as f:
            bolb = f.read()
            aeskey = win32crypt.CryptUnprotectData(bolb)[1]
            cipher = AES.new(aeskey, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(cookie.encode("utf-8"))
            with open(self.cookie_dir, "wb") as f:
                f.write(cipher.nonce + tag + ciphertext)




    def rotate_cookie(self):
        '''
        remove the cookie file and re-login
        '''
        cookie = self.get_cookie()
        if not cookie:return

        self.clear_login_data()
        self._create_AES_key()
        self._encrypt_cookie(cookie)
