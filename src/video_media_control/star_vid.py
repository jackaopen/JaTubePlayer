import json,os
from loader.media_data_list import media_data_list_template
from utils.get_media_info import *
from utils.additional_utils import is_url_valid
from loader.get_info_loader import get_info_loader_
import queue

class star_vid_handler:
    def __init__(self,
                appdata_dir:str,
                get_info_loader:get_info_loader_,
                ):
        self.appdata_dir = appdata_dir
        self.get_info_loader = get_info_loader
        self._reload()
        
    def _reload(self):
        with open(os.path.join(self.appdata_dir,'JaTubePlayer','starred_vid.json'),'rb') as f:
            self.starred_vid_dict = json.load(f)

    def _save(self):
        with open(os.path.join(self.appdata_dir,'JaTubePlayer','starred_vid.json'),'w') as f:
            json.dump(self.starred_vid_dict,f,indent=4)

    def add(self,
            url:str,
            thumb:str =None,
            title:str = None,
            channel:str = None,
            )->bool:
        try:
            if not os.path.exists(url):
                if not thumb or not title or not channel:
                    _,info = get_info(loader=self.get_info_loader,
                                    target_url=url,
                                    )
                    
                    try:thumb = info['thumbnail']
                    except: thumb = None

                    title = info.get('title',None)
                    channel = info.get('channel',None)
            
            else:
                thumb = None
                title = os.path.basename(url)
                channel = "local file"

            info_dict = {
                "thumb":thumb,
                "title":title,
                "channel":channel
            }
            if not is_url_valid(url):
                url = os.path.abspath(url)
            self.starred_vid_dict[url] = info_dict
            self._save()
        except Exception as e:
            self.get_info_loader.ytdlp_log_handle.info(f"Error adding starred video: {e}")
            return False
        return True


    def remove(self,url:str)->bool:
        try:
            self.starred_vid_dict.pop(url,None)
            self._save()
        except Exception as e:
            self.get_info_loader.ytdlp_log_handle.info(f"Error removing starred video: {e}")
            return False
        return True
    
    def search(self,url:str)->dict|None:
        if not is_url_valid(url):
            url = os.path.abspath(url)
        info = self.starred_vid_dict.get(url,None)
        return info
    
    def list_all(self,
                 loadingplaylist_flag=None
                 )->media_data_list_template:
        '''
        Run this in thread to avoid blocking the main thread, it will clear the input lists and fill them with the starred videos info, and also put the info into the treeview_queue for updating the treeview in the main thread
        This function is designed to be called when the user clicks the "Starred Videos" button, it will update the treeview with the starred videos info
        ([vid_url, 
        playlisttitles, 
        playlist_channel, 
        playlist_thumbnails])
        '''
        try:
            media_data_list = media_data_list_template()

            for url in self.starred_vid_dict.keys():
                media_data_list.vid_url.append(url)
                info = self.starred_vid_dict[url]
                media_data_list.playlisttitles.append(info['title'])
                media_data_list.playlist_channel.append(info['channel'])
                media_data_list.playlist_thumbnails.append(info['thumb'])
            return media_data_list
        except Exception as e:
            self.get_info_loader.ytdlp_log_handle.info(f"Error listing starred videos: {e}")
            return media_data_list_template()
        



            


        