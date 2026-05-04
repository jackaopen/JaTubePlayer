import enum
import queue
from loader.media_data_list import media_data_list_template


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
    include online/local
    '''
    def __init__(self,
                 media_data_list:media_data_list_template,
                 ui_queue:queue.Queue,
                 tree_view_queue:queue.Queue,
                 log_handle:object,
                 thumbnail_loader:object
                 ):
        self.media_data_list = media_data_list
        self.total_page = 0
        self.current_page = 1
        self.media_type = MediaType.NONE
        self.ui_queue = ui_queue
        self.tree_view_queue = tree_view_queue
        self.log_handle = log_handle
        self.thumbnail_loader = thumbnail_loader
    def _insert_to_ui_queue(self):
        '''
        insert the current page data to ui queue, to update the ui
        '''
        self.thumbnail_loader.clear_thumbnails()

        start_index = (self.current_page - 1) * 50
        end_index = min(self.current_page * 50, len(self.media_data_list.vid_url))
        self.log_handle(errtype='info', component='page_control',
                        content=f'load page {self.current_page}/{self.total_page} items {start_index}-{max(start_index, end_index - 1)}')
        for i in range(start_index, end_index):
            self.tree_view_queue.put((self.media_data_list.playlist_thumbnails[i],
                                      self.media_data_list.playlisttitles[i],
                                      self.media_data_list.playlist_channel[i]))

    def init_and_reload(self,
                        media_type:int,
                        new_media_data_list:media_data_list_template):
        
        self.media_data_list = new_media_data_list
        self.total_page = len(self.media_data_list.vid_url) // 50 + 1
        self.current_page = 1
        self.media_type = MediaType(media_type)
        self.log_handle(errtype='info', component='page_control',
                        content=f'init reload media_type={self.media_type.name} total_items={len(self.media_data_list.vid_url)} total_page={self.total_page}')
        self._insert_to_ui_queue()

    def next_page(self):
        if self.media_type in [MediaType.YOUTUBE,MediaType.FOLDER,MediaType.STARRED_VIDEO]:
            if self.current_page < self.total_page:
                self.current_page += 1
            else:
                self.current_page = 1
            self.log_handle(errtype='info', component='page_control',
                            content=f'next page -> {self.current_page}/{self.total_page}')
            self._insert_to_ui_queue()

    def prev_page(self):
        if self.media_type in [MediaType.YOUTUBE,MediaType.FOLDER,MediaType.STARRED_VIDEO]:
            if self.current_page > 1:
                self.current_page -= 1
            else:
                self.current_page = self.total_page
            self.log_handle(errtype='info', component='page_control',
                            content=f'previous page -> {self.current_page}/{self.total_page}')
            self._insert_to_ui_queue()
    
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
        
        


