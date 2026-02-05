# 📄 JaTubePlayer: YouTube Subscription & Likes Manager

This module enables JaTubePlayer to access the user's YouTube subscriptions and liked videos using Google OAuth. It also timestamps subscriptions via RSS for sorting by recent activity.

---

## ✅ Features Overview

- **Subscription List Fetching**
  - Uses YouTube API + OAuth to fetch all subscribed channel IDs.
  - Channels are timestamped using their RSS upload date for sorting.

- **Liked Video Fetching**
  - Retrieves all liked video URLs from the user's "LL" (Liked Videos) playlist.

- **Local Caching**
  - Saves data to:
    - `sub.json`: Sorted list of subscribed channels and their latest upload timestamps.
    - `liked.json`: List of liked YouTube video URLs.

---

## 🔧 Core Functions

### `fetch_feed(...)`
- Uses `aiohttp.ClientSession` for async HTTP requests
- Parses XML using `xml.etree.ElementTree.fromstring()`
- The YouTube RSS uses the **Atom XML namespace**, so all tag lookups use `{http://www.w3.org/2005/Atom}` prefix
- Extracts `<updated>` tag timestamps for each video entry
- Returns the latest available (past-published) video's upload epoch timestamp

### `get_all_feeds(...)`
- Runs multiple RSS fetches concurrently via `asyncio.gather(...)`
- Aggregates and sorts the channels by most recent uploads
- Outputs results to a `sub.json` file for use in the subscription module

### `update_like_list(api, cred, client_secert_path)`
- Authenticates with YouTube Data API.
- Fetches all videos from the user's liked playlist.
- Saves video URLs to `liked.json`.

### `_get_sub_timestamp(channel_list)`
- Concurrently parses RSS feeds for each channel.
- Sorts by upload timestamp in descending order.

### `_get_timestamp_info(item)`
- Parses the latest uploaded video timestamp via RSS.
- Converts published time to UNIX timestamp using `calendar.timegm`.

---
## 🌐 Atom XML Namespace Parsing

- YouTube's RSS uses the **Atom namespace**: `xmlns="http://www.w3.org/2005/Atom"`
- ElementTree requires full namespaced tag paths: e.g.,

```python
entry = root.find('{http://www.w3.org/2005/Atom}entry')
updated = entry.find('{http://www.w3.org/2005/Atom}updated').text
```

> Failing to specify the namespace will result in `find()` returning `None`

---

## 📦 Utility Methods

| Function          | Purpose                                      |
|------------------|----------------------------------------------|
| `dump()`         | Dumps data into `.json` with pretty format   |
| `liked_channel()`| Returns liked video URLs from `liked.json`   |
| `sub_channel()`  | Returns channel IDs from `sub.json`          |

---

## 📁 Local Cache Files

| File Name      | Content Description                                  |
|----------------|------------------------------------------------------|
| `sub.json`     | `[[channel_id, epoch_timestamp], ...]` (sorted)      |
| `liked.json`   | List of video URLs liked by the user                 |

