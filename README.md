# AI Gesture Studio

AI Gesture Studio is a Python-based computer vision application that uses a webcam to detect hand landmarks and recognize basic hand gestures in real time.

## Version
V1.0.0 - Initial Prototype

## Features

- Real-time webcam integration
- Hand detection using MediaPipe
- 21 hand landmark tracking
- Open Palm recognition
- Fist recognition
- Peace Sign recognition
- Gesture-based application states
- PyQt6 desktop dashboard
- Camera Start/Stop controls
- Activity logging

## Technologies

- Python
- OpenCV
- MediaPipe
- NumPy
- PyQt6

## Project Structure

```text
AI-Gesture-Studio/
|
├── hand_landmarker.task
├── requirements.txt
├── README.md
├── .gitignore
|
├── src/
|   └── ai_gesture_studio/
|       ├── ui.py
|       ├── camera.py
|       ├── camera_view.py
|       ├── gesture_recognizer.py
|       ├── hand_tracker.py
|       └── mouse_controller.py
|
└── tests/
    └── test_gestures.py


```

## Installation

Clone the repository:

```bash
git clone https://github.com/moazabeer/AI-Gesture-Studio.git
cd AI-Gesture-Studio
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Application

```bash
python src/ai_gesture_studio/main.py
```

## Gesture Controls

| Gesture | Application State |
|---|---|
| Open Palm | ACTIVE |
| Fist | PAUSED |
| Peace Sign | MODE SELECTED |

## Requirements

- Python 3.14.1 (tested environment)
- Webcam
- Windows (current camera configuration)

## Future Development

- Hand-controlled mouse movement
- Pinch-to-click
- Virtual drawing
- Keyboard control
- Additional gestures
- Improved desktop interface

## License

License not yet specified.