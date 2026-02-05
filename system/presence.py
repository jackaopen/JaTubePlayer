from pypresence import Presence,ActivityType,StatusDisplayType,DiscordNotFound
from notification.wintoast_notify import ToastNotification
import threading,queue,time
from typing import Callable

class DiscordPresence():
    def __init__(self,discord_status_run:Callable,discord_status_close:Callable):
        '''
        discord_status_run:function - function to run when discord presence is active
        discord_status_close:function - function to run when discord presence is closed
        '''
       

        self.is_connected = False
        self.is_enabled = False    


        self.discord_status_run = discord_status_run
        self.discord_status_close = discord_status_close


        self.cmdqueue = queue.Queue()
        self.cmdqueue.put("init")
        self.update_info_dict = {
            "song_title": "",
            "state": ""
        }

        self.listener_thread = threading.Thread(target=self._listen_for_events,daemon=True)
        self.listener_thread.start()

    def _listen_for_events(self):
            while True:
                time.sleep(0.1)
                cmd = self.cmdqueue.get()

                if cmd == "init":
                    try:
                        self.Presence = Presence(1445439992716329112)
                        self.Presence.connect()
                        self.is_connected = True
                        self.is_enabled = True
                        
                    except DiscordNotFound:
                        ToastNotification().notify(
                            title="Discord Not Found",
                            msg="Discord client not found. Discord Rich Presence will be disabled.",
                            duration='short'
                        )

                    except:pass


                elif cmd == "update":
                    try:
                        if not self.is_connected:
                            self.Presence.connect()
                            self.is_connected = True
                            self.is_enabled = True
                    except:pass 
                    try:
                        
                        state = self.update_info_dict.get("state","Listening, or maybe watching")
                        song_title = self.update_info_dict.get("song_title","")
                        self.Presence.update(state=state,
                                        details=f'JaTubePlayer - {song_title}' if song_title else "JaTubePlayer",
                                        name="JaTubePlayer",
                                        activity_type=ActivityType.LISTENING,
                                        status_display_type=StatusDisplayType.DETAILS,#wat field(detail,name,or state) to show in user status
                                        buttons=[
                                            {"label": "Check out JaTubePlayer!", "url": "https://github.com/jackaopen/JaTubePlayer"},
                                        ])  
                        self.discord_status_run() 

                    except Exception as e:
                        print(f"Failed to update Discord presence: {e}")
                        self.discord_status_close()


                elif cmd == "idle":
                    try:
                        if not self.is_connected:
                            self.Presence.connect()
                            self.is_connected = True
                            self.is_enabled = True
                    except:pass 
                    try:
                        self.update(song_title="",state="[Idling & Chillin' like a potato 🥔]")
                        self.discord_status_run()
                    except:
                        self.discord_status_close()



                   
                elif cmd == "clear":
                    try:
                        self.is_enabled = False 
                        self.Presence.clear()
                        self.discord_status_close()
                    except Exception as e:
                        print(f"Failed to clear Discord presence: {e}")





                elif cmd == "close":
                    try:
                        self.is_enabled = False
                        self.Presence.close()
                        break
                    except Exception as e:
                        print(f"Failed to close Discord presence: {e}")
                    finally:
                        break

          

        
    def update(self,song_title:str="",
               state:str="Listening, or maybe watching"):
        '''start to show presence and update presence info'''
        self.update_info_dict["song_title"] = song_title
        self.update_info_dict["state"] = state
        self.cmdqueue.put("update")
    
    def idle(self):
        self.cmdqueue.put("idle")

        
    def clear(self):
        '''Stop showing presence'''
        self.cmdqueue.put("clear")

    
    def close(self):
        '''
        Close the presence connection
        Only use for WM_CLOSE or app exit
        '''
        self.cmdqueue.put("close")


if __name__=="__main__":
    import time
    t = time.time()
    discord_presence = DiscordPresence()
    print(f"timne spent {time.time()-t}")
    discord_presence.update(song_title="some songs")
    import time
    while True:
        time. sleep(2)
        print("closing presence")
        discord_presence.clear()
        print("closed presence")
        time. sleep(2)
        print("updating presence again")
        discord_presence.update(song_title="some songs")
        