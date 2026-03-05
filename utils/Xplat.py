"""
Cross-platform switcher demo
Shows how to structure your code so Windows / Linux / macOS
are selected automatically at runtime.
"""

import platform
import queue
from typing import Callable

# ── detect once, use everywhere ──────────────────────────────────────────────
SYSTEM = platform.system()   # "Windows" | "Linux" | "Darwin"

print(f"[platform] Detected: {SYSTEM}")


# ─────────────────────────────────────────────────────────────────────────────
# 1.  DROP HANDLER  (same class on every platform via tkinterdnd2)
# ─────────────────────────────────────────────────────────────────────────────

def make_drop_handler(dnd_path_queue: queue.Queue, root):
    """
    tkinterdnd2 works on Windows / Linux / macOS — no branching needed here.
    The only difference is that your root window must be TkinterDnD.Tk().
    """
    from tkinterdnd2 import TkinterDnD, DND_FILES   # pip install tkinterdnd2
    import re

    class DropHandler:
        def __init__(self, q, widget):
            self.q = q
            self.enable_drop(widget, True)

        def enable_drop(self, widget, enable: bool):
            if enable:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<Drop>>", self._on_drop)
            else:
                widget.drop_target_unregister()

        def _on_drop(self, event):
            # tkinterdnd2 returns  {/path with spaces} /simple/path  etc.
            files = re.findall(r"\{([^}]+)\}|(\S+)", event.data)
            files = [a or b for a, b in files]
            self.q.put(files)
            print(f"[DnD] Dropped: {files}")

    return DropHandler(dnd_path_queue, root)


# ─────────────────────────────────────────────────────────────────────────────
# 2.  SHORTCUT / APP REGISTRATION  (one class, branches inside)
# ─────────────────────────────────────────────────────────────────────────────

class ShortcutManager:
    def __init__(self, app_user_model_id: str, main_path: str):
        self.app_id   = app_user_model_id
        self.main_path = main_path

    # public API ──────────────────────────────────────────────────────────────
    def create(self):
        dispatch = {
            "Windows": self._create_windows,
            "Linux":   self._create_linux,
            "Darwin":  self._create_mac,
        }
        dispatch.get(SYSTEM, self._unsupported)()

    def cleanup(self):
        dispatch = {
            "Windows": self._cleanup_windows,
            "Linux":   self._cleanup_linux,
            "Darwin":  self._cleanup_mac,
        }
        dispatch.get(SYSTEM, self._unsupported)()

    # Windows ─────────────────────────────────────────────────────────────────
    def _create_windows(self):
        import os
        from win32com.shell import shell, shellcon          # pip install pywin32
        from win32com.propsys import propsys
        import pythoncom

        start_menu    = shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0)
        shortcut_path = os.path.join(start_menu, "JaTubePlayer.lnk")

        shell_link = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
        )
        shell_link.SetPath(self.main_path)
        shell_link.SetDescription("JaTubePlayer")

        ps  = shell_link.QueryInterface(propsys.IID_IPropertyStore)
        key = propsys.PSGetPropertyKeyFromName("System.AppUserModel.ID")
        ps.SetValue(key, propsys.PROPVARIANTType(self.app_id))
        ps.Commit()

        shell_link.QueryInterface(pythoncom.IID_IPersistFile).Save(shortcut_path, 0)
        print(f"[Shortcut] Windows: {shortcut_path}")

    def _cleanup_windows(self):
        import os
        from win32com.shell import shell, shellcon
        path = os.path.join(
            shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0),
            "JaTubePlayer.lnk"
        )
        if os.path.exists(path):
            os.remove(path)

    # Linux ───────────────────────────────────────────────────────────────────
    def _create_linux(self):
        import os
        apps_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(apps_dir, exist_ok=True)
        path = os.path.join(apps_dir, "JaTubePlayer.desktop")
        with open(path, "w") as f:
            f.write(f"""[Desktop Entry]
Name=JaTubePlayer
Exec={self.main_path}
Type=Application
Categories=AudioVideo;
StartupWMClass=JaTubePlayer
""")
        os.chmod(path, 0o755)
        print(f"[Shortcut] Linux .desktop: {path}")

    def _cleanup_linux(self):
        import os
        path = os.path.expanduser("~/.local/share/applications/JaTubePlayer.desktop")
        if os.path.exists(path):
            os.remove(path)

    # macOS ───────────────────────────────────────────────────────────────────
    def _create_mac(self):
        # macOS uses app bundles + CFBundleIdentifier in Info.plist.
        # For a plain script (not bundled), write a LaunchAgent plist instead.
        import os, plistlib
        agents = os.path.expanduser("~/Library/LaunchAgents")
        os.makedirs(agents, exist_ok=True)
        path = os.path.join(agents, f"{self.app_id}.plist")
        plist = {
            "Label":           self.app_id,
            "ProgramArguments": [self.main_path],
            "RunAtLoad":       False,
        }
        with open(path, "wb") as f:
            plistlib.dump(plist, f)
        print(f"[Shortcut] macOS LaunchAgent: {path}")

    def _cleanup_mac(self):
        import os
        path = os.path.expanduser(f"~/Library/LaunchAgents/{self.app_id}.plist")
        if os.path.exists(path):
            os.remove(path)

    def _unsupported(self):
        print(f"[Shortcut] Platform '{SYSTEM}' not supported.")


