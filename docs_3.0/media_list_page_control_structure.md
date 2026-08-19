# Media List Page Control Structure
> This is a deprecated doc, but somewhat still explain a part of the MLPC

This note explains the current hand-coded media list structure as-is. It focuses on:

- `video_media_control/media_list_page_control.py`
- `ui/Treeview_and_thumbnail.py`
- `loader/media_data_list.py`
- the related wiring in `JaTubePlayer.py`

## Short Summary

`media_data_list` is the shared in-memory playlist data model.

`MediaList_PageControl_` owns page state and decides which slice of `media_data_list` should be shown.

`ThumbnailLoader` owns the actual Treeview row insertion, thumbnail download, row selection, and row tag coloring.

`JaTubePlayer.py` wires these pieces together and still directly edits `media_data_list` in several flows.

## Main Objects

### `media_data_list_template`

Defined in `loader/media_data_list.py`.

It is a simple parallel-list data container:

- `vid_url`: playable URL or local path.
- `playlisttitles`: title text for each item.
- `playlist_channel`: channel/uploader/source label.
- `playlist_thumbnails`: thumbnail URL or `None`.
- `current_media_page`: page where the currently playing item belongs.
- `current_playing_idx_num`: global index of the currently playing item.

The four media arrays must stay aligned by index. For example:

```text
vid_url[17]
playlisttitles[17]
playlist_channel[17]
playlist_thumbnails[17]
```

all describe the same media item.

`current_playing_idx_num` is a global index across the whole list, not the index inside the visible page.

## Queue Model

There are two important queues:

- `ui_queue`: stores callables that must run on the Tkinter UI thread.
- `insert_treeview_quene`: stores row data tuples for the playlist Treeview.

Treeview rows are passed as:

```python
(thumbnail_url, title, channel)
```

`MediaList_PageControl_` does not directly insert Treeview rows. It puts row tuples into `insert_treeview_quene`.

`ThumbnailLoader.treeview_queue_GetterLoop()` polls that queue every 20 ms and inserts rows into `playlisttreebox`.

## Initialization Flow

In `JaTubePlayer.py`, global objects are created first:

```python
ui_queue = queue.Queue()
insert_treeview_quene = queue.Queue()
media_data_list = media_data_list_template()
```

Later, `_init_load_extra_objs()` creates:

```python
thumbnail_loader = ThumbnailLoader(...)

Media_list_page_controller = MediaList_PageControl_(
    ui_queue=ui_queue,
    tree_view_queue=insert_treeview_quene,
    log_handle=log_handle,
    thumbnail_loader=thumbnail_loader,
    page_num_label=page_num_label
)
```

So the dependency direction is:

```text
JaTubePlayer.py
  owns global queues and global media_data_list
  creates ThumbnailLoader
  creates MediaList_PageControl_

MediaList_PageControl_
  uses media_data_list
  writes page rows into insert_treeview_quene
  asks ThumbnailLoader to clear/select/tag rows

ThumbnailLoader
  consumes insert_treeview_quene
  mutates playlisttreebox
  downloads thumbnail images asynchronously
```

## Page Size

The page size is hard-coded as 50 items.

Page slice calculation:

```python
start_index = (current_page - 1) * 50
end_index = min(current_page * 50, len(media_data_list.vid_url))
```

The visible row index is:

```python
page_index = global_index % 50
```

The global index from a selected Treeview row is calculated in `JaTubePlayer.py`:

```python
selected_song_number =
    playlisttreebox.index(selected_tree_item)
    + (Media_list_page_controller.current_page - 1) * 50
```

## YouTube Playlist Loading

The newer YouTube playlist path uses `MediaList_PageControl_`.

Flow:

```text
User selects playlist
  -> get_youtube_playlists()
  -> get_youtube_playlist_thread()
  -> Media_list_page_controller.youtube_init_and_reload(...)
  -> playlist_retriever.init_playlist_items(...)
  -> first 50 items are loaded into media_data_list
  -> MediaList_PageControl_ calculates total_page
  -> _insert_to_ui_queue()
  -> ThumbnailLoader renders visible rows
```

