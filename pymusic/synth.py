"""Synth — simple waveform synthesisers for rendering notes to audio."""

from __future__ import annotations
import math
import struct
from typing import Callable, Dict

# Waveform generators: f(phase) → sample in [-1, 1]
def _sine(phase: float) -> float:
    return math.sin(2 * math.pi * phase)

def _square(phase: float) -> float:
    return 1.0 if (phase % 1.0) < 0.5 else -1.0

def _sawtooth(phase: float) -> float:
    return 2.0 * (phase % 1.0) - 1.0

def _triangle(phase: float) -> float:
    t = phase % 1.0
    return 4.0 * t - 1.0 if t < 0.5 else 3.0 - 4.0 * t

def _noise(phase: float) -> float:
    import random
    return random.uniform(-1.0, 1.0)

_WAVEFORMS: Dict[str, Callable[[float], float]] = {
    "sine":     _sine,
    "square":   _square,
    "sawtooth": _sawtooth,
    "triangle": _triangle,
    "noise":    _noise,
}


class Synth:
    """
    A simple synthesiser that converts notes to PCM audio samples.

    Parameters
    ----------
    waveform : str
        One of ``'sine'``, ``'square'``, ``'sawtooth'``, ``'triangle'``, ``'noise'``.
    sample_rate : int
        Samples per second (default 44100).
    attack : float
        Attack time in seconds.
    decay : float
        Decay time in seconds.
    sustain : float
        Sustain level 0–1.
    release : float
        Release time in seconds.

    Examples
    --------
    >>> s = Synth("sine")
    >>> samples = s.render_note(Note("A4"), bpm=120)
    """

    def __init__(
        self,
        waveform: str = "sine",
        sample_rate: int = 44100,
        attack: float = 0.01,
        decay: float = 0.05,
        sustain: float = 0.8,
        release: float = 0.1,
    ):
        if waveform not in _WAVEFORMS:
            raise ValueError(
                f"Unknown waveform '{waveform}'. "
                f"Available: {list(_WAVEFORMS.keys())}"
            )
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self._wave_fn = _WAVEFORMS[waveform]

    @classmethod
    def waveforms(cls):
        return list(_WAVEFORMS.keys())

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_note(self, note, bpm: float = 120.0) -> bytes:
        """
        Render a single Note to raw 16-bit mono PCM bytes.

        Parameters
        ----------
        note : Note or _Rest
            The note to render.
        bpm : float
            Beats per minute (used to convert beats → seconds).
        """
        beat_sec = 60.0 / bpm
        duration_sec = note.duration * beat_sec

        if getattr(note, "midi", -1) < 0:
            # It's a rest
            n_samples = int(duration_sec * self.sample_rate)
            return b"\x00\x00" * n_samples

        freq = note.freq
        velocity = note.velocity / 127.0
        n_samples = int(duration_sec * self.sample_rate)
        samples = []

        for i in range(n_samples):
            t = i / self.sample_rate
            phase = t * freq
            raw = self._wave_fn(phase)
            env = self._envelope(t, duration_sec)
            sample = raw * env * velocity
            # Clamp and convert to 16-bit
            sample = max(-1.0, min(1.0, sample))
            samples.append(int(sample * 32767))

        return struct.pack(f"<{n_samples}h", *samples)

    def render_chord(self, chord, bpm: float = 120.0) -> bytes:
        """Render a Chord to raw 16-bit mono PCM bytes (notes mixed together)."""
        from .chord import Chord
        rendered = [self.render_note(n, bpm) for n in chord.notes]
        # Mix by averaging
        max_len = max(len(r) for r in rendered)
        # Pad shorter arrays
        padded = [r + b"\x00\x00" * ((max_len - len(r)) // 2) for r in rendered]
        n_notes = len(padded)
        result = []
        for i in range(0, max_len, 2):
            total = sum(
                struct.unpack_from("<h", buf, i)[0]
                for buf in padded
                if i + 1 < len(buf)
            )
            mixed = int(total / n_notes)
            mixed = max(-32768, min(32767, mixed))
            result.append(mixed)
        return struct.pack(f"<{len(result)}h", *result)

    # ------------------------------------------------------------------
    # Envelope
    # ------------------------------------------------------------------

    def _envelope(self, t: float, duration: float) -> float:
        """ADSR envelope value at time *t* seconds within *duration* seconds."""
        a, d, s, r = self.attack, self.decay, self.sustain, self.release
        note_on = max(0.0, duration - r)

        if t < a:
            return t / a if a > 0 else 1.0
        elif t < a + d:
            return 1.0 - (1.0 - s) * ((t - a) / d) if d > 0 else s
        elif t < note_on:
            return s
        elif t < duration:
            remaining = duration - note_on
            return s * (1.0 - (t - note_on) / remaining) if remaining > 0 else 0.0
        return 0.0

    def __repr__(self):
        return f"Synth('{self.waveform}', sr={self.sample_rate})"
