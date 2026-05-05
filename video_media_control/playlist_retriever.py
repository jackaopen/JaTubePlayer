import googleapiclient
import googleapiclient.errors

from notification.ctkmessagebox import ctk_messagebox as messagebox
from loader.media_data_list import media_data_list_template
import threading

class playlist_retriever:
    '''
    Mainly for retrieving the playlist items for youtube, and insert them into the media_data_list_template, then the media_list_page_control will insert them into the ui queue
    '''
    def __init__(self,log_handle:object,
                 ui_queue:object
                 ):
        self.youtube = None
        self.next_page_token = None
        self.log_handle = log_handle
        self.playlistID = None
        self.ui_queue = ui_queue

        self.total_playlist_count = 0
        self._playlist_items = []
        self.media_data_list = None
        


    def _prase_playlist(self):
        '''
        this function is for parsing the playlist items and insert them into the media_data_list_template
        '''
        for item in self._playlist_items:
            try:
                video_id = item['contentDetails']['videoId']
                title_response = self.youtube.videos().list(
                    part='snippet',
                    id=video_id
                ).execute()
                self.media_data_list.vid_url.append(f"https://www.youtube.com/watch?v={video_id}")
                vid_info = title_response['items'][0]['snippet']
                self.media_data_list.playlist_channel.append(vid_info['channelTitle'])
                self.media_data_list.playlisttitles.append(vid_info['title'])
                self.media_data_list.playlist_thumbnails.append(vid_info['thumbnails']['high']['url'])
                
            except Exception as e:
                self.log_handle(content=str(e))
        self._playlist_items.clear() #clear the playlist items to save memory
        

    def init_playlist_items(self,youtube:object,
                                playlist_id:str,
                                media_data_list:media_data_list_template,
                                ):
        '''
        This only get first 50 item for mlpc,
        '''
        try:
            self.media_data_list = media_data_list
            self.youtube = youtube
            self.playlistID = playlist_id
            playlist_response = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=self.playlistID,
                maxResults=50,
                
            ).execute()
            self._playlist_items.extend(playlist_response['items'])
            self.next_page_token = playlist_response.get('nextPageToken')
            self.total_playlist_count = playlist_response['pageInfo']['totalResults']
            self._prase_playlist()
            threading.Thread(target=self._retrieve_playlist_left, daemon=True).start()
        
        except googleapiclient.errors.HttpError as err: ######  handle stupid api
            self.log_handle(errtype='error', component='playlist_retriever',
                            content=f"An HTTP error occurred while retrieving playlist: {err}")
            self.ui_queue.put(lambda e=err: messagebox.showerror('JaTubePlayer', f"An HTTP error occurred while retrieving playlist: {e}")) 
        
        except Exception as e:
            self.log_handle(content=str(e))
            self.ui_queue.put(lambda err=e: messagebox.showerror('JaTubePlayer', f"An error occurred while retrieving playlist: {err}"))

    def _retrieve_playlist_left(self):
        '''
        This is for retrieving the rest of the playlist items, please use thread to call it
        '''
        while self.next_page_token:
            try:
                playlist_response = self.youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=self.playlistID,
                    maxResults=50,
                    pageToken=self.next_page_token
                ).execute()
                self._playlist_items.extend(playlist_response['items'])
                self.next_page_token = playlist_response.get('nextPageToken')
                self._prase_playlist()
            except Exception as e:
                self.log_handle(content=str(e))
                break
