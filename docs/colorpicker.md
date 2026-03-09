# CTk Color Picker — Code Explanation

## Overview
A `customtkinter` popup dialog (`AskColor`) that lets the user pick a color from a wheel, adjust brightness, adjust alpha, and return the result as an `#rrggbbaa` hex string.

---

## Original Code

### `__init__`
Sets up the window, loads the color wheel and target images, and builds three UI sections:
- **Canvas** — displays the color wheel image; binds `<B1-Motion>` for drag-to-pick.
- **Brightness slider** — `CTkSlider` (0–255) wired to `update_colors()`.
- **Preview label** — `CTkLabel` showing the current color as background + hex text.
- **Alpha slider** — existed in the original recontribution but had **no `command`**, so it did nothing.

### `on_mouse_drag(event)`
Called on every mouse drag over the canvas. Redraws the wheel, clamps the target cursor to the circle boundary, then calls `get_target_color()` + `update_colors()`.

### `get_target_color()`
Reads the pixel color from the wheel image at the cursor position and stores it in `self.rgb_color`.

### `update_colors()` *(original)*
Applied brightness scaling to `self.rgb_color`, formatted a `#rrggbb` hex, updated the slider progress bar color and label background. Alpha slider value was never read.

### `get()` / `_ok_event()`
Returned `self.label._fg_color` (the raw CTk internal color string).

### `set_initial_color(initial_color)`
Scans every pixel of the wheel image to find a pixel matching the given hex color and positions the target cursor there (beta / approximate).

### `projection_on_circle()`
Math helper — projects an out-of-bounds point onto the circle edge using `atan2`.

---

## Added / Changed Code

### `self.hex_color_with_alpha`
New instance variable initialized to `"#ffffffff"`. Stores the true `#rrggbbaa` output.

### Alpha slider `command`
Added `command=lambda x: self.update_colors()` so dragging the alpha slider now triggers a color update.

### `_hex_to_rgb(hex_color)` *(new)*
Simple helper that converts a `#rrggbb` string to an `(r, g, b)` tuple. Used to parse `self.bg_color` for blending.

### `update_colors()` *(rewritten)*
Now reads both `brightness` and `alpha` slider values.

1. Applies brightness scaling → gets opaque `r, g, b`.
2. Stores `self.hex_color_with_alpha = "#rrggbbaa"` — the true RGBA output.
3. **Alpha compositing** — blends the color against the window background to produce a visually correct opaque approximation for the label:
   $$\text{display} = \text{color} \times \frac{\alpha}{255} + \text{bg} \times \left(1 - \frac{\alpha}{255}\right)$$
4. Sets `label.fg_color` to the blended hex (visual preview only).
5. Sets `label.text` to the full `#rrggbbaa` string.
6. Updates **both** slider progress bar colors to match current hue.
7. Uses perceived brightness (weighted 0.299R + 0.587G + 0.114B) on the blended color to auto-switch label text between black and white.

### `get()` / `_ok_event()`
Now return `self.hex_color_with_alpha` (`#rrggbbaa`) instead of the internal CTk color string.

---

## Workflow Summary

```
User drags on wheel
  → on_mouse_drag()
      → get_target_color()   # read pixel from wheel image
      → update_colors()      # apply brightness + alpha → update label + sliders

User moves brightness slider  →  update_colors()
User moves alpha slider       →  update_colors()

User clicks OK
  → _ok_event()  →  returns "#rrggbbaa"
```

> **Why blend instead of RGBA on the label?**
> `CTkLabel.fg_color` only accepts opaque `#rrggbb`. The blending is purely a visual approximation for the preview; the actual alpha is preserved in `hex_color_with_alpha`.
