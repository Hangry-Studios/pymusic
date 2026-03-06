"""Note — a single musical pitch with duration."""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional

# MIDI note number for A4
_A4_MIDI = 69
_A4_FREQ = 440.0

# Note names → semitone offset within an octave
_NAME_TO_SEMI = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4,
    "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11,
}

_SEMI_TO_NAME = ["C", "C#", "D", "D#", "E", "F",
                 "F#", "G", "G#", "A", "A#", "B"]


def midi_to_freq(midi: int) -> float:
    """Convert a MIDI note number to frequency in Hz."""
    return _A4_FREQ * (2 ** ((midi - _A4_MIDI) / 12))


def freq_to_midi(freq: float) -> int:
    """Convert frequency in Hz to the nearest MIDI note number."""
    return round(_A4_MIDI + 12 * math.log2(freq / _A4_FREQ))


@dataclass
class Note:
    """
    Represents a musical note.

    Parameters
    ----------
    name : str
        Note name, e.g. ``"C4"``, ``"F#3"``, ``"Bb5"``.
    duration : float
        Duration in beats (1.0 = one quarter note by default).
    velocity : int
        MIDI velocity 0–127 (controls loudness).
    """

    name: str
    duration: float = 1.0
    velocity: int = 100

    def __post_init__(self):
        self._midi = self._parse_midi(self.name)

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_midi(cls, midi: int, duration: float = 1.0, velocity: int = 100) -> "Note":
        """Create a Note from a MIDI note number (0–127)."""
        octave = (midi // 12) - 1
        name = _SEMI_TO_NAME[midi % 12]
        return cls(f"{name}{octave}", duration=duration, velocity=velocity)

    @classmethod
    def from_freq(cls, freq: float, duration: float = 1.0, velocity: int = 100) -> "Note":
        """Create a Note from a frequency in Hz (snapped to nearest pitch)."""
        return cls.from_midi(freq_to_midi(freq), duration=duration, velocity=velocity)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def midi(self) -> int:
        """MIDI note number (0–127)."""
        return self._midi

    @property
    def freq(self) -> float:
        """Frequency in Hz."""
        return midi_to_freq(self._midi)

    @property
    def octave(self) -> int:
        name = self.name.rstrip("0123456789-")
        return int(self.name[len(name):])

    @property
    def pitch_class(self) -> str:
        """Return the pitch name without the octave, e.g. ``'F#'``."""
        return self.name.rstrip("0123456789-")

    # ------------------------------------------------------------------
    # Operators
    # ------------------------------------------------------------------

    def transpose(self, semitones: int) -> "Note":
        """Return a new Note shifted by *semitones*."""
        return Note.from_midi(
            max(0, min(127, self._midi + semitones)),
            duration=self.duration,
            velocity=self.velocity,
        )

    def __add__(self, semitones: int) -> "Note":
        return self.transpose(semitones)

    def __sub__(self, semitones: int) -> "Note":
        return self.transpose(-semitones)

    def with_duration(self, duration: float) -> "Note":
        """Return a copy with a different duration."""
        return Note(self.name, duration=duration, velocity=self.velocity)

    def with_velocity(self, velocity: int) -> "Note":
        """Return a copy with a different velocity."""
        return Note(self.name, duration=self.duration, velocity=velocity)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_midi(name: str) -> int:
        """Parse a note name like ``'C#4'`` into a MIDI number."""
        # Split pitch class from octave
        i = 0
        while i < len(name) and not (name[i].isdigit() or name[i] == "-"):
            i += 1
        pitch = name[:i]
        octave = int(name[i:])
        if pitch not in _NAME_TO_SEMI:
            raise ValueError(f"Unknown note name: '{pitch}'. Use names like C, D#, Bb.")
        semi = _NAME_TO_SEMI[pitch]
        midi = (octave + 1) * 12 + semi
        if not 0 <= midi <= 127:
            raise ValueError(f"MIDI note {midi} out of range for '{name}'.")
        return midi

    def __repr__(self):
        return f"Note('{self.name}', duration={self.duration}, velocity={self.velocity})"

    def __eq__(self, other):
        if isinstance(other, Note):
            return self._midi == other._midi and self.duration == other.duration
        return NotImplemented

    def __hash__(self):
        return hash((self._midi, self.duration))


# Singleton rest marker
class _Rest:
    """Represents a musical rest (silence)."""
    def __init__(self):
        self.duration = 1.0
        self.velocity = 0
        self.midi = -1
        self.freq = 0.0
        self.name = "REST"

    def with_duration(self, duration: float) -> "_Rest":
        r = _Rest()
        r.duration = duration
        return r

    def __repr__(self):
        return f"REST(duration={self.duration})"


REST = _Rest()