# ─────────────────────────────────────────────────────────────────────────────
# 3.  MEDIA CONTROLS  (different class per platform, same public API)
# ─────────────────────────────────────────────────────────────────────────────

def make_media_overlay(
    next_song_fun: Callable = None,
    prev_song_fun: Callable = None,
    pause_fun:     Callable = None,
):
    """
    Factory — returns the right implementation for the current OS.
    All three share the same public API:
        .update_media_info(title, artist, album, thumbnail_url=None)
        .set_playing()
        .set_paused()
        .destroy()
    """
    if SYSTEM == "Windows":
        return _MediaOverlayWindows(next_song_fun, prev_song_fun, pause_fun)
    elif SYSTEM == "Linux":
        return _MediaOverlayLinux(next_song_fun, prev_song_fun, pause_fun)
    elif SYSTEM == "Darwin":
        return _MediaOverlayMac(next_song_fun, prev_song_fun, pause_fun)
    else:
        raise RuntimeError(f"Unsupported platform: {SYSTEM}")


class _MediaOverlayWindows:
    """Uses winsdk / SMTC — your existing implementation."""

    def __init__(self, next_fn, prev_fn, pause_fn):
        from winsdk.windows.media.playback import BackgroundMediaPlayer   # pip install winsdk
        from winsdk.windows.media import (
            MediaPlaybackType, MediaPlaybackStatus, SystemMediaTransportControlsButton
        )
        from winsdk.windows.foundation import Uri
        from winsdk.windows.storage.streams import RandomAccessStreamReference

        self._Uri  = Uri
        self._Ref  = RandomAccessStreamReference
        self._MPT  = MediaPlaybackType
        self._MPS  = MediaPlaybackStatus
        self._Btn  = SystemMediaTransportControlsButton

        self.smtc = BackgroundMediaPlayer.current.system_media_transport_controls
        self.smtc.is_play_enabled = self.smtc.is_pause_enabled = True
        self.smtc.is_next_enabled = self.smtc.is_previous_enabled = True
        self.smtc.add_button_pressed(self._on_btn)

        self.next_fn  = next_fn
        self.prev_fn  = prev_fn
        self.pause_fn = pause_fn

        self.updater = self.smtc.display_updater
        self.updater.app_media_id = "Jackaopen.JaTubePlayer"

    def _on_btn(self, sender, args):
        btn = args.button
        Btn = self._Btn
        MPS = self._MPS
        if   btn == Btn.PLAY:     self.pause_fn and self.pause_fn(1); self.smtc.playback_status = MPS.PLAYING
        elif btn == Btn.PAUSE:    self.pause_fn and self.pause_fn(1); self.smtc.playback_status = MPS.PAUSED
        elif btn == Btn.NEXT:     self.next_fn  and self.next_fn()
        elif btn == Btn.PREVIOUS: self.prev_fn  and self.prev_fn()

    def update_media_info(self, title, artist, album, thumbnail_url=None):
        self.smtc.is_enabled = True
        self.updater.type = self._MPT.MUSIC
        p = self.updater.music_properties
        p.title = title; p.artist = artist; p.album_title = album
        if thumbnail_url:
            self.updater.thumbnail = self._Ref.create_from_uri(self._Uri(thumbnail_url))
        self.smtc.playback_status = self._MPS.PLAYING
        self.updater.update()

    def set_playing(self):  self.smtc.playback_status = self._MPS.PLAYING
    def set_paused(self):   self.smtc.playback_status = self._MPS.PAUSED
    def destroy(self):      self.smtc.is_enabled = False


