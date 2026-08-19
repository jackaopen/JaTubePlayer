# JaTubePlayer 3 — Update details
> this is general update details for reference, for exact implementation please refer to the commit history and merges


### Table of contents

[TOC]

---

## 1. Executive summary

The final branch adds five principal systems that final `main` does not contain:

1. **MLPC and shared media state:** centralized 50-item paging, selected/current-playing separation, cross-page previous/next/random, mutations, history integration, local media, URL drops, stars and extension actions.
2. **InnerTube retrieval stack:** page-derived configuration, authenticated browse/account requests, renderer parsing, continuations and result limits replace the old Data API playlist/subscription/like helpers.
3. **WebView2 account stack:** a dedicated browser profile captures YouTube cookies; cookies are AES-256-GCM encrypted and the AES key is protected with current-user DPAPI.
4. **Packaged Windows distribution:** code moves under `src/`, mutable state moves to AppData, and PyInstaller/Inno Setup definitions package the application, WebView helper, updater and extension.
5. **Separated yt-dlp updater:** the normal process downloads; a UAC-elevated component verifies and installs fixed payloads with backup/rollback handling.

The branch also adds MLPC history, OLE URL drops, configurable extension port/options, structured logging, stable/nightly yt-dlp selection, Streamlink-based Twitch live handling, explicit FFmpeg process cancellation, improved scaling/centering and targeted account/updater process verification.

### Baseline behavior deliberately excluded

The following exist in final `main` and are therefore **not counted as Test_update additions**:

- mpv EDL construction for separate video/audio streams;
- forwarding yt-dlp HTTP headers to mpv;
- subtitle selection and audio-only playback;
- mpv hardware decoding, cache/demuxer controls and their settings;
- the Chrome extension's direct-play, star and append context menus;
- Windows file/folder drag-and-drop itself;
- existing playback buttons, fullscreen, volume, hotkeys, Discord presence and the general settings window;
- the basic audio/video download capability and basic FFmpeg composition.

Where Test_update changes one of these existing flows, only the changed portion is recorded below.

## 2. Architecture and storage

Verified branch changes:

- `JaTubePlayer.py` and the accumulated branch modules are migrated under `src/` . The branch adds dedicated account, history, loader, UI, logging, updater and media-control modules.
- `media_data_list_template`, `MediaList_PageControl_`, `playlist_retriever_`, `innertube_handle` and `parser` divide media state, navigation, transport and response parsing.
- `account_handle`, `Account_token`, the C# WebView2 host, helper and verifier divide Python orchestration from the cookie-host process.
- `get_info_loader_` centralizes the runtime yt-dlp object, maximum resolution, Deno path, logger and decrypted cookie supplied to extraction calls.
- Mutable config, stars, logs, saved media, updater staging, WebView2 profile, encrypted key/cookie and one-run token are redirected to `%APPDATA%\JaTubePlayer` rather than the source/install tree.
- Frozen/development resource lookup is updated for the packaged `_internal` layout.
- PyInstaller and Inno Setup assets define a packaged application and a separately packaged updater.


## 3. Media List Page Control (MLPC)

### New shared model and modes

`media_data_list_template` adds aligned URL, title, channel and thumbnail arrays plus page and global playing-index state. `MediaType` distinguishes uninitialized, YouTube, likes, subscriptions, recommendations, folder/local, starred and direct-URL states.

### New controller behavior

- Central 50-item page calculation and visible-range loading.
- Previous/next page wrapping, with optional first/last selection.
- Separate selected item and currently playing item.
- Translation between visible tree indices and global media indices.
- Previous/next playback across page boundaries.
- Random selection across the complete model, followed by page reveal.
- Append/remove operations that update all aligned arrays, page count and playing index together.
- Playlist links excluded from directly playable media entries.
- `_busy`/loading guards around reload, search, drop, append and page-changing operations.
- Confirmation before replacing a list that is still loading.
- Correct restoration of the playing marker when its page becomes visible.

