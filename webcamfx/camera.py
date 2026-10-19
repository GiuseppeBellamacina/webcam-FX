import cv2
import pyvirtualcam

FONT = cv2.FONT_HERSHEY_SIMPLEX


def open_camera(index, w, h):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))  # senza MJPG il 720p va a 5-10 fps
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    if not cap.isOpened():
        raise SystemExit(f"webcam {index} non disponibile, prova --camera 1")
    return cap


class VirtualCam:
    """Output su OBS Virtual Camera; se non disponibile diventa un no-op."""

    def __init__(self, w, h, fps):
        try:
            self.cam = pyvirtualcam.Camera(w, h, fps, fmt=pyvirtualcam.PixelFormat.BGR, backend="obs")
            print("output su", self.cam.device)
        except RuntimeError as e:
            self.cam = None
            print("virtual cam non disponibile (OBS ha la virtual cam accesa?):", e)

    def send(self, frame):
        if self.cam:
            self.cam.send(frame)  # non specchiato: Meet/Teams specchiano gia' il self-view

    def close(self):
        if self.cam:
            self.cam.close()


class Preview:
    """Finestra locale specchiata con testo di stato. lines = [(testo, evidenziato), ...]"""

    def __init__(self, title):
        self.title = title

    def key(self):
        k = cv2.waitKey(1) & 0xFF
        return chr(k) if k != 255 else ""

    def show(self, frame, lines):
        img = cv2.flip(frame, 1)
        for i, (text, on) in enumerate(lines):
            org = (10, 28 + i * 26)
            cv2.putText(img, text, org, FONT, 0.65, (0, 0, 0), 4)
            cv2.putText(img, text, org, FONT, 0.65, (0, 255, 0) if on else (255, 255, 255), 2)
        cv2.imshow(self.title, img)

    def close(self):
        cv2.destroyAllWindows()
