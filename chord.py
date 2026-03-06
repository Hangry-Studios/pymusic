"""Chord — multiple notes played simultaneously."""

from __future__ import annotations
from typing import List, Union
from .note import Note, _Rest

NoteOrRest = Union[Note, _Rest]


# Common chord intervals (semitones from root)
_CHORD_TYPES = {
    "major":       [0, 4, 7],
    "minor":       [0, 3, 7],
    "dim":         [0, 3, 6],
    "aug":         [0, 4, 8],
    "sus2":        [0, 2, 7],
    "sus4":        [0, 5, 7],
    "maj7":        [0, 4, 7, 11],
    "min7":        [0, 3, 7, 10],
    "dom7":        [0, 4, 7, 10],
    "dim7":        [0, 3, 6, 9],
    "maj9":        [0, 4, 7, 11, 14],
    "min9":        [0, 3, 7, 10, 14],
    "add9":        [0, 4, 7, 14],
    "power":       [0, 7],
}


class Chord:
    """
    A set of notes sounded together.

    Parameters
    ----------
    notes : list of Note
        Notes in the chord.
    duration : float
        Duration in beats.

    Examples
    --------
    >>> Chord.build("C4", "major")
    Chord([C4, E4, G4])

    >>> Chord([Note("C4"), Note("E4"), Note("G4")])
    Chord([C4, E4, G4])
    """

    def __init__(self, notes: List[Note], duration: float = 1.0):
        self.notes = list(notes)
        self.duration = duration
        # Sync individual note durations
        for n in self.notes:
            n.duration = duration

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def build(cls, root: str, quality: str = "major", duration: float = 1.0) -> "Chord":
        """
        Build a chord from a root note name and a quality string.

        Parameters
        ----------
        root : str
            Root note name, e.g. ``"C4"`` or ``"F#3"``.
        quality : str
            Chord quality: ``'major'``, ``'minor'``, ``'dom7'``, etc.
        duration : float
            Duration in beats.
        """
        if quality not in _CHORD_TYPES:
            raise ValueError(
                f"Unknown chord type '{quality}'. "
                f"Available: {list(_CHORD_TYPES.keys())}"
            )
        root_note = Note(root)
        intervals = _CHORD_TYPES[quality]
        notes = [root_note.transpose(i).with_duration(duration) for i in intervals]
        return cls(notes, duration=duration)

    @classmethod
    def types(cls):
        """Return available chord quality names."""
        return list(_CHORD_TYPES.keys())

    # ------------------------------------------------------------------
    # Operators
    # ------------------------------------------------------------------

    def transpose(self, semitones: int) -> "Chord":
        """Return a new Chord transposed by *semitones*."""
        return Chord([n.transpose(semitones) for n in self.notes], self.duration)

    def __add__(self, semitones: int) -> "Chord":
        return self.transpose(semitones)

    def with_duration(self, duration: float) -> "Chord":
        return Chord([n.with_duration(duration) for n in self.notes], duration)

    def with_velocity(self, velocity: int) -> "Chord":
        return Chord([n.with_velocity(velocity) for n in self.notes], self.duration)

    def invert(self, n: int = 1) -> "Chord":
        """Return the nth inversion of the chord."""
        notes = list(self.notes)
        for _ in range(n % len(notes)):
            lowest = notes.pop(0)
            notes.append(lowest.transpose(12))
        return Chord(notes, self.duration)

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def __repr__(self):
        names = ", ".join(n.name for n in self.notes)
        return f"Chord([{names}], duration={self.duration})"

    def __iter__(self):
        return iter(self.notes)

    def __len__(self):
        return len(self.notes)
