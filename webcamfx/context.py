from dataclasses import dataclass
from functools import cached_property

import numpy as np


@dataclass
class Hand:
    gesture: str            # "Victory", "Thumb_Up", ... oppure "None"
    points: np.ndarray      # (21, 2) landmark in pixel del frame

    @property
    def center(self):
        return self.points[9]  # base del dito medio


def person_extent(mask):
    """(top, bottom, x_testa) della persona nella maschera, oppure None."""
    rows = np.flatnonzero(mask.max(axis=1) > 0.5)
    if rows.size == 0:
        return None
    top, bottom = int(rows[0]), int(rows[-1])
    head = np.flatnonzero(mask[top:top + 40].max(axis=0) > 0.5)
    return top, bottom, int(head.mean())


@dataclass
class FrameContext:
    """Tutto quello che un effetto puo' leggere sul frame corrente.
    `background` puo' essere sostituito da un effetto (es. TimeStop) per quelli successivi."""
    frame: np.ndarray        # frame originale BGR
    mask: np.ndarray         # probabilita' persona float32 (H, W)
    background: np.ndarray   # sfondo senza persona
    now: float               # secondi (monotonic)
    dt: float                # secondi dal frame precedente

    @cached_property
    def person_extent(self):
        return person_extent(self.mask)

    def anchor(self, hand=None):
        """Punto da cui far partire un effetto: la mano, altrimenti il centro della persona/frame."""
        if hand is not None:
            return hand.center
        ext = self.person_extent
        if ext:
            top, bottom, x = ext
            return np.array([x, (top + bottom) / 2], np.float32)
        h, w = self.mask.shape
        return np.array([w / 2, h / 2], np.float32)
