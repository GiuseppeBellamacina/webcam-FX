import cv2
import numpy as np

STABLE_FRAMES = 15   # frame consecutivi senza persona prima di aggiornare un pixel dello sfondo
INPAINT_EVERY = 15   # ogni quanti frame ricalcolare il riempimento delle zone mai viste


class BackgroundModel:
    """Sfondo senza persona. Catturato con `capture_in` resta bloccato; altrimenti si aggiorna
    solo dove la persona e' lontana (margine 40px) da STABLE_FRAMES frame, cosi' un errore
    momentaneo del segmenter non sporca lo sfondo. Le zone mai viste sono riempite con inpaint."""

    def __init__(self, first_frame):
        h, w = first_frame.shape[:2]
        self.plate = first_frame.copy()
        self.seen = np.zeros((h, w), bool)
        self.free_for = np.zeros((h, w), np.uint8)
        self.fill, self.age = first_frame, INPAINT_EVERY
        self.locked, self.grab_at = False, None

    def capture_in(self, seconds, now):
        self.grab_at = now + seconds

    def status(self, now):
        if self.grab_at:
            return f"sfondo tra {self.grab_at - now:.0f}s"
        return "sfondo OK" if self.locked else "premi b per lo sfondo"

    def update(self, frame, mask, now):
        if self.grab_at and now >= self.grab_at:
            self.plate[:], self.seen[:], self.locked, self.grab_at = frame, True, True, None
            print("sfondo catturato e bloccato")
        if not self.locked:
            free = cv2.erode((mask < 0.1).astype(np.uint8), np.ones((81, 81), np.uint8)).astype(bool)
            self.free_for = np.where(free, np.minimum(self.free_for, 254) + 1, 0).astype(np.uint8)
            ok = self.free_for >= STABLE_FRAMES
            self.plate[ok] = frame[ok]
            self.seen |= ok
        if self.seen.all():
            return self.plate
        self.age += 1
        if self.age >= INPAINT_EVERY:
            self.age = 0
            holes = (~self.seen).astype(np.uint8) * 255
            small = cv2.inpaint(cv2.resize(self.plate, (320, 180)), cv2.resize(holes, (320, 180)), 5, cv2.INPAINT_TELEA)
            self.fill = cv2.resize(small, self.plate.shape[1::-1])
        return np.where(self.seen[..., None], self.plate, self.fill)
