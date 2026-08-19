import re
import subprocess
import os


class twitch_handle:
    def __init__(self,
                 log_handle:object,
                 _internal_dir:str
                 ):
        self.twitch_streamlink_process = None
        self.log_handle = log_handle
        self.streamlink_path = os.path.join(_internal_dir,"streamlink","bin","streamlink.exe")


    def stop_twitch_streamlink(self):
        if (self.twitch_streamlink_process is None or 
            self.twitch_streamlink_process.poll() is not None):
            return
        self.twitch_streamlink_process.terminate()
        try:
            self.twitch_streamlink_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.twitch_streamlink_process.kill()
            self.twitch_streamlink_process.wait()
        finally:
            self.twitch_streamlink_process = None

    def start_twitch_streamlink(self,
                                twitch_url:str):

        self.stop_twitch_streamlink()

        command = [
            self.streamlink_path,
            "--loglevel", "info",
            "--player-external-http",
            "--player-external-http-interface", "127.0.0.1",
            "--player-external-http-port", "0",
            "--player-external-http-continuous", "no",
            twitch_url.strip(),
            "best",
        ]

        self.twitch_streamlink_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        self.log_handle(
            content="start process",
            errtype = "info",
            component = "twitch handle")

        # Streamlink prints the randomly selected local HTTP address.
        for line in iter(self.twitch_streamlink_process.stdout.readline, ""):
            self.log_handle(
                content=line.strip(),
                errtype="info",
                component="streamlink",
            )

            match = re.search(r"http://127\.0\.0\.1:\d+/?", line)
            if match:
                return match.group(0)

            if self.twitch_streamlink_process.poll() is not None:
                break

        self.stop_twitch_streamlink()
        return None