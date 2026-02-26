import json,os
from .get_media_info import *
import queue

class star_vid_handler:
    def __init__(self,
                current_dir:str,
                yt_dlp:object,
                deno_path:str,
                yt_dlp_log_handler:object,
                ):
        self.current_dir = current_dir
        self.yt_dlp = yt_dlp
        self.deno_path = deno_path
        self.yt_dlp_log_handler = yt_dlp_log_handler
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
            cookie_path:str=None)->bool:
        try:
            if not os.path.exists(url):
            
                if not thumb or not title or not channel:
                    _,info = get_info(yt_dlp=self.yt_dlp,#both yt and twitch
                                    maxres=1080,
                                    target_url=url,
                                    deno_path=self.deno_path,
                                    log_handler=self.yt_dlp_log_handler,
                                    cookie_path=cookie_path)
                    
                    try:thumb = info['thumbnails'][0]['url']
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
            self.yt_dlp_log_handler.info(f"Error adding starred video: {e}")
            return False
        return True


    def remove(self,url:str)->bool:
        try:
            self.starred_vid_dict.pop(url,None)
            self._save()
        except Exception as e:
            self.yt_dlp_log_handler.info(f"Error removing starred video: {e}")
            return False
        return True
    
    def search(self,url:str)->dict|None:
        info = self.starred_vid_dict.get(url,None)
        return info
    
    def list_all(self,
                 treeview_queue:queue.Queue,
                 vid_url:list,
                 playlisttitles:list,
                 playlist_channel:list,
                 playlist_thumbnails:list
                 )->bool:
        '''
        Run this in thread to avoid blocking the main thread, it will clear the input lists and fill them with the starred videos info, and also put the info into the treeview_queue for updating the treeview in the main thread
        This function is designed to be called when the user clicks the "Starred Videos" button, it will update the treeview with the starred videos info
        '''
        try:
            vid_url.clear()
            playlisttitles.clear()
            playlist_channel.clear()
            playlist_thumbnails.clear()
            
            for url in self.starred_vid_dict.keys():
                vid_url.append(url)
                info = self.starred_vid_dict[url]
                playlisttitles.append(info['title'])
                playlist_channel.append(info['channel'])
                playlist_thumbnails.append(info['thumb'])

                treeview_queue.put((info['thumb'],info['title'],info['channel']))
        except Exception as e:
            self.yt_dlp_log_handler.info(f"Error listing starred videos: {e}")
            return False
        return True


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
            


        