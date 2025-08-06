import cv2
import tkinter as tk
from tkinter import StringVar, Label, Button, Frame, simpledialog, messagebox
from PIL import Image, ImageTk
import datetime
import os
from face_recognition_module import recognize_face, load_known_faces
from emotion_detection_module import detect_emotion
from attention_tracking_module import is_attentive
from unauthorized_alert import handle_unauthorized
import pygame

# Songs dictionary
emotion_to_song = {
    'happy': 'songs/happy_song.mp3',
    'sad': 'songs/sad_song.mp3',
    'angry': 'songs/angry_song.mp3',
    'neutral': 'songs/neutral_song.mp3'
}

# Initialize pygame mixer
pygame.mixer.init()

def play_song(song_path):
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

def stop_song():
    pygame.mixer.music.stop()

def capture_face_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open camera")
        return None, None, None

    print("[INFO] Camera on. Press 'c' to capture, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame")
            break

        cv2.imshow("Camera Preview - Press 'c' to capture", frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('c'):
            print("[INFO] Capturing snapshot.")
            break
        elif key & 0xFF == ord('q'):
            print("[INFO] Quitting capture.")
            frame = None
            break

    cap.release()
    cv2.destroyAllWindows()

    if frame is None:
        return None, None, None

    person_name, face_location = recognize_face(frame)
    return frame, person_name, face_location

def launch_gui(frame, person_name, face_location):
    if frame is None:
        print("[ERROR] No frame captured to show GUI.")
        return

    # Crop face image for display
    top, right, bottom, left = face_location
    face_img = frame[top:bottom, left:right]

    # Get emotion & attention
    emotion = detect_emotion(frame)
    attention = is_attentive(frame)

    # Handle unauthorized (your existing code)
    if person_name == "Unknown":
        handle_unauthorized(frame)

    root = tk.Tk()
    root.title("Smart Face Surveillance System")
    root.configure(bg="orange")

    heading = Label(root, text="Smart Face Surveillance & Emotion Tracking System",
                    font=("Arial", 20, "bold"), bg="yellow", fg="black")
    heading.pack(pady=(15, 5))

    photo_frame = Frame(root, bg="black", bd=5)
    photo_frame.pack(pady=10)
    face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(face_img_rgb)
    pil_img = pil_img.resize((300, 300))
    photo = ImageTk.PhotoImage(pil_img)
    img_label = Label(photo_frame, image=photo)
    img_label.image = photo
    img_label.pack()

    details_frame = Frame(root, bg="#FFD580")
    details_frame.pack(side="left", anchor="s", padx=20, pady=20)

    info_text = StringVar()
    info_text.set(f"Name: {person_name}\nEmotion: {emotion}\nAttention: {attention}")
    info_label = Label(details_frame, textvariable=info_text, font=("Arial", 14), bg="#FFD580")
    info_label.pack(pady=5, anchor="w")

    now_playing_var = StringVar()
    now_playing_var.set("")

    song_label = Label(details_frame, textvariable=now_playing_var, font=("Arial", 12, "italic"), bg="#FFD580")
    song_label.pack(pady=5, anchor="w")

    song_path = emotion_to_song.get(emotion.lower())
    if song_path and os.path.exists(song_path):
        play_song(song_path)
        now_playing_var.set(f"Now Playing: {emotion.capitalize()} Song 🎵")

    btn_styles = {
        "Pause": {"bg": "#007BFF", "fg": "white", "activebackground": "#0056b3"},
        "Resume": {"bg": "#FFD700", "fg": "black", "activebackground": "#cca300"},
        "Stop": {"bg": "#FF4136", "fg": "white", "activebackground": "#b2221a"},
        "Restart": {"bg": "#2ECC40", "fg": "white", "activebackground": "#239b29"}
    }

    def pause_song():
        pygame.mixer.music.pause()
        now_playing_var.set("Paused")

    def resume_song():
        pygame.mixer.music.unpause()
        now_playing_var.set(f"Now Playing: {emotion.capitalize()} Song 🎵")

    def stop_song_and_clear():
        stop_song()
        now_playing_var.set("Stopped")

    def restart_current_song():
        if song_path:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            now_playing_var.set(f"🔁 Restarted: {os.path.basename(song_path)}")

    btn_frame = Frame(details_frame, bg="#FFD580")
    btn_frame.pack(pady=10)

    Button(btn_frame, text="Pause", command=pause_song, width=8, font=("Arial", 11, "bold"), **btn_styles["Pause"]).pack(side="left", padx=5)
    Button(btn_frame, text="Resume", command=resume_song, width=8, font=("Arial", 11, "bold"), **btn_styles["Resume"]).pack(side="left", padx=5)
    Button(btn_frame, text="Stop", command=stop_song_and_clear, width=8, font=("Arial", 11, "bold"), **btn_styles["Stop"]).pack(side="left", padx=5)
    Button(btn_frame, text="Restart", command=restart_current_song, width=8, font=("Arial", 11, "bold"), **btn_styles["Restart"]).pack(side="left", padx=5)

    if person_name == "Unknown":
        def add_to_authorized():
            new_name = simpledialog.askstring("Add Authorized Face", "Enter name of the person:")
            if not new_name:
                return

            safe_name = new_name.strip().replace(" ", "_").lower()
            save_path = os.path.join('dataset/authorized_faces', f"{safe_name}.jpg")
            cv2.imwrite(save_path, face_img)

            # Reload known faces after saving
            load_known_faces()

            info_text.set(f"Name: {new_name}\nEmotion: {emotion}\nAttention: {attention}")
            messagebox.showinfo("Success", f"Face added to authorized faces as '{new_name}'. You can now recognize this face.")
            add_auth_btn.config(state=tk.DISABLED)

        add_auth_btn = Button(details_frame, text="Add to Authorized", bg="#4CAF50", fg="white",
                              font=("Arial", 11, "bold"), command=add_to_authorized)
        add_auth_btn.pack(pady=10)

    root.mainloop()

def main():
    frame, person_name, face_location = capture_face_image()
    if frame is not None and person_name is not None and face_location is not None:
        launch_gui(frame, person_name, face_location)
    else:
        print("[INFO] No face captured or user quit.")

if __name__ == "__main__":
    main()
