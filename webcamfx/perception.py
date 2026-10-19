import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

from .context import Hand
from .gestures import classify

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODELS = {
    "gesture_recognizer.task": "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task",
    "selfie_segmenter.tflite": "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite",
}


def _model(name):
    p = MODELS_DIR / name
    if not p.exists():
        MODELS_DIR.mkdir(exist_ok=True)
        print("scarico", name)
        urllib.request.urlretrieve(MODELS[name], p)
    return BaseOptions(model_asset_path=str(p))


class Perception:
    """Modelli MediaPipe: maschera persona a ogni frame, mani e gesti ogni `gesture_every` frame."""

    def __init__(self, out_size, work_size=(640, 360), gesture_every=2):
        video = vision.RunningMode.VIDEO
        self.gestures = vision.GestureRecognizer.create_from_options(vision.GestureRecognizerOptions(
            base_options=_model("gesture_recognizer.task"), running_mode=video, num_hands=2))
        self.segmenter = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
            base_options=_model("selfie_segmenter.tflite"), running_mode=video))
        self.out_size, self.work_size, self.every = out_size, work_size, gesture_every
        self.i, self.last_ts = 0, -1

    def process(self, frame, now):
        """-> (mask float32 a piena risoluzione, lista di Hand oppure None se non analizzate ora)."""
        ts = max(int(now * 1000), self.last_ts + 1)  # MediaPipe vuole timestamp strettamente crescenti
        self.last_ts = ts
        small = mp.Image(image_format=mp.ImageFormat.SRGB,
                         data=cv2.cvtColor(cv2.resize(frame, self.work_size), cv2.COLOR_BGR2RGB))
        seg = self.segmenter.segment_for_video(small, ts).confidence_masks[0].numpy_view()
        mask = cv2.resize(cv2.GaussianBlur(seg.squeeze(), (0, 0), 1.5), self.out_size)

        self.i += 1
        if self.i % self.every:  # ponytail: gesti a frame alterni per tenere ~30fps; ogni frame se la CPU regge
            return mask, None
        w, h = self.out_size
        result = self.gestures.recognize_for_video(small, ts)
        hands = []
        for cats, lms in zip(result.gestures, result.hand_landmarks):
            pts = np.array([(lm.x * w, lm.y * h) for lm in lms], np.float32)
            hands.append(Hand(classify(cats[0], pts), pts))
        return mask, hands
