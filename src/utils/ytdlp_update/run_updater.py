import win32api
import win32con
import win32event
import win32process
import pywintypes
import winerror
import os
import subprocess
from win32com.shell import shell, shellcon


def run_as_admin_and_wait(
    exe_path: str,
    app_data_dir: str,
) -> int:

    try:
        info = shell.ShellExecuteEx(
            fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
            lpVerb="runas",
            lpFile=str(exe_path),
            lpParameters=subprocess.list2cmdline([app_data_dir]),
            lpDirectory=str(os.path.dirname(exe_path)),
            nShow=win32con.SW_HIDE,
        )
    except pywintypes.error as error:
        if error.winerror == winerror.ERROR_CANCELLED:
            return 1
        raise

    process = info["hProcess"]

    try:
        win32event.WaitForSingleObject(
            process,
            30_000 # Wait for 30 seconds
        )
        return win32process.GetExitCodeProcess(process)
    except subprocess.TimeoutExpired:
        return 1
    finally:
        win32api.CloseHandle(process)