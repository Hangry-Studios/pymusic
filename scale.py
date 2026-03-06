"""Scale — a collection of pitches in a key."""

from __future__ import annotations
from typing import List
from .note import Note

# Scale formulas as semitone intervals (from root to root+octave)
SCALES = {
    "major":            [0, 2, 4, 5, 7, 9, 11],
    "minor":            [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor":   [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor":    [0, 2, 3, 5, 7, 9, 11],
    "dorian":           [0, 2, 3, 5, 7, 9, 10],
    "phrygian":         [0, 1, 3, 5, 7, 8, 10],
    "lydian":           [0, 2, 4, 6, 7, 9, 11],
    "mixolydian":       [0, 2, 4, 5, 7, 9, 10],
    "locrian":          [0, 1, 3, 5, 6, 8, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues":            [0, 3, 5, 6, 7, 10],
    "chromatic":        list(range(12)),
    "whole_tone":       [0, 2, 4, 6, 8, 10],
    "diminished":       [0, 2, 3, 5, 6, 8, 9, 11],
    "augmented":        [0, 3, 4, 7, 8, 11],
}


class Scale:
    """
    A musical scale rooted on a given note.

    Parameters
    ----------
    root : str
        Root note name, e.g. ``"C4"`` or ``"A3"``.
    quality : str
        Scale type (see ``pymusic.SCALES`` for available names).

    Examples
    --------
    >>> s = Scale("C4", "major")
    >>> s.notes()          # all notes in the scale (one octave)
    >>> s[0]               # first degree (root)
    >>> s.degree(5)        # fifth degree
    >>> s.chord(1)         # triad built on the first degree
    """

    def __init__(self, root: str, quality: str = "major"):
        if quality not in SCALES:
            raise ValueError(
                f"Unknown scale '{quality}'. "
                f"Available: {list(SCALES.keys())}"
            )
        self.root = Note(root)
        self.quality = quality
        self._intervals = SCALES[quality]

    # ------------------------------------------------------------------
    # Note access
    # ------------------------------------------------------------------

    def notes(self, octaves: int = 1, duration: float = 1.0) -> List[Note]:
        """Return all notes in the scale over *octaves* octaves."""
        result = []
        for o in range(octaves):
            for interval in self._intervals:
                result.append(
                    self.root.transpose(interval + o * 12).with_duration(duration)
                )
        # Add the final root note at the top
        result.append(self.root.transpose(octaves * 12).with_duration(duration))
        return result

    def __getitem__(self, degree: int) -> Note:
        """Get the note at *degree* (0-indexed)."""
        n = len(self._intervals)
        octave_shift, idx = divmod(degree, n)
        return self.root.transpose(self._intervals[idx] + octave_shift * 12)

    def degree(self, n: int, duration: float = 1.0) -> Note:
        """Get a scale degree (1-indexed, like music theory)."""
        return self[n - 1].with_duration(duration)

    # ------------------------------------------------------------------
    # Chord building
    # ------------------------------------------------------------------

    def chord(self, degree: int, size: int = 3, duration: float = 1.0):
        """
        Build a diatonic chord on *degree* (1-indexed) by stacking thirds.

        Parameters
        ----------
        degree : int
            Scale degree (1 = tonic, 4 = subdominant, 5 = dominant, …).
        size : int
            Number of notes: 3 = triad, 4 = seventh chord, 5 = ninth.
        """
        from .chord import Chord
        notes = []
        for i in range(size):
            notes.append(self[degree - 1 + i * 2].with_duration(duration))
        return Chord(notes, duration=duration)

    def progression(self, degrees: List[int], duration: float = 2.0):
        """
        Return a list of chords for a degree progression.

        Example
        -------
        >>> s.progression([1, 4, 5, 1])   # I–IV–V–I
        """
        return [self.chord(d, duration=duration) for d in degrees]

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def __len__(self):
        return len(self._intervals)

    def __repr__(self):
        return f"Scale('{self.root.name}', '{self.quality}', {len(self._intervals)} notes)"
