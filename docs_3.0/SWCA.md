
# SetWindowCompositionAttribute — Unofficial Documentation
> All reverse engineered
## WINDOWCOMPOSITIONATTRIB Enum

| Value | Name |
|---|---|
| 0 | WCA_UNDEFINED |
| 1 | WCA_NCRENDERING_ENABLED |
| 2 | WCA_NCRENDERING_POLICY |
| 3 | WCA_TRANSITIONS_FORCEDISABLED |
| 4 | WCA_ALLOW_NCPAINT |
| 5 | WCA_CAPTION_BUTTON_BOUNDS |
| 6 | WCA_NONCLIENT_RTL_LAYOUT |
| 7 | WCA_FORCE_ICONIC_REPRESENTATION |
| 8 | WCA_EXTENDED_FRAME_BOUNDS |
| 9 | WCA_HAS_ICONIC_BITMAP |
| 10 | WCA_THEME_ATTRIBUTES |
| 11 | WCA_NCRENDERING_EXILED |
| 12 | WCA_NCADORNMENTINFO |
| 13 | WCA_EXCLUDED_FROM_LIVEPREVIEW |
| 14 | WCA_VIDEO_OVERLAY_ACTIVE |
| 15 | WCA_FORCE_ACTIVEWINDOW_APPEARANCE |
| 16 | WCA_DISALLOW_PEEK |
| 17 | WCA_CLOAK |
| 18 | WCA_CLOAKED |
| 19 | WCA_ACCENT_POLICY |
| 20 | WCA_FREEZE_REPRESENTATION |
| 21 | WCA_EVER_UNCLOAKED |
| 22 | WCA_VISUAL_OWNER |
| 23 | WCA_HOLOGRAPHIC |
| 24 | WCA_EXCLUDED_FROM_DDA |
| 25 | WCA_PASSIVEUPDATEMODE |
| 26 | WCA_USEDARKMODECOLORS |
| 27 | WCA_LAST |

---

## WCA_ACCENT_POLICY (19)

Passes a pointer to an `ACCENT_POLICY` struct.

### ACCENT_POLICY Fields


| Field | Type | Description |
|---|---|---|
| `AccentState` | `c_uint` | Effect type — see table below |
| `AccentFlags` | `c_uint` | Bitflags modifying the effect |
| `GradientColor` | `c_uint` | Tint color in `0xAABBGGRR` format |
| `AnimationId` | `c_uint` | Always `0`, presumably reserved |

### AccentState Values

| Value | Name | Description |
|---|---|---|
| 0 | `ACCENT_DISABLED` | No effect, normal window |
| 1 | `ACCENT_ENABLE_GRADIENT` | Solid `GradientColor` fill |
| 2 | `ACCENT_ENABLE_TRANSPARENTGRADIENT` | Transparent tinted fill |
| 3 | `ACCENT_ENABLE_BLURBEHIND` | Legacy blur (all Win10) |
| 4 | `ACCENT_ENABLE_ACRYLICBLURBEHIND` | Acrylic (Win10 1803+ / Win11) |
| 5 | `ACCENT_ENABLE_HOSTBACKDROP` | Host-driven backdrop (Win11 only) |

### AccentFlags Bitmask

| Value | Description |
|---|---|
| `0x0` | No border, plain effect |
| `0x2` | Luminosity border glow around window edges |
| `0x20` | Full-surface tint (used by taskbar) |

> Combine with OR: `0x2 \| 0x20`

### GradientColor Format — `0xAABBGGRR`

| Byte | Channel | Notes |
|---|---|---|
| `AA` | Alpha | Tint strength. `0x00` = pure blur, `0xFF` = fully opaque |
| `BB` | Blue | |
| `GG` | Green | |
| `RR` | Red | |

| Alpha | Opacity |
|---|---|
| `0x00` | 0% — pure blur, no tint |
| `0x40` | 25% |
| `0x80` | 50% |
| `0xCC` | 80% |
| `0xFF` | 100% — solid, blur not visible |

---

## WCA_USEDARKMODECOLORS (26)

Passes a single `BOOL` (`c_uint`).

| Value | Effect |
|---|---|
| `0` | Light mode NC area |
| `1` | Dark mode NC area (caption buttons, border) |

> **Note:** Has no effect if the native frame is removed (`overrideredirect(True)`).  
> Prefer `DWMWA_USE_IMMERSIVE_DARK_MODE` (attr `20`) via `DwmSetWindowAttribute` on Win11.