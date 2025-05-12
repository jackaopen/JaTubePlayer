# 📄 JaTubePlayer: Related Video Recommendation System

This module enhances JaTubePlayer with a related video recommendation system based on recently played tags and channels. It utilizes `yt_dlp` and threading to fetch data efficiently.

---

## ✅ Features Overview

- **Tag & Channel Memory System**
  - Stores up to 15 recent search tags and channel URLs.
  - Maintains these in `recent_tag.json` and `recent_channel_url.json`.

- **Recommendation Engine**
  - Fetches related videos from:
    - Past search tags (via YouTube search)
    - Channel upload lists (via their channel ID)

- **Parallelized Fetching**
  - Uses `ThreadPoolExecutor` for concurrent data fetching.
  - Separate threads for tag-based search and channel video lists.

---

## 🔧 Core Components

### `save_recent_vid_info(tag, channel_url, internal_dir)`
- Updates the tag and channel memory files.
- Ensures unique entries and limits to 15 items.

### `_search(youtubeDL, query, cookiedir)`
- Uses `ytsearch10:` with yt_dlp to fetch flat video metadata from a query.

### `_get_channel_video(youtubeDL, id, cookiedir)`
- Retrieves latest videos from a channel's upload playlist.

### `get_related_video(youtubeDL, internal_dir, cookiedir)`
- Combines the above to return:
  - `title_output`, `url_output`, `channel_output`, `thumbnail`
- Returns `None` if nothing valid is retrieved.

### `init_history(internal_dir)`
- Initializes recent tag and channel files with example values.
- Safe to call at startup for fresh config.

---

## 🧠 Data Files

| File Name                   | Content Type        |
|----------------------------|---------------------|
| `recent_tag.json`          | List of recent tags |
| `recent_channel_url.json`  | List of channel URLs|

---

## 📦 JSON Dump Utility

```python
def _dump(internal_dir, filename, content)
```
- Writes JSON data to the target directory using `indent=4`.

---


## ⚠️ Notes

- The system avoids duplicate entries.
- Threading prevents UI blocking and accelerates response.
- The module assumes `yt_dlp` is correctly initialized and functional.