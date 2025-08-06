# music_player.py
import os
import pygame

emotion_to_song = {
    'happy': 'songs/happy_song.mp3',
    'sad': 'songs/sad_song.mp3',
    'angry': 'songs/angry_song.mp3',
    'neutral': 'songs/neutral_song.mp3'
}

pygame.mixer.init()
last_played = None

def play_song_for_emotion(emotion, now_playing_var=None):
    global last_played
    song_path = emotion_to_song.get(emotion.lower())
    if song_path and os.path.exists(song_path) and song_path != last_played:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        last_played = song_path
        print(f"[INFO] Playing: {song_path}")
        if now_playing_var:
            now_playing_var.set(f"Now Playing: 🎵 {os.path.basename(song_path)}")

def pause_song():
    pygame.mixer.music.pause()

def resume_song():
    pygame.mixer.music.unpause()

def stop_song():
    pygame.mixer.music.stop()

def set_volume(volume_percent):
    pygame.mixer.music.set_volume(volume_percent / 100.0)
