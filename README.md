## Overview

JaTubePlayer is a feature-rich online and local media player built with Python, yt-dlp, and mpv. Designed for both online and offline use, it supports video and live stream playback, playlist access, video archiving, and secure OAuth-based login for personal content integration. The application features a modern GUI built with customtkinter, embracing Windows 11’s glass/acrylic blur aesthetic with a clean, polished interface.

>This application respects your privacy and encrypts Google credentials and API securely  Fernet+DPAPI system *locally*. 




## Features


### ✅ Core Features 

-  **Play local files and folders** — Enjoy your media directly from disk with support for multiple formats
-  **Search and play online videos** — Find and play content without leaving the app
-  **live streams** — Able to play live streams
-  **Video recommendations** — Discover new content based on your viewing history
-  **Supports more formats than WMP** — Play rare and uncommon file formats that Windows Media Player can't handle
-  **Modern glass/acrylic blur UI** — Embraces Windows 11's design language with translucent panels and blur effects
-  **Hot key shortcuts** — Full keyboard support for play/pause, navigation, volume control, and more
-  **Drag and drop support** — Simply drag files or folders into the app for instant playback
-  **Chrome extension integration** — Receive video links directly from a companion Chrome extension
-  **Discord Rich Presence** — Show your current playback status in Discord with customizable options
-  **Quick startup initialization** — Automatically load your preferred content when the app starts
-  **Hot-update yt_dlp** — Easily update yt_dlp by replacing files in the `_internal/` folder



---

### 🔐 Advanced Features (Requires Google API + Client Secrets)

-  **Access your personal YouTube playlists**
-  **Browse your liked videos and subscribed channel list**
-  **Bypass antibot verification and access member-only content** (via cookies)

> ⚠️ *Client secrets, API keys, and cookies are only required for these advanced features.*  
> 🔓 **Basic functionality** — local playback, video search, downloads — works fully **without login**.  
> You can enter your API key and load cookies anytime in `Settings`.



---

## Other features
  - Double click the listbox item to play video
  - Space bar or click the video screen to pause/play
  - Mouse wheel to adjust volume
  - Adjustable playback speed
  - Selectable resolution for online videos
  - Player buffer/cache information display
  - "Open With" integration — launch videos directly from File Explorer
  - System Media Transport Controls (SMTC) — Windows media controls in taskbar and action center
  - Windows system tray icon
  - Automatic version check


---

## 📖 Documentation

### GUI Manual
- [Complete GUI Guide](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/HJrhllGw-l)

### Setup Guides
- [How to Get Google API Key and Client Secrets](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/BybMxxzPZe)

---

## 🖥️ Spec reference 

>These are the **minimum recommended** specs for reference.

- **Processor (CPU):**
  - AMD Ryzen 3 1200
  - Intel Core i3-6100

- **Memory (RAM):**
  - 8 GB

- **Graphics (GPU / iGPU):**
  - NVIDIA GeForce GTX 750, or GT1030
  - AMD Radeon RX 460  
  - Integrated GPU :  Intel UHD 610 , vega 8

- **Storage:**
  - At least 2 GB available.

- **Operating System:**
  - Windows 10 / 11 (64-bit)


---

## Major Dependencies
#### Python Libraries
- **Python Version**: 3.11+
- **Core GUI**: `customtkinter`, `tkinter`
- **Media Processing**: `Pillow`, `ffmpeg-python`, `mpv`
- **Web/Networking**: `requests`, `aiohttp`
- **Google Integration**: `google-auth`, `google-api-python-client`
- **Encryption**: `cryptography`
- **Discord Integration**: `pypresence`
- **Windows Integration**: `winotify`, `pywin32`, `pywintypes`
- **Web Server**: `flask`, `flask-cors`

#### Bundled Binaries
- `yt_dlp` (included in `_internal/` folder)
- `ffmpeg.exe`, `ffprobe.exe` (bundled in root directory)
- `libmpv-2.dll` (inside `_internal/`)
> Not all the dependencies are listed


##  Author's Note

> *Since this project is maintained solely by me, some parts of the codebase include messy legacy logic from earlier stages of development.
A full refactor is not currently planned, as it would be a large task; however, some targeted refactors and logic refinements have already been made, with additional improvements planned over time.
Due to other ongoing work and commitments, pull requests will not be reviewed or merged, but issues and feedback are always welcome!*

### Contribution Guidelines

if you have ideas, suggestions, or improvements, feel free to:

- **Open an issue** first to discuss proposed changes
- **Fork the project** and experiment **locally**
- **Report bugs** or request features through GitHub Issues

I appreciate all feedback and suggestions! 🚀




---
> ##### This software is for **personal, research, and educational use**.



