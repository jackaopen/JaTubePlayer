# JaTubePlayer - YouTube Playlist Music Player

## Overview

JaTubePlayer is a feature-rich YouTube and local-file media player built with Python and VLC. Designed for both online and offline playback, it also includes YouTube playlist management, encrypted Google OAuth token storage, and lightweight GUI controls built with `tkinter` and `sv_ttk`.

> Note: This application respects your privacy and encrypts Google credentials securely using a dual-key Fernet system. Our Fernet-based encryption module is already **obfuscated** for enhanced protection.


## Features

### ✅ Core Features (No Google API Required):

- Play **local files or folders**
- Search and **play YouTube videos** directly
- **Download** YouTube videos selected inside the listbox
- **Fullscreen mode** support
- Use "Open With" context menu for direct playback from system explorer
- **Hot-update** support for `yt_dlp` — simply replace its folder in `_internal/` to stay up-to-date (download new zip, unzip, replace)
### 🔐 Advanced Features (Requires Google API + Client Secrets):

- Retrieve your **personal YouTube playlists**
- Access your **Liked videos** and **Subscribed channel list**

> Place your `client_secrets.json` inside the `_internal/` folder. Please note that the name must be exactly `client_secrets.json` or the application will not recognize it. This step is **only necessary** if you intend to use advanced features (like playlists, likes, and subscriptions), and **not required** for basic local playback, video search, or downloads. Enter your API key via `Settings > Enter YouTube API`.

---

## Minor addition
  - Double click the listbox item to play video
  - space bar to pause/play
  - up/down key for volume adjustment
  - version check system for both Player and yt_dlp
    
---

## Token & Key Management (Security)

- OAuth tokens are encrypted using **Fernet** with:
  - A local machine-dependent key
  - A second embedded static key inside the executable
- You can clear your local key via `Settings > Delete System Key`. A new one is generated at next startup.
- The encryption module is **obfuscated** for extra protection against tampering.

---

## GUI Options Breakdown
### Fullscreen:
  - Click the ⛶ icon beside the video screen to enter fullscreen
  - Click the arrow icon at the bottom right to return to windowed mode
  - Now v1.6.6 can toggle fullscreen with esc key

### Playlist Management:

- **Enter Playlist**: Load your YouTube playlist (retrieved once per session after login).
- **Update YouTube Playlists**: Refresh the list from the server manually.

### Selected/Playing video info
 - **Retreive video info including upload channel, upload date, description, video url with yt_dlp**

### Like & Subscribe System:

- **Sub System**: Randomly selects channels from your saved list and retrieves their latest uploads. (Experimental, evolving)
- **Like System**: Displays your liked videos **based on timestamp order**. Navigate entries via `Like Prev` / `Like Next` buttons. Pagination is not used.

### Settings Panel:

- **Resolution**: Set playback stream resolution.
- **Priority Mode**:
  - Audio Priority: Sync video to audio for better sound.
  - Video Priority: Sync audio to video for visual fidelity.
- **Network Cache**: Adjusts streaming buffer (e.g., for slower connections).
- **YouTube API Key**:
  - Enter via `Enter YouTube API` button
  - Remove saved key via `Delete Stored API`
- **Download Selected Video**: Downloads to `download_output/` directory.

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


---

## Dependencies

- Python 3.11+
- `tkinter`, `sv_ttk`, `ffmpeg`, `vlc`, `cryptography`, `google-auth`, `google-api-python-client`, `Pillow`, `requests`
- `yt_dlp` (included in `_internal/` folder)
- `ffmpeg.exe` (bundled in root directory)
- `libvlc.dll`, `libvlccore.dll`, and `plugins/` (inside `_internal/`)

> All required binaries, modules, and dependencies must be placed in the same directory or proper subfolder (`_internal/`, etc.) alongside the main executable.


---

## Contribution

Due to sensitive encryption and API mechanisms, pull requests (PRs) are not accepted directly.

If you have ideas, suggestions, or improvements, feel free to open an issue first to discuss proposed changes.

Forking the project and experimenting locally is always welcome.
---

## Acknowledgements

- YouTube Data API (v3)
- VLC Python Bindings
- `yt_dlp`
- Google OAuth Libraries

---

## Author Notes

Built to be robust and secure without sacrificing flexibility. More updates on Sub system, playlist integration, and UI improvements are in progress.

---

## NOTE

- Please dont span the command like 




---

## Screenshots


![螢幕擷取畫面 2025-04-05 222344](https://github.com/user-attachments/assets/469e5f8d-572c-4331-b3aa-742aecf0537d)


---

> For bugs or feature requests, open an issue in this repo.

