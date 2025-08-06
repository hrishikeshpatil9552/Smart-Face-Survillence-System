from deepface import DeepFace

def detect_emotion(frame):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        return result[0]['dominant_emotion']
    except Exception as e:
        print(f"[ERROR] Emotion detection failed: {e}")
        return "neutral"