### Sources moved onto MLPC

The controller becomes the branch path for InnerTube home, subscriptions, likes, user playlists and playlist contents; search results; local files/folders; file/folder/URL drops; starred entries; Chrome direct/star/append actions; and history restoration.

### Star integration changes

The existing star feature is changed rather than introduced: persistence moves to AppData, metadata lookup uses the shared extraction loader, fetched thumbnails change from the first candidate to the last candidate, and `list_all()` now returns a `media_data_list_template` instead of mutating four caller lists and the tree queue. MLPC deep-copies the activated starred model, and follow-up fixes keep visible-list removal, stored stars and active tree/page state synchronized.



## 4. Account and YouTube-data redesign

### Removed main implementation

The branch removes the installed-app Google OAuth/client-secret flow, encrypted Google `Credentials` objects, Fernet key/blob handling, browser OAuth callback and the old Data API list helpers. `account/fernet_pubnew_class.py`, `account/google_login.py`, `utils/get_related_video.py` and `utils/sub_and_like_public.py` disappear; `client_secret_path` and `cookie_path` are removed from the template.

### Added WebView2 account flow

- Dedicated WebView2 profile rather than a normal browser profile.
- Interactive login, silent cookie refresh and full profile-clear modes.
- Cookie detection using `LOGIN_INFO` or `SID` plus `APISID`.
- Cookie capture via `CoreWebView2.CookieManager`.
- Packaged waiting/success/error pages.
- Python hidden-process launch, stdin token delivery, concurrent stdout/stderr draining, exit-code handling and avatar/account refresh.
- Logout clears the encrypted cookie and retained InnerTube state; full reset also removes the AES key and clears WebView profile data.

### Added encrypted cookie storage

1. Python generates a random 32-byte AES key.
2. Current-user DPAPI protects it in `AES_key.enc`.
3. WebView2 serializes the YouTube cookies as a Cookie header.
4. AES-GCM encrypts the header with a random 12-byte nonce and a 16-byte authentication tag.
5. `cookie_key.enc` stores `nonce || tag || ciphertext`.
6. Python reads it with authenticated `decrypt_and_verify`.

The final flow stores no raw cookie text file. Invalid/missing key material clears incompatible login state, sensitive helper buffers are zeroed, and a non-blocking operation lock serializes login, refresh, decrypt and clear work.

### Added InnerTube transport, parser and retriever

The new stack:

- reads `ytcfg`, API key, visitor data and client version from YouTube pages;
- derives SAPISID authorization values from the decrypted cookie;
- maps page types to browse IDs and referers;
- sends browse and account-menu requests;
- parses old and new video/playlist renderer layouts;
- parses continuation tokens and follows continuation pages;
- filters Watch Later/Liked pseudo-playlists and playlist cards where appropriate;
- retries once through WebView2 refresh when authenticated state is not recognized;
- uses a separate handler instance for account/avatar traffic;
- applies per-category result limits.



## 5. Playback and extraction changes

Only final differences from main are listed:


- The YouTube format expression is changed to prefer bounded-height HTTPS video/audio and then non-native-HLS fallbacks.
- The final YouTube client list changes from main's `default, web_embedded, tv` selection to `default, -android_vr, web_embedded`.
- Existing Deno/EJS support is retained but its option construction/path handling is revised.
- The decrypted account cookie can be scoped to `.youtube.com` and loaded directly into yt-dlp instead of using the old configured cookie-file path.
- Requested-format `available_at` values can defer playback until the stream is available.
- Twitch non-VOD playback can launch bundled `_internal/streamlink/bin/streamlink.exe` with hidden process/output handling; Twitch VOD handling is kept separate.
- mpv's curl backend receives a 1 MiB maximum request size and 4 MiB buffer. The older mpv hardware/cache options and HTTP-header forwarding remain baseline behavior.
- Seek operations change to `absolute+exact`; the slider separates start-seek pause from release/resume.
- MLPC/history integration preserves the playing state across list/page/media transitions, and load/retry/force-stop paths receive additional cleanup and UI coordination.





