import time

import cv2

from .background import BackgroundModel
from .camera import Preview, VirtualCam, open_camera
from .context import FrameContext
from .effects import default_effects
from .gestures import LABELS, GestureTrigger
from .perception import Perception

W, H, FPS = 1280, 720, 30


class App:
    """Loop principale: webcam -> percezione -> sfondo -> gesti -> catena di effetti -> output."""

    def __init__(self, camera_index=0, effects=None):
        self.camera = open_camera(camera_index, W, H)
        self.perception = Perception((W, H))
        self.effects = effects if effects is not None else default_effects()
        self.triggers = GestureTrigger({e.gesture: e.hold for e in self.effects if e.gesture})
        self.output = VirtualCam(W, H, FPS)
        self.preview = Preview("Webcam FX - anteprima")

    def run(self):
        ok, frame = self.camera.read()
        if not ok:
            raise SystemExit("nessun frame dalla webcam")
        background = BackgroundModel(cv2.resize(frame, (W, H)))
        keys = " | ".join(f"{i + 1} {e.label}" for i, e in enumerate(self.effects))
        print(f"gesti o tasti: {keys} | b = cattura sfondo tra 3s | q = esci")
        prev, fps = time.monotonic(), 0.0
        try:
            while True:
                ok, frame = self.camera.read()
                if not ok:
                    break
                frame = cv2.resize(frame, (W, H))
                now = time.monotonic()
                mask, hands = self.perception.process(frame, now)
                ctx = FrameContext(frame, mask, background.update(frame, mask, now), now, now - prev)
                prev = now

                key = self.preview.key()
                if key == "q":
                    break
                if key == "b":
                    background.capture_in(3, now)
                fired = self.triggers.update(hands, now) if hands is not None else {}
                for i, e in enumerate(self.effects):
                    if e.gesture in fired or key == str(i + 1):
                        e.trigger(ctx, fired.get(e.gesture))

                out = frame
                for e in self.effects:
                    out = e.render(ctx, out)
                self.output.send(out)

                fps = fps * 0.9 + 0.1 / max(time.monotonic() - now, 1e-3)
                self.preview.show(out, [(f"{fps:.0f} fps | {background.status(now)}", False)] + [
                    (f"{i + 1} {e.label} [{LABELS.get(e.gesture, 'tasto')}]", e.active(now))
                    for i, e in enumerate(self.effects)])
        finally:
            self.camera.release()
            self.output.close()
            self.preview.close()
