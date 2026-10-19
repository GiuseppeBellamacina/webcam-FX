import cv2
import numpy as np

from .base import ToggleEffect

RING_TIME = 0.7   # durata dell'onda d'urto in secondi


class TimeStop(ToggleEffect):
    """Il mondo si congela in bianco e nero (tinta blu), tu continui a muoverti a colori.
    Sostituisce ctx.background, cosi' anche gli effetti successivi (es. teletrasporto) vedono il mondo fermo."""
    label, gesture, hold, duration = "Tempo fermo", "Open_Palm", 8, 0.5  # hold alto: il palmo si apre spesso parlando

    def __init__(self):
        super().__init__()
        self.frozen, self.ring = None, None

    def trigger(self, ctx, hand):
        super().trigger(ctx, hand)
        if self.state.on:
            gray = cv2.cvtColor(cv2.cvtColor(ctx.background, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
            self.frozen = cv2.addWeighted(gray, 0.85, np.full_like(gray, (90, 40, 0)), 0.3, 0)
        self.ring = (ctx.anchor(hand), ctx.now)

    def apply(self, ctx, out, t):
        ctx.background = cv2.addWeighted(self.frozen, t, ctx.background, 1 - t, 0)
        return cv2.blendLinear(out, ctx.background, ctx.mask, 1 - ctx.mask)

    def render(self, ctx, out):
        out = super().render(ctx, out)
        if self.ring is None or ctx.now - self.ring[1] > RING_TIME:
            return out
        center, start = self.ring
        k = (ctx.now - start) / RING_TIME
        layer = out.copy()
        cv2.circle(layer, tuple(int(v) for v in center), int(40 + k * 1500), (255, 240, 200), int(20 * (1 - k)) + 2, cv2.LINE_AA)
        return cv2.addWeighted(layer, 0.8 * (1 - k), out, 1 - 0.8 * (1 - k), 0)