`playlist_retriever` loads the first 50 playlist items synchronously, then starts a background thread to retrieve remaining pages.

This is why `next_page()` checks whether enough data has already arrived:

```python
_total_page_of_current_data = (len(media_data_list.vid_url) + 49) // 50
```

If the user asks for a page that has not been loaded into `media_data_list` yet, the controller returns `-1`.

## Rendering A Page

`MediaList_PageControl_._insert_to_ui_queue()` does the visible-page refresh:

1. Calls `thumbnail_loader.clear_thumbnails()`.
2. Updates `page_num_label` through `ui_queue`.
3. Calculates the current page slice.
4. Pushes each visible item into `tree_view_queue`.

The row tuple comes from aligned arrays:

```python
(
    media_data_list.playlist_thumbnails[i],
    media_data_list.playlisttitles[i],
    media_data_list.playlist_channel[i]
)
```

Then `ThumbnailLoader.treeview_queue_GetterLoop()` inserts those rows into `playlisttreebox`.

## Thumbnail Loading

`ThumbnailLoader` starts an asyncio event loop in a separate thread.

For online-style modes:

- `playing_vid_mode == 0`: YouTube
- `playing_vid_mode == 4`: starred videos

it downloads thumbnails with `aiohttp`, resizes/crops them with PIL, stores `ImageTk.PhotoImage` objects in `self.temp`, then sends a UI-thread update through `ui_queue`.

`self.temp` is important because Tkinter images need a Python reference. Without it, images can disappear after garbage collection.

For local-folder mode, the Treeview column for images is hidden because thumbnails are not loaded.

## Page Navigation

The UI buttons call:

```python
page_control(1)  # next
page_control(2)  # previous
```

`page_control()` calls:

```python
Media_list_page_controller.next_page()
Media_list_page_controller.prev_page()
```

Return codes:

- `0`: page changed successfully.
- `-1`: page is still loading or controller is busy.
- `-2`: failed.
- `-3`: current media type does not support page control.

Supported page-control media types in `media_list_page_control.py`:

- `YOUTUBE`
- `FOLDER`
- `STARRED_VIDEO`

However, in the current app, some folder/starred paths still fill the Treeview directly from `JaTubePlayer.py` instead of fully initializing the page controller state.

## Selection And Playback State

There are two separate ideas:

- current selection: what row the user clicked in the Treeview.
- current playing: what item the player is actually playing.

They are often the same, but the code allows them to be different.

### Current Selection

Current selection is stored in the global variable:

```python
selected_song_number
```

This is a global media index, not a page-local Treeview index.

The Treeview only contains the current page, so `get_selected_vid()` converts the selected row into a global index:

```python
selected_song_number =
    playlisttreebox.index(playlisttreebox.selection()[0])
    + (Media_list_page_controller.current_page - 1) * 50
```

Example:

```text
current_page = 3
clicked Treeview row = 4
selected_song_number = 4 + (3 - 1) * 50 = 104
```

After selection, `get_selected_vid()` also updates the star button state by checking:

```python
star_vid_handle.search(media_data_list.vid_url[selected_song_number])
```

So selection drives UI controls such as the star button, but it does not automatically mean playback has changed.

### Current Playing

Current playing is stored inside `media_data_list`:

```python
media_data_list.current_playing_idx_num
media_data_list.current_media_page
```

`current_playing_idx_num` is the global index of the playing item.

`current_media_page` is the page where that playing item belongs.

When playback starts from the list, `download_and_play()` updates:

```python
media_data_list.current_playing_idx_num = selected_song_number
media_data_list.current_media_page = Media_list_page_controller.current_page
```

Then it pushes a load command:

```python
load_thread_queue.put((None, media_data_list.vid_url[selected_song_number]))
```

for YouTube/online media, or:

