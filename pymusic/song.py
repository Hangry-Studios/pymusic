"""Song — a container for tracks, BPM, and time signature."""

from __future__ import annotations
from typing import List, Dict, Optional
from .track import Track


class Song:
    """
    A complete musical composition.

    Parameters
    ----------
    title : str
        Name of the song.
    bpm : float
        Beats per minute (tempo).
    time_signature : tuple[int, int]
        e.g. ``(4, 4)`` or ``(3, 4)``.

    Examples
    --------
    >>> song = Song("My Song", bpm=120)
    >>> melody = Track("Melody", instrument=0)
    >>> melody.add(Note("C4"))
    >>> song.add_track(melody)
    >>> export_wav(song, "my_song.wav")
    """

    def __init__(
        self,
        title: str = "Untitled",
        bpm: float = 120.0,
        time_signature: tuple = (4, 4),
    ):
        self.title = title
        self.bpm = bpm
        self.time_signature = time_signature
        self._tracks: List[Track] = []

    # ------------------------------------------------------------------
    # Track management
    # ------------------------------------------------------------------

    def add_track(self, track: Track) -> "Song":
        """Add a Track to the song."""
        self._tracks.append(track)
        return self

    def remove_track(self, name: str) -> "Song":
        """Remove a track by name."""
        self._tracks = [t for t in self._tracks if t.name != name]
        return self

    def get_track(self, name: str) -> Optional[Track]:
        """Return the first track matching *name*, or None."""
        for t in self._tracks:
            if t.name == name:
                return t
        return None

    @property
    def tracks(self) -> List[Track]:
        return list(self._tracks)

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------

    @property
    def beat_duration(self) -> float:
        """Duration of a single beat in seconds."""
        return 60.0 / self.bpm

    @property
    def duration(self) -> float:
        """Duration of the song in beats (length of the longest track)."""
        if not self._tracks:
            return 0.0
        return max(t.duration for t in self._tracks)

    @property
    def duration_seconds(self) -> float:
        """Duration of the song in seconds."""
        return self.duration * self.beat_duration

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"Song('{self.title}', bpm={self.bpm}, "
            f"{len(self._tracks)} tracks, "
            f"duration={self.duration_seconds:.1f}s)"
        )

    def __len__(self):
        return len(self._tracks)

    def __iter__(self):
        return iter(self._tracks)
