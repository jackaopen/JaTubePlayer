from google.oauth2.credentials import Credentials
from utils.check_internet import check_internet,check_internet_silent
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
import os,json,subprocess,webbrowser,threading
from google.auth.transport.requests import Request
from notification.wintoast_notify import ToastNotification
from typing import Callable
from account.fernet_pubnew_class import Ferner_encrptor
from notification.ctkmessagebox import ctk_messagebox


class custom_chrome:
    def open(self, url, new=0, autoraise=True):
        global chrome_process
        chrome_process = subprocess.Popen([
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            f'--app={url}',
        ])
        return True
    


class google_auth_control(object):
    '''
    Google cred control class to handle google login,logout and credential management.
    
    '''
    def __init__(self, ver:str,
                current_dir:str,
                ctk_messagebox: ctk_messagebox,
                log_handle:Callable,youtubeAPI:str=""):
        with open(os.path.join(current_dir, 'user_data','config.json'),'r') as f:
            self.CONFIG = json.load(f)
        self.ver = ver
        self.client_secret_path = self.CONFIG['client_secret_path']
        self.youtubeAPI = youtubeAPI
        self.log_handle = log_handle
        self.current_dir = current_dir
        self.ctk_messagebox = ctk_messagebox  #object from root
        self.Fernet_encryptor = Ferner_encrptor(os.path.join(current_dir,'user_data'),ctk_messagebox=ctk_messagebox)
        webbrowser.register('chrome_app', None, custom_chrome())



    def load_token_from_env(self)->Credentials|None:
        '''
        Load and decrypt the saved Google OAuth2 credentials from the environment.
        Returns:
            Credentials: The decrypted Google OAuth2 credentials if available and valid.
            None: If the credentials are not found or cannot be decrypted or are expired.
        This is the funtion for checking cred at init , without force login


        '''
        try:
                cred = self.Fernet_encryptor.decrypte_cred() 

                if not cred:return None
                if cred.expired and cred.refresh_token:
                    try:
                        cred.refresh(Request())
                        self.Fernet_encryptor.encrypt_cred(cred)
                        return cred
                    except:
                        return None
                return cred
        except FileNotFoundError:
            return None
        except Exception as e:
            ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {self.ver}', msg=str(e), duration='short', icon='')
            return None
    




    @check_internet_silent
    def get_userinfo(self,cred:Credentials)->dict|None:## and auto refresh !!!!!!
        ''' 
        # Getting userinfo 
        after checking and refreshing the credential if needed.
        retrns None if cred is expired .
        '''
        try:

            if cred:
                if not cred.expired:

                    #refresh not needed and get userinfo
                    re = requests.get('https://www.googleapis.com/oauth2/v3/userinfo',headers={'Authorization': f'Bearer {cred.token}'})
                    userinfo = re.json()
                    self.log_handle('no refresh')
                    if 'error_description' in userinfo:
                        err_msg = userinfo['error_description']
                        ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {self.ver}', msg=f'got some problem:{err_msg}\n try to login again!', duration='short', icon='')
                        return None
                    else:
                        return userinfo
                else:return None
            else:return None
        except Exception as e:
            ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {self.ver}', msg=str(e), duration='short', icon='')
            return None


    def google_logout_clear_data(self)->bool|Exception:
        '''
        Clear the saved credential data to logout the user.
        1. delete cred.enc
        2. delete liked.json
        3. delete sub.json
        '''
        try:
            try:
                player_enc_path = os.path.join(self.current_dir, 'user_data', 'cred.enc')
                if os.path.exists(player_enc_path):
                    os.remove(player_enc_path)
            except FileNotFoundError:pass
            try:

                liked_json_path = os.path.join(self.current_dir, 'user_data', 'liked.json')
                if os.path.exists(liked_json_path):
                    os.remove(liked_json_path)
            except FileNotFoundError:pass
            try:
                sub_json_path = os.path.join(self.current_dir, 'user_data', 'sub.json')
                if os.path.exists(sub_json_path):
                    os.remove(sub_json_path)
            except FileNotFoundError:pass
            return True
        except Exception as e : return e


    
    @check_internet
    def get_google_cred_and_save(self)->None:
        '''

        
        please make sure to run this function in a separate thread to avoid blocking the main thread.


        **NOTE**: And please make sure that the flow.py file in google_auth_oauthlib package has been modified to support html success message.\n
        for account safety,if a new(same) account is logged in , please check if the liked.json and sub.json are updated after login, if not , please try to delete the old liked.json and sub.json to let the app generate new one.

        '''
        ToastNotification().notify(app_id="JaTubePlayer", title=f'JaTubePlayer {self.ver}', msg='Starting Google login process...\nPlease finish the login within 2 minutes.', duration='short', icon='')
        if self.client_secret_path and os.path.exists(self.client_secret_path):
            if self.youtubeAPI: 
                
                    scopes = ["https://www.googleapis.com/auth/youtube.readonly"
                              ,"https://www.googleapis.com/auth/userinfo.profile"]
                    flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_path, scopes=scopes)
                    try:
                        html_file_path = os.path.join(self.current_dir,'_internal','google_login_suc_red_page.html')
                        with open(html_file_path, 'r', encoding='utf-8') as f:
                            html = f.read()
                        credentials = flow.run_local_server(
                            port=0,
                            timeout_seconds=120,
                            success_message=html,#changed the flow.py class _RedirectWSGIApp to support html success message
                            browser='chrome_app'
                            )

                        self.Fernet_encryptor.encrypt_cred(credentials)
                        if credentials:
                            print("Google login successful.")
                        else:
                            print("Google login failed or was cancelled.")
                        return credentials

                    except:pass
                    




            else:
                self.ctk_messagebox.showerror("JaTubePlayer","There is no API, please check at setting -> account & authentication.")
                return None
        else:
            self.ctk_messagebox.showerror("JaTubePlayer","There is no client secrets, please check at setting -> account & authentication.")
            return None
        
    
    def get_google_cred(self)->Credentials|None:
        '''
        force google login in a separate thread and return the cred after login finished.
        '''
        thread = threading.Thread(target=self.get_google_cred_and_save)
        thread.start()
        thread.join()

        cred = self.load_token_from_env()
        return cred
            
        
    def get_cred(self)->Credentials|None:
        try:
            cred = self.load_token_from_env()
            
            if not cred:
                print("loaded cred from env")
                cred = self.get_google_cred()
            return cred
        except:pass

    
if __name__ == "__main__":
    gac = google_auth_control(ver='1.6.0',youtubeAPI=None,current_dir=os.getcwd(),log_handle=print)
    cred = gac.get_cred()
    print(gac.get_userinfo(cred))
