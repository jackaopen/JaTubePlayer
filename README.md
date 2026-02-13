
<img width="1143" height="313" alt="canvas" src="https://github.com/user-attachments/assets/e87d5ae2-35cf-4938-9d4d-caa90e2001f4" />

<div align="center">

### 🎬 A Feature-Rich Media Player for the Modern Era

**JaTubePlayer** seamlessly bridges online streaming and local playback with **Python**, **yt-dlp**, and **mpv**.  
Stream videos, access playlists, archive content —all through a stunning **Windows 11-inspired** interface featuring **glass/acrylic blur effects** and intuitive **customtkinter** design.

> 🔒 **Privacy-First Architecture** — Your Google credentials and API keys are encrypted locally using **Fernet + DPAPI**.

</div>

<img width="1318" height="710" alt="螢幕擷取畫面 2026-02-06 015335" src="https://github.com/user-attachments/assets/d6d55326-0634-42fb-b1a1-cdad71a3c147" />


## Features


<div align="center">

## ✨ Features

</div>

### ✅ Core Features 

**Media Playback**
- **Play local files and folders** — Enjoy your media directly from disk with support for multiple formats
- **Search and play online videos** — Find and play content without leaving the app
- **Live streams** — Able to play live streams
- **Supports more formats than WMP** — Play rare and uncommon file formats that Windows Media Player can't handle

**User Interface & Experience**
- **Modern glass/acrylic blur UI** — Embraces Windows 11's design language with translucent panels and blur effects
- **Hot key shortcuts** — Full keyboard support for play/pause, navigation, volume control, and more
- **Drag and drop support** — Simply drag files or folders into the app for instant playback

**Integration & Enhancement**
- **Video recommendations** — Discover new content based on your viewing history
- **Chrome extension integration** — Receive video links directly from a companion Chrome extension
- **Discord Rich Presence** — Show your current playback status in Discord with customizable options
- **Quick startup initialization** — Automatically load your preferred content when the app starts
- **Hot-update yt_dlp** — Easily update yt_dlp by replacing files in the `_internal/` folder

<br>

<div align="center">

### 🔐 Advanced Features 
*(Requires Google API + Client Secrets)*

</div>

-  **Access your personal YouTube playlists**
-  **Browse your liked videos and subscribed channel list**
-  **Bypass antibot verification and access member-only content** (via cookies)

<br>

<div align="center">

> ⚠️ *Client secrets, API keys, and cookies are only required for these advanced features.*  
> 🔓 **Basic functionality** — local playback, video search, downloads — works fully **without login**.  
> You can enter your API key and load cookies anytime in `Settings`.

</div>

<br>

<div align="center">
  
## 🛠️ Additional Functionalities

</div>

**Playback & Control**
- Double click the listbox item to play video
- Space bar or click the video screen to pause/play
- Mouse wheel to adjust volume
- Adjustable playback speed
- Selectable resolution for online videos


**System Integration & Convenience**
- Player buffer/cache information display
- "Open With" integration — launch videos directly from File Explorer
- System Media Transport Controls (SMTC) — Windows media controls in taskbar and action center
- Windows system tray icon
- Automatic version check
- Able to display subtitles from online videos

<br>

<div align="center">

---

## 📖 Documentation

**[📚 Complete GUI Guide](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/HJrhllGw-l)** &nbsp;|&nbsp; **[🔑 API Setup Guide](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/BybMxxzPZe)** &nbsp;|&nbsp; **[🧩 Extension Setup](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/By1q6Nzwbg)**

---

## 🖥️ System Recommendations

| Component | Minimum Specs |
| :--- | :--- |
| **Processor** | AMD Ryzen 3 1200 / Intel Core i3-6100 |
| **Memory** | 8 GB RAM |
| **Graphics** | NVIDIA GTX 750 or GT1030 / AMD Radeon RX 460 / Intel UHD 610 or Vega 8 |
| **Storage** | 2 GB available |
| **OS** | Windows 10 / 11 (64-bit) |

<br>

## 📦 Major Dependencies

| Category | Libraries / Components |
| :--- | :--- |
| **Runtime** | Python 3.11+ |
| **GUI** | `customtkinter`, `tkinter` |
| **Media** | `Pillow`, `ffmpeg-python`, `mpv`, `yt_dlp` |
| **Network** | `requests`, `aiohttp`, `flask`, `flask-cors` |
| **Integration** | `google-auth`, `google-api-python-client`, `winotify`, `pywin32`, `pypresence` |
| **Security** | `cryptography` |
| **Bundled** | `ffmpeg.exe`, `ffprobe.exe`, `libmpv-2.dll` |

> *Not all dependencies are listed.*

</div>

<br>


##  Author's Note

> *Since this project is maintained solely by me, some parts of the codebase include messy legacy logic from earlier stages of development.
A full refactor is not currently planned, as it would be a large task; however, some targeted refactors and logic refinements have already been made, with additional improvements planned over time.
Due to other ongoing work and commitments, pull requests will not be reviewed or merged, but issues and feedback are always welcome!*

### Contribution Guidelines

if you have ideas, suggestions, or improvements, feel free to **Open an issue** first to discuss proposed changes. I appreciate all feedback and suggestions! 🚀
>you can check out some code explantion in `docs`folder



---
>This project is provided for educational and research purposes. Users are responsible for complying with applicable laws and the terms of service of any platforms they interact with.







