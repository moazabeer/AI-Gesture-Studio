import time
import pyautogui


class MouseController:

    def __init__(self, smoothing=0.45, click_cooldown=0.6):

        self.screen_width, self.screen_height = pyautogui.size()

        self.smoothing = smoothing
        self.click_cooldown = click_cooldown

        self.current_x = 0
        self.current_y = 0

        self.enabled = False
        self.last_click_time = 0

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def move_cursor(self, landmark_x, landmark_y):

        if not self.enabled:
            return

        landmark_x = max(0, min(1, landmark_x))
        landmark_y = max(0, min(1, landmark_y))

        target_x = landmark_x * (self.screen_width - 1)
        target_y = landmark_y * (self.screen_height - 1)

        self.current_x += (
            target_x - self.current_x
        ) * self.smoothing

        self.current_y += (
            target_y - self.current_y
        ) * self.smoothing

        pyautogui.moveTo(
            int(self.current_x),
            int(self.current_y)
        )

    def pinch_to_click(self, thumb, index):

        if not self.enabled:
            return False

        distance = (
            (thumb.x - index.x) ** 2
            + (thumb.y - index.y) ** 2
        ) ** 0.5

        if distance < 0.045:

            current_time = time.monotonic()

            if current_time - self.last_click_time >= self.click_cooldown:

                pyautogui.click()
                self.last_click_time = current_time

                return True

        return False