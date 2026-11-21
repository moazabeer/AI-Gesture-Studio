import sys
import cv2
import time
import mediapipe as mp

from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFrame, QTextEdit
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gesture_recognizer import recognize_gesture


# Project configuration
MODEL_PATH = Path(__file__).resolve().parents[2] / "hand_landmarker.task"

CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]



class GestureStudio(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Gesture Studio")
        self.setMinimumSize(950, 650)

        self.cap = None
        self.detector = None
        self.current_gesture = "None"
        self.app_status = "WAITING"

        self.candidate = None
        self.stable_frames = 0
        self.last_timestamp = -1

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)

        self.setup_ui()

    def setup_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("AI GESTURE STUDIO")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #55C2FF;"
        )

        subtitle = QLabel("Real-Time Hand Tracking & Gesture Recognition")
        subtitle.setStyleSheet("color: #AAAAAA; font-size: 13px;")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        content = QHBoxLayout()

        # Camera panel
        camera_panel = QVBoxLayout()

        self.camera_label = QLabel("Camera is stopped")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumSize(600, 400)
        self.camera_label.setStyleSheet(
            "background-color: #111827;"
            "color: #AAAAAA;"
            "border: 1px solid #334155;"
            "border-radius: 12px;"
            "font-size: 18px;"
        )

        camera_panel.addWidget(self.camera_label)

        # Information panel
        info_panel = QVBoxLayout()

        self.gesture_label = QLabel("Gesture: None")
        self.status_label = QLabel("Status: WAITING")

        for label in [self.gesture_label, self.status_label]:
            label.setStyleSheet(
                "background-color: #1E293B;"
                "color: white;"
                "padding: 15px;"
                "border-radius: 8px;"
                "font-size: 16px;"
            )
            info_panel.addWidget(label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Activity log...")
        self.log.setMaximumWidth(270)
        self.log.setStyleSheet(
            "background-color: #111827;"
            "color: #D1D5DB;"
            "border: 1px solid #334155;"
            "border-radius: 8px;"
        )

        info_panel.addWidget(QLabel("ACTIVITY LOG"))
        info_panel.addWidget(self.log)

        content.addLayout(camera_panel, 3)
        content.addLayout(info_panel, 1)

        main_layout.addLayout(content)

        # Controls
        controls = QHBoxLayout()

        self.start_button = QPushButton("START CAMERA")
        self.stop_button = QPushButton("STOP CAMERA")

        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        self.stop_button.setEnabled(False)

        self.start_button.setStyleSheet(
            "background-color: #087E5B; color: white;"
            "padding: 14px; border-radius: 7px; font-weight: bold;"
        )

        self.stop_button.setStyleSheet(
            "background-color: #B83232; color: white;"
            "padding: 14px; border-radius: 7px; font-weight: bold;"
        )

        controls.addWidget(self.start_button)
        controls.addWidget(self.stop_button)

        main_layout.addLayout(controls)

        self.setStyleSheet(
            "QMainWindow { background-color: #0B1120; }"
            "QLabel { color: white; }"
            "QPushButton:disabled { background-color: #475569; }"
        )

    def add_log(self, message):
        self.log.append(
            time.strftime("%H:%M:%S") + " - " + message
        )

    def start_camera(self):

        if not MODEL_PATH.exists():
            self.add_log("ERROR: Hand model not found.")
            return

        try:
            base_options = python.BaseOptions(
                model_asset_path=str(MODEL_PATH)
            )

            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                num_hands=2
            )

            self.detector = vision.HandLandmarker.create_from_options(
                options
            )

            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

            if not self.cap.isOpened():
                self.add_log("ERROR: Camera could not open.")
                self.stop_camera()
                return

            self.current_gesture = "None"
            self.app_status = "WAITING"
            self.candidate = None
            self.stable_frames = 0
            self.last_timestamp = -1

            self.timer.start(30)

            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            self.add_log("Camera started successfully.")

        except Exception as error:
            self.add_log(f"ERROR: {error}")
            self.stop_camera()

    def update_camera(self):

        if self.cap is None:
            return

        ret, frame = self.cap.read()

        if not ret:
            self.add_log("Camera frame unavailable.")
            self.stop_camera()
            return

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp = time.monotonic_ns() // 1_000_000
        self.last_timestamp = max(
            timestamp, self.last_timestamp + 1
        )

        results = self.detector.detect_for_video(
            mp_image, self.last_timestamp
        )

        detected = "None"

        if results.hand_landmarks:

            hand = results.hand_landmarks[0]
            detected = recognize_gesture(hand)

            height, width, _ = frame.shape
            points = []

            for landmark in hand:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                points.append((x, y))

            for start, end in CONNECTIONS:
                cv2.line(
                    frame, points[start], points[end],
                    (0, 255, 0), 2
                )

            for point in points:
                cv2.circle(
                    frame, point, 5, (0, 0, 255), -1
                )

        # Gesture stabilization
        if detected == self.candidate:
            self.stable_frames += 1
        else:
            self.candidate = detected
            self.stable_frames = 1

        if self.stable_frames >= 5:
            if detected != self.current_gesture:

                self.current_gesture = detected

                if detected == "Open Palm":
                    self.app_status = "ACTIVE"

                elif detected == "Fist":
                    self.app_status = "PAUSED"

                elif detected == "Peace Sign":
                    self.app_status = "MODE SELECTED"

                else:
                    self.app_status = "WAITING"

                self.add_log(
                    f"{detected} detected - {self.app_status}"
                )

        cv2.putText(
            frame,
            self.current_gesture,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        self.gesture_label.setText(
            f"Gesture: {self.current_gesture}"
        )

        self.status_label.setText(
            f"Status: {self.app_status}"
        )

        image = QImage(
            frame.data,
            frame.shape[1],
            frame.shape[0],
            frame.strides[0],
            QImage.Format.Format_BGR888
        )

        pixmap = QPixmap.fromImage(image)

        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def stop_camera(self):

        self.timer.stop()

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        if self.detector is not None:
            self.detector.close()
            self.detector = None

        self.camera_label.clear()
        self.camera_label.setText("Camera is stopped")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        self.current_gesture = "None"
        self.app_status = "WAITING"

        self.gesture_label.setText("Gesture: None")
        self.status_label.setText("Status: WAITING")

        self.add_log("Camera stopped.")

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = GestureStudio()
    window.show()

    sys.exit(app.exec())