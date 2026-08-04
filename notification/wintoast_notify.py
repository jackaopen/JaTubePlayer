from win11toast import notify as show_toast
class ToastNotification:
    def notify(
        self,
        title: str,
        msg: str,
        app_id: str = "Jackaopen.JaTubePlayer",
        duration: str = "short",
        icon: str = "",
    ):
        try:
            show_toast(
                title,
                msg,
                app_id=app_id,
                duration=duration,
                icon={
                    "src": icon,
                    "placement": "appLogoOverride",
                } if icon else None,
                audio="ms-winsoundevent:Notification.Reminder",
            )
        except Exception as e:
            print(f"Error showing notification: {e}")