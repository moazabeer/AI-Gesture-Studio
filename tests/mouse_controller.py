import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "src" / "ai_gesture_studio"

sys.path.insert(0, str(APP_PATH))

from mouse_controller import MouseController


@patch("pyautogui.moveTo")
def test_mouse_disabled_by_default(mock_move):
    controller = MouseController()

    controller.move_cursor(0.5, 0.5)

    mock_move.assert_not_called()


@patch("pyautogui.moveTo")
def test_mouse_moves_when_enabled(mock_move):
    controller = MouseController()
    controller.enable()

    controller.move_cursor(0.5, 0.5)

    mock_move.assert_called_once()


def test_mouse_disable():
    controller = MouseController()

    controller.enable()
    controller.disable()

    assert controller.enabled is False