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
        '''
        default 0, globally from 1 to end
        '''
        self.current_playing_idx_num = -1
        '''
        globally from 0 to len(vid_url)-1, default -1
        '''
        
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
        
    def set(self, mdl: 'media_data_list_template'):
        self.vid_url = mdl.vid_url
        self.playlisttitles = mdl.playlisttitles
        self.playlist_channel = mdl.playlist_channel
        self.playlist_thumbnails = mdl.playlist_thumbnails
        self.current_media_page = mdl.current_media_page
        self.current_playing_idx_num = mdl.current_playing_idx_num