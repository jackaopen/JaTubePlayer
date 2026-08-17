import os
import win32crypt
import secrets
import hashlib
import win32file
import win32con

EXPTECTED_HASH = "1579edd6c97911e962d372245f020950657e1a2cfd53f741e282c6e65450c7a4"
class account_token:
    def __init__(self,
                 appdata_dir:str,
                 log_handle:object):
        self.token_dir = os.path.join(appdata_dir,"JaTubePlayer","account_token.enc")
        self.log_handle = log_handle
        self.clear_token_file()
        
    def gen_and_encrypt(self):
        try:
            self.clear_token_file()
            with open(self.token_dir,"wb") as f:
                f.write(win32crypt.CryptProtectData(secrets.token_bytes(32)))
            self.log_handle(
                content=f"gen_and_encrypt",
                errtype="info",
                component = "account token"
            )
        except Exception as e:
            self.log_handle(
                content=f"error when gen_and_encrypt token file {e}",
                errtype="error",
                component = "account token"
            )


    def clear_token_file(self):
        try:
            if os.path.exists(self.token_dir):
                os.remove(self.token_dir)

        except Exception as e:
            self.log_handle(
                content=f"error when clear token file {e}",
                errtype="error",
                component = "account token"
            )

    def verify_WV_hash(self,
                       target_path:str)->tuple[bool,object]:
        lock_handle = None
        try:
            lock_handle = win32file.CreateFile(
                target_path,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ,  # permits open() and Popen; denies write/delete
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_ATTRIBUTE_NORMAL,
                None,
            )
        

            with open(target_path,"rb") as f:
                target_path_hash = hashlib.file_digest(f,"sha256").hexdigest()
                self.log_handle(
                    content=f"checking hash...",
                    errtype="info",
                    component = "account token"
                )
            return  target_path_hash == EXPTECTED_HASH, lock_handle
        except Exception as e:
            self.log_handle(
                content=f"error when verify_WV_hash {e}",
                errtype="error",
                component = "account token"

            )
        if lock_handle is not None:
            lock_handle.Close()
        return False, None
        
        

    