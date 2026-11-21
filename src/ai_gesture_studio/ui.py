import sys
import cv2
import time

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QTextEdit
)

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

from gesture_recognizer import recognize_gesture
from hand_tracker import HandTracker
from mouse_controller import MouseController


class GestureStudio(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Gesture Studio")
        self.setMinimumSize(950, 650)

        self.cap = None
        self.tracker = None

        self.mouse = MouseController(smoothing=0.45)

        self.current_gesture = "None"
        self.app_status = "WAITING"

        self.candidate = None
        self.stable_frames = 0
        self.no_hand_frames = 0

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

        subtitle = QLabel(
            "Real-Time Hand Tracking & Gesture Recognition"
        )

        subtitle.setStyleSheet(
            "color: #AAAAAA; font-size: 13px;"
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        content = QHBoxLayout()
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

        info_panel = QVBoxLayout()

        self.gesture_label = QLabel("Gesture: None")
        self.status_label = QLabel("Status: WAITING")
        self.hand_count_label = QLabel("Hands detected: 0")

        for label in [
            self.gesture_label,
            self.status_label,
            self.hand_count_label
        ]:
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

        info_panel.addWidget(QLabel("ACTIVITY LOG"))
        info_panel.addWidget(self.log)

        content.addLayout(camera_panel, 3)
        content.addLayout(info_panel, 1)

        main_layout.addLayout(content)

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

        mouse_controls = QHBoxLayout()

        self.mouse_enable_button = QPushButton("ENABLE MOUSE")
        self.mouse_disable_button = QPushButton("DISABLE MOUSE")

        self.mouse_status_label = QLabel("Mouse: DISABLED")
        self.click_status_label = QLabel("Click: READY")

        self.mouse_enable_button.clicked.connect(
            self.enable_mouse
        )

        self.mouse_disable_button.clicked.connect(
            self.disable_mouse
        )

        self.mouse_disable_button.setEnabled(False)

        self.mouse_enable_button.setStyleSheet(
            "background-color: #087E5B; color: white;"
            "padding: 12px; border-radius: 7px; font-weight: bold;"
        )

        self.mouse_disable_button.setStyleSheet(
            "background-color: #B83232; color: white;"
            "padding: 12px; border-radius: 7px; font-weight: bold;"
        )

        mouse_controls.addWidget(self.mouse_enable_button)
        mouse_controls.addWidget(self.mouse_disable_button)
        mouse_controls.addWidget(self.mouse_status_label)
        mouse_controls.addWidget(self.click_status_label)

        main_layout.addLayout(mouse_controls)

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

        try:
            self.tracker = HandTracker()

            self.cap = cv2.VideoCapture(
                0,
                cv2.CAP_DSHOW
            )

            if not self.cap.isOpened():
                raise RuntimeError("Camera could not open.")

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            actual_width = int(
                self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            )

            actual_height = int(
                self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            )

            self.add_log(
                f"Camera resolution: {actual_width}x{actual_height}"
            )

            self.current_gesture = "None"
            self.app_status = "WAITING"

            self.candidate = None
            self.stable_frames = 0
            self.no_hand_frames = 0

            self.timer.start(30)

            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            self.add_log("Camera started successfully.")

        except Exception as error:

            self.add_log(f"ERROR: {error}")
            self.stop_camera()

    def update_camera(self):

        if self.cap is None or self.tracker is None:
            return

        ret, frame = self.cap.read()

        if not ret:
            self.add_log("Camera frame unavailable.")
            self.stop_camera()
            return

        frame = cv2.flip(frame, 1)

        results = self.tracker.process_frame(frame)

        hands = results.hand_landmarks or []

        detected = "None"

        self.hand_count_label.setText(
            f"Hands detected: {len(hands)}"
        )

        if hands:

            self.no_hand_frames = 0

            # Draw every detected hand
            for detected_hand in hands:
                self.tracker.draw_landmarks(
                    frame,
                    detected_hand
                )

            # Find the largest hand
            def hand_area(hand):

                xs = [point.x for point in hand]
                ys = [point.y for point in hand]

                return (
                    (max(xs) - min(xs))
                    * (max(ys) - min(ys))
                )

            selected_hand = max(
                hands,
                key=hand_area
            )

            detected = recognize_gesture(selected_hand)

            # Mouse movement follows the selected hand
            index_tip = selected_hand[8]

            self.mouse.move_cursor(
                index_tip.x,
                index_tip.y
            )
            # Pinch-to-click detection
            thumb_tip = selected_hand[4]

            clicked = self.mouse.pinch_to_click(
            thumb_tip,
            index_tip
            )

            if clicked:
                self.add_log("Left mouse click detected.")

        else:

            self.no_hand_frames += 1

            # Reset gesture after brief detection loss
            if self.no_hand_frames >= 5:

                self.candidate = None
                self.stable_frames = 0

                if self.current_gesture != "None":

                    self.current_gesture = "None"
                    self.app_status = "WAITING"

        # Gesture stability
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
        ).copy()

        pixmap = QPixmap.fromImage(image)

        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def enable_mouse(self):

        if self.cap is None or self.tracker is None:

            self.add_log(
                "Start camera before enabling mouse."
            )
            return

        self.mouse.enable()

        self.mouse_enable_button.setEnabled(False)
        self.mouse_disable_button.setEnabled(True)

        self.mouse_status_label.setText("Mouse: ENABLED")

        self.add_log("Mouse control enabled.")

    def disable_mouse(self):

        self.mouse.disable()

        self.mouse_enable_button.setEnabled(True)
        self.mouse_disable_button.setEnabled(False)

        self.mouse_status_label.setText("Mouse: DISABLED")

        self.add_log("Mouse control disabled.")

    def stop_camera(self):

        self.timer.stop()

        self.disable_mouse()

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        if self.tracker is not None:
            self.tracker.close()
            self.tracker = None

        self.camera_label.clear()
        self.camera_label.setText("Camera is stopped")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        self.current_gesture = "None"
        self.app_status = "WAITING"

        self.candidate = None
        self.stable_frames = 0
        self.no_hand_frames = 0

        self.gesture_label.setText("Gesture: None")
        self.status_label.setText("Status: WAITING")
        self.hand_count_label.setText("Hands detected: 0")

        self.add_log("Camera stopped.")

    def closeEvent(self, event):

        self.stop_camera()
        event.accept()