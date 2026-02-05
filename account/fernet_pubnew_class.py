
from cryptography.fernet import Fernet
import os
from google.oauth2.credentials import Credentials
from notification.ctkmessagebox import ctk_messagebox
import pywintypes
import win32crypt
import json


class Ferner_encrptor(object):
    def __init__(self,
                 user_data_dir:str,
                 ctk_messagebox:ctk_messagebox):
        '''
        Check for the fernet key file, if not present create one
        for messagebox please pass the messagebox instance from the main app
        '''
        self.user_data_dir = user_data_dir
        self.ctk_messagebox = ctk_messagebox

        self.check_and_create_sys_key()
        self.Fernet_cred = self._get_cred_key()
        self.Fernet_API = self._get_API_key()


    def check_and_create_sys_key(self):
        '''
        Check for the fernet key file existence.
        if not present create one.
        '''
        if not os.path.exists(os.path.join(self.user_data_dir,'fernet_cred_key.enc')):
            self._create_cred_key()
            if os.path.exists(os.path.join(self.user_data_dir,'cred.enc')):
                self.ctk_messagebox.showwarning(title="JaTubePlayer",
                                 message="The credential key seems to be missing, recreate one will also delete the stored credential , please login again afterward!")
                os.remove(os.path.join(self.user_data_dir,'cred.enc'))

                

        if not os.path.exists(os.path.join(self.user_data_dir,'fernet_API_key.enc')):
            self._create_API_key()
            
            if os.path.exists(os.path.join(self.user_data_dir,'API.enc')):
                self.ctk_messagebox.showwarning(title="JaTubePlayer",
                                 message="The API key seems to be missing, recreate one will also delete the stored API , please login again afterward!")
                os.remove(os.path.join(self.user_data_dir,'API.enc'))
        self.Fernet_cred = self._get_cred_key()
        self.Fernet_API = self._get_API_key()


    def _create_cred_key(self):
        key = Fernet.generate_key()
        bolb = win32crypt.CryptProtectData(key)
        with open(os.path.join(self.user_data_dir,'fernet_cred_key.enc'),"wb") as f:
            f.write(bolb)

    def _create_API_key(self):
        key = Fernet.generate_key()
        bolb = win32crypt.CryptProtectData(key)
        with open(os.path.join(self.user_data_dir,'fernet_API_key.enc'),"wb") as f:
            f.write(bolb)
        

    def _get_cred_key(self)->Fernet:
        try:
            with open(os.path.join(self.user_data_dir,'fernet_cred_key.enc'),"rb") as f:
                bolb = f.read()
            key = win32crypt.CryptUnprotectData(bolb)[1]
            return Fernet(key)
        except pywintypes.error as e:
            self.ctk_messagebox.showerror_and_wait(title="JaTubePlayer",
                                 message=f"FATAL ERROR: \nget credential key failed: {e.strerror}\nPlease delete the file fernet_cred_key.enc and restart the app")
                                 
            os._exit(1)
            
        
    def _get_API_key(self)->Fernet:
        try:
            with open(os.path.join(self.user_data_dir,'fernet_API_key.enc'),"rb") as f:
                bolb = f.read()
            key = win32crypt.CryptUnprotectData(bolb)[1]
            return Fernet(key)
        except pywintypes.error as e:
             
            self.ctk_messagebox.showerror_and_wait(title="JaTubePlayer",
                                 message=f"FATAL ERROR: \nget API key failed: {e.strerror}\nPlease delete the file fernet_API_key.enc and restart the app")
            os._exit(1)
               
    
    def encrypt_api(self,api:str):
        self.check_and_create_sys_key()
        encryted = self.Fernet_API.encrypt(api.encode())
        with open(os.path.join(self.user_data_dir,'API.enc'),'wb') as f:
            f.write(encryted)

    def decrypte_api(self)->str:
        '''
        if no fernet api key, and we force to generate one, the api key will be different from the previous one, so we let the fernet api key be none, return None in this case.
        '''
        try:
            with open(os.path.join(self.user_data_dir,'API.enc'),'rb') as f:
                return self.Fernet_API.decrypt(f.read()).decode()
        except FileNotFoundError:return None
        except Exception as e:
            self.ctk_messagebox.showerror(title="JaTubePlayer",
                                 message=f"ERROR: decrypt API key failed: {e}")
            return None

    def encrypt_cred(self,cred:Credentials):
        self.check_and_create_sys_key()
        try:
            cred_in_str= cred.to_json()
            cred_in_byte = cred_in_str.encode()
            encryted = self.Fernet_cred.encrypt(cred_in_byte)
            with open(os.path.join(self.user_data_dir,'cred.enc'),'wb') as f:
                f.write(encryted)
        except Exception as e:
            self.ctk_messagebox.showerror(title="JaTubePlayer",
                                 message=f"ERROR: encrypt credential failed: {e}")

    def decrypte_cred(self)->Credentials:
        '''
        if no fernet cred key, and we force to generate one, the cred key will be different from the previous one, so we let the fernet cred key be none, return None in this case.
        '''
        try:
            with open(os.path.join(self.user_data_dir,'cred.enc'),'rb') as f:
                cred_in_byte = self.Fernet_cred.decrypt(f.read()).decode()
                return Credentials.from_authorized_user_info(json.loads(cred_in_byte))
        except FileNotFoundError:return None
        except Exception as e:
            self.ctk_messagebox.showerror(title="JaTubePlayer",
                                 message=f"ERROR: decrypt credential failed: {e}")
            return None
    def clear_sys_key(self)->None:
        '''
        Clear the saved sys key to reset encryption system.
        Note this will delete both 
        1. fernet_cred_key.enc
        2. fernet_API_key.enc
        3. cred.enc
        4. API.enc
        '''
        try:
            os.remove(os.path.join(self.user_data_dir,'fernet_cred_key.enc'))
        except:pass
        try:        
            os.remove(os.path.join(self.user_data_dir,'fernet_API_key.enc'))
        except:pass
        try:
            os.remove(os.path.join(self.user_data_dir,'cred.enc'))
        except:pass
        try:        
            os.remove(os.path.join(self.user_data_dir,'API.enc'))
        except:pass
        self.Fernet_cred = None
        self.Fernet_API = None  

        


    
    
    