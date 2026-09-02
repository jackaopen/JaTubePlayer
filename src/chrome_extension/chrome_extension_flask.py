from flask import Flask, request
import threading
import queue
from werkzeug.serving import make_server
import urllib.parse as urlparse
from notification.wintoast_notify import ToastNotification
from flask_cors import CORS
from video_media_control.media_list_page_control import MediaList_PageControl_
from video_media_control.star_vid import star_vid_handler
from notification.ctkmessagebox import ctk_messagebox
from utils.get_media_info import get_info
from loader.get_info_loader import get_info_loader_

class ChromeExtensionServer:
    def __init__(self, 
                 log_handle: object,
                 media_list_page_controller: MediaList_PageControl_,
                 Chrome_ext_server_ui_functions: object,
                 star_vid_handle: star_vid_handler,
                 messagebox:ctk_messagebox,
                 ui_queue: queue.Queue,
                 get_info_loader: get_info_loader_):
        

        self.log_handle = log_handle
        self.media_list_page_controller = media_list_page_controller
        self.ext_ui_functions = Chrome_ext_server_ui_functions
        self.star_vid_handle = star_vid_handle
        self.messagebox = messagebox
        self.ui_queue = ui_queue
        self.get_info_loader = get_info_loader
        self.server_port = 5000  # Default port for the Flask server
        self.chrome_flaskapp = Flask(__name__)
        
        CORS(self.chrome_flaskapp, resources={r"/receive_url": {"origins": "chrome-extension://*"}})
        

        self.server = None
        self._register_routes()


    def direct_url(self,url:str)-> None:
        self.log_handle(
            content=f"Direct URL received: {url}",
            errtype='info',
            component='chrome_ext',
        )
        
        if self.media_list_page_controller.handle_url_drop(url):
            self.ext_ui_functions.direct_url(url=url)



    def _register_routes(self):
        @self.chrome_flaskapp.after_request
        def _pna(resp):
            resp.headers["Access-Control-Allow-Private-Network"] = "true"
            return resp

        @self.chrome_flaskapp.route("/receive_url/<action>", methods=["POST"])
        def _receive_url(action):
            try:
                url = request.data.decode().split("&")[0]
                if urlparse.urlparse(url).scheme not in ["http", "https"]:
                    self.log_handle(
                        content=f"Received URL with unsupported scheme from Chrome extension: {url}",
                        errtype='error',
                        component='chrome_ext',
                    )
                    return "unsupported scheme", 400
                if urlparse.urlparse(url).hostname not in ["www.youtube.com", "youtu.be","www.twitch.tv"]:
                    self.log_handle(
                        content=f"Received URL with unsupported hostname from Chrome extension: {url}",
                        errtype='error',
                        component='chrome_ext',
                    )
                    return "unsupported hostname", 400
                self.log_handle(
                    content=f"Received URL from Chrome extension: {url} with action: {action}",
                    errtype='info',
                    component='chrome_ext',
                )
                auth = request.headers.get("X-auth")

                if auth != "Jatubeplayerextensionbyjackaopen":
                    return "forbidden", 403
                
                if action == 'dir':
                    self.direct_url(url)

                

                elif action == 'star':
                    self.log_handle(
                        content=f"chrome extension star video url: {url}",
                        errtype='info',
                        component='chrome_ext',
                    )
                    if not self.star_vid_handle.search(url):
                        res = self.star_vid_handle.add(url)
                        if res:ToastNotification().notify(app_id="JaTubePlayer", 
                                                        title=f'JaTubePlayer ', 
                                                        msg='Added starred video to playlist\nFetching data...', 
                                                        duration='short')
                        else:
                            self.log_handle(
                                content=f"Failed to add starred video from chrome extension, error in adding: {res}",
                                errtype='error',
                                component='chrome_ext',
                            )
                            self.ui_queue.put(lambda: self.messagebox.showerror(f'JaTubePlayer ', "Failed to add starred video to playlist.\nError in adding video."))
                        if self.ext_ui_functions.get_playing_vid_mode() == 4:
                            self.ext_ui_functions.show_star_video()

                    else:
                        self.ui_queue.put(lambda: self.messagebox.showinfo(f'JaTubePlayer ', "This video is already in your starred list."))
                
                
                elif action == 'add_to_end':
                    playing_vid_mode = self.ext_ui_functions.get_playing_vid_mode()
                    if playing_vid_mode ==0 or playing_vid_mode == 3 or playing_vid_mode == 4:
                        self.log_handle(
                            content=f"Adding video to playlist from chrome extension: {url}",
                            errtype='info',
                            component='chrome_ext',
                        )
                        try:

                            ToastNotification().notify(app_id="JaTubePlayer", 
                                                        title=f'JaTubePlayer', 
                                                        msg='Added video to playlist\nFetching data...', 
                                                        duration='short', 
                                    )
                            _,info = get_info(loader=self.get_info_loader,          
                                                target_url=url
                            )

                            try:thumb = info['thumbnail']
                            except:thumb = None
                            
                            self.media_list_page_controller.add_to_page_end(
                                video_url=url,
                                title=info['title'],
                                channel=info['uploader'],
                                thumbnail_url=thumb
                            )


                            ToastNotification().notify(app_id="JaTubePlayer",
                                                        title=f'JaTubePlayer',
                                                        msg='Added video to playlist',
                                                        duration='short')
                        except Exception as e:
                            self.log_handle(
                                content=f"Error adding video to playlist: {e}",
                                errtype='error',
                                component='chrome_ext',
                            )
                            self.ui_queue.put(lambda: self.messagebox.showerror(f'JaTubePlayer ', f"Failed to add video to playlist.\nError: {e}"))
                    else:
                        self.ui_queue.put(lambda: self.messagebox.showinfo(f'JaTubePlayer ', "You are in local media mode, cannot add video to playlist.\nYou can star the video to add it to the starred list, then go to starred mode to watch it."))
                return "ok", 200
            except Exception as e:
                self.log_handle(
                    content='Error receiving URL from Chrome extension: ' + str(e),
                    errtype='error',
                    component='chrome_ext',
                )
                return "failed", 403

    def _shutdown_server(self, server):
        self.log_handle(
            content='Chrome extension server shutdown initiated.',
            errtype='info',
            component='chrome_ext',
        )
        server.shutdown()      # stop serve_forever() 
        server.server_close()  # release the socket 
        self.log_handle(
            content='Chrome extension server has been shut down.',
            errtype='info',
            component='chrome_ext',
        )

    def shutdown(self, icondir: str = None):
        if self.server:
            threading.Thread(
                target=lambda: self._shutdown_server(self.server),
                daemon=True
            ).start()
        else:
            self.log_handle(
                content='shutdown() called but server is not running.',
                errtype='info',
                component='chrome_ext',
            )

    def run_flask_app(self, icondir: str = None):
        self.server = make_server("127.0.0.1", self.server_port, self.chrome_flaskapp, threaded=True)
        self.server.timeout = 1
        self.server.protocol_version = "HTTP/1.0"  # disables keep-alive
        ToastNotification().notify(
            title="Chrome Extension Server",
            msg="Started\nRunning at http://127.0.0.1:" + str(self.server_port),
            duration='short',
            icon=icondir
        )
        self.log_handle(
            content=f"Chrome extension server started at {self.server}",
            errtype='info',
            component='chrome_ext',
        )
        self.server.serve_forever(poll_interval=0.5)

