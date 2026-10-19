"""Self-check senza webcam: uv run check.py"""
import cv2
import numpy as np

from webcamfx.context import FrameContext
from webcamfx.effects import default_effects
from webcamfx.effects.teleport import teleport


def scene():
    frame = np.full((720, 1280, 3), 200, np.uint8)
    bg = np.zeros_like(frame)
    mask = np.zeros((720, 1280), np.float32)
    mask[150:720, 500:780] = 1
    return frame, bg, mask


def check_teleport():
    f, bg, m = scene()
    assert teleport(f, bg, m, 0) is f
    assert teleport(f, bg, m, 1) is bg
    mid = teleport(f, bg, m, 0.4)
    assert mid[170, 640].sum() > 0 and mid[5, 5].sum() == 0  # testa visibile, angolo intatto
    edge = np.pad(m[:, 400:], ((0, 0), (0, 400)))
    assert (teleport(f, bg, edge, 0.9)[:, -5:] == 0).all()  # niente strisce dai bordi


def check_effects():
    f, bg, m = scene()
    for effect in default_effects():
        changed = False
        for i in range(90):  # 3 secondi a 30fps
            ctx = FrameContext(f, m, bg, i / 30, 1 / 30)
            if i == 0:
                effect.trigger(ctx, None)
            out = effect.render(ctx, f)
            assert out.shape == f.shape and out.dtype == np.uint8, effect.label
            changed |= not np.array_equal(out, f)
        assert changed, f"{effect.label} non ha modificato nessun frame"
        print("ok", effect.label)


def check_app():
    """Loop completo con webcam finta e tasti simulati (1..6, b)."""
    frame, _, _ = scene()

    class FakeCam:
        n = 0
        def __init__(self, *a): pass
        def set(self, *a): return True
        def isOpened(self): return True
        def release(self): pass
        def read(self):
            FakeCam.n += 1
            return (True, frame) if FakeCam.n <= 120 else (False, None)

    keys = iter([-1] * 5 + [ord(c) for c in "123456b"] + [-1] * 1000)
    cv2.VideoCapture, cv2.waitKey, cv2.imshow = FakeCam, lambda *a: next(keys), lambda *a: None
    from webcamfx.app import App
    app = App()
    app.run()
    print("ok app")


if __name__ == "__main__":
    check_teleport()
    check_effects()
    check_app()
    print("tutto ok")
