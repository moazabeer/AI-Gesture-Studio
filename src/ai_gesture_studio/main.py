from ui import GestureStudio

import sys
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)

    window = GestureStudio()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()