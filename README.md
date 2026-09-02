
<img width="1143" height="313" alt="canvas" src="https://github.com/user-attachments/assets/e87d5ae2-35cf-4938-9d4d-caa90e2001f4" />

<div align="center">

##  A Feature-Rich Media Player for the Modern Era

**JaTubePlayer** seamlessly bridges online streaming and local playback with **Python**, **yt-dlp**, and **mpv**.  
Stream videos, access playlists, archive content —all through a stunning **Windows 11-inspired** interface featuring **glass/acrylic blur effects** and intuitive **customtkinter** design.


> [!Important] 🔒 **Privacy-First Architecture**
> Your login session cookies are encrypted locally with **AES-256-GCM**, and the encryption key is protected for the current Windows user with **DPAPI**.

</div>
<img width="1448" height="772" alt="螢幕擷取畫面 2026-08-16 220359" src="https://github.com/user-attachments/assets/ab78c615-effd-4d68-b86b-3d7acab7dbd3" />


---

<div align="center">
<h2> Features </h2>

<p>
  <img alt="Local and online playback" src="https://img.shields.io/badge/Playback-Local%20%26%20Online-E63946?style=for-the-badge&amp;" />
  <img alt="YouTube and Twitch streaming" src="https://img.shields.io/badge/Streaming-YouTube%20%26%20Twitch-9B5DE5?style=for-the-badge&amp;" />
  <img alt="Starred media and playback history" src="https://img.shields.io/badge/Library-Stars%20%26%20History-4776E6?style=for-the-badge&amp;" />
  <br>
  <img alt="Quick Init startup modes" src="https://img.shields.io/badge/Startup-Quick%20Init-FF9F1C?style=for-the-badge&amp;" />
  <img alt="AES and DPAPI protected account data" src="https://img.shields.io/badge/Privacy-AES%20%26%20DPAPI-54ad2d?style=for-the-badge&amp;" />
</p>

#### ***Uninterrupted, just how you like it***
<br>
</div>
<h3>&nbsp;🔹Playback &amp; Media Lists</h3>


- **Play local media** — Open a single file, multiple files, or an entire folder, with support for formats beyond Windows Media Player
- **Search and play online media** — Search or open supported video and playlist URLs directly
- **Live streams** — Play live streams and Twitch channels through the integrated media pipeline
- **Media List Page Control (MLPC)** — Browse large media lists in 50-item pages, keep selected and playing items distinct, and navigate previous, next, or random items across the full list
- **Playback history and starred media** — Revisit previously played items and maintain a persistent starred list
- **Playback options** — Select online resolution, use audio-only mode, adjust playback speed, and display available subtitles

<br>

<h3>&nbsp;🔹Interface &amp; Windows Integration</h3>


- **Windows 11-style glass UI** — Acrylic/glass effects, DPI-aware scaling, theme controls, and a card-based Settings window
- **Flexible viewing modes** — Normal window, fullscreen with controls, fullscreen-to-window, and configurable hover controls
- **Keyboard, mouse, and drag-and-drop controls** — Hotkeys, click-to-pause, mouse-wheel volume, and file, folder, multi-file, or URL drops
- **Windows integration** — System Media Transport Controls, taskbar/action-center controls, system tray support, toast notifications, and File Explorer “Open With”
- **Player information** — View playback, buffering, cache, and structured diagnostic information from the interface

<br>

<h3>&nbsp;🔹Integration, Startup &amp; Saving</h3>


- **Chrome extension integration** — Send, star, or add YouTube and Twitch pages to JaTubePlayer through a configurable local port
- **Discord Rich Presence** — Display current playback status with configurable privacy options
- **Quick Init** — Start with a search, online source or playlist, starred media, or a local folder
- **Media saving** — Save audio or video, choose a saving path, open the destination folder, cancel active work, and clean up partial output
- **yt-dlp hot update** — Select stable or nightly builds, verify update metadata and files, install with Windows elevation when needed, and restore the previous copy on failure
- **Persistent application data** — Store settings, stars, history, saved-media records, encrypted account state, and logs under the user application-data directory

