from winotify import Notification, audio , Notifier,Registry
import time

class ToastNotification:
    def __init__(self):pass
    def notify(self,
               
               title: str,
               msg: str,
               app_id: str="JaTubePlayer",
               duration: str = 'short',
               icon: str = ""):
        '''
        icon cant be None, it must be a string, if you don't want to use an icon, just set it to an empty string.
        '''
        try:
            self.toast = Notification(
                app_id="JaTubePlayer",
                title=title,
                msg=msg,
                duration=duration,
                icon=icon
            )
            self.toast.set_audio(audio.Reminder, loop=False)
            self.toast.show()
        except Exception as e:
            print(f"Error showing notification: {e}")


if __name__ == "__main__":
    @Notifier(Registry(app_id="k")).register_callback()
    def hi():
        print("Action button clicked!")
    
    ToastNotification().notify_with_actions( title='JaTubePlayer', msg='...', launch=hi)


    