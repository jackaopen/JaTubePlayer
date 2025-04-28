# JaTubePlayer - YouTube Playlist Music Player

## Overview

JaTubePlayer is a feature-rich **YouTube** and **local-file** media player built with Python yt_dlp and mpv. Designed for both online and offline playback, it also includes YouTube playlist management, youtube video download function, and encrypted Google OAuth token storage, and lightweight GUI controls built with `tkinter` and `sv_ttk`.

> Note: This application respects your privacy and encrypts Google credentials securely using a dual-key Fernet system. Our Fernet-based encryption module is already **obfuscated** for enhanced protection.

![螢幕擷取畫面 2025-04-09 163853](https://github.com/user-attachments/assets/bcc42066-73d6-4adb-9709-9b11c1c22858)

## Features


### ✅ Core Features (No Google API Required):

- Play **local files or folders**
- Play **Youtube Videos and live streams**
- Search and **play YouTube videos** directly
- **Download** YouTube videos selected inside the listbox
- **Fullscreen mode** support
- Use "Open With" context menu for direct playback from system explorer
- **Hot-update** support for `yt_dlp` — simply replace its folder in `_internal/` and the `yt_dlp.exe` to stay up-to-date.
- **Version check sysyem** to check if the `yt_dlp` or the player needs any update
### 🔐 Advanced Features (Requires Google API + Client Secrets):

- Retrieve your **personal YouTube playlists**
- Access your **Liked videos** and **Subscribed channel list**

> Client secrets and API keys are **only necessary** if you intend to use advanced features (playlists, likes, and subscriptions), and **not required** for basic local playback, video search, or downloads. Enter your API key via `Settings `.

---

## Minor addition
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

### Playlist Management:

- **Enter Playlist**: Load your YouTube playlist (retrieved once per session after login).
  -After selected a playlist, **press the button again** to get into the playlist!!

### Selected/Playing video info
 - **Retreive video info including upload channel, upload date, description, video url with yt_dlp**

### Like & Subscribe System:

- **Sub System**: Randomly selects channels from your saved list and retrieves their latest uploads. (Experimental, evolving)
- **Like System**: Displays your liked videos **based on timestamp order**. Navigate entries via `Like Prev` / `Like Next` buttons. Pagination is not used.

## Settings Panel:
![螢幕擷取畫面 2025-04-28 155235](https://github.com/user-attachments/assets/7c8f12fe-823f-437b-aabd-afdb16cbe0cf)

### New version (>= v1.6.8)
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

- **YouTube API Key**  
  - `Enter YouTube API`: Insert the API key
  - `Delete Stored API`: Remove the saved API key

- **Cookie Management**  
  - `Select Cookie`: Load a YouTube cookie into the player  
  - `Remove Stored Cookie`: Delete the loaded cookie from the player
  - > Cookies are **optional**. Only needed to bypass YouTube's "Sign in to confirm you are not a robot" restriction.  
  - > Cookies are used solely for authentication bypass — **no personal data is accessed or stored**.

- **Client Secret Management**  
  - `Select Client Secret`: Load your OAuth client_secret.json  
  - `Remove Stored Client Secret`: Delete the loaded secret

- **Advanced Player Setting**  
  - `Max resolution`: Set maximum playback resolution (to save PC resources)  
  - `Auto retry`: Enable automatic retry if MPV fails to load  
  - `Fullscreen with console`: Toggle between full-frame maximize vs real fullscreen behavior
  - `Show MPV log`: Observe error logs from MPV for troubleshooting

- **Version & Info Panel**  
  - Display current and latest versions of yt-dlp and JaTubePlayer  
  - Option to toggle "check for updates at startup"
  - Direct links to yt-dlp and JaTubePlayer websites


### Old version (<= v1.6.7)
- **YouTube API Key**:
  - Enter via `Enter YouTube API` button
  - Remove saved key via `Delete Stored API`
- **Download Selected Video**: Downloads to `download_output/` directory.
- **Delete System Key**:clear your local key. A new one is generated at next startup.
- **Login/sys logout Gooele**:login/logout your google account.
  - Login:Create and store your token inside the player with our encryption logic.
  - Logout:Delete the stored token, liked video, subscription data.
- **update liked video/subsciption channel list**:update the stored data.   
- **Update YouTube Playlists**: Refresh the playlist inside the dropdown from the server manually.
- **Insert/delete cookie**: 
  - load the chosen cookie into player/ delete cookie from player, and your `cookie.txt` if you want
  - Not required if you dont encounter the yt_dlp problem!
  - > We only use your cookie to bypass the YouTube 'Sign in to confirm you are not a robot' restriction in yt-dlp. The cookie is not used to access or store any other personal data.
- **show mpv log** :To better observe the error code from mpv if necessary
---

## Yt_dlp Hot update
- Go https://github.com/yt-dlp/yt-dlp/releases and download both `yt-dlp.exe` and `yt-dlp.tar.gz`
  - Replace the `yt-dlp.exe` in the `_internal` folder
  - Unzip the `yt-dlp.tar.gz`, and find the `yt_dlp` folder in `yt-dlp.tar.gz/yt-dlp`
  - Replace the `yt_dlp` folder in `_internal`. 
---
## Author Notes

- Built to be robust and secure without sacrificing flexibility. More updates on Sub system, playlist integration, and UI improvements are in progress.
- Please read the readme and release notes for better experience
- If player suddenly pauses, please try to click the pause button to try to replay it
  - If still not playing, try to reload the video

- Although rare, if the yt_dlp asks you to authenticate, please try to simply reload the video
  - If the problem continues, please go to `setting>select cookie` and select your cookie file, this should solve the problem
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

## Acknowledgements

- YouTube Data API (v3)
- python mpv
- `yt_dlp`
- Google OAuth Libraries


---

> For bugs or feature requests, open an issue in this repo.

