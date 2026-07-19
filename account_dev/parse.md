# InnerTube Browse Entry Structures

YouTube can switch between newer `lockupViewModel` entries and older renderer entries. A parser should recognize both forms.

## Page Summary

| Page | Browse ID | Common initial entries |
|---|---|---|
| Home | `FEwhat_to_watch` | `tabRenderer.content.richGridRenderer.contents[]` |
| Subscriptions | `FEsubscriptions` | `tabRenderer.content.richGridRenderer.contents[]` |
| History | `FEhistory` | `tabRenderer.content.sectionListRenderer.contents[]` or `tabRenderer.content.richGridRenderer.contents[]` |
| Playlists page | `FEplaylist_aggregation` | `tabRenderer.content.richGridRenderer.contents[]` or nested `gridRenderer.items[]` |
| Playlist by ID | `VL<PLAYLIST_ID>` | Nested `playlistVideoListRenderer.contents[]` |
| Liked videos | `VLLL` | Nested `playlistVideoListRenderer.contents[]` |
| Watch Later | `VLWL` | Nested `playlistVideoListRenderer.contents[]` |

The shared beginning of an initial browse response is usually:

```text
contents
└── twoColumnBrowseResultsRenderer
    └── tabs[]
        └── tabRenderer
            └── content
```

## Home

Exact common initial path:

```python
response["contents"] \
    ["twoColumnBrowseResultsRenderer"] \
    ["tabs"][selected_tab] \
    ["tabRenderer"] \
    ["content"] \
    ["richGridRenderer"] \
    ["contents"]
```

```text
tabRenderer.content
└── richGridRenderer
    └── contents[]
        ├── richItemRenderer
        │   └── content
        │       └── lockupViewModel
        ├── richSectionRenderer
        ├── richItemRenderer
        │   └── content
        │       └── adSlotRenderer
        └── continuationItemRenderer
```

Media entry:

```python
entry["richItemRenderer"]["content"]["lockupViewModel"]
```

## Subscriptions

Exact common initial path:

```python
response["contents"] \
    ["twoColumnBrowseResultsRenderer"] \
    ["tabs"][selected_tab] \
    ["tabRenderer"] \
    ["content"] \
    ["richGridRenderer"] \
    ["contents"]
```

```text
tabRenderer.content
└── richGridRenderer
    └── contents[]
        ├── richItemRenderer
        │   └── content
        │       ├── lockupViewModel
        │       └── videoRenderer
        └── continuationItemRenderer
```

Media entry variants:

```python
entry["richItemRenderer"]["content"]["lockupViewModel"]
entry["richItemRenderer"]["content"]["videoRenderer"]
```

## History

History may contain multiple `itemSectionRenderer` sections for dates such as Today or Yesterday.

Common section-list path:

```python
response["contents"] \
    ["twoColumnBrowseResultsRenderer"] \
    ["tabs"][selected_tab] \
    ["tabRenderer"] \
    ["content"] \
    ["sectionListRenderer"] \
    ["contents"][section_index] \
    ["itemSectionRenderer"] \
    ["contents"]
```

Possible rich-grid path:

```python
response["contents"] \
    ["twoColumnBrowseResultsRenderer"] \
    ["tabs"][selected_tab] \
    ["tabRenderer"] \
    ["content"] \
    ["richGridRenderer"] \
    ["contents"]
```

```text
tabRenderer.content
└── sectionListRenderer
    └── contents[]
        └── itemSectionRenderer
            ├── header
            │   └── itemSectionHeaderRenderer
            └── contents[]
                ├── videoRenderer
                ├── richItemRenderer
                │   └── content
                │       └── lockupViewModel
                └── continuationItemRenderer
```

Media entry variants:

```python
entry["videoRenderer"]
entry["richItemRenderer"]["content"]["lockupViewModel"]
```

## Playlists Page

Browse ID: `FEplaylist_aggregation`.

Newer layout:

```python
response["contents"] \
    ["twoColumnBrowseResultsRenderer"] \
    ["tabs"][selected_tab] \
    ["tabRenderer"] \
    ["content"] \
    ["richGridRenderer"] \
    ["contents"]
```

```text
tabRenderer.content
└── richGridRenderer
    └── contents[]
        ├── richItemRenderer
        │   └── content
        │       └── lockupViewModel
        └── continuationItemRenderer
```

The lockup identifies itself as a playlist:

```python
lockup["contentType"] == "LOCKUP_CONTENT_TYPE_PLAYLIST"
```

Older layout:

```python
response["contents"] \
    ["twoColumnBrowseResultsRenderer"] \
    ["tabs"][selected_tab] \
    ["tabRenderer"] \
    ["content"] \
    ["sectionListRenderer"] \
    ["contents"][section_index] \
    ["itemSectionRenderer"] \
    ["contents"][content_index] \
    ["gridRenderer"] \
    ["items"]
```

```text
tabRenderer.content
└── sectionListRenderer
    └── contents[]
        └── itemSectionRenderer
            └── contents[]
                └── gridRenderer
                    └── items[]
                        └── gridPlaylistRenderer
```

Media entry variants:

```python
entry["richItemRenderer"]["content"]["lockupViewModel"]
entry["gridPlaylistRenderer"]
```

## Playlist by ID

This includes normal URLs such as `https://www.youtube.com/playlist?list=PLxxxx`.

Browse ID: `VL<PLAYLIST_ID>`. For example, playlist `PLabc` uses browse ID `VLPLabc`.

