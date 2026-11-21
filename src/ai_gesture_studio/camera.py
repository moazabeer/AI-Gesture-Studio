import cv2


def start_camera():
    print("Starting AI Gesture Studio camera...")

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: Could not open webcam.")
        print("Check whether your webcam is connected or being used by another app.")
        camera.release()
        return

    print("Webcam connected successfully!")
    print("Press Q to close the camera.")

    while True:
        success, frame = camera.read()

        if not success:
            print("ERROR: Could not read webcam frame.")
            break

        cv2.imshow("AI Gesture Studio - Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()
    print("Camera closed.")


if __name__ == "__main__":
    start_camera()