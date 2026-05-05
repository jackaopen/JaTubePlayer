import enum
import queue
from loader.media_data_list import media_data_list_template
from ui.thumbnail import ThumbnailLoader
from .playlist_retriever import playlist_retriever


class MediaType(enum.IntEnum):
    '''
    0. youtube video
    1. single open with (local file)
    2. folder (local folder)
    3. chrome
    4. starred video (starred video list)
    '''
    NONE = -1# not inited
    YOUTUBE = 0
    SINGLE_OPEN_WITH = 1
    FOLDER = 2
    CHROME = 3
    STARRED_VIDEO = 4


class MediaList_PageControl_:
    '''
    this class controls the media list and page control,
    include online/local,
    will insert the current page data to ui queue, to update the ui
    This will only do job for yt playlist(playlist,sub,like), folders, star 
    search currently dose not support page control
    '''
    def __init__(self,
                 ui_queue:queue.Queue,
                 tree_view_queue:queue.Queue,
                 log_handle:object,
                 thumbnail_loader:ThumbnailLoader,
                 page_num_label = object
                 ):
        self.total_page = 0
        self.current_page = 1
        self.media_type = MediaType.NONE
        self.media_data_list = None
        self.ui_queue = ui_queue
        self.tree_view_queue = tree_view_queue
        self.log_handle = log_handle
        self.thumbnail_loader = thumbnail_loader
        self.page_num_label = page_num_label # for controling UI
        
        self.yt_playlist_retriever = playlist_retriever(
            log_handle=self.log_handle,
            ui_queue=self.ui_queue)



    def _insert_to_ui_queue(self):
        '''
        insert the current page data to ui queue, to update the ui
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




    def youtube_init_and_reload(self,
                        media_data_list:media_data_list_template,
                        youtube:object=None,
                        playlist_id:str=None,
                        ):
               
        self.current_page = 1
        self.media_data_list = media_data_list
        self.log_handle(errtype='info', component='page_control',
                        content=f'init reload media_type= youtube total_items={len(self.media_data_list.vid_url)} total_page={self.total_page}')
        self.media_type = MediaType.YOUTUBE
        
        
        self.yt_playlist_retriever.init_playlist_items(
            youtube=youtube,
            playlist_id=playlist_id,
            media_data_list=self.media_data_list,
        )
        self.total_page = (self.yt_playlist_retriever.total_playlist_count + 49) // 50

        self._insert_to_ui_queue()
    
    def add():
        #TODO: add media item to current media list
        pass

    def next_page(self)->int:
        '''
        return 0 if successfully load next page, return -1 if still loading, return -2 if failed -3 if media type does not support page control
        
        '''
        _total_page_of_current_data = (len(self.media_data_list.vid_url) + 49) // 50
        if _total_page_of_current_data < self.current_page + 1 and self.current_page != self.total_page:
            self.log_handle(errtype='warning', component='page_control',
                            content=f'page still loading, current_page={self.current_page} total_page={self.total_page}')
            
            
            
            return -1
        try:
            if self.media_type in [MediaType.YOUTUBE,MediaType.FOLDER,MediaType.STARRED_VIDEO]:
                if self.current_page < self.total_page:
                    self.current_page += 1
                else:
                    self.current_page = 1
                self.log_handle(errtype='info', component='page_control',
                                content=f'next page -> {self.current_page}/{self.total_page}')
                self._insert_to_ui_queue()
                return 0
            else:
                self.log_handle(errtype='warning', component='page_control',
                                content=f'current media type does not support page control, media_type={self.media_type}')
                return -3
        except Exception as e:
            self.log_handle(content=str(e))
            return -2

    def prev_page(self):
        '''
         return 0 if successfully load previous page, return -1 if still loading, return -2 if failed -3 if media type does not support page control
        '''
        _total_page_of_current_data = (len(self.media_data_list.vid_url) + 49) // 50
        if _total_page_of_current_data < self.current_page and self.current_page != self.total_page:
            self.log_handle(errtype='warning', component='page_control',
                            content=f'page still loading, current_page={self.current_page} total_page={self.total_page}')
            return -1
        try:
            if self.media_type in [MediaType.YOUTUBE,MediaType.FOLDER,MediaType.STARRED_VIDEO]:
                if self.current_page > 1:
                    self.current_page -= 1
                else:
                    self.current_page = self.total_page
                self.log_handle(errtype='info', component='page_control',
                                content=f'previous page -> {self.current_page}/{self.total_page}')
                self._insert_to_ui_queue()
                return 0
            else:
                self.log_handle(errtype='warning', component='page_control',
                                content=f'current media type does not support page control, media_type={self.media_type}')
        except Exception as e:
            self.log_handle(content=str(e)) 
            return -3

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
        
        


