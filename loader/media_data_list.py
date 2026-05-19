class media_data_list_template:
    '''
    ### This class it the loader template for media data for playlisttreebox
    - vid_url
    - playlisttitles
    - playlist_channel
    - playlist_thumbnails
    - current_media_page
    - current_playing_idx_num
    '''
    def __init__(self):
        self.vid_url = []
        self.playlisttitles = []
        self.playlist_channel = []
        self.playlist_thumbnails = []
        self.current_media_page = 0
        self.current_playing_idx_num = -1
        
    def clear(self):
        self.vid_url.clear()
        self.playlisttitles.clear()
        self.playlist_channel.clear()
        self.playlist_thumbnails.clear()
        self.current_media_page = 0
        self.current_playing_idx_num = -1
    def stopped_playing(self):
        self.current_playing_idx_num = -1
        self.current_media_page = 0