<br>

<h3>&nbsp;🔹Account &amp; Privacy</h3>


- **Sign in through the built-in WebView2 account window** — Complete the sign-in flow without copying browser cookies
- **Personal sources** — Load account playlists, subscriptions, and liked videos through the internal retriever and parser
- **Large-list continuation support** — Retrieve additional playlist, subscription, and liked-video pages up to the configured result limit
- **Encrypted account sessions** — Protect captured cookies with AES-256-GCM and protect the AES key with current-user Windows DPAPI
- **Account lifecycle controls** — Login, refresh, logout, delete the protected system key, and retry once after a recognized authentication failure
- **Optional signed-in media requests** — Allow yt-dlp to use the encrypted account session for media available to the signed-in account

<br>

> [!NOTE]
> **The essentials work without signing in.** Local playback, online search, playback lists, starred media, and media saving are immediately available.
>
> Personal playlists, subscriptions, liked videos, and optional signed-in requests are enabled from **Settings → Account & Playlist → Login Google**. No manually entered API key, client-secret file, or raw cookie file is required.

<br>
<div align="center">

## 🛠️ Additional Functionalities

</div>

**Playback & Control**
- Double-click a media-list item to play it
- Press Space or click the video area to pause or resume
- Use the mouse wheel to adjust volume
- Navigate across the full active list with previous, next, and random controls
- Keep the highlighted selection separate from the currently playing item
- Use the star button to bookmark the current item
- Choose among three configurable fullscreen modes

**Media-List Management**
- Add, remove, reorder, and clear items while preserving the original source
- Browse long lists with 50-item pages and page controls
- Load local files, folders, search results, recommendations, account sources, and remote playlists into the shared media-list flow

- Queue media from the Chrome extension without replacing the active item

**System Integration & Diagnostics**
- Display available online subtitles and playback/cache details
- Use SMTC, the system tray, Windows notifications, and File Explorer integration
- Check application versions and manage verified yt-dlp updates from Settings

**Logging System**
- Record structured entries as `time | severity | component | message`, and mirror them to the live GUI viewer
- Combine application events with normalized mpv and yt-dlp messages, so playback, extraction, downloads, account activity, history, extension requests, and other components share one log flow
- Keep the latest 5,000 entries in memory; open or refresh them from **Settings → Advanced → Show MPV Log**
- Write the current session to `%APPDATA%\JaTubePlayer\JaTubePlayer_log.txt`, flushing queued entries every second, immediately for warnings and errors, and once more during shutdown
- Translate recognized yt-dlp failures into clearer user-facing messages and stop the active loading operation when appropriate

<br>

### 🔹Keeping yt-dlp Current

- Update **yt-dlp** before reporting online playback, extraction, playlist, or download failures because supported sites change frequently.
- The built-in updater supports both **Stable** and **Nightly** channels. If the latest stable build still fails, install the latest nightly build and try the same operation again.
- Reproduce the issue after updating and attach the new session log when reporting it.



<br>

<div align="center">

---

## 📖 Documentation

