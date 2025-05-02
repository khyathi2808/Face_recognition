import cv2
import datetime
import os
import time


calibrated_center = None
off_screen_start_time = None
off_screen_logged = False
current_off_direction = None

def detect_gaze(frame, face_landmarks, person_name, folder="violations"):
    global calibrated_center, off_screen_start_time, off_screen_logged, current_off_direction

    def gaze_ratio(eye):
        left = eye[0]
        right = eye[3]
        return abs(right[0] - left[0])

    if 'left_eye' not in face_landmarks or 'right_eye' not in face_landmarks:
        return "Unknown"

    left_eye = face_landmarks['left_eye']
    right_eye = face_landmarks['right_eye']
    left = gaze_ratio(left_eye)
    right = gaze_ratio(right_eye)
    current_ratio = (left + right) / 2.0

    threshold = 0.3
    gaze = "Center"

    if calibrated_center is None:
        calibrated_center = current_ratio
        print(f"[CALIBRATED] Center gaze ratio set to {calibrated_center:.2f}")
        return "Center"

    if current_ratio < calibrated_center - threshold:
        gaze = "Off"
    elif current_ratio > calibrated_center + threshold:
        gaze = "Off"
    else:
        gaze = "Center"

  
    if gaze == "Off":
        if off_screen_start_time is None or current_off_direction != "Off":
            off_screen_start_time = time.time()
            off_screen_logged = False
            current_off_direction = "Off"
        elif not off_screen_logged and (time.time() - off_screen_start_time) >= 3:
            log_off_screen(person_name, folder)
            off_screen_logged = True
    else:
        off_screen_start_time = None
        off_screen_logged = False
        current_off_direction = None

    return gaze

def log_off_screen(person_name, folder):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(folder, f"{person_name}_{date_str}.txt")

    os.makedirs(folder, exist_ok=True)

    with open(filename, "a") as f:
        f.write(f"- Gaze off-screen at {timestamp}\n")
