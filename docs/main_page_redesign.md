# Main Page UI Redesign — Complete Documentation

> **Date:** February 25, 2026  
> **Scope:** Full reorganization of all main page widgets in `JaTubePlayer.py`  
> **Functions Modified:** Widget creation section (lines ~4397–4818), `fullscreen_widget_change()` normal mode  
> **Logic Changed:** None — all callbacks, variable bindings, event handlers, threads, and control flow are identical

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Layout Comparison](#layout-comparison)
3. [Detailed Changes](#detailed-changes)
   - [Header Bar](#1-header-bar)
   - [Status Panel](#2-status-panel)
   - [Right Panel (Playlist)](#3-right-panel-playlist)
   - [Playlist Buttons](#4-playlist-buttons)
   - [Video Container](#5-video-container)
   - [Transport Bar (Controls)](#6-transport-bar-controls)
   - [Fullscreen Mode](#7-fullscreen-mode)
4. [New Visual Elements](#new-visual-elements)
5. [Widget Position Map](#widget-position-map)
6. [Color & Style Changes](#color--style-changes)
7. [What Was NOT Changed](#what-was-not-changed)

---

## Design Philosophy

The redesign takes inspiration from **modern media players** (Spotify, YouTube Music, Apple Music) with these principles:

1. **Full-width transport bar** — The controls frame now spans the entire window width at the bottom, creating a persistent "media bar" feel
2. **Prominent "Now Playing"** — Song title displayed in a full-width strip at the top of the transport bar
3. **Horizontal transport row** — Mode, Playback, Volume, and Action buttons organized in a clear left-to-right horizontal flow
4. **Pill-shaped playback controls** — Transport buttons in a rounded container with ghost-style prev/stop/next buttons
5. **Hero "Play Selected" button** — The primary action is now the most prominent element in the playlist button area
6. **Compact header** — Icon-only labels for search/playlist save vertical space
7. **Accent-bordered video** — Blue border on the video container draws the eye to the content

---

## Layout Comparison

### Before (Old Layout)
```
┌──────────────────────────────────────────────────────────────────────┐
│ HEADER BAR (7.35% height)                                           │
│ 🎵 JaTubePlayer  🔍 Search:[___] 🔎  📁 Playlist:[___][▶Enter]    │
│                                          [Status Panel]             │
├──────────────────────────────┬───────────────────────────────────────┤
│  VIDEO CONTAINER (60.2%w)    │  RIGHT PANEL (37.5%w, 68.4%h)        │
│  ┌────────────────────────┐  │  ┌─────────────────────────────────┐  │
│  │     Frame_for_mpv      │  │  │ 📋 Mode header + text           │  │
│  │     (video player)     │  │  ├─────────────────────────────────┤  │
│  │                        │  │  │ Playlist Treeview (79.6% h)     │  │
│  │                        │  │  │                                 │  │
│  └────────────────────────┘  │  │                                 │  │
├──────────────────────────────┤  └─────────────────────────────────┘  │
│  CONTROLS (60.2%w, 23.5%h)  ├───────────────────────────────────────┤
│  [00:00 ══════════ 00:00]   │  PLAYLIST BTNS (37.5%w, 21.3%h)      │
│  Mode[▶▶🔁🔀]              │  ✨Recommend│📺Subs│❤Liked           │
│     ⏮ ▶ ⏹ ⏭   🔊═══      │  📄File│📁Folder│▶Play Selected      │
│  🎶 Now Playing...          │  [◀ Prev] [Next ▶] [📄 page]        │
│  ⚙️settings ℹ️sel 📊play ⛶ │                                       │
└──────────────────────────────┴───────────────────────────────────────┘
```

### After (New Layout)
```
┌──────────────────────────────────────────────────────────────────────┐
│ HEADER BAR (6.3% height — more compact)                             │
│ 🎵 JaTubePlayer 🔍[Search YouTube...][🔎] 📁[▼ Playlist][▶Enter]  │
│                                       [     Wider Status Panel     ]│
├────────────────────────────────┬─────────────────────────────────────┤
│  VIDEO CONTAINER (60.7%w)      │  RIGHT PANEL (37.7%w, 49%h)        │
│  ┌──────────────────────────┐  │  ┌───────────────────────────────┐  │
│  │      Frame_for_mpv       │  │  │📋 Mode (compact header)       │  │
│  │    (blue accent border)  │  │  ├───────────────────────────────┤  │
│  │                          │  │  │                               │  │
│  │                          │  │  │ Playlist Treeview (83.8% h)   │  │
│  │                          │  │  │   (more rows visible)         │  │
│  └──────────────────────────┘  │  │                               │  │
│                                │  └───────────────────────────────┘  │
│                                ├─────────────────────────────────────┤
│                                │ PLAYLIST BTNS (37.7%w, 16.2%h)     │
│                                │ [▶▶▶▶  Play Selected  ▶▶▶▶]       │
│                                │ ✨Rec│📺Sub│❤Like│📄File│📁Folder  │
│                                │ [◀ Prev] [Next ▶]  📄 page        │
├────────────────────────────────┴─────────────────────────────────────┤
│ TRANSPORT BAR ═══════════════════════════════════ (99%w, 26%h)      │
│ 🎶 Now Playing: Song Title Here...                                  │
│ 00:00 ════════════════════════════════════════════════════════ 03:45 │
│ ─────────────────────────────────────────────────────────────────── │
│ [Mode     ] [   ⏮    ▶    ⏹    ⏭   ] 🔊══════ ⚙️Settings ℹ️📊 ⛶│
│ [▶▶🔁🔀 ] [  pill-shaped controls  ] volume    action buttons      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Changes

### 1. Header Bar

| Property | Before | After |
|----------|--------|-------|
| Height | 7.35% (50px) | 6.3% (43px) |
| Search label | `🔍 Search:` | `🔍` (icon only) |
| Playlist label | `📁 Playlist:` | `📁` (icon only) |
| Search placeholder | `"Search..."` | `"Search YouTube..."` |
| Search entry width | `relwidth=0.197` | `relwidth=0.215` |
| Status panel width | `relwidth=0.256` | `relwidth=0.328` (wider) |
| Status panel start | `relx=0.738` | `relx=0.665` (shifted left) |

**Why:** Removing text labels saves ~100px of horizontal space, allowing the search field, playlist combo, and status panel to breathe. The status panel is wider to better display Google account info.

### 2. Status Panel

| Property | Before | After |
|----------|--------|-------|
| Width | 25.6% of header | 32.8% of header |
| Position | `relx=0.738` | `relx=0.665` |
| Height | 80% of header | 82% of header |

Internal widgets (Chrome dot, Discord dot, Google profile, separators) keep their relative positions — the wider panel gives them more room.

### 3. Right Panel (Playlist)

| Property | Before | After |
|----------|--------|-------|
| Position | `relx=0.617, rely=0.081` | `relx=0.618, rely=0.070` |
| Height | 68.4% of window | 49.0% of window |
| Mode header height | 12.9% of panel | 10.5% of panel |
| Mode icon size | 20pt font | 18pt font |
| Treeview start | `rely=0.161` | `rely=0.125` |
| Treeview height | 79.6% of panel | 83.8% of panel |
| Scrollbar positions | Match old treeview | Match new treeview |

**Why:** The panel is shorter because the controls frame now takes the full bottom width. But the treeview gets a LARGER proportion (83.8% vs 79.6%) because the mode header is more compact. More playlist items are visible.

### 4. Playlist Buttons

This section was **completely reorganized**:

| Aspect | Before | After |
|--------|--------|-------|
| Position | `relx=0.617, rely=0.765` | `relx=0.618, rely=0.566` |
| Height | 21.3% of window (145px) | 16.2% of window (110px) |
| Layout | 3 rows × 3 columns | Hero button + 5-column source row + nav |
| "Play Selected" | Bottom-right, 30% width | **Full-width hero button** at top |
| Source buttons | 2 rows of 3 (Rec/Sub/Like + File/Folder) | **Single row of 5** compact buttons |
| Button radius | `corner_radius=8` | `corner_radius=6` for source buttons |
| Button font | `('Segoe UI', 13)` | `('Segoe UI', 11)` for source buttons |
| Button labels | `✨ Recommend`, `📺 Subscriptions`, `❤️Liked` | `✨ Rec`, `📺 Sub`, `❤ Like` (shorter) |

**New structure:**
```
Row 1: [▶▶▶▶▶▶▶▶  Play Selected  ▶▶▶▶▶▶▶▶]  (full width, prominent blue)
Row 2: [✨Rec] [📺Sub] [❤Like] [📄File] [📁Folder]  (5 equal compact buttons)
Row 3: [◀ Prev] [Next ▶]  📄 page  (page navigation)
```

**Why:** "Play Selected" is the primary action — it deserves to be the most prominent element. The 5 source buttons fit in one row (using shorter labels) which eliminates a whole row of buttons.

### 5. Video Container

| Property | Before | After |
|----------|--------|-------|
| Position | `relx=0.008, rely=0.081` | `relx=0.005, rely=0.070` |
| Size | `relw=0.602, relh=0.669` | `relw=0.607, relh=0.655` |
| Border color | `#333333` | **`#3e62dc`** (blue accent) |
| Frame_for_mpv position | `relx=0.015, rely=0.096` | `relx=0.011, rely=0.084` |
| Frame_for_mpv size | `relw=0.587, relh=0.640` | `relw=0.595, relh=0.634` |

**Why:** The blue accent border makes the video area pop and creates a visual anchor. Slightly wider aspect ratio for the video.

### 6. Transport Bar (Controls)

This is the **biggest structural change** — the controls frame now spans the full window width.

| Property | Before | After |
|----------|--------|-------|
| Width | 60.2% of window | **99.0% of window** |
| Height | 23.5% (160px) | 26.0% (177px) |
| Position | `relx=0.008, rely=0.757` | `relx=0.005, rely=0.734` |
| Background | `#1a1a1a` | `#141414` (slightly darker) |
| Border | `#333333` | `#2a2a2a` (subtle dark border) |
| Internal layout | Mixed stacked/overlapping | **3 horizontal rows** |

#### Internal Structure — 3 Rows:

**Row 1: Now Playing Strip** (top 24%)
- Full-width `#1c1c1c` frame with `corner_radius=8`
- 🎶 icon + song title text spanning the entire bar width
- `width=130` characters (was `width=40`) — fills the wide bar
- Background matches frame: `bg='#1c1c1c'` (was `#252525`)

**Row 2: Progress Bar** (next 23%)
- Full-width slider spanning `relwidth=0.890` (was `0.784`)
- Time labels use `relwidth=0.050` (was `0.092`) — proportionally smaller in the wider bar

**Row 3: Transport Controls** (bottom 42%, below divider)

Organized as 4 side-by-side sections:

| Section | relx | relwidth | Content |
|---------|------|----------|---------|
| Mode | 0.008 | 0.132 | Mode label + ▶▶/🔁/🔀 radio buttons |
| Playback | 0.150 | 0.320 | ⏮ ▶ ⏹ ⏭ in pill-shaped container |
| Volume | 0.485 | 0.195 | 🔊 icon + volume slider |
| Actions | 0.695 | 0.300 | Settings, Sel info, Now info, Fullscreen |

#### Playback Pill Design
```
┌─────────────────────────────────────────────────┐
│  ⏮   │   ▶   │   ⏹   │   ⏭   │  Loading...  │
│ ghost │ BLUE  │ ghost │ ghost │              │
│       │ accent│       │       │              │
└─────────────────────────────────────────────────┘
corner_radius=20 (pill shape)
```

- **Play/Pause** (`pausebutton`): `fg_color='#3e62dc'` — the only colored button, immediately identifiable
- **Prev/Stop/Next**: `fg_color='transparent'` with `hover_color='#333333'` — ghost buttons that appear on hover
- **Font size**: 17pt (was 15pt) — larger touch targets in the wider transport bar
- **Container**: `fg_color='#1c1c1c'`, `corner_radius=20` — distinctive pill shape

#### Transport Divider
A new thin `CTkFrame` element:
```python
_transport_divider = ctk.CTkFrame(controls_frame, fg_color='#2a2a2a', height=1)
```
Placed at `rely=0.530` — visually separates the progress area from the transport controls row.

#### Action Buttons (New Layout)
| Button | Before | After |
|--------|--------|-------|
| Settings | `⚙️ settings`, 77.8% width, 46.7% height | `⚙️ Settings`, 44.5% width, 88% height |
| Sel Info | `ℹ️selected info`, 38% width | `ℹ️ Sel`, 17.5% width |
| Playing Info | `📊 playing info`, 37% width | `📊 Now`, 17.5% width |
| Fullscreen | `⛶`, 14.8% width | `⛶`, 15% width, 16pt font |

All action buttons now sit in a **single horizontal row** (was 2-row grid) and are the same height (`relheight=0.88`).

### 7. Fullscreen Mode

#### Normal → Zoomed Transition
All `place_configure` calls in `fullscreen_widget_change()` were updated to match the new normal-mode coordinates. The zoomed-mode layout is unchanged except:
- `_transport_divider.place_forget()` added — hides the divider in fullscreen since the compact controls bar doesn't need it

#### Zoomed mode behavior (unchanged):
- Header, right panel, playlist buttons, video container, action buttons, now playing all hidden
- Frame_for_mpv fills 93% of screen
- Controls bar shows as a compact 7.3% strip at the bottom
- Hover-fullscreen logic works identically

---

## New Visual Elements

| Element | Type | Purpose |
|---------|------|---------|
| `_transport_divider` | `CTkFrame` | Thin `#2a2a2a` line separating progress from transport controls |
| `_src_w`, `_src_gap` | Variables | Reusable width/gap values for 5-column source button layout |

---

## Widget Position Map

### Normal Mode (1320×680)

```
HEADER:          relx=0,     rely=0,     relw=1.000, relh=0.063
VIDEO:           relx=0.005, rely=0.070, relw=0.607, relh=0.655
  Frame_for_mpv: relx=0.011, rely=0.084, relw=0.595, relh=0.634
RIGHT PANEL:     relx=0.618, rely=0.070, relw=0.377, relh=0.490
  Mode header:   relx=0.020, rely=0.010, relw=0.960, relh=0.105
  Playlist tree: relx=0.020, rely=0.125, relw=0.925, relh=0.838
PLAYLIST BTNS:   relx=0.618, rely=0.566, relw=0.377, relh=0.162
  Play Selected: relx=0.020, rely=0.036, relw=0.960, relh=0.245
  Source row:    relx=0.020, rely=0.318, relw=5×0.183
  Page nav:      relx=0.020, rely=0.573, relw=0.960, relh=0.391
TRANSPORT BAR:   relx=0.005, rely=0.734, relw=0.990, relh=0.260
  Now Playing:   relx=0.008, rely=0.022, relw=0.984, relh=0.240
  Progress:      relx=0.008, rely=0.285, relw=0.984, relh=0.230
  Divider:       relx=0.015, rely=0.530, relw=0.970, relh=0.006
  Mode:          relx=0.008, rely=0.555, relw=0.132, relh=0.415
  Playback:      relx=0.150, rely=0.555, relw=0.320, relh=0.415
  Volume:        relx=0.485, rely=0.575, relw=0.195, relh=0.380
  Actions:       relx=0.695, rely=0.555, relw=0.300, relh=0.415
```

---

## Color & Style Changes

| Element | Before | After |
|---------|--------|-------|
| Video border | `#333333` | `#3e62dc` (blue accent) |
| Controls bg | `#1a1a1a` | `#141414` (darker) |
| Controls border | `#333333` | `#2a2a2a` (subtler) |
| Now Playing bg | `#252525` | `#1c1c1c` (darker inset) |
| Mode frame bg | `#252525` | `#1c1c1c` (matches now playing) |
| Playback frame bg | transparent | `#1c1c1c` with `corner_radius=20` (pill) |
| Prev/Stop/Next bg | `#2E2E2E` | `transparent` (ghost buttons) |
| Prev/Stop/Next hover | `#404040` | `#333333` (subtler hover) |
| Playback font | 15pt | 17pt (larger) |
| Settings label | `⚙️ settings` | `⚙️ Settings` (capitalized) |
| Sel info label | `ℹ️selected info` | `ℹ️ Sel` (compact) |
| Playing info label | `📊 playing info` | `📊 Now` (compact) |
| Fullscreen font | 15pt | 16pt |
| Source btn radius | 8 | 6 (tighter) |
| Source btn font | 13pt | 11pt (compact) |
| Divider line | _(none)_ | `#2a2a2a` at 0.6% height |

---

## What Was NOT Changed

The following are **completely preserved**:

- **All function callbacks** — `youtube_search`, `enterplaylist`, `download_and_play`, `get_selected_vid`, `page_control`, `scale_click`, `scale_release`, `pause`, `stop_playing_video`, `playprevsong`, `playnextsong`, `set_volume`, `set_volume_wheel`, `setting_frame`, `vid_info_frame`, `fullscreen_change_state`, `load_local_files`, `init_get_recommendation`, `get_sub_channel`, `get_liked_vid`
- **All variable references** — `pos_for_label`, `pauseStr`, `player_mode_selector`, `user_playlists_name`, `playing_vid_mode`
- **All widget variable names** — `playlisttreebox`, `modetextbox`, `playing_title_textbox`, `player_position_scale`, `player_volume_scale`, `searchentry`, `userplaylistcombobox`, every button/label/frame name
- **All event bindings** — `<Return>`, `<Double-1>`, `<ButtonRelease-1>`, `<MouseWheel>`, `<Escape>`, `<space>`, `<KeyPress-Left/Right>`, `<KeyRelease-Left/Right>`, `<Button-1>`
- **Fullscreen zoomed mode layout** — Only addition is `_transport_divider.place_forget()`
- **Hover fullscreen behavior** — `full_screen_contorl_hover_thread` works identically
- **Threading logic** — All `root.after()` calls, daemon threads, UI queue processing
- **Treeview styling** — `sv_ttk.use_dark_theme()`, `ttk.Style()` configuration
- **Status functions** — `chrome_ext_status_run/close`, `discord_status_run/close`, `google_status_update`
- **Window properties** — Size (`1320x680`), title format, icon, `WM_DELETE_WINDOW` protocol