```python
load_thread_queue.put((media_data_list.vid_url[selected_song_number], None))
```

for local files.

The player then uses `load_thread_queue` to load either:

```python
(None, direct_url)      # YouTube/online
(file_path, None)       # local file
```

### Playing Title Label

The visible "now playing" title is not driven by selection. It is updated by `load_thread()` after the player successfully loads media.

For online media, the label comes from `playing_vid_info_dict['title']`:

```python
playing_title_textbox.insert(tk.END, playing_vid_info_dict['title'])
```

For local media, the label comes from the path or basename:

```python
playing_title_textbox.insert(tk.END, os.path.basename(str(chosen_file)))
```

So the current selection can move without changing the now-playing label. The label follows successful playback, not Treeview clicks.

### Playing Tag

The orange/playing row marker is a Treeview tag, not the same as selection.

When playback succeeds, `load_thread()` calls:

```python
Media_list_page_controller.set_playing_tag(current_idx, "playing")
```

`set_playing_tag()` only applies the Treeview tag if the playing item is on the currently visible page:

```python
if media_data_list.current_media_page == current_page:
    thumbnail_loader.set_item_color(page_idx, tag)
```

This prevents trying to color a row that is not currently rendered.

Before loading a new item, `load_thread()` calls:

```python
Media_list_page_controller.remove_playing_tag()
```

That clears all row tags on the currently visible page through:

```python
ThumbnailLoader.clear_all_tag()
```

If the old playing item was on another page, there is no visible row to clear. When that page is rendered later, the controller decides whether to re-apply the playing tag by comparing `current_page` with `current_media_page`.

### Selection vs Playing Tag

Selection and playing tag are independent:

- selection is controlled with `playlisttreebox.selection_set(...)`.
- playing marker is controlled with `playlisttreebox.item(..., tags=("playing",))`.

This is why one row can be selected because the user clicked it, while another row can be the actual playing item.

## Next / Previous Playback

`playnextsong()` and `playprevsong()` use `media_data_list.current_playing_idx_num` as the source of truth.

When the current playing item is at a page boundary:

- next from index `49`, `99`, etc. calls `Media_list_page_controller.next_page(...)`
- previous from index `0`, `50`, etc. calls `Media_list_page_controller.prev_page(...)`

If the visible selection should follow playback, these methods also adjust `selected_song_number` and select the corresponding Treeview row after the page refresh.

### `selected_follow`

Before moving to the next or previous item, the code calculates:

```python
selected_follow =
    media_data_list.current_playing_idx_num == selected_song_number
```

Meaning:

- `True`: the selected row is also the currently playing item.
- `False`: the user selected a different row while another item is playing.

This controls whether page navigation should also move the visible selection.

If `selected_follow` is `False`, playback can move to the next/previous item without forcing the user's current selection to move.

### Next Playback Logic

`playnextsong()` works in this order:

1. Requires `media_data_list.current_playing_idx_num != -1`.
2. Stops current playback and clears the playing tag.
3. Calculates `selected_follow`.
4. If the current playing item is at the end of a page, calls `next_page(...)`.
5. Advances `current_playing_idx_num`.
6. If `selected_follow` is true, advances `selected_song_number` and selects the visible row.
7. Pushes the next item into `load_thread_queue`.

The page boundary check is:

```python
if (
    media_data_list.current_playing_idx_num % 50 == 49
    or media_data_list.current_playing_idx_num == len(media_data_list.vid_url) - 1
):
    pageRes = Media_list_page_controller.next_page(
        select_first_of_next_page=True,
        selected_follow=selected_follow
    )
```

So next-page loading happens before `current_playing_idx_num` is incremented.

After a successful page turn, `playnextsong()` updates the playing page:

```python
if media_data_list.current_media_page == Media_list_page_controller.total_page:
    media_data_list.current_media_page = 1
    if selected_follow:
        selected_song_number = -1
else:
    media_data_list.current_media_page += 1
```

