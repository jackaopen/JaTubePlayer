from flask import Flask,request
import time,requests,threading
from werkzeug.serving import make_server
from notification.wintoast_notify import ToastNotification
from flask_cors import CORS
chrome_flaskapp = Flask(__name__)
CORS(chrome_flaskapp,resources={r"/receive_url": {"origins": "chrome-extension://*"}})
chrome_extension_url = None


@chrome_flaskapp.after_request
def _pna(resp):
    # Add Access-Control-Allow-Private-Network header to every response
    resp.headers["Access-Control-Allow-Private-Network"] = "true"
    return resp

def _shutdown_server(server):
    time.sleep(0.1)
    server.shutdown()
    
@chrome_flaskapp.route("/receive_url", methods=["POST"])
def _receive_url():

    try:
        global chrome_extension_url
        url = request.data.decode()
        print(url)
        auth = request.headers.get("X-auth")

        '''if url.split('https://www.youtube.com/')[1] == '':
            return "invalid url",403'''
        chrome_extension_url = url
        
        if auth == "Jatubeplayerextensionbyjackaopen":
            
                return "ok",200
        else:return "forbidden",403
    except Exception as e:
        print(e)
        return "failed",403


@chrome_flaskapp.route("/Shutdown",methods = ["POST"])
def _shutdown():
    global server
    print(server)
    auth = request.headers.get("X-auth")
    icondir = request.headers.get("X-icon")
    
    if auth == "Jatubeplayerextensionbyjackaopen":
        try:
            print('1',server)
            threading.Thread(target=lambda :_shutdown_server(server)).start()
            ToastNotification().notify(title="JaTubePlayer",
                                msg="JaTubePlayer Chrome Extension Server Stopped",
                                duration='short',
                                icon=icondir)                                  
            return "ok",200
        except Exception as e :
            print(e)
            return "failed",403
    else:return "forbidden",403

def run_flask_app(icondir:str=None):
    '''
    Note: This function will block the main thread.
    please run it in a separate thread if you want to keep your main thread responsive.
    '''
    global server
    server = make_server("127.0.0.1", 5000, chrome_flaskapp)
    ToastNotification().notify(title="JaTubePlayer",
                        msg="JaTubePlayer Chrome Extension Server Started\nRunning at http://127.0.0.1:5000",
                        duration='short',
                        icon=icondir)
    print('0',server)
    server.serve_forever()
    

def _chrome_flask_run():
    global server
    t = threading.Thread(
            target= run_flask_app,
            daemon=True
        )
    t.start()
    time.sleep(1)

if __name__ == "__main__":

    threading.Thread(target=run_flask_app).start()
    print("Sending shutdown request...")
    time.sleep(2)
    try:
        res = requests.post('http://localhost:5000/Shutdown',headers={'X-auth':'Jatubeplayerextensionbyjackaopen'},timeout=5)
        print(f"Error:{res}")
    except Exception as e:
       print(f"Error:{e}")
