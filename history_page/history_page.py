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
     
    @staticmethod
    def _format_history_entry(history_entry: dict) -> str:
        """Return readable history data, including the media-list contents."""
        media_data = history_entry.get("media_data")
        formatted_entry = {
            "current_playing": history_entry.get("current_playing"),
            "playlistname": history_entry.get("playlistname"),
            "media_type": history_entry.get("media_type"),
            "media_data": vars(media_data) if media_data is not None else None,
        }
        return pformat(formatted_entry, width=120, sort_dicts=False)

    def record_history(self, 
                       current_playing_url:str, 
                       media_data:media_data_list_template,
                       media_type:int,
                       playlistname:str):
        
        for _ in range(self.current_index):
            self.history_list.pop()
        self.current_index = 0
        if media_data.vid_url or current_playing_url:# not empty
            self.log_handle(component="history_page", content=(f"Recording history: {current_playing_url}, media_type: {media_type}," 
                                                               f" playlistname: {playlistname}, media_data length: {len(media_data.vid_url)}"
                                                               f" current_index: {self.current_index}, history_list length: {len(self.history_list)}"))
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
                component="history_page",
                content=(
                    f"Recorded history entry {len(self.history_list) - 1}:\n"
                    f"{self._format_history_entry(history_dict_template)}"
                ),
            )

    def read_history_backward(self)->dict|None:
        if self.current_index < len(self.history_list):
            self.current_index += 1
            history_entry = self.history_list[-self.current_index]
            self.log_handle(
                component="history_page",
                content=(
                    f"Loading history backward (current_index={self.current_index}):\n"
                    f"{self._format_history_entry(history_entry)}"
                ),
            )
            return history_entry
        else:

            self.log_handle(component="history_page", content="No more history to read")
            self.messagebox.showinfo("Jatubeplayer", "No more history to read")
            return None
    
    def read_history_forward(self)->dict|None:
        if self.current_index > 1:
            self.current_index -= 1
            history_entry = self.history_list[-self.current_index]
            self.log_handle(
                component="history_page",
                content=(
                    f"Loading history forward (current_index={self.current_index}):\n"
                    f"{self._format_history_entry(history_entry)}"
                ),
            )
            return history_entry
        else:
            self.log_handle(component="history_page", content="No more history to read")
            self.messagebox.showinfo("Jatubeplayer", "No more history to read")
            return None

    
            
            
