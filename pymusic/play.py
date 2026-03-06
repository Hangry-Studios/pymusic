"""play — play a Song directly in the terminal."""

from __future__ import annotations
import sys
import tempfile
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .song import Song
    from .synth import Synth


def play(song: "Song", synth: "Synth | None" = None) -> None:
    """
    Render and play a Song through the system's audio output.

    Works on Windows (winsound), macOS (afplay), and Linux (aplay/paplay).

    Parameters
    ----------
    song : Song
        The song to play.
    synth : Synth, optional
        Synthesiser to use. Defaults to a sine-wave synth.

    Examples
    --------
    >>> from pymusic import Song, Track, Note, play
    >>> song = Song("Test", bpm=120)
    >>> t = Track("melody")
    >>> t.add(Note("C4"))
    >>> song.add_track(t)
    >>> play(song)
    """
    from .export import export_wav

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name

    try:
        export_wav(song, path, synth=synth)
        _play_wav(path)
    finally:
        os.unlink(path)


def _play_wav(path: str) -> None:
    """Play a WAV file using the best available method for the current OS."""
    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)

    elif sys.platform == "darwin":
        import subprocess
        subprocess.run(["afplay", path], check=True)

    else:
        # Linux — try paplay (PulseAudio), then aplay (ALSA)
        import subprocess
        for cmd in [["paplay", path], ["aplay", "-q", path]]:
            try:
                subprocess.run(cmd, check=True)
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        raise RuntimeError(
            "No audio player found. Install 'pulseaudio-utils' (paplay) "
            "or 'alsa-utils' (aplay)."
        )
