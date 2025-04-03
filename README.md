# JaTubePlayer - YouTube Playlist Music Player

## Overview

JaTubePlayer is a feature-rich YouTube playlist and local media player built with Python and VLC. Designed for both online and offline media playback, it also includes YouTube playlist management, encrypted Google OAuth token storage, and lightweight GUI controls built with `tkinter` and `sv_ttk`.

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

## Token & Key Management (Security)

- OAuth tokens are encrypted using **Fernet** with:
  - A local machine-dependent key
  - A second embedded static key inside the executable
- You can clear your local key via `Settings > Delete System Key`. A new one is generated at next startup.
- The encryption module is **obfuscated** for extra protection against tampering.

---

## GUI Options Breakdown

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

To access playlist, liked videos, and subscription features, you'll need to:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable **YouTube Data API v3** for that project
4. Go to OAuth consent screen:
   - Choose External
   - Fill in application name, company, and description — these fields do not impact functionality for personal use
   - Add your Google account email as a test user (important for free-tier access)
6. Navigate to **Credentials**:
   - Click **Create Credentials > OAuth Client ID**
   - Application type: Desktop App
   - Download the generated `client_secrets.json`
7. Place `client_secrets.json` inside the `_internal/` folder (filename must be exact)
8. Get your **API key** from the same Credentials tab and paste it into the app via `Settings > Enter YouTube API`


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

## Screenshots

![player](https://github.com/user-attachments/assets/64340da3-5054-4fb9-a26d-cc205de037fc)


---

> For bugs or feature requests, open an issue in this repo.

