import face_recognition
import os
import numpy as np

known_face_encodings = []
known_face_names = []

def load_known_faces(known_faces_dir='known_faces'):
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(known_faces_dir):
        if filename.endswith(('.jpg', '.png')):
            path = os.path.join(known_faces_dir, filename)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                name = os.path.splitext(filename)[0]
                known_face_names.append(name)
            else:
                print(f"Warning: No face found in {filename}")

def recognize_faces(frame):
    import cv2
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    results = []
    for face_encoding, location in zip(face_encodings, face_locations):
        distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if len(distances) > 0:
            best_match_index = np.argmin(distances)
            match = distances[best_match_index] < 0.5
            name = known_face_names[best_match_index] if match else "Unknown"
            distance = distances[best_match_index]
        else:
            match = False
            name = "Unknown"
            distance = 1.0
        results.append((name, match, distance, location))

    return results, len(face_encodings)