Exact common initial path:

```python
response["contents"] \
    ["twoColumnBrowseResultsRenderer"] \
    ["tabs"][selected_tab] \
    ["tabRenderer"] \
    ["content"] \
    ["sectionListRenderer"] \
    ["contents"][section_index] \
    ["itemSectionRenderer"] \
    ["contents"][content_index] \
    ["playlistVideoListRenderer"] \
    ["contents"]
```

The common response uses `selected_tab = 0`, `section_index = 0`, and `content_index = 0`, but these indexes must not be assumed permanently.

```text
tabRenderer.content
└── sectionListRenderer
    └── contents[]
        └── itemSectionRenderer
            └── contents[]
                └── playlistVideoListRenderer
                    └── contents[]
                        ├── playlistVideoRenderer
                        └── continuationItemRenderer
```

Media entry:

```python
entry["playlistVideoRenderer"]
```

Newer layouts may instead contain a `lockupViewModel`.

## Liked Videos

Liked videos is the special playlist with ID `LL`.

Browse ID: `VLLL`.

Exact common initial path:

```python
response["contents"] \
    ["twoColumnBrowseResultsRenderer"] \
    ["tabs"][selected_tab] \
    ["tabRenderer"] \
    ["content"] \
    ["sectionListRenderer"] \
    ["contents"][section_index] \
    ["itemSectionRenderer"] \
    ["contents"][content_index] \
    ["playlistVideoListRenderer"] \
    ["contents"]
```

The common concrete indexes are `["tabs"][0]`, both `["contents"][0]`, but recursive renderer lookup is safer.

```text
tabRenderer.content
└── sectionListRenderer
    └── contents[]
        └── itemSectionRenderer
            └── contents[]
                └── playlistVideoListRenderer
                    └── contents[]
                        ├── playlistVideoRenderer
                        └── continuationItemRenderer
```

Media entry:

```python
entry["playlistVideoRenderer"]
```

## Watch Later

Watch Later is the special playlist with ID `WL` and normally has the same entry structure as Liked Videos.

Browse ID: `VLWL`.

Exact common initial path:

```python
response["contents"] \
    ["twoColumnBrowseResultsRenderer"] \
    ["tabs"][selected_tab] \
    ["tabRenderer"] \
    ["content"] \
    ["sectionListRenderer"] \
    ["contents"][section_index] \
    ["itemSectionRenderer"] \
    ["contents"][content_index] \
    ["playlistVideoListRenderer"] \
    ["contents"]
```

The common concrete indexes are `["tabs"][0]`, both `["contents"][0]`, but recursive renderer lookup is safer.

```text
tabRenderer.content
└── sectionListRenderer
    └── contents[]
        └── itemSectionRenderer
            └── contents[]
                └── playlistVideoListRenderer
                    └── contents[]
                        ├── playlistVideoRenderer
                        └── continuationItemRenderer
```

Media entry:

```python
entry["playlistVideoRenderer"]
```

## Continuation Responses

Modern rich-grid or history response:

```text
onResponseReceivedActions[]
└── appendContinuationItemsAction
    └── continuationItems[]
        ├── media entry
        └── continuationItemRenderer
```

Alternative modern response:

```text
onResponseReceivedEndpoints[]
└── appendContinuationItemsAction
    └── continuationItems[]
```

Playlist continuation response:

```text
continuationContents
└── playlistVideoListContinuation
    └── contents[]
        ├── playlistVideoRenderer
        └── continuationItemRenderer
```

The common continuation token path inside a continuation entry is:

```python
entry["continuationItemRenderer"] \
    ["continuationEndpoint"] \
    ["continuationCommand"] \
    ["token"]
```

## Renderer Keys

The media walker should recognize these keys:

```python
MEDIA_RENDERERS = {
    "lockupViewModel",
    "videoRenderer",
    "gridVideoRenderer",
    "playlistVideoRenderer",
    "gridPlaylistRenderer",
}
```

## Card Types by Page

The entries array is mixed. Media cards and non-media entries can appear together.

| Page | Media card renderers | Other entries to expect |
|---|---|---|
| Home | `lockupViewModel` for video or playlist; older `videoRenderer`; Shorts may use `reelItemRenderer` | `adSlotRenderer`, `richSectionRenderer`, `continuationItemRenderer` |
| Subscriptions | `lockupViewModel`, `videoRenderer`, possible `reelItemRenderer` | Shelves/sections, empty-state messages, `continuationItemRenderer` |
| History | `videoRenderer`, newer `lockupViewModel` | Date headers/sections, messages, `continuationItemRenderer` |
| Playlists page | `lockupViewModel` with `LOCKUP_CONTENT_TYPE_PLAYLIST`, older `gridPlaylistRenderer` or `playlistRenderer` | Section headers, create-playlist controls, `continuationItemRenderer` |
| Playlist by ID | `playlistVideoRenderer`, possible newer video `lockupViewModel` | Unavailable video entries, messages, `continuationItemRenderer` |
| Liked videos | `playlistVideoRenderer`, possible newer video `lockupViewModel` | Unavailable video entries, messages, `continuationItemRenderer` |
| Watch Later | `playlistVideoRenderer`, possible newer video `lockupViewModel` | Unavailable video entries, messages, `continuationItemRenderer` |

The parser must check the renderer key for each individual entry. Do not assume every entry in one `contents[]` array has the same card type.
