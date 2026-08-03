import enum
import queue
import random
from loader.media_data_list import media_data_list_template
from ui.Treeview_and_thumbnail import ThumbnailLoader
from .playlist_retriever import playlist_retriever_,playlist_type
from .star_vid import star_vid_handler
from .local_media_handle import local_media_handle
from notification.ctkmessagebox import ctk_messagebox
from history_page.history_page import history_page
from typing import Callable
import copy

class MediaType(enum.IntEnum):
    '''
    - -1:None
    - 0 Youtube playlist
    - 1 Youtube liked videos    
    - 2 Youtube subscriptions
    - 3 Youtube recommend videos
    - 4 Local folder
    - 5 Starred video 
    - 6 Direct URL drop
    '''
    NONE = -1# not inited
    YOUTUBE = 0
    LIKE = 1
    SUB = 2
    RECOMMEND = 3
    FOLDER = 4
    STARRED_VIDEO = 5
    DIRECT_URL_DROP = 6


class MediaList_PageControl_:
    '''
    The MLPC (Media List Page Control)
    this class controls the media list and page control,
    include online/local,
    will insert the current page data to ui queue, to update the ui
    This will only do job for yt playlist(playlist,sub,like), folders, star 
    search currently dose not support page control

    all passed mdl must belong to jtp
    '''
    def __init__(self,
                 ui_queue:queue.Queue,
                 tree_view_queue:queue.Queue,
                 log_handle:object,
                 thumbnail_loader:ThumbnailLoader,
                 page_num_label :object,
                 load_thread_queue:queue.Queue,
                 playlist_retriever:playlist_retriever_,
                 history_page_handler:history_page,
                 Chrome_ext_server_ui_functions:object,
                 messagebox:ctk_messagebox,
                 get_cur_playing_url:Callable,
                 get_cur_playlist_title:Callable,
                 ):
        self.total_page = 0
        self.current_page = 1
        '''
        page num for which page treebox is showing
        '''
        self.media_type = MediaType.NONE
        self.media_data_list = media_data_list_template()
        self.local_media_handler = local_media_handle(log_handle=log_handle)

        self.ui_queue = ui_queue
        self.tree_view_queue = tree_view_queue
        self.log_handle = log_handle
        self.thumbnail_loader = thumbnail_loader
        self.yt_playlist_retriever = playlist_retriever
        self.history_page_handler = history_page_handler
        self.Chrome_ext_server_ui_functions = Chrome_ext_server_ui_functions
        self.page_num_label = page_num_label # for controling UI
        self.messagebox = messagebox
        self.loading_page = False

        self.user_playlist_dict = {"name":'',
                                    "url":''}
        self.user_playlist_dict_list = []


        
        

        self.load_thread_queue = load_thread_queue
        self._get_cur_playing_url = get_cur_playing_url
        self._get_cur_playlist_title = get_cur_playlist_title
        self._prev_playlist_name=""
        '''
        This is used to record the playlist name brfore retrieving playlisttype.PLAYLISTS is changed
        \n thus the playlist name can be restored correctly
        '''

    def _insert_to_ui_queue(self):
        '''
        insert the current page data to ui queue, to update the ui

        will calculate the start and end index of the current page, and insert the data to ui queue
        '''

        self.thumbnail_loader.clear_thumbnails()
        self.ui_queue.put(lambda: self.page_num_label.configure(text=f'page {self.current_page}/{self.total_page}'))
        start_index = (self.current_page - 1) * 50
        end_index = min(self.current_page * 50, len(self.media_data_list.vid_url))
        self.log_handle(errtype='info', component='page_control',
                        content=f'load page {self.current_page}/{self.total_page} items {start_index}-{max(start_index, end_index - 1)}')
        for i in range(start_index, end_index):
            self.tree_view_queue.put((self.media_data_list.playlist_thumbnails[i],
                                      self.media_data_list.playlisttitles[i],
                                      self.media_data_list.playlist_channel[i]))
        

    def _record_history(self,
                        playlistname:str=None)->bool:
        current_playing_url = ''
        try:
            current_playing_url = self._get_cur_playing_url()
        except Exception as e:
            self.log_handle(errtype='error', component='page_control/HPH',content=f'Failed to get current playing url: {e}')
            
        result = self.history_page_handler.record_history(current_playing_url=current_playing_url, 
                                                media_data=self.media_data_list,
                                                media_type=self.media_type,
                                                playlistname=playlistname or self._get_cur_playlist_title())
        if result:
            self.log_handle(errtype='info', component='page_control/HPH',content=f'record hisory PLAYLIST{playlistname or self._get_cur_playlist_title()} ')
            return True
        else:
            self.log_handle(errtype='warning', component='page_control/HPH',content=f'Failed to record history PLAYLIST{playlistname or self._get_cur_playlist_title()} ')
            return False


    def youtube_init_and_reload(self,
                        media_data_list:media_data_list_template,
                        page:playlist_type,
                        playlist_id:str=None
                        ):
        '''
        Follow the page type to init and reload the media_data_list for youtube playlist, liked videos, subscriptions, recommend videos\n
        > IMPORTANT: PLEASE make sure the cookie and AES key are valid before calling this function, otherwise it will return without loading data\n
        if page is playlist_type.PLAYLIST, the playlist_id must be provided, and the user_playlist_dict_list will be filled with the playlist content\n
        if page is not playlist_type.PLAYLIST, the media_data_list will be filled with
        if page is playlist_type.PLAYLISTS, the user_playlist_dict_list will be filled with the playlist content, mdl and other var will not be modified\n
        '''
        if page!= playlist_type.PLAYLISTS:
            self.log_handle(errtype='info', component='page_control',content=f'init reload media_type= youtube page={page} playlist_id={playlist_id} total_items={len(media_data_list.vid_url)}')
            if page == playlist_type.PLAYLIST:
                
                self._record_history(self._prev_playlist_name if self._prev_playlist_name else None)
                self._prev_playlist_name = ''
            else:
                self._record_history()

            self.current_page = 1
            self.media_data_list = media_data_list
            self.media_type = MediaType.YOUTUBE
            self.media_data_list.clear()
        else:
            self._prev_playlist_name = self._get_cur_playlist_title()
            self.log_handle(errtype='info', component='page_control',content=f'record prev playlist name={self._prev_playlist_name}')
    
        if self.yt_playlist_retriever.innertube_handle.account_handle.check_aes_key() == False:return 
        if self.yt_playlist_retriever.innertube_handle.account_handle.check_cookie_exist() == False: return
        
        if page != playlist_type.PLAYLISTS:
            self.media_data_list = self.yt_playlist_retriever.get_playlist_content(page=page, playlist_id=playlist_id)
            self.total_page = (len(self.media_data_list.vid_url) + 49) // 50
            self._insert_to_ui_queue()

        else:
            self.user_playlist_dict_list.clear()
            temp_mdl = self.yt_playlist_retriever.get_playlist_content(page=page, playlist_id=playlist_id)
            for name,url in zip(temp_mdl.playlisttitles,temp_mdl.vid_url):
                self.user_playlist_dict = {"name":name,
                                           "url":url}
                self.user_playlist_dict_list.append(self.user_playlist_dict)
        
        self.log_handle(errtype='info', component='page_control',
                        content=f'init reload media_type= youtube total_items={len(self.media_data_list.vid_url)} total_page={self.total_page}')

    

    def star_video_init_and_reload(self,
                                    star_vid_handler_:star_vid_handler,
                                    ):
        self._record_history()
        self.current_page = 1
        self.media_type = MediaType.STARRED_VIDEO
        
        self.media_data_list = copy.deepcopy(star_vid_handler_.list_all())
        self.media_data_list.current_media_page = 1  
        self.media_data_list.current_playing_idx_num = -1
        
        self.total_page = (len(self.media_data_list.vid_url) + 49) // 50

        self._insert_to_ui_queue()
        self.log_handle(errtype='info', component='page_control',
                        content=f'init reload media_type= starred videos total_items={len(self.media_data_list.vid_url)} total_page={self.total_page}')

        
    def local_files_init_and_reload(self,
                                    media_data_list:media_data_list_template,
                                    quick_start_folder_path:str=None,
                                    mode_for_local_files:int = -1,
                                    dnd_mode:bool=False,
                                    )->None|bool:
        '''
        will be called by local_media_handler to init and reload the media_data_list for local files
        mode_for_local_files: 0 for single file, 1 for folder

        return : None if successfully load, False if failed
        '''
        self._record_history()
        self.current_page = 1
        self.media_type = MediaType.FOLDER
        
        if dnd_mode is False:# JTP called this, calling local_media_handler to get the data
            mdl_result = self.local_media_handler.load_local_files(mode=mode_for_local_files, 
                                                                             local_folder_path=quick_start_folder_path)
            if mdl_result is not None:
                media_data_list.set(mdl_result)
                self.media_data_list = media_data_list
            else:
                return False
        else: # dnd called this, media_data_list is already filled
            self.media_data_list = media_data_list

        self.media_data_list.current_media_page = 1  
        self.media_data_list.current_playing_idx_num = -1
        
        self.total_page = (len(self.media_data_list.vid_url) + 49) // 50

        self._insert_to_ui_queue()
        self.log_handle(errtype='info', component='page_control',
                        content=f'init reload media_type= localfiles total_items={len(self.media_data_list.vid_url)} total_page={self.total_page}')
    


    def handle_url_drop(self, url:str):
        self._record_history()
        self.media_type = MediaType.DIRECT_URL_DROP
        self.log_handle(content=f"URL dropped: {url}")
        self.thumbnail_loader.clear_thumbnails()
        self.log_handle(errtype='info', component='page_control',
                        content=f'handle url drop, url={url}')
        self.load_thread_queue.put((None,url))
        self.log_handle(errtype='info', component='page_control',
                        content=f'put url drop to load_thread_queue, url={url}')
        

    def search_init_and_reload(self,
                                media_data_list:media_data_list_template,
                                searchentry:str,
                                yt_dlp:object,
                                ytdlp_log_handle:object,
                                cookie:str):
        
        self._record_history()
        self.thumbnail_loader.clear_thumbnails()
        self.media_data_list.clear()
        self.current_page = 1
        self.media_type = MediaType.YOUTUBE


        search_url_vid = f"https://www.youtube.com/results?search_query={searchentry}&sp=EgIQAQ%253D%253D "  
        search_url_stream = f"https://www.youtube.com/results?search_query={searchentry}&sp=EgJAAQ%253D%253D "  
        ydl_opts = {
            'quiet': True,        
            'extract_flat': True,  # Get video list without downloading
            'force_generic_extractor': True,
            'skip_download':True,
            'playlistend':40,
        }

        if cookie:
            ydl_opts.setdefault("http_headers", {})["Cookie"] = cookie
        ydl_opts['logger'] = ytdlp_log_handle

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            vid_search_results = ydl.extract_info(search_url_vid, download=False)
            #ydl_opts['playlistend'] = 30
            stream_search_results = ydl.extract_info(search_url_stream, download=False)
        

        for item in stream_search_results['entries']:
            if item and  'url' in item:
                if item['url'].split('youtube.com/')[1].split('/')[0] != 'channel':
                    try:
                        thumbnail_url = f"https://i.ytimg.com/vi/{item['url'].split('v=')[1]}/hqdefault.jpg"
                    except IndexError:
                        thumbnail_url = f"https://i.ytimg.com/vi/{item['url'].split('shorts/')[1]}/hqdefault.jpg"

                    media_data_list.vid_url.append(item['url'])
                    media_data_list.playlisttitles.append(f"🛑LIVE {item['title']}")
                    media_data_list.playlist_thumbnails.append(thumbnail_url)
                    media_data_list.playlist_channel.append(item['channel'])



        for item in vid_search_results['entries']:
            if item and  'url' in item:
                if item['url'].split('youtube.com/')[1].split('/')[0] != 'channel':
                    try:
                        thumbnail_url = f"https://i.ytimg.com/vi/{item['url'].split('v=')[1]}/hqdefault.jpg"
                    except IndexError:
                        thumbnail_url = f"https://i.ytimg.com/vi/{item['url'].split('shorts/')[1]}/hqdefault.jpg"

                    media_data_list.vid_url.append(item['url'])
                    media_data_list.playlisttitles.append(item['title'])
                    media_data_list.playlist_thumbnails.append(thumbnail_url)
                    media_data_list.playlist_channel.append(item['channel'])

        self.media_data_list = media_data_list
        self.media_data_list.current_media_page = 1  
        self.media_data_list.current_playing_idx_num = -1 
        self.total_page = (len(self.media_data_list.vid_url) + 49) // 50

        self._insert_to_ui_queue()


    def history_page_init_and_reload(self,
                                    media_data_list:media_data_list_template,
                                    media_type:int):
        self.thumbnail_loader.clear_thumbnails()
        self.media_data_list.clear()
        self.current_page = 1
        self.media_type = media_type
        
        self.media_data_list.set(copy.deepcopy(media_data_list))
        self.total_page = (len(self.media_data_list.vid_url) + 49) // 50
        
        self._insert_to_ui_queue()
        self.log_handle(errtype='info', component='page_control',
                        content=f'init reload media_type= history page total_items={len(self.media_data_list.vid_url)} total_page={self.total_page}')
        


    def _other_loading(self):
        #TODO
        pass
    
    def add_to_page_end(self,
            video_url:str,
            title:str, 
            channel:str,
            thumbnail_url:str):
        '''
        insert video wether there is page inited or not,
        at the last current page, miaght exceed 50
        '''

        self.media_type = MediaType.YOUTUBE
        if self.total_page == 0:# mdl not inited
            self.total_page = 1
            self.current_page = 1

        try:
            if self.current_page == self.total_page:
                insert_idx = len(self.media_data_list.vid_url)
            else:
                insert_idx = (self.current_page-1) * 50

            title = f"[Added] {title}"
            self.media_data_list.vid_url.insert(insert_idx, video_url)
            self.media_data_list.playlisttitles.insert(insert_idx, title)
            self.media_data_list.playlist_channel.insert(insert_idx, channel)
            self.media_data_list.playlist_thumbnails.insert(insert_idx, thumbnail_url)
            self.Chrome_ext_server_ui_functions.add_to_end()
            self.tree_view_queue.put((thumbnail_url,
                                        title,
                                        channel))
            self.log_handle(errtype='info', component='page_control',
                            content=f'added video to media list, at index {insert_idx}, title={title} channel={channel} url={video_url} thumbnail={thumbnail_url}')
            
        except Exception as e:
            self.log_handle(content=str(e))


    def clear_selected(self,
                        selected_idx:int,
                        selected_tree_ID:str):
        '''
        clear the selected video from the media data list and treeview, and clear the playing tag if the selected video is playing
        '''
        try:
            self.media_data_list.vid_url.pop(selected_idx)
            self.media_data_list.playlisttitles.pop(selected_idx)
            self.media_data_list.playlist_channel.pop(selected_idx)
            self.media_data_list.playlist_thumbnails.pop(selected_idx)
            self.thumbnail_loader.clear_thumb(selected_tree_ID)



        except Exception as e:
            self.log_handle(content=str(e))
        


    def next_page(self,
                  select_first_of_next_page:bool=False,
                  selected_follow:bool=True)->int:
        '''
        return 0 if successfully load next page, return -1 if still loading, return -2 if failed -3 if media type does not support page control
        selected_follow: if True, will load the page of treeview, else only change the page number, and load the page when the page is selected
        '''
        _total_page_of_current_data = (len(self.media_data_list.vid_url) + 49) // 50
        if _total_page_of_current_data < self.current_page + 1 and self.current_page != self.total_page:
            self.log_handle(errtype='warning', component='page_control',
                            content=f'page still loading,totalpagecurrentdata ={_total_page_of_current_data}, total_page={self.total_page}, current_page={self.current_page}')
            
            
            
            return -1
        self.log_handle(errtype='info', component='page_control',
                        content=f'try to load next page,totalpagecurrentdata ={_total_page_of_current_data}, current_page={self.current_page} total_page={self.total_page}')
        try:
            if self.loading_page:
                self.log_handle(errtype='warning', component='page_control',
                                content=f'This page is still loading, current_page={self.current_page} total_page={self.total_page}')
                return -1
            self.loading_page = True
            if self.media_type in [MediaType.YOUTUBE,MediaType.FOLDER,MediaType.STARRED_VIDEO]:
                if selected_follow:
                    if self.current_page < self.total_page:
                        self.current_page += 1
                    else:
                        self.current_page = 1
                    self.log_handle(errtype='info', component='page_control',
                                    content=f'next page -> {self.current_page}/{self.total_page}\n current media page in MDL {self.media_data_list.current_media_page}')
                
                    self._insert_to_ui_queue()
                    
                    if select_first_of_next_page:
                        self.thumbnail_loader.select_first_item()
                        
                        self.log_handle(errtype='info', component='page_control',
                                        content=f'select first item of next page')
                    if self.current_page == self.media_data_list.current_media_page:
                        self.set_playing_tag(self.media_data_list.current_playing_idx_num)
                return 0
            else:
                self.log_handle(errtype='warning', component='page_control',
                                content=f'current media type does not support page control, media_type={self.media_type}')
                return -3
        except Exception as e:
            self.log_handle(content=str(e))
            return -2
        finally:
            self.loading_page = False



    def prev_page(self, 
                select_last_of_prev_page:bool=False,
                selected_follow:bool=True)->int:
        '''
        return 0 if successfully load previous page, return -1 if still loading, return -2 if failed -3 if media type does not support page control
        selected_follow: if True, will load the page of treeview, else only change the page number, and load the page when the page is selected
        '''
        _total_page_of_current_data = (len(self.media_data_list.vid_url) + 49) // 50
        if self.current_page == 1 and _total_page_of_current_data < self.total_page:
            self.log_handle(errtype='warning', component='page_control',
                            content=f'page still loading,totalpagecurrentdata ={_total_page_of_current_data}, total_page={self.total_page}, current_page={self.current_page}')
            return -1
        self.log_handle(errtype='info', component='page_control',
                        content=f'try to load previous page,totalpagecurrentdata ={_total_page_of_current_data}, current_page={self.current_page} total_page={self.total_page}')
        try:
            if self.loading_page:
                self.log_handle(errtype='warning', component='page_control',
                                content=f'This page is still loading, current_page={self.current_page} total_page={self.total_page}')
                return -1
            self.loading_page = True   
            if self.media_type in [MediaType.YOUTUBE,MediaType.FOLDER,MediaType.STARRED_VIDEO]:
                if selected_follow:
                    if self.current_page > 1:
                        self.current_page -= 1
                    else:
                        self.current_page = self.total_page
                    self.log_handle(errtype='info', component='page_control',
                                    content=f'previous page -> {self.current_page}/{self.total_page}\n current media page in MDL {self.media_data_list.current_media_page}')
                    
                    self._insert_to_ui_queue()
                    if select_last_of_prev_page:
                        self.thumbnail_loader.select_last_item()
                        self.log_handle(errtype='info', component='page_control',
                                        content=f'select last item of previous page')
                    if self.current_page == self.media_data_list.current_media_page:
                        self.set_playing_tag(self.media_data_list.current_playing_idx_num)
                return 0
            else:
                self.log_handle(errtype='warning', component='page_control',
                                content=f'current media type does not support page control, media_type={self.media_type}')
        except Exception as e:
            self.log_handle(content=str(e)) 
            return -3
        finally:
            self.loading_page = False


    def random_media(self,
                     selected_idx : int = -1) -> int:
        '''
        random select a video from the mediadata list and return the idx
        will automatically load the page of the video if the video is not in the current page
        return -2 if list are not fully loaded, return -1 if failed
        '''
        if len(self.media_data_list.vid_url)//50+1 != self.total_page:
            return -2
        try:
            random_idx = random.randint(0, len(self.media_data_list.vid_url)-1)
            self.current_page = random_idx//50+1
            if self.media_data_list.current_playing_idx_num == selected_idx:
                self._insert_to_ui_queue()
                self.thumbnail_loader.root.after(1000, lambda: self.thumbnail_loader.select_item(random_idx%50))
            self.log_handle(errtype='info', component='page_control',
                            content=f'randomly selected video: {random_idx}, page: {self.current_page}')
            self.media_data_list.current_media_page = self.current_page
            self.media_data_list.current_playing_idx_num = random_idx

        except Exception as e:
            self.log_handle(content=str(e))
            return -1
        return random_idx


    def set_playing_tag(self, idx:int, tag:str = "playing"):
        '''
        idx: the index of the video in the media data list, 
        tag : "playing" or "normal"
        only set the tag when the video is in the current page, otherwise do nothing, since the tag will be set when the page is loaded
        '''

        page_idx = idx % 50
        if self.media_data_list.current_media_page == self.current_page:
            self.thumbnail_loader.set_item_color(page_idx % 50, tag)

    def remove_playing_tag(self)->None:
        '''
        remove ALL the placed tag in current page
        '''
        self.thumbnail_loader.clear_all_tag()
            
    def clear(self):
        '''
        mainly for single and chrome mode, clear the media data list and reset the page control
        does not automatically clear thumbtreeview, need to call thumbnail_loader.clear_thumbnails() to clear the treeview
        '''
        self.media_data_list = media_data_list_template()
        self.total_page = 0
        self.current_page = 1
        self.media_type = MediaType.NONE
        self.log_handle(errtype='info', component='page_control',
                        content=f'cleared media data and reset page control')
        
        
        


