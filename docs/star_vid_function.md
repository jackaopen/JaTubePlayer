# Starred Video Functionality

This document explains the **starred video** feature used by JaTubePlayer. The feature
allows users to save and replay favorite videos (local or online) in a persistent list.
The relevant code is located in `utils/star_vid.py` and is orchestrated by the main
application (`JaTubePlayer.py`).

---

## Overview

The starred video system is implemented by the `star_vid_handler` class. It manages a
JSON-backed dictionary of URLs to metadata (thumbnail URL, title, uploader/channel).
Users can add, remove, search, and list starred videos. The list is used to populate
the playlist treeview when the user selects the "★ Star" button in the UI.

Operations are designed to run in background threads to avoid blocking the UI.


## Class Definition

```python
class star_vid_handler:
    def __init__(self, current_dir: str, yt_dlp: object, deno_path: str,
                 yt_dlp_log_handler: object):
        self.current_dir = current_dir
        self.yt_dlp = yt_dlp
        self.deno_path = deno_path
        self.yt_dlp_log_handler = yt_dlp_log_handler
        self._reload()
```

- `current_dir` – project root; used to locate `user_data/starred_vid.json`.
- `yt_dlp` – reference to the downloader library used for metadata retrieval.
- `deno_path` – path to Deno runtime for yt-dlp's JS environment.
- `yt_dlp_log_handler` – logger used for error/debug messaging.

The constructor immediately loads existing data by calling `_reload()`.


### Internal helpers

```python
    def _reload(self):
        with open(os.path.join(self.current_dir,'user_data','starred_vid.json'),'rb') as f:
            self.starred_vid_dict = json.load(f)

    def _save(self):
        with open(os.path.join(self.current_dir,'user_data','starred_vid.json'),'w') as f:
            json.dump(self.starred_vid_dict,f,indent=4)
```

- `_reload()` deserializes the JSON file. It should be called whenever the
  file may have changed.
- `_save()` writes the in-memory dictionary back to disk, pretty-printed for manual
  inspection.


## Public API

### `add(url, thumb=None, title=None, channel=None, cookie_path=None)`

Adds a video to the starred list. If the `url` refers to a local file (`os.path.exists`
returns `True`), metadata is generated from the filename. Otherwise, metadata is
fetched via `utils.get_media_info.get_info` using `yt_dlp`.

```python
if not os.path.exists(url):
    if not thumb or not title or not channel:
        _,info = get_info(...)
        thumb = info['thumbnails'][0]['url'] if available
        title = info.get('title')
        channel = info.get('channel')
else:
    thumb = None
    title = os.path.basename(url)
    channel = "local file"

self.starred_vid_dict[url] = {
    "thumb": thumb,
    "title": title,
    "channel": channel
}
self._save()
```

Returns `True` on success, `False` on error; errors are logged via
`yt_dlp_log_handler`.


### `remove(url)`

Deletes an entry and persists the change.

```python
self.starred_vid_dict.pop(url,None)
self._save()
```


### `search(url)`

Returns metadata for the given `url`, or `None` if not starred.


### `list_all(treeview_queue, vid_url, playlisttitles, playlist_channel, playlist_thumbnails)`

Populates both the supplied lists and the `treeview_queue` used by the main UI.
This method is intended to run in a background thread. It clears the provided lists
and then iterates through the dictionary, copying values and queuing thumbnail data
for insertion into the playlist treeview.

```python
for url in self.starred_vid_dict.keys():
    vid_url.append(url)
    info = self.starred_vid_dict[url]
    playlisttitles.append(info['title'])
    playlist_channel.append(info['channel'])
    playlist_thumbnails.append(info['thumb'])

    treeview_queue.put((info['thumb'],info['title'],info['channel']))
```

Returns `True` on success, `False` if any exception occurs.


## Integration with Main Application

- **Adding**: various UI callbacks call `star_vid.handle.add(...)` when the user
  stars a video, passing the current URL and optionally cached metadata. Upon
  success they also immediately insert into the playlist via `insert_treeview_quene`.

- **Listing**: when the "★ Star" button is pressed, `get_starred_vid()` (defined
  elsewhere) spawns a thread to call `star_vid_handler.list_all(...)`, which then
  updates the UI asynchronously. The lists `vid_url`, `playlisttitles`, etc.
  are used for playback logic once a starred track is selected.

- **Searching/Removal**: used by UI elements to highlight starred videos or to
  remove them from the list.


## Example Usage (from `__main__` block)

```python
if __name__ == "__main__":
    ...
    star_vid_handler = star_vid_handler(...)
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    star_vid_handler.add(url=url)
    print(star_vid_handler.search(url=url))
    star_vid_handler.remove(url=url)
```

This simple test shows how to create the handler and invoke each public method.


## Notes and Tips

- The `starred_vid.json` file is created automatically; ensure `user_data`
  directory exists or `_reload()` will raise `FileNotFoundError`.
- For local files the `thumb` value is always `None`; UI code should handle
  displaying a default icon.
- Thread safety: methods themselves are not synchronized. The caller should ensure
  only one thread modifies the handler at a time (which the main application does
  by serializing calls through its own thread).  

---

This markdown should live under `/docs` and can be updated as the feature evolves.
