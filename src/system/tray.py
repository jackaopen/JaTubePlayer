import pystray
from pystray import Menu,MenuItem
from PIL import Image
from notification.ctkmessagebox import ctk_messagebox

class Playertray():
    def __init__(self,iconpath:str,
                 ver:str,
                 parent:object,
                 ctk_messagebox:object
                 ):
        self.iconpath = iconpath
        self.ver = ver
        self.ctkmsg = ctk_messagebox
        self.ctkmsg.master = parent
        self.menu = Menu(
            MenuItem(text=f"JatubePlayer {self.ver}",action=lambda :self.ctkmsg.showinfo("JatubePlayer",f"JatubePlayer Version : {self.ver}")),
        )
        self.icon =  pystray.Icon(
            name = "JatubePlayer",
            icon = Image.open(self.iconpath),
            title = "JatubePlayer",
            menu = self.menu
        )

    def run(self):
        self.icon.run()


