from flask import Flask, request
import time, requests, threading
from werkzeug.serving import make_server
from notification.wintoast_notify import ToastNotification
from flask_cors import CORS


class ChromeExtensionServer:
    def __init__(self):
        self.chrome_flaskapp = Flask(__name__)
        CORS(self.chrome_flaskapp, resources={r"/receive_url": {"origins": "chrome-extension://*"}})
        self.chrome_extension_url = None
        self.chrome_extension_star_video = None
        self.chrome_extension_add_to_end = None
        self.server = None
        self._register_routes()

    def _register_routes(self):
        # 'self' is captured via closure — Flask never needs to pass it
        @self.chrome_flaskapp.after_request
        def _pna(resp):
            resp.headers["Access-Control-Allow-Private-Network"] = "true"
            return resp

        @self.chrome_flaskapp.route("/receive_url/<action>", methods=["POST"])
        def _receive_url(action):
            try:
                url = request.data.decode()
                print(url)
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
                print(e)
                return "failed", 403

        @self.chrome_flaskapp.route("/Shutdown", methods=["POST"])
        def _shutdown():
            print(self.server)
            auth = request.headers.get("X-auth")
            icondir = request.headers.get("X-icon")

            if auth == "Jatubeplayerextensionbyjackaopen":
                try:
                    threading.Thread(target=lambda: self._shutdown_server(self.server)).start()
                    ToastNotification().notify(
                        title="JaTubePlayer",
                        msg="JaTubePlayer Chrome Extension Server Stopped",
                        duration='short',
                        icon=icondir
                    )
                    return "ok", 200
                except Exception as e:
                    print(e)
                    return "failed", 403
            else:
                return "forbidden", 403

    def _shutdown_server(self, server):
        time.sleep(0.1)
        server.shutdown()

    def run_flask_app(self, icondir: str = None):
        '''
        Note: This function will block the calling thread.
        Please run it in a separate thread if you want to keep your main thread responsive.
        '''
        self.server = make_server("127.0.0.1", 5000, self.chrome_flaskapp)
        ToastNotification().notify(
            title="JaTubePlayer",
            msg="JaTubePlayer Chrome Extension Server Started\nRunning at http://127.0.0.1:5000",
            duration='short',
            icon=icondir
        )
        print('0', self.server)
        self.server.serve_forever()


if __name__ == "__main__":
    instance = ChromeExtensionServer()
    threading.Thread(target=instance.run_flask_app, args=(None,)).start()
    print("Sending shutdown request...")
    time.sleep(2)
    try:
        res = requests.post('http://localhost:5000/Shutdown', headers={'X-auth': 'Jatubeplayerextensionbyjackaopen'}, timeout=5)
        print(f"Response: {res}")
    except Exception as e:
        print(f"Error: {e}")