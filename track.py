"""Track — an ordered sequence of notes, rests, and chords."""

from __future__ import annotations
from typing import List, Union, Iterator
from .note import Note, _Rest
from .chord import Chord

_Event = Union[Note, _Rest, Chord]


class Track:
    """
    A melodic or harmonic track: an ordered sequence of events.

    Parameters
    ----------
    name : str
        Optional human-readable name.
    instrument : int
        General MIDI program number (0–127). Default 0 = Acoustic Grand Piano.
    channel : int
        MIDI channel (0–15). Channel 9 is traditionally drums.

    Examples
    --------
    >>> t = Track("melody")
    >>> t.add(Note("C4"))
    >>> t.add(Note("E4", duration=0.5))
    >>> t.add(Chord.build("G3", "major"))
    >>> t.add(REST.with_duration(1.0))
    >>> t += [Note("A4"), Note("B4")]     # extend with a list
    """

    def __init__(self, name: str = "Track", instrument: int = 0, channel: int = 0):
        self.name = name
        self.instrument = instrument
        self.channel = channel
        self._events: List[_Event] = []

    # ------------------------------------------------------------------
    # Adding events
    # ------------------------------------------------------------------

    def add(self, event: _Event) -> "Track":
        """Append a single note, rest, or chord."""
        self._events.append(event)
        return self

    def extend(self, events) -> "Track":
        """Append an iterable of events."""
        for e in events:
            self._events.append(e)
        return self

    def __iadd__(self, events) -> "Track":
        return self.extend(events)

    def __lshift__(self, event: _Event) -> "Track":
        """``track << Note("C4")`` — fluent append."""
        return self.add(event)

    # ------------------------------------------------------------------
    # Manipulation
    # ------------------------------------------------------------------

    def transpose(self, semitones: int) -> "Track":
        """Return a new Track transposed by *semitones*."""
        t = Track(self.name, self.instrument, self.channel)
        for e in self._events:
            t.add(e.transpose(semitones))
        return t

    def reverse(self) -> "Track":
        """Return a new Track with events in reverse order."""
        t = Track(self.name, self.instrument, self.channel)
        t._events = list(reversed(self._events))
        return t

    def repeat(self, times: int) -> "Track":
        """Return a new Track with this track repeated *times* times."""
        t = Track(self.name, self.instrument, self.channel)
        for _ in range(times):
            t.extend(self._events)
        return t

    def __mul__(self, times: int) -> "Track":
        return self.repeat(times)

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------

    @property
    def duration(self) -> float:
        """Total duration in beats."""
        total = 0.0
        for e in self._events:
            if isinstance(e, Chord):
                total += e.duration
            else:
                total += e.duration
        return total

    def __len__(self):
        return len(self._events)

    def __iter__(self) -> Iterator[_Event]:
        return iter(self._events)

    def __repr__(self):
        return (
            f"Track('{self.name}', {len(self._events)} events, "
            f"duration={self.duration:.2f} beats, instrument={self.instrument})"
        )
