import numpy as np

GESTURE_SCORE = 0.6   # soglia del classificatore MediaPipe
COOLDOWN = 1.5        # secondi minimi tra due trigger dello stesso gesto

# nomi brevi per l'anteprima
LABELS = {
    "Victory": "V", "Thumb_Up": "pollice su", "Thumb_Down": "pollice giu", "Open_Palm": "palmo",
    "Pointing_Up": "indice su", "ILoveYou": "rock", "Closed_Fist": "pugno",
}


def _looks_like_v(pts):
    """Indice e medio estesi e divaricati, anulare e mignolo piegati: regge anche la V di lato."""
    d = lambda i, j: float(np.linalg.norm(pts[i] - pts[j]))
    ext = lambda tip, pip: d(0, tip) > d(0, pip) * 1.15
    curled = lambda tip, pip: d(0, tip) < d(0, pip)
    return ext(8, 6) and ext(12, 10) and curled(16, 14) and curled(20, 18) and d(8, 12) > d(5, 9) * 1.3


def classify(category, pts):
    """Nome del gesto: classificatore se sicuro, altrimenti fallback V sui landmark."""
    if category.score >= GESTURE_SCORE and category.category_name != "None":
        return category.category_name
    return "Victory" if _looks_like_v(pts) else "None"


class GestureTrigger:
    """Debounce: un gesto scatta una volta dopo `hold` rilevamenti consecutivi, poi cooldown."""

    def __init__(self, holds, default_hold=4):
        self.holds, self.default_hold = holds, default_hold
        self.counts, self.last = {}, {}

    def update(self, hands, now):
        """hands -> {gesto: Hand} dei gesti scattati ora."""
        current = {h.gesture: h for h in hands if h.gesture != "None"}
        self.counts = {g: self.counts.get(g, 0) + 1 for g in current}
        fired = {}
        for g, hand in current.items():
            if self.counts[g] == self.holds.get(g, self.default_hold) and now - self.last.get(g, -1e9) > COOLDOWN:
                fired[g] = hand
                self.last[g] = now
        return fired
