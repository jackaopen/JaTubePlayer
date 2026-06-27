import json,os
from utils.get_media_info import *
from loader.get_info_loader import get_info_loader_
import queue

class star_vid_handler:
    def __init__(self,
                current_dir:str,
                get_info_loader:get_info_loader_,
                ):
        self.current_dir = current_dir
        self.get_info_loader = get_info_loader
        self._reload()
        
    def _reload(self):
        with open(os.path.join(self.current_dir,'user_data','starred_vid.json'),'rb') as f:
            self.starred_vid_dict = json.load(f)

    def _save(self):
        with open(os.path.join(self.current_dir,'user_data','starred_vid.json'),'w') as f:
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
        info = self.starred_vid_dict.get(url,None)
        return info
    
    def list_all(self,
                 loadingplaylist_flag=None
                 )->tuple[list, list, list, list]|bool:
        '''
        Run this in thread to avoid blocking the main thread, it will clear the input lists and fill them with the starred videos info, and also put the info into the treeview_queue for updating the treeview in the main thread
        This function is designed to be called when the user clicks the "Starred Videos" button, it will update the treeview with the starred videos info
        ([vid_url, 
        playlisttitles, 
        playlist_channel, 
        playlist_thumbnails])
        '''
        try:
            vid_url = []
            playlisttitles = []
            playlist_channel = []
            playlist_thumbnails = []
            
            for url in self.starred_vid_dict.keys():
                vid_url.append(url)
                info = self.starred_vid_dict[url]
                playlisttitles.append(info['title'])
                playlist_channel.append(info['channel'])
                playlist_thumbnails.append(info['thumb'])

        except Exception as e:
            self.get_info_loader.ytdlp_log_handle.info(f"Error listing starred videos: {e}")
            return False
        if loadingplaylist_flag is not None:
            loadingplaylist_flag = False

        return ([vid_url, 
                playlisttitles, 
                playlist_channel, 
                playlist_thumbnails])



if __name__ == "__main__":
    class ytdlp_log_handler():
        def debug(self, msg):
            print(msg)
        def info(self, msg):
            print(msg)
        def warning(self, msg):
            print(f"[WARN] {msg}")
        def error(self, msg):
            print(f"[ERROR] {msg}")
    import yt_dlp
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    star_vid_handler = star_vid_handler(current_dir=current_dir,
                                        yt_dlp=yt_dlp,
                                        deno_path=os.path.join(current_dir,'_internal','deno'),
                                        yt_dlp_log_handler=ytdlp_log_handler())
    
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    star_vid_handler.add(url=url)
    print(star_vid_handler.search(url=url))
    star_vid_handler.remove(url=url)
            


        