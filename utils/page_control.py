from loader.media_data_list import media_data_list_template
from ui.thumbnail import ThumbnailLoader
class page_control_:
    def __init__(self,
                 media_data_list:media_data_list_template,
                 ui_queue:object,
                 log_handle:object,
                 ):
        self.media_data_list = media_data_list
        self