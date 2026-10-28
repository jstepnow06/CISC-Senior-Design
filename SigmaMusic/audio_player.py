from pathlib import Path

import customtkinter as ctk
import pygame
from mutagen import File as MutagenFile

from styles import BUTTON_STYLE


class AudioPlayer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(1, weight=1)

        self.file_label = ctk.CTkLabel(
            self,
            text="No audio file selected",
            text_color="gold",
            font=("Centaur", 20),
        )
        self.file_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 4))

        self.play_pause_btn = ctk.CTkButton(
            self,
            text="Play",
            width=100,
            command=self.toggle_playback,
            state="disabled",
            **BUTTON_STYLE,
        )
        self.play_pause_btn.grid(row=1, column=0, padx=(10, 5), pady=8)

        self.seek_slider = ctk.CTkSlider(
            self,
            from_=0,
            to=1,
            command=self.seek_audio,
            state="disabled",
            progress_color="gold",
            button_color="gold",
            button_hover_color="#d4af37",
        )
        self.seek_slider.set(0)
        self.seek_slider.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        self.seek_slider.bind("<ButtonPress-1>", self.seek_started)
        self.seek_slider.bind("<ButtonRelease-1>", self.seek_finished)

        self.time_label = ctk.CTkLabel(self, text="00:00 / 00:00")
        self.time_label.grid(row=1, column=2, padx=(5, 10), pady=8)

        self.audio_path: Path | None = None
        self.audio_duration = 0.0
        self.is_paused = False
        self.is_seeking = False
        self.update_playback_position()

    def load_audio(self, audio_path: Path) -> bool:
        audio_info = MutagenFile(audio_path)
        if audio_info is None or audio_info.info.length <= 0:
            self.file_label.configure(text="Could not read the audio duration")
            self.play_pause_btn.configure(state="disabled")
            self.seek_slider.configure(state="disabled")
            return False

        self.stop_audio()
        self.audio_path = audio_path
        self.audio_duration = float(audio_info.info.length)
        self.file_label.configure(text=f"Loaded: {audio_path.name}")
        self.time_label.configure(text=f"00:00 / {self.format_time(self.audio_duration)}")
        self.seek_slider.configure(to=self.audio_duration, state="normal")
        self.seek_slider.set(0)
        self.play_pause_btn.configure(text="Play", state="normal")
        return True

    def toggle_playback(self):
        if self.audio_path is None:
            return

        self.initialize_mixer()
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        elif pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True
        else:
            pygame.mixer.music.load(str(self.audio_path))
            pygame.mixer.music.play()
            self.seek_slider.set(0)
            self.is_paused = False

        self.play_pause_btn.configure(text="Pause" if not self.is_paused else "Play")

    def seek_audio(self, value):
        if self.audio_path is None or self.is_seeking:
            return

        self.initialize_mixer()
        was_playing = pygame.mixer.music.get_busy() and not self.is_paused
        pygame.mixer.music.load(str(self.audio_path))
        pygame.mixer.music.play(start=float(value))
        if not was_playing:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.play_pause_btn.configure(text="Play")

    def seek_finished(self, _event=None):
        self.is_seeking = False
        self.seek_audio(self.seek_slider.get())

    def update_playback_position(self):
        if self.audio_path is not None and pygame.mixer.get_init() and not self.is_seeking:
            if pygame.mixer.music.get_busy() and not self.is_paused:
                position = max(0.0, pygame.mixer.music.get_pos() / 1000)
                position = min(position, self.audio_duration)
                self.seek_slider.set(position)
                self.time_label.configure(
                    text=f"{self.format_time(position)} / {self.format_time(self.audio_duration)}"
                )
            elif self.seek_slider.get() >= self.audio_duration and self.audio_duration:
                self.play_pause_btn.configure(text="Play")
                self.is_paused = False

        self.after(250, self.update_playback_position)

    def stop_audio(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.is_paused = False

    def close(self):
        self.stop_audio()
        if pygame.mixer.get_init():
            pygame.mixer.quit()

    def initialize_mixer(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    def seek_started(self, _event=None):
        self.is_seeking = True

    @staticmethod
    def format_time(seconds):
        total_seconds = max(0, int(seconds))
        return f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"
