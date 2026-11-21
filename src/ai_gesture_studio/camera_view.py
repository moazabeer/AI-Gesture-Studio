import cv2
import mediapipe as mp
import time
from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# Model setup
MODEL_PATH = Path(__file__).resolve().parents[2] / "hand_landmarker.task"

base_options = python.BaseOptions(
    model_asset_path=str(MODEL_PATH)
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2
)

detector = vision.HandLandmarker.create_from_options(options)


# Gesture recognition
def finger_up(hand, tip, pip):
    return hand[tip].y < hand[pip].y


def recognize_gesture(hand):
    index = finger_up(hand, 8, 6)
    middle = finger_up(hand, 12, 10)
    ring = finger_up(hand, 16, 14)
    pinky = finger_up(hand, 20, 18)

    if index and middle and ring and pinky:
        return "Open Palm"

    if not index and not middle and not ring and not pinky:
        return "Fist"

    if index and middle and not ring and not pinky:
        return "Peace Sign"

    return "Unknown"


# Camera setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    detector.close()
    raise SystemExit("Camera could not open.")


# Application state
app_status = "WAITING"
current_gesture = "None"
candidate_gesture = None
stable_frames = 0

last_timestamp = -1

print("AI Gesture Studio Started!")
print("Open Palm = Start")
print("Fist = Stop")
print("Peace Sign = Select Mode")
print("Press Q to quit.")


try:
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp = time.monotonic_ns() // 1_000_000
        last_timestamp = max(timestamp, last_timestamp + 1)

        results = detector.detect_for_video(
            mp_image, last_timestamp
        )

        detected = "None"

        if results.hand_landmarks:
            hand = results.hand_landmarks[0]
            detected = recognize_gesture(hand)

            for point in hand:
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])

                cv2.circle(
                    frame, (x, y), 5, (0, 0, 255), -1
                )

        # Stabilize gesture recognition
        if detected == candidate_gesture:
            stable_frames += 1
        else:
            candidate_gesture = detected
            stable_frames = 1

        # Perform action after stable detection
        if stable_frames >= 5 and detected != current_gesture:
            current_gesture = detected

            if detected == "Open Palm":
                app_status = "ACTIVE"

            elif detected == "Fist":
                app_status = "PAUSED"

            elif detected == "Peace Sign":
                app_status = "MODE SELECTED"

            elif detected == "None":
                app_status = "WAITING"

        # Display information
        cv2.putText(
            frame,
            f"Gesture: {current_gesture}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"App Status: {app_status}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 200, 0),
            2
        )

        cv2.imshow("AI Gesture Studio", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    detector.close()
    cv2.destroyAllWindows()

print("AI Gesture Studio Stopped.")