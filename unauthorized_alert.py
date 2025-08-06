import cv2
import datetime
import os

def handle_unauthorized(frame):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = "dataset/unknown_faces"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"unauthorized_{timestamp}.jpg")
    cv2.imwrite(path, frame)
    print(f"[ALERT] Unauthorized detected. Saved: {path}")