Then the global playing index moves:

```python
if media_data_list.current_playing_idx_num == len(media_data_list.vid_url) - 1:
    media_data_list.current_playing_idx_num = 0
else:
    media_data_list.current_playing_idx_num += 1
```

If selection is following playback, the visible row is selected after the page has had time to render:

```python
cur_page_idx = media_data_list.current_playing_idx_num % 50
root.after(1000, lambda: playlisttreebox.selection_set(
    playlisttreebox.get_children()[cur_page_idx]
))
root.after(1000, lambda: playlisttreebox.see(
    playlisttreebox.get_children()[cur_page_idx]
))
selected_song_number += 1
```

The `root.after(1000, ...)` delay is important because page rendering goes through queues and `ThumbnailLoader.treeview_queue_GetterLoop()`.

### Previous Playback Logic

`playprevsong()` is the reverse flow.

It calls previous page when the current playing item is at the start of a page:

```python
if (
    media_data_list.current_playing_idx_num % 50 == 0
    or media_data_list.current_playing_idx_num == 0
):
    pageRes = Media_list_page_controller.prev_page(
        select_last_of_prev_page=True,
        selected_follow=selected_follow
    )
```

After a successful page turn, it updates `current_media_page`:

```python
if media_data_list.current_media_page == 1:
    media_data_list.current_media_page = Media_list_page_controller.total_page
    if selected_follow:
        selected_song_number = len(media_data_list.vid_url)
else:
    media_data_list.current_media_page -= 1
```

Then it moves the playing index:

```python
if media_data_list.current_playing_idx_num == 0:
    media_data_list.current_playing_idx_num = len(media_data_list.vid_url) - 1
else:
    media_data_list.current_playing_idx_num -= 1
```

If selection follows playback, it selects and scrolls to the page-local row:

```python
cur_page_idx = media_data_list.current_playing_idx_num % 50
root.after(1000, lambda: playlisttreebox.selection_set(
    playlisttreebox.get_children()[cur_page_idx]
))
root.after(1000, lambda: playlisttreebox.see(
    playlisttreebox.get_children()[cur_page_idx]
))
selected_song_number -= 1
```

### Page Controller Selection Helpers

When page navigation is called from playback, `MediaList_PageControl_` can select the first or last row after loading:

```python
next_page(select_first_of_next_page=True, selected_follow=selected_follow)
prev_page(select_last_of_prev_page=True, selected_follow=selected_follow)
```

Inside `next_page()`:

```python
if select_first_of_next_page:
    thumbnail_loader.select_first_item()
```

Inside `prev_page()`:

```python
if select_last_of_prev_page:
    thumbnail_loader.select_last_item()
```

These helpers schedule their selection after 500 ms:

```python
root.after(500, self._select_first_item)
root.after(500, self._select_last_item)
```

This is another delay used to wait for Treeview rows to exist.

### Page Label Following

`page_num_label` follows `MediaList_PageControl_.current_page`, not the playing index directly.

Every time `_insert_to_ui_queue()` renders a page, it sends this UI update:

```python
self.ui_queue.put(
    lambda: self.page_num_label.configure(
        text=f'page {self.current_page}/{self.total_page}'
    )
)
```

So the page label updates when the controller renders a page.

During next/previous playback, the page label changes only when `next_page()` or `prev_page()` actually reloads the visible page. If playback advances inside the same page, the page label stays the same.

### Playing Tag Following Page Changes

After a normal next/previous page render, the controller checks:

```python
if self.current_page == self.media_data_list.current_media_page:
    self.set_playing_tag(self.media_data_list.current_playing_idx_num)
```

This makes the playing tag reappear when the user navigates back to the page containing the current playing item.

If the visible page is not `current_media_page`, no playing tag is applied.

This is the main tag-following rule:

```text
playing tag follows current_playing_idx_num
but only appears when current_page == current_media_page
```

## Random Playback

Random mode calls:

