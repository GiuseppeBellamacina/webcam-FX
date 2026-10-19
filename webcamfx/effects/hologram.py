import cv2
import numpy as np

from ..particles import rng
from .base import ToggleEffect

TINT = np.array([1.0, 0.85, 0.35], np.float32)   # BGR: azzurro-blu
LIFT = np.array([60, 30, 0], np.float32)


class Hologram(ToggleEffect):
    """La persona diventa un ologramma blu semitrasparente con scanline e glitch."""
    label, gesture, duration = "Ologramma", "Pointing_Up", 0.6

    def apply(self, ctx, out, t):
        ys, xs = np.nonzero(ctx.mask[::8, ::8] > 0.05)  # lavora solo nel riquadro della persona
        if ys.size == 0:
            return out
        h, w = out.shape[:2]
        y0, y1 = max(ys.min() * 8 - 16, 0), min(ys.max() * 8 + 24, h)
        x0, x1 = max(xs.min() * 8 - 16, 0), min(xs.max() * 8 + 24, w)
        crop, mask, bg = out[y0:y1, x0:x1], ctx.mask[y0:y1, x0:x1], ctx.background[y0:y1, x0:x1]

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
        holo = gray * TINT + LIFT
        holo[(np.arange(y0, y1) + int(ctx.now * 80)) % 6 < 2] *= 0.5  # scanline che scorrono
        holo = np.clip(holo, 0, 255).astype(np.uint8)
        if rng.random() < 0.2:  # glitch: bande orizzontali spostate
            for _ in range(rng.integers(1, 4)):
                y, bh = int(rng.integers(0, max(y1 - y0 - 30, 1))), int(rng.integers(4, 30))
                holo[y:y + bh] = np.roll(holo[y:y + bh], int(rng.integers(-40, 40)), axis=1)
        k = float(0.7 + 0.1 * np.sin(ctx.now * 30))  # sfarfallio della trasparenza
        person = cv2.blendLinear(holo, bg, mask * k, 1 - mask * k)
        a = mask * float(t)
        out = out.copy()
        out[y0:y1, x0:x1] = cv2.blendLinear(person, crop, a, 1 - a)
        return out
