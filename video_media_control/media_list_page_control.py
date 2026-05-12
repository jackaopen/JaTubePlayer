import enum
import queue
from loader.media_data_list import media_data_list_template
from ui.thumbnail import ThumbnailLoader
from .playlist_retriever import playlist_retriever


class MediaType(enum.IntEnum):
    '''
    - -1:None
    - 0 Youtube playlist
    - 1 Youtube liked videos    
    - 2 Youtube subscriptions
    - 3 Youtube recommend videos
    - 4 Local folder
    - 5 Starred video 
    '''
    NONE = -1# not inited
    YOUTUBE = 0
    LIKE = 1
    SUB = 2
    RECOMMEND = 3
    FOLDER = 4
    STARRED_VIDEO = 5


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
        self.media_data_list = media_data_list_template()

        self.ui_queue = ui_queue
        self.tree_view_queue = tree_view_queue
        self.log_handle = log_handle
        self.thumbnail_loader = thumbnail_loader
        self.page_num_label = page_num_label # for controling UI

        self.loading_page = False
        
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
        self.media_type = MediaType.YOUTUBE
    
        
        self.yt_playlist_retriever.init_playlist_items(
            youtube=youtube,
            playlist_id=playlist_id,
            media_data_list=self.media_data_list,
        )
        self.total_page = (self.yt_playlist_retriever.total_playlist_count + 49) // 50

        self._insert_to_ui_queue()
        self.log_handle(errtype='info', component='page_control',
                        content=f'init reload media_type= youtube total_items={len(self.media_data_list.vid_url)} total_page={self.total_page}')

    
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
        try:
            if self.current_page == self.total_page:
                insert_idx = len(self.media_data_list.vid_url)
            else:
                insert_idx = (self.current_page) * 50

            title = f"[Added] {title}"
            self.media_data_list.vid_url.insert(insert_idx, video_url)
            self.media_data_list.playlisttitles.insert(insert_idx, title)
            self.media_data_list.playlist_channel.insert(insert_idx, channel)
            self.media_data_list.playlist_thumbnails.insert(insert_idx, thumbnail_url)

            self.tree_view_queue.put((self.media_data_list.playlist_thumbnails[insert_idx],
                                        self.media_data_list.playlisttitles[insert_idx],
                                        self.media_data_list.playlist_channel[insert_idx]))
            self.log_handle(errtype='info', component='page_control',
                            content=f'added video to media list, at index {insert_idx}, title={title} channel={channel} url={video_url} thumbnail={thumbnail_url}')

        except Exception as e:
            self.log_handle(content=str(e))


    def clear_selected(self,
                        selected_idx:int,
                        selected_tree_ID:str):
        try:
            self.media_data_list.vid_url.pop(selected_idx)
            self.media_data_list.playlisttitles.pop(selected_idx)
            self.media_data_list.playlist_channel.pop(selected_idx)
            self.media_data_list.playlist_thumbnails.pop(selected_idx)
            self.thumbnail_loader.clear_thumb(selected_tree_ID)



        except Exception as e:
            self.log_handle(content=str(e))
        


    def next_page(self,
                  select_first_of_next_page:bool=False)->int:
        '''
        return 0 if successfully load next page, return -1 if still loading, return -2 if failed -3 if media type does not support page control
        
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
                if self.current_page < self.total_page:
                    self.current_page += 1
                else:
                    self.current_page = 1
                self.log_handle(errtype='info', component='page_control',
                                content=f'next page -> {self.current_page}/{self.total_page}')
                self._insert_to_ui_queue()
                
                if select_first_of_next_page:
                    self.thumbnail_loader.root.after(100, self.thumbnail_loader.select_first_item)
                    self.log_handle(errtype='info', component='page_control',
                                    content=f'select first item of next page')

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
                    select_last_of_prev_page:bool=False):
        '''
         return 0 if successfully load previous page, return -1 if still loading, return -2 if failed -3 if media type does not support page control
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
                if self.current_page > 1:
                    self.current_page -= 1
                else:
                    self.current_page = self.total_page
                self.log_handle(errtype='info', component='page_control',
                                content=f'previous page -> {self.current_page}/{self.total_page}')
                self._insert_to_ui_queue()
                if select_last_of_prev_page:
                    self.thumbnail_loader.root.after(100, self.thumbnail_loader.select_last_item)
                return 0
            else:
                self.log_handle(errtype='warning', component='page_control',
                                content=f'current media type does not support page control, media_type={self.media_type}')
        except Exception as e:
            self.log_handle(content=str(e)) 
            return -3
        finally:
            self.loading_page = False

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
        
        
        


