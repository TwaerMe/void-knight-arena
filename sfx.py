import os
import sys
import time
import pygame


def _res_path(rel_path):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)


class SoundManager:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.volume = 0.65
        self.sounds = {}
        self.last_played = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(32)
            self.enabled = True
            self._load_all()
        except Exception:
            self.enabled = False

    def _load_all(self):
        sfx_dir = _res_path(os.path.join("assets", "sfx"))
        if not os.path.isdir(sfx_dir):
            return
        for fname in os.listdir(sfx_dir):
            if fname.endswith(".wav"):
                key = fname[:-4]
                try:
                    snd = pygame.mixer.Sound(os.path.join(sfx_dir, fname))
                    snd.set_volume(self.volume)
                    self.sounds[key] = snd
                except Exception:
                    pass

    def toggle_mute(self):
        self.muted = not self.muted

    def adjust_volume(self, delta):
        self.volume = max(0.0, min(1.0, round(self.volume + delta, 2)))
        for snd in self.sounds.values():
            snd.set_volume(self.volume)

    def play(self, name, vol_mult=1.0, cooldown=0.025):
        if not self.enabled or self.muted:
            return
        snd = self.sounds.get(name)
        if not snd:
            return
        now = time.perf_counter()
        if now - self.last_played.get(name, 0.0) < cooldown:
            return
        self.last_played[name] = now
        snd.set_volume(max(0.0, min(1.0, self.volume * vol_mult)))
        snd.play()
