import cv2
import mediapipe as mp

from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


class HandTracker:

    def __init__(self, model_path=None):

        if model_path is None:
            model_path = (
                Path(__file__).resolve().parents[2]
                / "hand_landmarker.task"
            )

        if not model_path.exists():
            raise FileNotFoundError(
                f"Hand model not found: {model_path}"
            )

        base_options = python.BaseOptions(
            model_asset_path=str(model_path)
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2
        )

        self.detector = (
            vision.HandLandmarker.create_from_options(options)
        )

        self.last_timestamp = -1

    def process_frame(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        import time

        timestamp = time.monotonic_ns() // 1_000_000

        self.last_timestamp = max(
            timestamp,
            self.last_timestamp + 1
        )

        results = self.detector.detect_for_video(
            mp_image,
            self.last_timestamp
        )

        return results

    def draw_landmarks(self, frame, hand):

        height, width, _ = frame.shape

        points = [
            (int(point.x * width), int(point.y * height))
            for point in hand
        ]

        for start, end in CONNECTIONS:
            cv2.line(
                frame,
                points[start],
                points[end],
                (0, 255, 0),
                2
            )

        for point in points:
            cv2.circle(
                frame,
                point,
                5,
                (0, 0, 255),
                -1
            )

        return frame

    def close(self):

        if self.detector is not None:
            self.detector.close()
            self.detector = None