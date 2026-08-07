from loader.media_data_list import media_data_list_template
from notification.ctkmessagebox import ctk_messagebox
from typing import Callable
import copy
from pprint import pformat



class history_page:
    def __init__(self,
                log_handle:Callable,
                messagebox:ctk_messagebox
                 ):
        '''
        store history of media data, and provide interface to access the history
        '''
        
        self.maxlength = 20
        self.history_list = list()
        self.current_index = 0
        self.log_handle = log_handle
        self.messagebox = messagebox
       
        '''
        This is used to count the currtent idx from the right of the list\n
        default is 0
        
        '''
     
    

    def record_history(self, 
                       current_playing_url:str, 
                       media_data:media_data_list_template,
                       media_type:int,
                       playlistname:str)->bool:
        
        for _ in range(self.current_index):
            self.history_list.pop()
        self.current_index = 0
        if media_data.vid_url or current_playing_url:# not empty
            self.log_handle(
                content=f"Recording history: {current_playing_url}, media_type: {media_type}," 
                                                               f" playlistname: {playlistname}, media_data length: {len(media_data.vid_url)}"
                                                               f" current_index: {self.current_index}, history_list length: {len(self.history_list)}",
                errtype='info',
                component="history",
            )
            history_dict_template = {"current_playing":"",
                                        "media_data":None,
                                        "playlistname":"",
                                        "media_type":-1
                                        }
            history_dict_template["current_playing"] = current_playing_url
            history_dict_template["media_data"] = copy.deepcopy(media_data)
            history_dict_template["playlistname"] = playlistname
            history_dict_template["media_type"] = media_type
            self.history_list.append(history_dict_template)
            if len(self.history_list) > self.maxlength:
                self.history_list.pop(0)
            self.log_handle(
                content=f"Recorded history entry {len(self.history_list) - 1}:\n",
                errtype='info',
                component="history",
            )
            return True
        return False

    def read_history_backward(self)->dict|None:
        if self.current_index < len(self.history_list):
            self.current_index += 1
            history_entry = self.history_list[-self.current_index]
            self.log_handle(
                content=f"Loading history backward (current_index={self.current_index}):\n",
                errtype='info',
                component="history",
            )
            return history_entry
        else:

            self.log_handle(
                content="No more history to read",
                errtype='warning',
                component="history",
            )
            self.messagebox.showinfo("Jatubeplayer", "No more history to read")
            return None
    
    def read_history_forward(self)->dict|None:
        if self.current_index > 1:
            self.current_index -= 1
            history_entry = self.history_list[-self.current_index]
            self.log_handle(
                content=f"Loading history forward (current_index={self.current_index}):\n",
                errtype='info',
                component="history",
            )
            return history_entry
        else:
            self.log_handle(
                content="No more history to read",
                errtype='warning',
                component="history",
            )
            self.messagebox.showinfo("Jatubeplayer", "No more history to read")
            return None

    
            
            
