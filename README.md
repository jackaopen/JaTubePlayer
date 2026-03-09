
<img width="1143" height="313" alt="canvas" src="https://github.com/user-attachments/assets/e87d5ae2-35cf-4938-9d4d-caa90e2001f4" />

<div align="center">

# 🎬 A Feature-Rich Media Player for the Modern Era

### *Uninterrrupted, just how you like it*

**JaTubePlayer** seamlessly bridges online streaming and local playback with **Python**, **yt-dlp**, and **mpv**.  
Stream videos, access playlists, archive content —all through a stunning **Windows 11-inspired** interface  
featuring **glass/acrylic blur effects** and intuitive **customtkinter** design.

> 🔒 **Privacy-First Architecture** — Your Google credentials and API keys are encrypted locally using **Fernet + DPAPI**.

</div>
<img width="1645" height="884" alt="螢幕擷取畫面 2026-03-02 163837" src="https://github.com/user-attachments/assets/95ae727d-1a68-4211-a3a2-b5c79c2a32ea" />



## Features


<div align="center">

## ✨ Features

</div>

### ✅ Core Features 

**Media Playback**
- **Play local files and folders** — Enjoy your media directly from disk with support for multiple formats
- **Search and play online videos** — Find and play content without leaving the app
- **Live streams** — Able to play live streams (YouTube & Twitch)
- **Twitch support** — Stream Twitch live channels directly, including via the Chrome extension
- **Supports more formats than WMP** — Play rare and uncommon file formats that Windows Media Player can't handle

**User Interface & Experience**
- **Modern glass/acrylic blur UI** — Embraces Windows 11's design language with translucent panels and blur effects
- **Redesigned Settings panel** — Card-style layout with reorganized sections for API, playback, cache, downloads, hotkeys, and external services
- **Multiple fullscreen modes** — Choose between Normal, Fullscreen (all widgets), or Fullscreen-to-window; dedicated fullscreen button in playback controls
- **Hover fullscreen** — Optionally trigger control sectopn on mouse hover over the video area
- **Hot key shortcuts** — Full keyboard support for play/pause, navigation, volume control, and more
- **Drag and drop support** — Simply drag files or folders into the app for instant playback
- **Toast notifications** — Get notified when videos are added to the playlist
- **Adjustable background color** - Enjoy your custom player

**Integration & Enhancement**

-  **Star/bookmark videos** — Save any video to a persistent starred local list and replay instantly
- **Video recommendations** — Discover new content based on your viewing history

- **Chrome extension integration** — Companion Chrome extension with three context menu actions on YouTube & Twitch pages:
    - **Send to JTP** : play immediately
    - **Star on JTP** : add to starred video list
    - **Add to JTP playlist** : queue to end of currnet playlist
- **Discord Rich Presence** — Show your current playback status in Discord with customizable options
- **Quick startup initialization** — Automatically load your preferred content when the app starts
- **Hot-update yt_dlp** — Easily update yt_dlp by replacing files in the `_internal/` folder
- **Configurable download path** — Set and reset your download destination directly from Settings
- **Configurable cache/buffer controls** — Tune `cache_secs`, `demuxer_max_bytes`, `demuxer_max_back_bytes`, and `audio_wait_open` via sliders in Settings
- **Automatic credential refresh** — Google OAuth2 credentials refresh automatically without re-login

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
- Star button to bookmark the currently playing video
- Dedicated fullscreen button with three configurable fullscreen modes

**Playlist Management**
- Remove a selected item from the playlist via Settings — without affecting the original source
- Chrome extension **Add to JTP playlist** queues a video to the end of the current playlist without changing the active source


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

## ⚠️ MPV Build Note

> There are different MPV builds that look identical in metadata but behave differently at runtime.  
> **Only the MPV binary included in the distributed compressed archive (`.zip` / release package) has been tested and verified to work correctly.**  
> Do not substitute it with a separately downloaded MPV build, even if the version number matches for this may cause subtle playback issues.
> SHA256 of the `libmpv-2.dll`:9de0e4615a22d6eba29c6678a4cda3591cae746f54834b6bfe7cafae1b55887c
---

## 📖 Documentation

**[📚 Complete GUI Guide](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/HkiZya7YZl)** &nbsp;|&nbsp; **[🔑 API Setup Guide](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/BybMxxzPZe)** &nbsp;|&nbsp; **[🧩 Extension Setup](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/By1q6Nzwbg)**

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




##  Author's Note

> *Since this project is maintained solely by me, some parts of the codebase include messy legacy logic from earlier stages of development.
A full refactor is not currently planned, as it would be a large task; however, some targeted refactors and logic refinements have already been made, with additional improvements planned over time.
Due to other ongoing work and commitments, pull requests will not be reviewed or merged, but issues and feedback are always welcome!*

### Contribution Guidelines

if you have ideas, suggestions, or improvements, feel free to **Open an issue** first to discuss proposed changes. I appreciate all feedback and suggestions! 🚀
>you can check out some code explantion in `docs`folder



---
>This project is provided for educational and research purposes. Users are responsible for complying with applicable laws and the terms of service of any platforms they interact with.







