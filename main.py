import cv2
import face_recognition
from recognizer import load_known_faces, recognize_faces
from violation_logger import handle_violation, finalize_report
from gaze_detection import detect_gaze

def main():
    load_known_faces()
    video_capture = cv2.VideoCapture(0)
    print("Press 'q' to quit monitoring...")

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Unable to access the camera.")
                break

            results, face_count = recognize_faces(frame)
            handle_violation(face_count, results)

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            landmarks_list = face_recognition.face_landmarks(rgb_small_frame)

            for (name, match, distance, location) in results:
                if not match:
                    continue  # Only log gaze for identified people

                for i, landmark in enumerate(landmarks_list):
                    if i < len(face_locations) and location == face_locations[i]:
                        detect_gaze(frame, landmark, name)  # Gaze logging with 3s off-screen
                        break

                top, right, bottom, left = [v * 4 for v in location]
                label = f"Face Matched: {name}"
                color = (0, 255, 0)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, label, (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

            cv2.imshow("Identity Verification", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        video_capture.release()
        cv2.destroyAllWindows()
        finalize_report()

if __name__ == "__main__":
    main()
