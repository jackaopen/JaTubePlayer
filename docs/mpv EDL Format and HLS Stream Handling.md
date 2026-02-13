

# Technical Documentation: mpv EDL Format and HLS Stream Handling

## Based on Official mpv Documentation and Source Code Analysis


**Primary Sources:**

* [mpv EDL Documentation](https://github.com/mpv-player/mpv/blob/master/DOCS/edl-mpv.rst)
* User Debugging Logs (mpv 0.39.0+)

---

## Table of Contents

1. [What is EDL](https://www.google.com/search?q=%231-what-is-edl)
2. [Audio Track Handling: The "Unified Cache" Architecture](https://www.google.com/search?q=%232-audio-track-handling)
3. [M3U8 Duration Detection: The "Virtual Timeline" Constraint](https://www.google.com/search?q=%233-m3u8-duration-detection)
4. [Implementation Details: Syntax, Escaping, and Pitfalls](https://www.google.com/search?q=%234-implementation-details-syntax-escaping-and-pitfalls)

---

## 1. What is EDL?

### Definition

**EDL (Edit Decision List)** in `mpv` is a **virtual file format** that defines a timeline. It allows you to stitch together multiple media sources (local files, HTTP streams, HLS manifests) into a single, continuous, or parallel playback experience.

### Key Syntax

The file **must** avoid BOM (Byte Order Mark) and use Unix line breaks. The fundamental structure for a segment is:

`filename,start_time,length`

**Sequential (Timeline - Default):**
Plays `file1` then `file2`.

```text
# mpv EDL v0
file1.mkv
file2.mkv

```

**Parallel (Multiplexing - The Fix for Youtube):**
Plays `video` and `audio` simultaneously.

```text
# mpv EDL v0
!new_stream
video_url
!new_stream
audio_url

```

---

## 2. Audio Track Handling: The "Unified Cache" Architecture

### The Problem

When you use the command line:

```bash
mpv --audio-file=audio.m3u8 video.m3u8

```

Users often experience **desynchronization**, **buffering loops**, or **lag**.

### The Root Cause: Split Demuxers

When using `--audio-file`, `mpv` spawns **two completely independent demuxers** (data readers).

1. **Video Demuxer:** Has its own buffer/cache (e.g., 100MB).
2. **Audio Demuxer:** Has its own buffer/cache (e.g., 100MB).

**The Failure State:** If the video stream encounters a network hiccup, the video demuxer pauses to buffer. However, the audio demuxer *doesn't know this*, so it keeps downloading. Eventually, the two streams drift apart in time. `mpv` tries to resync them by skipping frames or pausing, causing "lag."

### The Solution: EDL "Unified Cache"

When you use an EDL with `!new_stream`:

```text
# mpv EDL v0
!new_stream
video.m3u8
!new_stream
audio.m3u8

```

**Why it works (Official Confirmation):**
According to `mpv` documentation: *"This will use a **unified cache** for all streams."*

The EDL parser creates a **Single Virtual Demuxer**. This demuxer manages the download state of *both* the video and audio URLs simultaneously. If one stalls, the entire virtual demuxer stalls, keeping them perfectly locked in sync.

---

## 3. M3U8 Duration Detection: The "Virtual Timeline" Constraint

### The Problem

**Direct URL:**

```bash
mpv https://example.com/stream.m3u8
# Result: Duration: 00:00 / ??:?? (Seeking Broken)

```

**EDL Wrapped:**

```text
# mpv EDL v0
!new_stream
https://example.com/stream.m3u8,0,196.5

```

```bash
mpv stream.edl
# Result: Duration: 03:16 (Seeking Works)

```

### Deep Search: Why Does This Happen?

Based on the architecture of `mpv` and `libavformat` (FFmpeg), we can define three technical reasons why EDL fixes duration detection.

#### Reason 1: The "Lazy" vs. "Eager" Probing

* **Direct URL (Lazy):** When `mpv` opens a URL directly, it prioritizes **Time-to-First-Frame**. It grabs the HLS manifest, finds the *current* live segment, and starts playing immediately. It does *not* read the entire playlist to calculate the total length because that takes time (and bandwidth). It assumes the stream is "Live" (infinite).
* **EDL (Eager):** An EDL is a "Decision List." To construct the virtual timeline, `mpv` **MUST** know where the clip starts and ends. You cannot place a clip of "infinite length" onto a specific point in a timeline. Therefore, the EDL parser forces the underlying demuxer to **fully parse the HLS playlist** (summing up all `#EXTINF` tags) to calculate a concrete duration *before* playback begins.

#### Reason 2: The "Virtual Container" Abstraction

When playing a URL directly, `mpv` interacts with the **Network Stream** directly.
When playing an EDL, `mpv` interacts with a **Virtual File**.

* For a Network Stream, `mpv` expects the duration to change (dynamic).
* For a Virtual File, `mpv` expects the duration to be fixed (static).

By wrapping the URL in EDL, you force `mpv` to treat the HLS manifest as a **Static File** (VOD) rather than a dynamic Live Stream. This enables the seek bar because `mpv` now believes it is playing a local file with a fixed end point.

---

## 4. Implementation Details: Syntax, Escaping, and Pitfalls

This section covers the critical syntax rules discovered during debugging (Feb 2026).

### A. URL Escaping vs. Playback Duration

There is a critical distinction between the `%length%` syntax and the `length` parameter.

| Feature | Syntax | Purpose | Example |
| --- | --- | --- | --- |
| **String Escaping** | `%N%url` | Tells mpv the URL string is `N` bytes long. Prevents parsing errors if URL contains `;` or `,`. | `%24%https://site.com/vid.mp4` |
| **Playback Duration** | `,start,N` | Tells mpv the video lasts `N` seconds. Controls the seek bar. | `https://site.com/vid.mp4,0,3600` |

**Fatal Error to Avoid:**
Do NOT put the duration in the percentage wrapper (e.g., `%3600%url`). This tells `mpv` to read 3600 bytes of characters as the filename, causing it to swallow the rest of the EDL file and crash with `No file found`.

### B. Correct Parameter Placement

The duration MUST be placed as the **3rd positional argument** after the filename/URL.

**Correct Syntax:**

```text
!new_stream;%len(url)%url,start_offset,duration_in_seconds

```

**Example (Python):**

```python
# Video is 196.5 seconds long
edl_line = f"!new_stream;%{len(url)}%{url},0,196.5"

```

### C. The `!delay_open` Trap

**Recommendation:** Do **NOT** use `!delay_open` for simple HLS streams.

* **Behavior:** This directive is an optimization for large playlists.
* **The Bug:** It is extremely strict about syntax. If the `media_type` is not declared perfectly, or if `mpv` gets confused by the HLS manifest headers, it throws: `Invalid or missing !delay_open media type`.
* **Fix:** Remove it. The stream loads fine without it, and the error disappears.

