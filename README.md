# 🎵 pymusic

**Make music with Python code.** Define notes, chords, scales, and tracks — then export to WAV or MIDI. No dependencies, pure Python 3.9+.

```python
from pymusic import Note, Scale, Track, Song, export_wav, export_midi

scale = Scale("C4", "major")
melody = Track("Melody", instrument=0)
melody.extend(scale.notes(duration=0.5))

song = Song("Hello, Music!", bpm=120)
song.add_track(melody)

export_wav(song, "hello.wav")
export_midi(song, "hello.mid")
```

---

## Installation

```bash
pip install pymusic           # once published to PyPI
# or install directly from source:
git clone https://github.com/Hangry-Studios/pymusic
cd pymusic
pip install -e .
```

---

## Core concepts

| Class | Description |
|-------|-------------|
| `Note` | A single pitch with duration and velocity |
| `REST` | A silence with duration |
| `Chord` | Multiple notes sounded together |
| `Scale` | A key + mode, with helper methods |
| `Track` | An ordered sequence of notes/chords |
| `Song` | Multiple tracks + tempo + time signature |
| `Synth` | Renders notes to audio (sine, square, sawtooth, triangle) |
| `Pattern` | A rhythm template (list of durations) |

---

## Notes

```python
from pymusic import Note, REST

n = Note("C4")              # middle C
n = Note("F#3", duration=2.0, velocity=80)
n = Note.from_midi(69)      # A4 = MIDI 69
n = Note.from_freq(440.0)   # nearest pitch to 440 Hz

n.midi     # → 69
n.freq     # → 440.0
n.octave   # → 4
n.pitch_class  # → "A"

n + 7      # transpose up 7 semitones → E5
n - 12     # transpose down one octave

REST.with_duration(1.0)    # one beat of silence
```

Supported note names: `C`, `C#` / `Db`, `D`, `D#` / `Eb`, `E`, `F`, `F#` / `Gb`, `G`, `G#` / `Ab`, `A`, `A#` / `Bb`, `B` — followed by an octave number (`C4`, `Bb2`, `F#5`, etc.)

---

## Chords

```python
from pymusic import Chord

c = Chord.build("C4", "major")       # C E G
c = Chord.build("G3", "dom7")        # G B D F
c = Chord.build("A4", "minor")       # A C E

c.transpose(5)          # up a perfect fourth
c.invert(1)             # first inversion
c.with_velocity(90)

Chord.types()           # list all available chord types
```

Available chord types: `major`, `minor`, `dim`, `aug`, `sus2`, `sus4`, `maj7`, `min7`, `dom7`, `dim7`, `maj9`, `min9`, `add9`, `power`.

---

## Scales

```python
from pymusic import Scale, SCALES

s = Scale("C4", "major")
s = Scale("A3", "pentatonic_minor")
s = Scale("D4", "blues")

s.notes()               # list of Note objects (one octave)
s.notes(octaves=2)      # two octaves
s.degree(5)             # 5th scale degree (1-indexed)
s[4]                    # 5th degree (0-indexed)
s.chord(1)              # triad on degree 1
s.chord(5, size=4)      # seventh chord on degree 5
s.progression([1,4,5,1])  # I-IV-V-I chord progression

list(SCALES.keys())     # all scale names
```

Available scales: `major`, `minor`, `harmonic_minor`, `melodic_minor`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `locrian`, `pentatonic_major`, `pentatonic_minor`, `blues`, `chromatic`, `whole_tone`, `diminished`, `augmented`.

---

## Rhythm

```python
from pymusic.rhythm import whole, half, quarter, eighth, sixteenth, Pattern

p = Pattern([quarter, eighth, eighth, half])
notes = [Note("C4"), Note("D4"), Note("E4"), Note("F4")]
rhythmic_notes = p.apply(notes)  # assigns durations cyclically
```

Duration constants (in beats): `whole=4`, `half=2`, `quarter=1`, `eighth=0.5`, `sixteenth=0.25`, `dotted_half=3`, `dotted_quarter=1.5`, `triplet_quarter≈0.667`.

---

## Tracks

```python
from pymusic import Track, Note, REST
from pymusic import Chord

t = Track("Melody", instrument=0, channel=0)

t.add(Note("C4"))
t.add(REST.with_duration(1.0))
t.add(Chord.build("G3", "major"))

t << Note("A4") << Note("B4")          # fluent append

t.extend([Note("C4"), Note("E4")])     # add a list
t += [Note("G4"), Note("C5")]          # same with +=

t.transpose(12)    # new track one octave up
t.reverse()        # new track in reverse
t * 4              # repeat 4 times
t.duration         # total duration in beats
```

General MIDI instruments: `0` = Piano, `25` = Acoustic Guitar, `27` = Clean Electric Guitar, `32` = Acoustic Bass, `40` = Violin, `48` = Strings, `56` = Trumpet, `73` = Flute, and [many more](https://en.wikipedia.org/wiki/General_MIDI#Program_change_events).

---

## Songs

```python
from pymusic import Song

song = Song("My Song", bpm=120, time_signature=(4, 4))
song.add_track(melody_track)
song.add_track(chord_track)
song.add_track(bass_track)

song.duration           # beats
song.duration_seconds   # seconds
song.get_track("Bass")  # retrieve a track by name
song.remove_track("Bass")
```

---

## Synth & export

```python
from pymusic import Synth, export_wav, export_midi

# Export using the default sine synth
export_wav(song, "output.wav")
export_midi(song, "output.mid")

# Custom synth
syn = Synth(
    waveform="sawtooth",  # sine | square | sawtooth | triangle | noise
    sample_rate=44100,
    attack=0.02,
    decay=0.1,
    sustain=0.7,
    release=0.15,
)
export_wav(song, "output.wav", synth=syn)
```

---

## Full example: Twinkle Twinkle

```python
from pymusic import Note, Track, Song, export_wav
from pymusic.rhythm import quarter, half

melody = Track("Melody")
pairs = [
    ("C4", quarter), ("C4", quarter), ("G4", quarter), ("G4", quarter),
    ("A4", quarter), ("A4", quarter), ("G4", half),
    ("F4", quarter), ("F4", quarter), ("E4", quarter), ("E4", quarter),
    ("D4", quarter), ("D4", quarter), ("C4", half),
]
for name, dur in pairs:
    melody.add(Note(name, duration=dur))

song = Song("Twinkle Twinkle", bpm=100)
song.add_track(melody)
export_wav(song, "twinkle.wav")
```

See the [`examples/`](examples/) folder for more complete demos.

---

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

---

## License

MIT © Hangry Studios
