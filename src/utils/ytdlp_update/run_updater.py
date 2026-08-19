import win32api
import win32con
import win32event
import win32process
import pywintypes
import winerror
import os
import subprocess
from win32com.shell import shell, shellcon
from enum import Enum, auto

class UpdaterState(Enum):
    COMPLETED = auto()
    TIMED_OUT = auto()
    CANCELLED = auto()

def run_as_admin_and_wait(
    exe_path: str,
    app_data_dir: str,
) -> tuple[UpdaterState, int | None]:

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
            return UpdaterState.CANCELLED, None
        raise (error) from error

    process = info["hProcess"]

    try:
        wait_result = win32event.WaitForSingleObject(
            process,90_000)
        
        if wait_result == win32event.WAIT_TIMEOUT:
            return UpdaterState.TIMED_OUT, None

        if wait_result != win32event.WAIT_OBJECT_0:
            raise RuntimeError(f"Unexpected wait result: {wait_result}")

        return (UpdaterState.COMPLETED,
                win32process.GetExitCodeProcess(process))
    finally:
        win32api.CloseHandle(process)