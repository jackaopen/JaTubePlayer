from flask import Flask, request
import threading
import queue
from werkzeug.serving import make_server

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

        self.chrome_flaskapp = Flask(__name__)
        
        CORS(self.chrome_flaskapp, resources={r"/receive_url": {"origins": "chrome-extension://*"}})
        

        self.server = None
        self._register_routes()


    def direct_url(self,url:str)-> None:
        self.log_handle(f"Direct URL received: {url}")
        self.ext_ui_functions.direct_url()
        self.media_list_page_controller.handle_url_drop(url)



    def _register_routes(self):
        @self.chrome_flaskapp.after_request
        def _pna(resp):
            resp.headers["Access-Control-Allow-Private-Network"] = "true"
            return resp

        @self.chrome_flaskapp.route("/receive_url/<action>", methods=["POST"])
        def _receive_url(action):
            try:
                url = request.data.decode().split("&")[0]
                self.log_handle(f"Received URL from Chrome extension: {url} with action: {action}")
                auth = request.headers.get("X-auth")

                if action == 'dir':
                    self.direct_url(url)



                elif action == 'star':
                    self.log_handle(content=f"chrome extension star video url: {url}")
                    if not self.star_vid_handle.search(url):
                        res = self.star_vid_handle.add(url)
                        if res:ToastNotification().notify(app_id="JaTubePlayer", 
                                                        title=f'JaTubePlayer ', 
                                                        msg='Added starred video to playlist\nFetching data...', 
                                                        duration='short')
                        else:
                            self.log_handle(content=f"Failed to add starred video from chrome extension, error in adding: {res}")
                            self.ui_queue.put(lambda: self.messagebox.showerror(f'JaTubePlayer ', "Failed to add starred video to playlist.\nError in adding video."))
                        if self.ext_ui_functions.get_playing_vid_mode() == 4:
                            self.ext_ui_functions.show_star_video()

                    else:
                        self.ui_queue.put(lambda: self.messagebox.showinfo(f'JaTubePlayer ', "This video is already in your starred list."))
                
                
                elif action == 'add_to_end':
                    playing_vid_mode = self.ext_ui_functions.get_playing_vid_mode()
                    if playing_vid_mode ==0 or playing_vid_mode == 3 or playing_vid_mode == 4:
                        self.log_handle(content=f"Adding video to playlist from chrome extension: {url}")
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
                            self.log_handle(content=f"Error adding video to playlist: {e}")
                            self.ui_queue.put(lambda: self.messagebox.showerror(f'JaTubePlayer ', f"Failed to add video to playlist.\nError: {e}"))
                    else:
                        self.ui_queue.put(lambda: self.messagebox.showinfo(f'JaTubePlayer ', "You are in local media mode, cannot add video to playlist.\nYou can star the video to add it to the starred list, then go to starred mode to watch it."))





                if auth == "Jatubeplayerextensionbyjackaopen":
                    return "ok", 200
                else:
                    return "forbidden", 403
            except Exception as e:
                self.log_handle('Error receiving URL from Chrome extension: ' + str(e))
                return "failed", 403

    def _shutdown_server(self, server):
        self.log_handle('Chrome extension server shutdown initiated.')
        server.shutdown()      # stop serve_forever() 
        server.server_close()  # release the socket 
        self.log_handle('Chrome extension server has been shut down.')

    def shutdown(self, icondir: str = None):
        if self.server:
            threading.Thread(
                target=lambda: self._shutdown_server(self.server),
                daemon=True
            ).start()
        else:
            self.log_handle('shutdown() called but server is not running.')

    def run_flask_app(self, icondir: str = None):
        self.server = make_server("127.0.0.1", 5000, self.chrome_flaskapp, threaded=True)
        self.server.timeout = 1
        self.server.protocol_version = "HTTP/1.0"  # disables keep-alive
        ToastNotification().notify(
            title="JaTubePlayer",
            msg="JaTubePlayer Chrome Extension Server Started\nRunning at http://127.0.0.1:5000",
            duration='short',
            icon=icondir
        )
        self.log_handle(f"Chrome extension server started at {self.server}")
        self.server.serve_forever(poll_interval=0.5)



'''
if playing_vid_mode ==0 or playing_vid_mode == 3 or playing_vid_mode == 4:
            url = chrome_extension_flask.chrome_extension_add_to_end.split("&")[0]
            log_handle(content=f"Adding video to playlist from chrome extension: {url}")
            try:
                modetitle = modetextbox.get("1.0", "end").strip()

                ui_queue.put(lambda: modetextbox.configure(state="normal"))
                if "[with added video]" not in modetitle:
                    ui_queue.put(lambda mt=modetitle: (
                        modetextbox.delete(1.0, tk.END),
                        modetextbox.insert(tk.END, f"{mt} [with added video]")
                    ))
                ui_queue.put(lambda: modetextbox.configure(state="disabled"))


                if playing_vid_mode == 3:
                    playing_vid_mode = 0
                    selected_song_number = None

                ToastNotification().notify(app_id="JaTubePlayer", 
                                            title=f'JaTubePlayer ', 
                                            msg='Added video to playlist\nFetching data...', 
                                            duration='short', 
                                            icon=icondir)
                _,info = get_info(loader=get_info_loader,          
                                    target_url=url
                )
                log_handle(content = info['thumbnail'])

                try:thumb = info['thumbnail']
                except:thumb = None
                
                Media_list_page_controller.add_to_page_end(
                    video_url=url,
                    title=info['title'],
                    channel=info['uploader'],
                    thumbnail_url=thumb
                )


                ToastNotification().notify(app_id="JaTubePlayer",
                                            title=f'JaTubePlayer ',
                                            msg='Added video to playlist',
                                            duration='short',
                                            icon=icondir)
            except Exception as e:
                log_handle(content=f"Error adding video to playlist: {e}")
                messagebox.showerror(f'JaTubePlayer ', f"Failed to add video to playlist.\nError: {e}")    
            finally:
                chrome_extension_flask.chrome_extension_add_to_end = None
        else:
            ui_queue.put(lambda: messagebox.showinfo(f'JaTubePlayer ', "You are in local media mode, cannot add video to playlist.\nYou can star the video to add it to the starred list, then go to starred mode to watch it."))



'''