## 6. Download and yt-dlp downloader 

### Existing download flow changed

- The default output path moves from `[player]/user_data/downloaded_file` to `[appdata]/JaTubePlayer/saved_file`.
- A select/default/**Open Folder** UI is added for the download destination.
- The configured plaintext cookie path is replaced by the decrypted account cookie, scoped to YouTube before loading into yt-dlp.
- YouTube client and Deno option construction are aligned with the new extraction loader.
- Existing audio/video downloads are reworked to invoke the bundled FFmpeg explicitly through a hidden `subprocess.Popen`, retain the process handle and log its stderr.
- Cancellation disables controls, updates progress text, signals yt-dlp, terminates/kills FFmpeg when needed, uses bounded joins and queues partial/output files for retrying cleanup.
- Startup/final cleanup additionally removes `.part`/`.ytdl` artifacts.
- Twitch video downloads use an appropriate single-stream path and reject unsupported live-download conditions.
- Resolution validation is limited to modes that require it.

### New updater flow

- Stable/nightly selection changes version checks, labels and download URLs.
- The old `utils/auto_ytdlp_update.py` is replaced by downloader, UAC launcher and elevated updater modules.
- UI results distinguish cancellation, timeout, failure and success; cancellation is disabled after elevation begins, and the latest flow displays a warning when cancellation is attempted after the updater has started.
- Added hash verification, fixed destinations, backup/rollback and result-file handling.



## 7. Flow of Account handler and Yt-dlp Updater 


### WebView2 helper controls

- Fresh 32-byte per-run token, DPAPI-protected on disk and sent to the child over stdin.
- Fixed-time token comparison, token-memory clearing and token-file cleanup.
- Hard-coded SHA-256 check of `WebView2Host.exe`.
- Read-only helper handle held from hashing through process exit with write/delete sharing denied.
- Resource-root validation for expected development and packaged locations.
- SHA-256 checks for the three packaged login HTML files.
- WebView2 extensions, DevTools, context menus, host objects, accelerator keys and web messages disabled.
- Normal navigation limited to HTTPS/443 and exact YouTube/account hosts.
- Regional `SetSID` navigation limited to embedded account hosts and the expected path.
- New-window interception and query-free navigation logging.
- Local navigation matched to the full normalized path of the three packaged pages.


### Elevated updater controls

- Network download remains in the normal user process; installed-file replacement is delegated to a `runas` process.
- The launcher retains the elevated process handle and distinguishes completion, UAC cancellation and timeout.
- Inno Setup registers the expected updater directory in HKLM64.
- The elevated updater requires its own resolved directory to match that registered directory.
- Destination paths are fixed under the registered internal directory.
- The downloader fetches stable/nightly checksum data, detached signature and payloads with timeouts.
- The elevated updater verifies the checksum-list OpenPGP signature with the embedded yt-dlp key, then hashes the opened payload streams against signed sums.
- Opened verified streams are held during the process and are used for extraction/copy, tar extraction uses `filter="data"`.
- Existing installed files are backed up; failure restores them and writes structured result JSON.
- Failed verification removes staged/copied payloads.





## 8. Chrome extension and drag-and-drop changes

### Chrome extension

- adding parsed URL acceptance for YouTube watch/shorts, `youtu.be` and Twitch;
- adding extension-local port storage with default 5000;
- adding an options page, toolbar action and application icons;
- widening localhost host permission so the configured port can be used;
- replacing fixed-port fetches with the stored port and surfacing HTTP response errors.

The Flask server changes from polled action fields to direct MLPC/star/info-loader actions, verifies the existing header before dispatch, supports the configured port, sends UI work through the UI queue, and retains threaded loopback HTTP/1.0 startup/shutdown handling. Packaging moves the unpacked extension to the top-level `chrome_ext_pack` and the installer copies it to AppData with load instructions.

### Drag-and-drop

Windows `WM_DROPFILES` file/folder support is inherited from main. Test_update adds:

- an OLE `IDropTarget` handler for URL/text clipboard formats;
- COM initialization/registration on the Tk root thread and explicit revoke/uninitialize cleanup;
- one listener that combines URL and file queues with MLPC;
- supported-media extension filtering for single files, multiple files and folder contents;
- routing for single file, multiple files, folder and accepted URL drops into the shared media model;
- MLPC busy-state blocking while another list operation is active.


## 9. History, UI, logging and lifecycle changes

### History

A new in-memory history stores up to 20 deep-copied snapshots containing URL, full media model, playlist name and media type. Back/forward restores the corresponding list/page and playback state. Follow-up commits correct recording order, preserve names/non-empty state across YouTube, direct URL, starred and local transitions, and prevent shared DnD-list mutation.



### Logging

`log_handler_` adds component-tagged entries with time, severity and content; a queue writes to `%APPDATA%\JaTubePlayer\JaTubePlayer_log.txt`, periodically flushes and flushes immediately for warnings/errors. A GUI viewer reads the log. mpv and yt-dlp adapters map their levels into the same system, and migrated modules replace many direct prints/callback signatures with structured calls.



### UI and lifecycle deltas

- Existing source/page widgets are rewired to MLPC; history navigation, loading/busy states and source-specific status handling are added.
- Settings are reorganized into cards and gain result limits, account/cookie actions, download destination/Open Folder, Chrome extension port, Discord idle wording and stable/nightly yt-dlp selection.
- The settings button gains a 200 ms debounce.
- Satisfy font/license and a banner image are added.
- Video-information handling is extracted to `src/ui/video_info_frame.py`; no-selection/no-playing cases get explicit messages.
- Exact seek behavior, thumbnail/listener fixes and starred-list removal fixes are applied.
- Effective scaling combines per-monitor DPI with available-screen fitting; window/dialog centering, tree dimensions and several widget scaling paths are corrected.
- The Windows blur implementation moves to `src/effect/blur_for_client.py` and receives structure, accent, dark-mode and final sizing corrections.
- Notifications switch from `winotify` to `win11toast`; shortcut creation uses the application icon.
- Discord added configurable idle wording
- More worker-originated UI work is queued through `ui_queue`/`root.after`, with additional locks, busy flags and `finally` cleanup around account, history, media and shutdown paths.
- Version checking defaults on; several download, existence-check and shutdown edge cases are corrected.


## 10. Packaging and configuration

### Packaging

- New onedir PyInstaller application spec gathers project/dynamic/Windows modules and runtime assets while excluding the elevated updater module.
- Separate one-file updater spec packages updater/OpenPGP/native requirements.
- Inno Setup installs x64/admin to Program Files, seeds user files only if missing, records the updater directory, creates shortcuts, launches as the original user, offers optional AppData cleanup and displays extension-loading instructions.
- The source/resource tree moves under `src/` plus packaged `_internal` assets.

### Exact configuration-template changes

Added: `searchmode_keyword`, four `max_result_count` values, `ytdlp_use_cookie`, `ytdlp_use_nightly_build`, `chrome_ext_server_port` and `discord_idle_presence_wording`.

Removed: `entrymode_entry_content`, duplicate playlist-name key, `cache_secs`, `client_secret_path`, `cookie_path`, `record_history` and `enable_drag_and_drop`.

Changed defaults:

- back buffer 256 → 512 MiB;
- cache pause wait 3 → 1 second;
- version check false → true;
- automatic liked refresh true → false;
- Discord “show playing” false → true;
- cache display true → false;
- download path → AppData saved-file directory;
- blur color `#10101000` → `#101010`;
- nightly selection defaults false.