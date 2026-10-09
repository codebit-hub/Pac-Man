"""
Audio manager for loading and playing game sounds and music.
"""

import os
import pygame


class AudioManager:
    """Manages audio loading, looping and playback."""

    def __init__(self) -> None:
        """Init mixer and load audio assests."""

        # Initiating the pygame mixer
        try:
            pygame.mixer.init()

        except pygame.error:
            print("Warning: No audio device detected. Sound disabled.")

        # Validating the path routing
        # base = os.path.dirname(__file__)
        # self.path = os.path.normpath(
        #    os.path.join(base, "..", "assets", "audio", "wav")
        #)
        import sys
        base = getattr(
            sys, '_MEIPASS', os.path.join(os.path.dirname(__file__), "..")
            )
        self.path = os.path.normpath(
            os.path.join(base, "assets", "audio", "wav")
            )

        # sfx dict stores single-shot sound files
        self.sfx: dict[str, pygame.mixer.Sound | None] = {}
        # bgm dict stores only looping sounds
        self.bgm_paths: dict[str, str] = {}
        self.current_bgm: str | None = None

        # Mute state
        self.muted: bool = False

        self._load_assets()

    def _get_path(self, filename: str) -> str:
        """Return the absolute path for an audio file."""
        return os.path.join(self.path, filename)

    def _load_assets(self) -> None:
        """Map filenames and load SFX tightly into memory."""

        self.bgm_paths = {
            "menu": self._get_path("01_menu_intermission.wav"),
            "siren": self._get_path("06_ghost_move.wav"),
            "flee": self._get_path("12_ghost_blue_is_frightened.wav"),
            "victory": self._get_path("16_victory.wav"),
            "pause": self._get_path("18_pause.wav")
        }

        sfx_files = {
            "intro": "02_level_start_intro.wav",
            "waka": "03_pacman_eats_pacgum.wav",
            "power": "04_pacman_eats_power_pellet.wav",
            "eat_ghost": "05_pacman_eats_ghost.wav",
            "respawn": "14_ghost_respawning.wav",
            "death": "15_fail_pacman_dies.wav",
            "game_over": "17_game_over.wav",
            "tick": "19_ui_blip.wav"
        }

        for key, filename in sfx_files.items():
            file_path = self._get_path(filename)
            try:
                self.sfx[key] = pygame.mixer.Sound(file_path)
            except (pygame.error, FileNotFoundError):
                self.sfx[key] = None

    def play_sfx(self, name: str) -> None:
        """Plays specific sound effect once"""

        sound = self.sfx.get(name)
        if sound:
            sound.play()

    def stop_sfx(self) -> None:
        """Stops all currently playing sound effects (e.g., intro, waka)."""
        try:
            pygame.mixer.stop()
        except pygame.error:
            pass

    def play_bgm(self, name: str, loops: int = -1) -> None:
        """Plays a looping track, replaces current track."""

        # Keep playing current loop without restart
        if self.current_bgm == name:
            return

        path = self.bgm_paths.get(name)
        if path and os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(loops)
                self.current_bgm = name

            except pygame.error:
                pass

    def stop_bgm(self) -> None:
        """Stops current looping sound."""

        try:
            pygame.mixer.music.stop()
            self.current_bgm = None

        except pygame.error:
            pass

    def toggle_mute(self) -> None:
        """Toggle mute state for all audio (BGM and SFX)."""
        self.muted = not self.muted
        vol = 0.0 if self.muted else 1.0
        try:
            pygame.mixer.music.set_volume(vol)
            for sound in self.sfx.values():
                if sound:
                    sound.set_volume(vol)
        except pygame.error:
            pass