**[📚 Complete GUI Guide](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/HkiZya7YZl)** &nbsp;|&nbsp; **[🆕 Version 3 Update Details](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/BybMxxzPZe)** &nbsp;|&nbsp; **[🧩 Extension Setup](https://hackmd.io/@XtGB9ScDSjK6uua6PYhF2A/By1q6Nzwbg)**

---

## 🖥️ System Recommendations

| Component | Minimum Specs |
| :--- | :--- |
| **Processor** | AMD Ryzen 3 1200 / Intel Core i3-6100 |
| **Memory** | 8 GB RAM |
| **Graphics** | NVIDIA GTX 750 or GT1030 / AMD Radeon RX 460 / Intel UHD 610 or Vega 8 |
| **Storage** | At least 4 GB available |
| **OS** | Windows 10 / 11 (64-bit) |

<br>

## 📦 Major Dependencies

| Category | Libraries / Components |
| :--- | :--- |
| **Runtime** | Python 3.13+ |
| **GUI** | `customtkinter`, `tkinter`, `CTkMessagebox`, `sv_ttk` , `CTkColorPicker`|
| **Media** | `Pillow`, `ffmpeg-python`, `python-mpv`, `yt-dlp`, Deno, Streamlink |
| **Network & services** | `requests`, `aiohttp`, `Flask`, `flask-cors`, `google-api-python-client` |
| **Windows integration** | `pywin32`, `win11toast`, `winsdk`, `pystray`, `pynput`, `pypresence` |
| **Security & updates** | `pycryptodome`, Windows DPAPI, WebView2, `rpgp-py` |
| **Bundled** | `ffmpeg.exe`, `ffprobe.exe`, `libmpv-2.dll`, Deno, yt-dlp, Streamlink, WebView2Host |

> *Not all dependencies are listed.*

</div>



##  Security & User Precautions

JaTubePlayer 3.0 includes general safeguards against common risks. They support safer operation but still users are required to have basic security awareness.

#### What we implemented

- **Account and WebView2 checks** — Account data uses AES-256-GCM and DPAPI. The app and WebView2 host perform two-sided checks covering the helper hash, launch location, local pages, and per-run token.
- **Update checks** — The updater verifies the OpenPGP `.sig` and SHA-256 hashes, validates its registered installation location, limits elevated replacement paths, and supports backup and rollback.
- **General operation guards** — Network retrieval stays outside the elevated updater, while local-interface restrictions, input checks, busy guards, cancellation, and cleanup reduce common misuse and inconsistent operations.

#### Recommended precautions

- Use the default installation folder under **`Program Files`**, where standard Windows permissions better protect application files.
- Obtain JaTubePlayer and its extension from official sources, and approve UAC only after starting an update from the app.
- Keep Windows and application components current, and protect account files and logs from unauthorized access or sharing.

#### Windows SmartScreen

A newly downloaded JaTubePlayer build may show **“Windows protected your PC”** when Microsoft SmartScreen has not established enough reputation for that file. This warning alone does not identify the file as malware.

- Download JaTubePlayer only from the official project release.
- Confirm the expected filename, source, signature, or published hash before continuing.
- If the file is the expected official build, select **More info → Run anyway**.
- Stop if the source, filename, signature, or hash is unexpected, and report it instead of launching the file.



---

### Contribution Guidelines

If you have problems, ideas, suggestions, or improvements, feel free to **Open an issue** first to discuss proposed changes. I appreciate all feedback and suggestions! 🚀
> [!Note]
>  Before opening an issue, update yt-dlp (try the latest **Nightly** build when the stable build still fails), reproduce the problem, and collect the log from the same session.
> 
>  you can check out part of codebase explantion in `docs_3.0`folder

Every bug report must include:

1. **Description** — What happened, what you expected, and whether the problem is reproducible.
2. **Log** — Attach `%APPDATA%\JaTubePlayer\JaTubePlayer_log.txt` from the affected session


Remove account identifiers, cookies, tokens, local usernames, and other private data before attaching a log.


Issues missing both a useful description and the relevant log may be closed until the required information is provided.



---
> [!Note] Author's Note
> *Since this project is maintained solely by me, some parts of the codebase include messy legacy logic from earlier stages of development.
A full refactor is not currently planned, as it would be a large task; however, some targeted refactors and logic refinements have already been made, with additional improvements planned over time.
Due to other ongoing work and commitments, pull requests will not be reviewed or merged, but issues and feedback are always welcome!*

---

>This project is provided for educational and research purposes. Users are responsible for complying with applicable laws and the terms of service of any platforms they interact with.