class _MediaOverlayLinux:
    """Uses MPRIS2 over D-Bus — pip install dbus-python PyGObject"""

    def __init__(self, next_fn, prev_fn, pause_fn):
        import dbus, dbus.service
        from dbus.mainloop.glib import DBusGMainLoop
        from gi.repository import GLib
        import threading

        DBusGMainLoop(set_as_default=True)
        bus      = dbus.SessionBus()
        bus_name = dbus.service.BusName("org.mpris.MediaPlayer2.JaTubePlayer", bus)

        # Build the D-Bus object inline
        class _MPRISObject(dbus.service.Object):
            def __init__(inner, next_fn, prev_fn, pause_fn):
                super().__init__(bus_name, "/org/mpris/MediaPlayer2")
                inner._next    = next_fn
                inner._prev    = prev_fn
                inner._pause   = pause_fn
                inner._meta    = {}
                inner._status  = "Playing"

            @dbus.service.method("org.mpris.MediaPlayer2")
            def Raise(inner): pass
            @dbus.service.method("org.mpris.MediaPlayer2")
            def Quit(inner):  pass

            @dbus.service.method("org.mpris.MediaPlayer2.Player")
            def PlayPause(inner):
                if inner._pause: inner._pause(1)
            @dbus.service.method("org.mpris.MediaPlayer2.Player")
            def Next(inner):
                if inner._next: inner._next()
            @dbus.service.method("org.mpris.MediaPlayer2.Player")
            def Previous(inner):
                if inner._prev: inner._prev()

            @dbus.service.signal("org.freedesktop.DBus.Properties", signature="sa{sv}as")
            def PropertiesChanged(inner, iface, changed, invalid): pass

            def _emit(inner, changed):
                inner.PropertiesChanged("org.mpris.MediaPlayer2.Player", changed, [])

        self._obj  = _MPRISObject(next_fn, prev_fn, pause_fn)
        self._loop = GLib.MainLoop()
        threading.Thread(target=self._loop.run, daemon=True).start()

    def update_media_info(self, title, artist, album, thumbnail_url=None):
        import dbus
        meta = {
            "xesam:title":  title,
            "xesam:artist": dbus.Array([artist], signature="s"),
            "xesam:album":  album,
        }
        if thumbnail_url:
            meta["mpris:artUrl"] = thumbnail_url
        self._obj._meta   = meta
        self._obj._status = "Playing"
        self._obj._emit({
            "Metadata":       dbus.Dictionary(meta, signature="sv"),
            "PlaybackStatus": "Playing",
        })

    def set_playing(self):
        self._obj._status = "Playing"
        self._obj._emit({"PlaybackStatus": "Playing"})

    def set_paused(self):
        self._obj._status = "Paused"
        self._obj._emit({"PlaybackStatus": "Paused"})

    def destroy(self):
        self._loop.quit()


class _MediaOverlayMac:
    """Uses MPNowPlayingInfoCenter — pip install pyobjc-framework-MediaPlayer"""

    def __init__(self, next_fn, prev_fn, pause_fn):
        from MediaPlayer import (                           # pyobjc
            MPNowPlayingInfoCenter, MPRemoteCommandCenter,
            MPMediaItemPropertyTitle, MPMediaItemPropertyArtist,
            MPMediaItemPropertyAlbumTitle,
            MPNowPlayingInfoPropertyPlaybackRate,
        )
        self._ic   = MPNowPlayingInfoCenter.defaultCenter()
        self._keys = (
            MPMediaItemPropertyTitle,
            MPMediaItemPropertyArtist,
            MPMediaItemPropertyAlbumTitle,
            MPNowPlayingInfoPropertyPlaybackRate,
        )
        cmd = MPRemoteCommandCenter.sharedCommandCenter()
        cmd.playCommand().addTargetWithHandler_(lambda _: (pause_fn and pause_fn(1), 0)[1])
        cmd.pauseCommand().addTargetWithHandler_(lambda _: (pause_fn and pause_fn(1), 0)[1])
        cmd.nextTrackCommand().addTargetWithHandler_(lambda _: (next_fn and next_fn(), 0)[1])
        cmd.previousTrackCommand().addTargetWithHandler_(lambda _: (prev_fn and prev_fn(), 0)[1])

    def update_media_info(self, title, artist, album, thumbnail_url=None):
        T, A, AL, R = self._keys
        self._ic.setNowPlayingInfo_({T: title, A: artist, AL: album, R: 1.0})

    def set_playing(self):
        info = dict(self._ic.nowPlayingInfo() or {})
        info[self._keys[3]] = 1.0
        self._ic.setNowPlayingInfo_(info)

    def set_paused(self):
        info = dict(self._ic.nowPlayingInfo() or {})
        info[self._keys[3]] = 0.0
        self._ic.setNowPlayingInfo_(info)

    def destroy(self):
        self._ic.setNowPlayingInfo_(None)


# ─────────────────────────────────────────────────────────────────────────────
# DEMO ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n=== Platform demo running on: {SYSTEM} ===\n")

    # Shortcuts
    sm = ShortcutManager("Jackaopen.JaTubePlayer", "/usr/local/bin/jatubeplayerr")
    sm.create()

    # Media overlay
    overlay = make_media_overlay(
        next_song_fun = lambda: print("[demo] next song"),
        prev_song_fun = lambda: print("[demo] prev song"),
        pause_fun     = lambda _: print("[demo] pause/play toggled"),
    )
    overlay.update_media_info("Never Gonna Give You Up", "Rick Astley", "Whenever You Need Somebody")

    import time
    time.sleep(3)
    overlay.set_paused()
    time.sleep(2)
    overlay.set_playing()
    time.sleep(3)
    overlay.destroy()

    sm.cleanup()
    print("\n=== Demo complete ===")
