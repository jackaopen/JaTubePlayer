# Settings UI Redesign — Detailed Documentation

> **Date:** February 25, 2026  
> **Scope:** Full visual overhaul of all 7 tabs in the `setting_frame()` function  
> **File Modified:** `JaTubePlayer.py` — function `setting_frame()` (lines ~559–2134)  
> **Logic Changed:** None — all function callbacks, variable bindings, and control flow are preserved identically

---

## Table of Contents

1. [Design Language](#design-language)
2. [Color System](#color-system)
3. [Tab-by-Tab Breakdown](#tab-by-tab-breakdown)
   - [Advanced Player Setting](#1-advanced-player-setting)
   - [Personal Playlist](#2-personal-playlist)
   - [Download](#3-download)
   - [Quick Init](#4-quick-init)
   - [Account & Authentication](#5-account--authentication)
   - [Version Info](#6-version-info)
   - [Hotkeys](#7-hotkeys)
4. [Widget Style Reference](#widget-style-reference)
5. [Layout Spacing Reference](#layout-spacing-reference)
6. [What Was NOT Changed](#what-was-not-changed)

---

## Design Language

Every tab now follows a **card-based layout** with these consistent principles:

| Element | Style |
|---------|-------|
| **Card frames** | `fg_color='#2B2B2B'`, `corner_radius=8` |
| **Card headers** | `▸` prefix, `font=('Arial', 13, 'bold')`, unique accent color per section |
| **Labels** | `text_color='#B0B0B0'`, `font=('Arial', 11)` — soft gray for readability |
| **Checkboxes** | `fg_color='#3A3A3A'`, `hover_color='#505050'`, `text_color='#C8C8C8'` |
| **Buttons (neutral)** | `fg_color='#3A3A3A'`, `hover_color='#505050'`, `font=('Arial', 12, 'bold')` |
| **Buttons (action/green)** | `fg_color='#2E7D32'`, `hover_color='#388E3C'` — login, update, download |
| **Buttons (danger/red)** | `fg_color='#8B0000'`, `hover_color='#A52A2A'` — delete, remove, reset |
| **Text inputs / displays** | `fg_color='#1a1a1a'`, `text_color='#C8C8C8'`, `corner_radius=6` |
| **Combo boxes** | `dropdown_fg_color='#333333'`, `button_color='#444444'` |

### Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| Frame backgrounds | Flat `#2E2E2E`, no radius | `#2B2B2B` with `corner_radius=8` |
| Section headers | Plain white `14pt bold` | Accent-colored `13pt bold` with `▸` prefix |
| Section dividers | ASCII `───` lines inline | Separate card frames with visual separation |
| Checkboxes | `fg_color='#242424'` (nearly invisible) | `#3A3A3A` with `#505050` hover |
| Buttons | Default CTk styling, no hover feedback | Explicit neutral/green/red color coding |
| Text displays | `fg_color='#242424'` blending with background | `#1a1a1a` dark inset with `corner_radius=6` |
| Layout padding | Inconsistent `padx=10`/`padx=20` mix | Uniform `padx=16` for frames, `padx=(24,8)` for content |

---

## Color System

Each card section has a unique accent color for its header label. This creates visual hierarchy and helps users quickly identify sections when scrolling.

### Per-Tab Accent Colors

#### Advanced Player Setting
| Section | Accent Color | Hex |
|---------|-------------|-----|
| General | Blue | `#7EB8E0` |
| Speed & Subtitle | Green | `#7EE0A8` |
| Cache & Buffer | Amber | `#E0C48C` |
| Interface | Purple | `#C0A0E0` |
| Advanced | Red | `#E08080` |
| External Services | Cyan | `#80C0E0` |

#### Personal Playlist
| Section | Accent Color | Hex |
|---------|-------------|-----|
| YouTube Data | Rose | `#FF6B8A` |
| History | Teal | `#7EDAE0` |

#### Download
| Section | Accent Color | Hex |
|---------|-------------|-----|
| Selected Video | Coral | `#E0A07E` |
| Format | Lavender | `#D4A0E0` |
| Resolution | Sky Blue | `#80C8E0` |

#### Quick Init
| Section | Accent Color | Hex |
|---------|-------------|-----|
| Quick Startup (header) | Lime | `#90D080` |
| Search | Amber | `#E0C48C` |
| Playlist | Sky Blue | `#80C8E0` |
| Local Folder | Purple | `#C0A0E0` |
| Recommendation | Red | `#E08080` |

#### Account & Authentication
| Section | Accent Color | Hex |
|---------|-------------|-----|
| Google Account | Orange | `#FFB347` |
| API Key | Blue | `#7EB8E0` |
| Cookie | Green | `#7EE0A8` |
| Client Secrets | Purple | `#C0A0E0` |

#### Version Info
| Section | Accent Color | Hex |
|---------|-------------|-----|
| YT-DLP | Green | `#7EE0A8` |
| JaTubePlayer | Blue | `#7EB8E0` |
| Version numbers (current) | Green | `#7EE0A8` |
| Version numbers (latest) | Cyan | `#80C8E0` |

#### Hotkeys
| Section | Accent Color | Hex |
|---------|-------------|-----|
| Set Hotkey | Amber | `#E0C48C` |
| Playback | Rose | `#FF6B8A` |
| Playback Mode | Green | `#7EE0A8` |
| Volume | Sky Blue | `#80C8E0` |
| Player | Purple | `#C0A0E0` |

---

## Tab-by-Tab Breakdown

### 1. Advanced Player Setting

**6 card-style sections** inside a `CTkScrollableFrame`:

- **General** — Max resolution combo, auto-retry checkbox, audio-only checkbox, hover fullscreen checkbox
- **Speed & Subtitle** — Playback speed slider (green-themed: `progress_color='#4A9E6E'`, `button_color='#7EE0A8'`), subtitle combo box
- **Cache & Buffer** — 5 amber-themed sliders: cache duration, max buffer size, max back buffer, read-ahead duration, audio wait open. All sliders share `_slider_kw` dict for consistency (`progress_color='#8E7A4A'`, `button_color='#E0C48C'`)
- **Interface** — Acrylic blur checkbox, auto-fullscreen checkbox
- **Advanced** — MPV log button, drag-and-drop checkbox, force stop button, show cache checkbox
- **External Services** — Chrome extension switch, Discord presence switch, show-playing checkbox

**Slider value labels** use the same accent color as the slider (`#7EE0A8` for speed, `#E0C48C` for cache) and bold font for easy reading.

### 2. Personal Playlist

**2 card sections:**

- **YouTube Data** (`#FF6B8A` rose header)
  - Update Liked Videos button + auto-update checkbox
  - Update Subscriptions button + auto-update checkbox
  - Update Playlists button
- **History** (`#7EDAE0` teal header)
  - Record history checkbox
  - Reset History button

### 3. Download

**3 card sections + action area:**

- **Selected Video** (`#E0A07E` coral) — Video title display in dark inset textbox
- **Format** (`#D4A0E0` lavender) — MP3/MP4 radio buttons side by side
- **Resolution** (`#80C8E0` sky blue) — Resolution combo + "Get Available" button
- **Action area** — Large green "Download Selected Video" button (`fg_color='#2E7D32'`, `corner_radius=8`), status label in `#80C8E0`

Format and Resolution cards sit **side by side** (`column=0` / `column=1`) with `sticky="nsew"` for equal height.

### 4. Quick Init

**5 card sections in a 2-column grid:**

- **Quick Startup** (full width, row 0) — Enable toggle checkbox + current mode display textbox
- **Search** (left column, row 1) — Radio button + entry field + set button
- **Playlist** (right column, row 1) — Radio button + combobox + get/set buttons
- **Local Folder** (left column, row 2) — Radio button + select folder button
- **Recommendation** (right column, row 2) — Radio button

Side-by-side cards use `padx=(16, 4)` left / `padx=(4, 16)` right for symmetric gutters.

### 5. Account & Authentication

**4 card sections** inside a `CTkScrollableFrame`:

- **Google Account** (`#FFB347` orange) — Combined title with "API & Client Secret required" note, account name display, Login (green) / Logout (neutral) / Delete System Key (red) buttons
- **API Key** (`#7EB8E0` blue) — API label + entry + current value display, Set API (neutral) + Delete Stored API (red) buttons
- **Cookie** (`#7EE0A8` green) — Cookie path display, Select Cookie (neutral) + Remove Cookie (red) buttons
- **Client Secrets** (`#C0A0E0` purple) — Path display, Select (neutral) + Remove (red) buttons

**Button color coding:**
- Green (`#2E7D32`) = positive action (Login)
- Neutral (`#3A3A3A`) = standard action (Set, Select)
- Red (`#8B0000`) = destructive action (Delete, Remove)

### 6. Version Info

**2 card sections + checkbox:**

- **YT-DLP** (`#7EE0A8` green header)
  - Sub-frames with `fg_color='#1a1a1a'`, `corner_radius=6` for current/latest versions
  - Current version in green, latest in cyan
  - Update button (green) + Visit Website button (neutral)
- **JaTubePlayer** (`#7EB8E0` blue header)
  - Same sub-frame structure
  - Visit Website button
- **Auto-check** checkbox below both cards

### 7. Hotkeys

**5 card sections** inside a `CTkScrollableFrame`:

- **Set Hotkey** (`#E0C48C` amber) — Function combobox (with styled dropdown) + Set Hotkey button + "Reset All to Default" (red) button
- **Playback** (`#FF6B8A` rose) — Play/Pause, Stop, Next, Previous — each with label + display textbox
- **Playback Mode** (`#7EE0A8` green) — Repeat, Random, Continuous
- **Volume** (`#80C8E0` sky blue) — Volume Up, Volume Down
- **Player** (`#C0A0E0` purple) — Toggle Minimize

All hotkey display textboxes share `_hk_textbox_kw` dict: `fg_color='#1a1a1a'`, `text_color='#C8C8C8'`, `corner_radius=6`, `state='disabled'`.

Label column has `minsize=160` for alignment consistency across all hotkey cards.

---

## Widget Style Reference

### Shared Keyword Dictionaries

```python
# Cache slider styling (Advanced Player → Cache & Buffer)
_slider_kw = dict(
    progress_color='#8E7A4A',
    button_color='#E0C48C',
    button_hover_color='#F0D8A0'
)

# Hotkey card frames
_hk_card_kw = dict(fg_color='#2B2B2B', corner_radius=8)

# Hotkey display textboxes
_hk_textbox_kw = dict(
    font=('Arial', 11), width=200, height=1,
    state='disabled', fg_color='#1a1a1a',
    text_color='#C8C8C8', corner_radius=6
)
```

### Button Categories

| Category | `fg_color` | `hover_color` | Usage |
|----------|-----------|--------------|-------|
| Neutral | `#3A3A3A` | `#505050` | Standard actions, settings |
| Positive | `#2E7D32` | `#388E3C` | Login, Update, Download |
| Destructive | `#8B0000` | `#A52A2A` | Delete, Remove, Reset to Default |

---

## Layout Spacing Reference

All tabs follow this consistent spacing system:

| Element | Padding |
|---------|---------|
| Card frame to tab edge | `padx=16` |
| First card top margin | `pady=(10, 4)` |
| Between cards | `pady=4` |
| Last card bottom margin | `pady=(4, 10)` |
| Header inside card | `padx=8, pady=(10, 6)` |
| Labels (left column) | `padx=(24, 8)` |
| Controls (right column) | `padx=8` or `padx=(8, 24)` |
| Last row in card bottom | `pady=(5, 12)` or `pady=(4, 12)` |
| Side-by-side cards (left) | `padx=(16, 4)` |
| Side-by-side cards (right) | `padx=(4, 16)` |

---

## What Was NOT Changed

The following remain **completely untouched**:

- **All function definitions** — Every callback (`switch_blur_window`, `switch_audio_only`, `max_resolution_select`, `enter_youtube_api`, `google_login_setting`, etc.) is unchanged
- **All variable bindings** — `tkinter.IntVar`, `tkinter.StringVar`, `tkinter.BooleanVar` references preserved
- **All threading logic** — Background threads for network operations, version checking, listener loops
- **Configuration save/load** — `CONFIG` dict writes and `save_config()` calls
- **Tab creation order** — Same 7 tabs in same order
- **Widget variable names** — All widget variables (`subtitlecombobox`, `maxresolutioncombobox`, `apilabel`, etc.) keep their original names
- **Event bindings** — `<ButtonRelease-1>` on sliders, combobox callbacks
- **Window properties** — Size (`720x500`), title, resizable settings, blur integration
- **Main UI outside settings** — Everything outside `setting_frame()` is untouched
- **Functional flow** — `setting_frame_listener()`, `init_quickstart_data()`, `get_version_setting_thread()`, `get_hotkey_setting_thread()` — all run identically