```python
Media_list_page_controller.random_media(selected_song_number)
```

The controller refuses random selection if the full list is not loaded yet.

When it succeeds:

1. Picks a random global index.
2. Sets `current_page` from that index.
3. Refreshes the Treeview if the visible selection follows playback.
4. Updates `media_data_list.current_media_page`.
5. Updates `media_data_list.current_playing_idx_num`.

## Adding Items From Chrome Extension

Chrome extension "add to end" eventually calls:

```python
Media_list_page_controller.add_to_page_end(...)
```

This inserts the new item into all four `media_data_list` arrays at the end of the current page position:

- if currently on the last page: append at the end of the list.
- otherwise: insert at `current_page * 50`.

It also immediately pushes that one row into `tree_view_queue`.

The inserted title is prefixed with:

```text
[Added]
```

## Removing A Selected Item

The settings action `remove_selected_from_playlist_setting()` calls:

```python
Media_list_page_controller.clear_selected(
    selected_idx=selected_song_number,
    selected_tree_ID=item_id
)
```

This removes the item from all four arrays and deletes the Treeview row by ID through `ThumbnailLoader.clear_thumb()`.

Important detail: the selected index passed here is the global index, while the Treeview item id must belong to the visible page.

## Direct Paths That Bypass Page Controller

Several flows still directly manipulate `media_data_list` and `insert_treeview_quene` in `JaTubePlayer.py`:

- YouTube search
- starred video listing
- local folder listing
- drag-and-drop local lists
- some older liked/subscription paths

These paths usually do:

```python
media_data_list.clear()
media_data_list.vid_url.append(...)
media_data_list.playlisttitles.append(...)
media_data_list.playlist_channel.append(...)
media_data_list.playlist_thumbnails.append(...)
insert_treeview_quene.put(...)
```

This means the current design is mixed:

- `MediaList_PageControl_` handles page-aware rendering for the newer YouTube playlist path.
- Other modes still render rows directly.
- Playback code still uses the same global `media_data_list`, regardless of who filled it.

## State Ownership

Current practical ownership:

| State | Main owner | Notes |
| --- | --- | --- |
| `media_data_list` arrays | `JaTubePlayer.py` and loaders | Shared mutable data model. |
| `current_page` | `MediaList_PageControl_` | UI-visible page. |
| `total_page` | `MediaList_PageControl_` | Calculated from source count for playlist path. |
| `current_playing_idx_num` | `media_data_list` | Global playing index. |
| `current_media_page` | `media_data_list` | Page containing playing item. |
| Treeview rows | `ThumbnailLoader` | Inserted from `insert_treeview_quene`. |
| Thumbnail images | `ThumbnailLoader` | Async download and `PhotoImage` lifetime storage. |
| Selected item | `JaTubePlayer.py` | Stored as global `selected_song_number`. |

## Important Mental Model

Think of the system as three layers:

```text
Data layer:
  media_data_list

Page/controller layer:
  MediaList_PageControl_

View/render layer:
  ThumbnailLoader + playlisttreebox
```

`JaTubePlayer.py` sits above all three and coordinates user actions, playback, and mode changes.

The page controller does not own the full application playlist behavior yet. It is a page-slice and Treeview-refresh helper around the shared `media_data_list`.

## Notes / Current Quirks

- The page size is duplicated as literal `50` in several places.
- `media_data_list` uses parallel arrays, so every insert/pop must touch all arrays in the same order.
- Some media modes use the page controller, but some still bypass it.
- `MediaType.FOLDER` and `MediaType.STARRED_VIDEO` are supported by controller methods, but not every local/starred loading path sets `Media_list_page_controller.media_type` and `total_page`.
- `selected_song_number` is global index, while Treeview row index is page-local.
- `ThumbnailLoader.clear_thumbnails()` clears pending queue items and async thumbnail tasks before rendering a new page.
- UI changes from background work should go through `ui_queue`; Treeview row data should go through `insert_treeview_quene`.
