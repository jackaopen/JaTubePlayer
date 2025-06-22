
![螢幕擷取畫面 2025-05-05 134202](https://github.com/user-attachments/assets/20ed6f6b-3af3-424e-8925-bc29cdd7f8df)

## Overview

JaTubePlayer is a feature-rich online and local media player built with Python, yt_dlp, and mpv. Designed for both online and offline playback, it supports online videos & live streams playback,  playlist access, video archiving, secure OAuth login for personal content integration, and a lightweight GUI built with `tkinter` and `sv_ttk`.

> Note: This application respects your privacy and encrypts Google credentials securely using a dual-key Fernet system. Our Fernet-based encryption module is already **obfuscated** for enhanced protection.
> ### This software is for **personal, research, and educational use only**.



## Features
![螢幕擷取畫面 2025-05-12 140527](https://github.com/user-attachments/assets/7dc3686f-16b7-4b76-9869-3f349960b1a0)


### ✅ Core Features (No Google API Required)

-  **Play local files and folders** — enjoy your media directly from disk
-  **Stream online videos and live streams** — just search or paste a link
-  **Search and play YouTube videos** without leaving the app
-  **Supports more formats than WMP** — including rare, uncommon file formats WMP can’t play
-  **Archive selected online videos** from the listbox for offline viewing
-  **Get smart video recommendations** based on your recent watch history
-  **Fullscreen mode support** for an immersive playback experience
-  **“Open With” integration** — launch videos directly from File Explorer
-  **Hot-update yt_dlp** — simply replace the `yt_dlp.exe` and `yt_dlp `folder in `_internal/` to stay updated
-  **Automatic version check** — get notified if your `yt_dlp` or player is out of date

---

### 🔐 Advanced Features (Requires Google API + Client Secrets)

-  **Access your personal YouTube playlists**
-  **Browse your liked videos and subscribed channel list**

> ⚠️ *Client secrets and API keys are only required for these advanced features.*  
> 🔓 **Basic functionality** — local playback, video search, downloads — works fully **without login**.  
> You can enter your API key anytime in `Settings`.

---

## ✅ Best For
- Music & video lovers who want full control
- Tech-savvy users tired of browser ads
- Anyone who wants to watch or listen offline
## 🛠️ Use Cases
- Save lectures, music, or VODs for travel
- Use on low-resource systems (it's fast & lightweight)

---

## Other features
  - Double click the listbox item to play video
  - space bar or click the video screen to pause/play
  - version check system for both Player and yt_dlp
  - Mouse wheel to adjust volume
> Note:Please read the brief introduction of the relesase page to better understand more of the features and functions!

---

## Token & Key Management (Security)

- OAuth tokens are encrypted using **Fernet** with:
  - A local machine-dependent key
  - A second embedded static key inside the executable
- You can clear your local key via `Settings > Delete System Key`. A new one is generated at next startup.
- The encryption module is **obfuscated** for extra protection against tampering.

---

## GUI Breakdown
### Fullscreen:
  - Click the ⛶ icon beside the video screen to enter fullscreen
  - Click the arrow icon at the bottom right to return to windowed mode
  - Now v1.6.6 can toggle fullscreen with esc key

### Playlist:

- **Enter Playlist**: Load your YouTube  playlist (retrieved once per session after login).
  - After selected a playlist, **press the button again** to get into the playlist!!

### Selected/Playing video info
 - **Retreive video info including upload channel, upload date, description, video url with yt_dlp**

### Like & Subscription System:

- **Sub System**:
  - Stores your YouTube  subscribed channel list along with the timestamp of each channel’s latest video at the time of retrieval locally.
  - When accessing, the player uses the saved timestamps to check and display each channel’s newest content.


- **Like System**: Displays your YouTube liked videos **based on timestamp order**. Navigate entries via `Like Prev` / `Like Next` buttons. Pagination is not used.
  
---

## Settings Panel:

![Screenshot 2025-06-21 235916](https://github.com/user-attachments/assets/17b004e3-67e7-4b8c-ba36-7704b0578961)


### New version (v1.6.8 or up)
- **Update Lists**  
  - `update Subscribe channel list`, `update Liked video list`, `Update YouTube playlists`  
  - Fetch the latest data manually from YouTube server

- **Google Account & System Key**  
  - `Login Google`: Login and create a local encrypted token for YouTube data access  
  - `Logout Google`: Delete the stored token, clear liked videos and subscriptions  
  - `Delete system key`: Clear local encryption keys; new keys will be auto-generated at next startup

- **Download Video**  
  - Select a format (`mp3` or `mp4`)  
  - Choose an available resolution  
  - `Download Selected Video`: Downloads to `download_output/` directory
  > Note:Do not click on other video while downloading 

- **YouTube API Key**  
  - `Enter YouTube API`: Insert the API key
  - `Delete Stored API`: Remove the saved API key

- **Cookie Management**  
  - `Select Cookie`: Load a YouTube cookie into the player  
  - `Remove Stored Cookie`: Delete the loaded cookie from the player
  > Cookies are **optional**. Only needed to bypass the error's "Sign in to confirm you are not a robot" restriction.  
  > Cookies are used solely for authentication bypass — **no personal data is accessed or stored**.

- **Client Secret Management**  
  - `Select Client Secret`: Load your OAuth client_secret.json  
  - `Remove Stored Client Secret`: Delete the loaded secret

- **Advanced Player Setting**  
  - `Max resolution`: Set maximum playback resolution (to save PC resources)  
  - `Auto retry`: Enable automatic retry if MPV fails to load  
  - `Fullscreen with console`: Toggle between full-frame maximize vs real fullscreen behavior
  - `Show MPV log`: Observe error logs from MPV for troubleshooting
 
- **Recommendation & History** (version >= v1.6.9)
  - `Record History`: When enabled, stores tags and channel info of watched videos locally
  - `Reset History`: Clears all recorded data and restores default recommendation settings

- **Version & Info Panel**  
  - Display current and latest versions of yt-dlp and JaTubePlayer  
  - Option to toggle "check for updates at startup"
  - Direct links to yt-dlp and JaTubePlayer websites

- **Quick Startup Init (Ver 1.7.1 or up)**
  > *(Below the toggle)*: Shows which startup mode is currently active  
  - `toggle quick startup init`: Enable or disable the startup auto-load feature  
  - `init search`: Auto-start with a YouTube search (requires pressing `set init search`)  
  - `init playlist`: Load a selected YouTube playlist at launch (press `get` → select → `set`)  
  - `init local folder`: Auto-play from a local folder of media files  
  - `init Recommendation`: Load smart video suggestions  
    - Requires `Record History` to be ON  
  - `set init ...` buttons: Save your selected mode and parameters  

---

## Yt_dlp Hot update
- Go https://github.com/yt-dlp/yt-dlp/releases and download both `yt-dlp.exe` and `yt-dlp.tar.gz`
  - Replace the `yt-dlp.exe` in the `_internal` folder
  - Unzip the `yt-dlp.tar.gz`, and find the `yt_dlp` folder in `yt-dlp.tar.gz(or yt-dlp~)/yt-dlp`
  - Replace the `yt_dlp` folder in `_internal`. 
---
## 📝 Author Notes

- When the currently playing stream ends, please select another video or stream to continue playback.
- Before accessing the subscription list, it’s recommended to update it via `Settings > Update Subscribe Channel List`.
- We suggest not using the **Recommendation List** too frequently, as it may trigger the request limit of `yt_dlp`.
- If you open the application frequently, consider disabling **Quick startup init** in the `Settings` page to improve startup speed and avoid getting rate limited by `ytdlp`.
- For the best experience, please read this README and the release notes.
- While downloading, don't click on other video as it might cause unexpected error 


### 🔄 Playback Troubleshooting
- If the player suddenly pauses:
  - Try clicking the **pause/play button** again.
  - If it still doesn't resume, try reloading the video.

- If `yt_dlp` prompts for authentication:
  - First, try reloading the video.
  - If the issue persists, go to `Settings > Select Cookie` and load your cookie file. This usually resolves the problem.
---
## How to Get Google API Key and Client Secrets

Follow this step-by-step guide to use advanced features (like accessing your playlists or subscriptions):

1. Visit https://console.cloud.google.com/
2. In the top bar, click the **Project dropdown** → **New Project** → enter any project name → click **Create**
3. From the main dashboard, go to `API & Services > Library`
4. Search for **YouTube Data API v3**, click it, and click **Enable**

### Setup OAuth Consent:

5. Go to `OAuth Consent Screen` on the left
6. Choose **External** user type
7. Fill in **App name**, **User support email**, and add your email in **Developer Contact Info**
8. Click **Save and Continue** (Scopes can be left as default)
9. In the **Test Users** section, add your Google account email (required for free-tier testing)

### Setup Credentials:

10. Go to `API & Services > Credentials`
11. Click `+ Create Credentials > OAuth Client ID`
12. Choose **Desktop App**, name it anything
13. Click **Create** and download the `client_secrets.json`
14. Rename the file **exactly** to `client_secrets.json` and place it inside the `_internal/` folder

### Get API Key:

15. In the same `Credentials` page, click `+ Create Credentials > API Key`
16. Copy the API Key
17. Open JaTubePlayer and go to `Settings > Enter YouTube API`, paste your key
18. (Optional but recommended) In the same credentials list, click the 3-dot menu beside the key → `Edit API Key`
    - Set Application Restrictions: None
    - Set API Restrictions: Restrict to only `YouTube Data API v3`

---



## Dependencies

- Python 3.11+
- `tkinter`, `sv_ttk`, `ffmpeg`, `mpv`, `cryptography`, `google-auth`, `google-api-python-client`, `Pillow`, `requests`
- `yt_dlp` (included in `_internal/` folder)
- `ffmpeg.exe`, `ffprobe.exe` (bundled in root directory)
- `libmpv-2.dll` (inside `_internal/`)

> All required binaries, modules, and dependencies must be placed in the same directory or proper subfolder (`_internal/`, etc.) alongside the main executable.


---

## Contribution

Due to sensitive encryption and API mechanisms, pull requests (PRs) are not accepted directly.

If you have ideas, suggestions, or improvements, feel free to open an issue first to discuss proposed changes.

Forking the project and experimenting locally is always welcome.

---

## 🧩 Partial Open Source Disclosure
To help users better understand how JaTubePlayer works, we’ve decided to open-source selected modules of the application.
You can refer to the corresponding `_summary.md` files and the `.py` source code available in the main branch.

---
## Acknowledgements

- YouTube Data API (v3)
- python mpv
- `yt_dlp`
- Google OAuth Libraries


---

> For bugs or feature requests, open an issue in this repo.

