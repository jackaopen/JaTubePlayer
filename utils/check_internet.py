from notification.wintoast_notify import ToastNotification
import socket


def check_internet(func):
    def wrapper(*arg,**kwarg): 
        if check_internet_socket():  # Use fastest socket method
            return func(*arg,**kwarg)
        else:
            ToastNotification().notify(
                app_id="JaTubePlayer",
                title="JaTubePlayer",
                msg='Internet connection failed, please check your internet connection',
                duration='short',            
            )
            return None
    return wrapper

def check_internet_silent(func):
    def wrapper(*arg,**kwarg):  
        if check_internet_socket():
            return func(*arg,**kwarg)
        else:
            return None
    return wrapper

def check_internet_socket():
    """Ultra-fast socket-based internet check - typically 10-50ms"""
    dns_servers = [
        ('8.8.8.8', 53),     # Google DNS (DNS port)
        ('1.1.1.1', 53),     # Cloudflare DNS (DNS port)
        ('208.67.222.222', 53),  # OpenDNS (DNS port)
        ('8.8.8.8', 80),     # Google DNS (HTTP port)
        ('1.1.1.1', 80),     # Cloudflare DNS (HTTP port)
    ]
    
    for host, port in dns_servers:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.05)  # Increased timeout to 1 second
                sock.connect((host, port))
                return True
        except (socket.error, socket.timeout):
            continue
    return False


@check_internet
def main():
    print('hi')


if __name__ == '__main__':
    
    import time
    start = time.time()
    main()
    print(f"Check took {time.time() - start:.3f} seconds")