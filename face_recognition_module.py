import face_recognition
import cv2
import os
import numpy as np

# Folder containing authorized face images
AUTHORIZED_FOLDER = 'dataset/authorized_faces'

# Lists to store face encodings and names
known_face_encodings = []
known_face_names = []

def load_known_faces():
    """Loads all known faces from the authorized folder."""
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(AUTHORIZED_FOLDER):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(AUTHORIZED_FOLDER, filename)
            image = cv2.imread(path)

            if image is None:
                print(f"[ERROR] Could not load {filename}")
                continue

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb)

            if not face_locations:
                print(f"[WARNING] No face found in {filename}")
                continue

            encodings = face_recognition.face_encodings(rgb, face_locations)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(filename)[0])  # Remove file extension
                print(f"[INFO] Loaded: {filename}")
            else:
                print(f"[WARNING] No encoding found in {filename}")

# Initial load
load_known_faces()

def recognize_face(frame, tolerance=0.45):
    """
    Recognizes a face in the given frame.
    Returns (name, face_location) tuple.
    If not recognized confidently, returns "Unknown".
    """
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb)

    if not face_locations:
        return "Unknown", None

    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
        # Compare with a stricter threshold
        matches = face_recognition.compare_faces(known_face_encodings, encoding, tolerance=tolerance)
        name = "Unknown"

        if True in matches:
            distances = face_recognition.face_distance(known_face_encodings, encoding)
            best_match = np.argmin(distances)

            if matches[best_match]:
                name = known_face_names[best_match]

        return name, (top, right, bottom, left)

    return "Unknown", None
