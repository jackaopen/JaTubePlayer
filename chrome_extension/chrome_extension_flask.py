from flask import Flask, request
import socket, threading
from werkzeug.serving import make_server
from notification.wintoast_notify import ToastNotification
from flask_cors import CORS


class ChromeExtensionServer:
    def __init__(self, log_handle: object):
        self.log_handle = log_handle
        self.chrome_flaskapp = Flask(__name__)
        CORS(self.chrome_flaskapp, resources={r"/receive_url": {"origins": "chrome-extension://*"}})
        self.chrome_extension_url = None
        self.chrome_extension_star_video = None
        self.chrome_extension_add_to_end = None
        self.server = None
        self._register_routes()

    def _register_routes(self):
        @self.chrome_flaskapp.after_request
        def _pna(resp):
            resp.headers["Access-Control-Allow-Private-Network"] = "true"
            return resp

        @self.chrome_flaskapp.route("/receive_url/<action>", methods=["POST"])
        def _receive_url(action):
            try:
                url = request.data.decode()
                self.log_handle(f"Received URL from Chrome extension: {url} with action: {action}")
                auth = request.headers.get("X-auth")

                if action == 'dir':
                    self.chrome_extension_url = url
                elif action == 'star':
                    self.chrome_extension_star_video = url
                elif action == 'add_to_end':
                    self.chrome_extension_add_to_end = url

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