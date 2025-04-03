# JaTubePlayer - YouTube Playlist Music Player

## Overview

JaTubePlayer is a feature-rich YouTube playlist and local media player built with Python and VLC. Designed for both online and offline media playback, it also includes YouTube playlist management, encrypted Google OAuth token storage, and lightweight GUI controls built with `tkinter` and `sv_ttk`.

> Note: This application respects your privacy and encrypts Google credentials securely using a dual-key Fernet system.

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

> Place your `client_secrets.json` inside the _internal/ folder, please note that the name has to be exactly 'client_secrets.json' or the execution may not read it correctly, and enter your API key via `Settings >  YouTube API`

---

## Token & Key Management (Security)

- OAuth tokens are encrypted using **Fernet** with:
  - A local machine-dependent key
  - A second embedded static key inside the executable
- You can clear your local key via `Settings > Delete System Key`. A new one is generated at next startup.

---

## GUI Options Breakdown

### Playlist Management:

- **Enter Playlist**: Load your YouTube playlist (retrieved once per session after login).
- **Update YouTube Playlists**: Refresh the list from the server manually.

### Like & Subscribe System:

- **Sub System**: Randomly selects channels from your saved list and retrieves their latest uploads. (Experimental, evolving)
- **Like System**: Displays your liked videos **based on timestamp order** — navigate through entries via `Like Prev` / `Like Next` buttons.

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
4. Go to **OAuth consent screen**, set it up (choose "External" and fill in app info)
5. Navigate to **Credentials**:
   - Click **Create Credentials > OAuth Client ID**
   - Application type: Desktop App
   - Download the generated `client_secret.json`
6. Place `client_secret.json` inside the `_internal/` folder
7. Get your **API key** from the same Credentials tab and paste it into the app via `Settings > Enter YouTube API`

---

## Dependencies

- Python 3.11+
- `tkinter`, `sv_ttk`, `ffmpeg`, `vlc`, `cryptography`, `google-auth`, `google-api-python-client`, `Pillow`, `requests`
- `yt_dlp` (included in `_internal/` folder)
- `ffmpeg.exe` (bundled in root directory)
- `libvlc.dll`, `libvlccore.dll`, and `plugins/` (inside `_internal/`)

> All required binaries, modules, and dependencies must be placed in the same directory or proper subfolder (`_internal/`, etc.) alongside the main executable.

---

## License

This project includes third-party components under various licenses.
Please refer to each module's license if you're redistributing or modifying.

The core application logic and UI are provided for educational and personal use.
Commercial use is not permitted without the author’s explicit permission.

---

## Contribution

Due to sensitive content encryption and API usage, PRs are currently not accepted.
Feel free to fork and experiment locally.

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

(Coming Soon)

---

> For bugs or feature requests, open an issue in this repo.

