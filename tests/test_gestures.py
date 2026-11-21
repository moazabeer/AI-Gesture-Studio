import sys
from pathlib import Path
from types import SimpleNamespace

# Add application directory to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "src" / "ai_gesture_studio"

sys.path.insert(0, str(APP_PATH))

from gesture_recognizer import recognize_gesture


def create_hand(index, middle, ring, pinky):
    hand = [
        SimpleNamespace(x=0.5, y=0.8)
        for _ in range(21)
    ]

    fingers = [
        (index, 8, 6),
        (middle, 12, 10),
        (ring, 16, 14),
        (pinky, 20, 18),
    ]

    for is_up, tip, pip in fingers:
        hand[tip].y = 0.2 if is_up else 0.9
        hand[pip].y = 0.5

    return hand


def test_open_palm():
    hand = create_hand(True, True, True, True)
    assert recognize_gesture(hand) == "Open Palm"


def test_fist():
    hand = create_hand(False, False, False, False)
    assert recognize_gesture(hand) == "Fist"


def test_peace_sign():
    hand = create_hand(True, True, False, False)
    assert recognize_gesture(hand) == "Peace Sign"


def test_unknown_gesture():
    hand = create_hand(True, False, True, False)
    assert recognize_gesture(hand) == "Unknown"