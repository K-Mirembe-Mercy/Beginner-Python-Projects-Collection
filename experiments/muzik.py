import os
import tkinter as tk
from tkinter import filedialog
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Define the MusicPlayer class
class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")
        self.root.geometry("400x200")

        # Add Play, Stop, Pause, and Load buttons
        self.is_playing = False
        self.is_paused = False

        self.play_button = tk.Button(self.root, text="Play", width=10, command=self.play_music)
        self.play_button.pack(pady=10)

        self.pause_button = tk.Button(self.root, text="Pause", width=10, command=self.pause_music)
        self.pause_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", width=10, command=self.stop_music)
        self.stop_button.pack(pady=10)

        self.load_button = tk.Button(self.root, text="Load", width=10, command=self.load_music)
        self.load_button.pack(pady=10)

        self.music_file = ""

    def play_music(self):
        if self.music_file and not self.is_playing:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def pause_music(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
        elif self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def load_music(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav;*.ogg")])
        if file_path:
            self.music_file = file_path
            self.is_playing = False
            self.is_paused = False
            print(f"Loaded: {file_path}")

# Create the main window (root)
root = tk.Tk()

# Instantiate the MusicPlayer class
music_player = MusicPlayer(root)

# Run the main loop
root.mainloop()
