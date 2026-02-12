import os
from win32com.shell import shell, shellcon  # type: ignore
from win32com.propsys import propsys  # type: ignore
import pythoncom

class ShortcutManager:
    def __init__(self, app_user_model_id: str, main_path: str):
        self.app_id = app_user_model_id
        self.main_path = main_path
        start_menu = shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0)
        self.shortcut_path = os.path.join(start_menu, f"JaTubePlayer.lnk")
        
    def create(self):
        try:
            
            target = os.path.join(self.main_path)
            
            
            
            shell_link = pythoncom.CoCreateInstance(
                shell.CLSID_ShellLink, None,
                pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
            )
            
            shell_link.SetPath(target)
            shell_link.SetDescription("JaTube Player")
            shell_link.SetIconLocation(os.path.join(os.path.dirname(self.main_path),'_internal','jtp.ico'), 0)
            
           
            property_store = shell_link.QueryInterface(propsys.IID_IPropertyStore)
            key = propsys.PSGetPropertyKeyFromName("System.AppUserModel.ID")
            propvar = propsys.PROPVARIANTType(self.app_id)
            property_store.SetValue(key, propvar)
            property_store.Commit()
            

            # Save to Start Menu
            persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
            persist_file.Save(self.shortcut_path, 0)
            
            print(f"[Shortcut] Registered AppID '{self.app_id}' at: {self.shortcut_path}")
            
        except Exception as e:
            print(f"[Shortcut] Failed to register: {e}")

    def cleanup(self):
        if os.path.exists(self.shortcut_path):
            try:
                os.remove(self.shortcut_path)
                print(f"[Shortcut] Unregistered: {self.shortcut_path}")
            except Exception as e:
                print(f"[Shortcut] Cleanup failed: {e}")