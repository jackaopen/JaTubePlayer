
<div align="center">

<img width="1143" height="313" alt="canvas" src="https://github.com/user-attachments/assets/e87d5ae2-35cf-4938-9d4d-caa90e2001f4" />

### 🎬 A Feature-Rich Media Player for the Modern Era

<p>
<strong>JaTubePlayer</strong> seamlessly bridges online streaming and local playback with <strong>Python</strong>, <strong>yt-dlp</strong>, and <strong>mpv</strong>.<br>
Stream videos, access playlists, archive content—all through a stunning <strong>Windows 11-inspired</strong> interface<br>
featuring <strong>glass/acrylic blur effects</strong> and intuitive <strong>customtkinter</strong> design.
</p>

<table>
<tr>
<td align="center">
🔒 <strong>Privacy-First Architecture</strong><br>
<sub>Google credentials & API keys encrypted locally using <strong>Fernet + DPAPI</strong></sub>
</td>
</tr>
</table>

</div>

<br>

<img width="1316" height="709" alt="螢幕擷取畫面 2026-02-05 171250" src="https://github.com/user-attachments/assets/2c213941-edab-427d-8853-06d1386975d9" />

<br>


<h2 align="center">✨ Features</h2>

<table>
<tr><td>

### 🎯 Core Features 

<table>
<tr>
<td width="50%">

**🎵 Media Playback**
- Play local files and folders
- Search and play online videos
- Live stream support
- Video recommendations

</td>
<td width="50%">

<table>
<tr><td>

### 🔐 Advanced Features
<sub>Requires Google API + Client Secrets</sub>

- Access your personal YouTube playlists
- Browse your liked videos and subscribed channel list
- Bypass antibot verification and access member-only content (via cookies)

<table>
<tr>
<td>
⚠️ <em>Client secrets, API keys, and cookies are only required for these advanced features.</em><br>
🔓 <strong>Basic functionality</strong> — local playback, video search, downloads — works fully <strong>without login</strong>.<br>
<sub>You can enter your API key and load cookies anytime in <code>Settings</code>.</sub>
</td>
</tr>
</table>

</td></tr>
</table>

<details>
<summary><b>📋 Additional Features & Controls</b></summary>
<br>

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
- Hot-update yt_dlp — Easily update yt_dlp by replacing files in the `_internal/` folder

</details>
</tr>
</table>

</td></tr>
</table>



---

### 🔐 Advanced Features (Requires Google API + Client Secrets)

-  **Access your personal YouTube playlists**
-  **Browse your liked videos and subscribed channel list**
-  **Bypass antibot verification and access member-only content** (via cookies)

> ⚠️ *Client secrets, API keys, and cookies are only required for these advanced features.*  
> 🔓 **Basic functionality** — local playback, video search, downloads — works fully **without login**.  
> You can enter your API key and load cookies anytime in `Settings`.



---

<br>

<h2 align="center">📖 Documentation</h2>

<div align="center">

| 📚 Resource | 🔗 Link |
|-------------|---------|
| **Complete GUI Guide** | [Read the Manual](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/HJrhllGw-l) |
| **Get Google API Key & Client Secrets** | [Setup Guide](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/BybMxxzPZe) |
| **Chrome Extension Installation** | [Installation Guide](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/By1q6Nzwbg) |

</div>

<br>
## 📖 Documentation

### GUI Manual
- [Complete GUI Guide](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/HJrhllGw-l)
<h2 align="center">💻 System Requirements</h2>

<div align="center">
<sub>Minimum recommended specifications</sub>
</div>

<table>
<tr>
<td width="33%">

**Processor (CPU)**
- AMD Ryzen 3 1200
- Intel Core i3-6100

**Memory (RAM)**
- 8 GB

</td>
<td width="33%">

**Graphics**
- NVIDIA GTX 750 / GT1030
- AMD Radeon RX 460
- Intel UHD 610 / Vega 8

</td>
<td width="33%">
<details>
<summary><h2>🔧 Major Dependencies</h2></summary>

<table>
<tr>
<td width="50%">

**Python Environment**
- Python 3.11+

**Core GUI**
- `customtkinter`
- `tkinter`

**Media Processing**
- `Pillow`
- `ffmpeg-python`
- `mpv`

**Web/Networking**
- `requests`
- `aiohttp`

</td>
<td width="50%">

**Google Integration**
- `google-auth`
- `google-api-python-client`

**Security**
- `cryptography`
<br>

<h2 align="center">👨‍💻 Author's Note</h2>

<table>
<tr><td>

> *Since this project is maintained solely by me, some parts of the codebase include messy legacy logic from earlier stages of development.
A full refactor is not currently planned, as it would be a large task; however, some targeted refactors and logic refinements have already been made, with additional improvements planned over time.
Due to other ongoing work and commitments, pull requests will not be reviewed or merged, but issues and feedback are always welcome!*

</td></tr>
</table>

<div align="center">

### 🤝 Contribution Guidelines

**If you have ideas, suggestions, or improvements, feel free to:**

| Action | Description |
|--------|-------------|
| 💬 **Open an Issue** | Discuss proposed changes before implementation |
| 🍴 **Fork the Project** | Experiment locally with your own modifications |
| 🐛 **Report Bugs** | Help improve the project by reporting issues |

<sub>💡 Check out code explanations in the <code>docs/</code> folder</sub>

</div>

---

<div align="center">

**This software is for personal, research, and educational use.**

</div>

- **Operating System:**
  - Windows 10 / 11 (64-bit)






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
>you can check out some code explantion in `docs`folder



---
> ##### This software is for **personal, research, and educational use**.



