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