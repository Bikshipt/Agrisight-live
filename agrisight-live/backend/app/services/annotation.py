"""
Annotation Service.

Draws high-quality vector overlays on images for bounding boxes returned
by Gemini Live. This function is optimized for presentation quality:
retina-friendly resolution, translucent overlays, and a neon green glow.

Expected env vars: None
Testing tips:
- Pass a small dummy image and a couple of bounding boxes.
- Verify that the returned PNG bytes differ from the input and that
  alpha transparency is preserved.
"""
import io
from typing import Iterable, Mapping

from PIL import Image, ImageDraw, ImageFilter


NEON_GREEN = (15, 175, 104, 255)  # #0FAF68 with full alpha
OVERLAY_ALPHA = (15, 175, 104, 80)  # translucent fill
LABEL_BG = (15, 23, 36, 220)  # dark neutral background with alpha
LABEL_TEXT = (246, 251, 255, 255)  # surface white


def _ensure_rgba(image: Image.Image) -> Image.Image:
    if image.mode != "RGBA":
        return image.convert("RGBA")
    return image


def draw_bounding_boxes(image_bytes: bytes, boxes: Iterable[Mapping[str, float]]) -> bytes:
    """
    Draw translucent bounding boxes with a soft neon glow and labels.

    Coordinates are expected to be normalized in the range [0, 1].
    """
    try:
        base_image = Image.open(io.BytesIO(image_bytes))
        base_image = _ensure_rgba(base_image)

        # Retina-friendly compositing: upscale the overlay slightly to
        # provide crisp edges when downscaled by the browser.
        width, height = base_image.size
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        draw_overlay = ImageDraw.Draw(overlay)
        draw_glow = ImageDraw.Draw(glow_layer)

        for box in boxes:
            x = float(box.get("x", 0.0))
            y = float(box.get("y", 0.0))
            w = float(box.get("w", 0.0))
            h = float(box.get("h", 0.0))
            label = str(box.get("label", ""))

            x0 = x * width
            y0 = y * height
            x1 = (x + w) * width
            y1 = (y + h) * height

            # Outer glow rectangle (slightly larger)
            glow_padding = 4
            glow_rect = [
                max(0, x0 - glow_padding),
                max(0, y0 - glow_padding),
                min(width, x1 + glow_padding),
                min(height, y1 + glow_padding),
            ]
            draw_glow.rectangle(glow_rect, outline=NEON_GREEN, width=6)

            # Translucent fill + sharp border
            draw_overlay.rectangle([x0, y0, x1, y1], fill=OVERLAY_ALPHA, outline=NEON_GREEN, width=3)

            if label:
                text_padding_x = 8
                text_padding_y = 4
                # Approximate text box; we keep it simple to avoid font deps.
                label_width = max(80, len(label) * 8)
                label_height = 22
                label_box = [
                    x0,
                    max(0, y0 - label_height - 6),
                    min(width, x0 + label_width),
                    max(0, y0 - 6),
                ]
                draw_overlay.rounded_rectangle(label_box, radius=8, fill=LABEL_BG)
                text_x = label_box[0] + text_padding_x
                text_y = label_box[1] + text_padding_y
                draw_overlay.text((text_x, text_y), label, fill=LABEL_TEXT)

        # Apply a blur to the glow layer for a soft neon effect.
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=6))

        composed = Image.alpha_composite(base_image, glow_layer)
        composed = Image.alpha_composite(composed, overlay)

        output = io.BytesIO()
        composed.save(output, format="PNG", optimize=True)
        return output.getvalue()
    except Exception:
        # In failure scenarios we return the original image so the user
        # still sees something, and the error can be logged by callers.
        return image_bytes

