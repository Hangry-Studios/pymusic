"""
examples/twinkle.py
-------------------
Renders "Twinkle Twinkle Little Star" to both WAV and MIDI.
"""

from pymusic import Note, REST, Track, Song, Synth, export_wav, export_midi
from pymusic.rhythm import quarter, half

# --- Build the melody track ---
melody = Track("Melody", instrument=0)   # Acoustic Grand Piano

notes = [
    Note("C4"), Note("C4"), Note("G4"), Note("G4"),
    Note("A4"), Note("A4"), Note("G4"),              # "Twinkle twinkle little star"
    Note("F4"), Note("F4"), Note("E4"), Note("E4"),
    Note("D4"), Note("D4"), Note("C4"),              # "How I wonder what you are"
]
durations = [
    quarter, quarter, quarter, quarter,
    quarter, quarter, half,
    quarter, quarter, quarter, quarter,
    quarter, quarter, half,
]

for note, dur in zip(notes, durations):
    melody.add(note.with_duration(dur))

# --- Assemble song ---
song = Song("Twinkle Twinkle", bpm=100)
song.add_track(melody)

print(song)

# --- Export ---
export_wav(song, "twinkle.wav")
export_midi(song, "twinkle.mid")
print("Saved twinkle.wav and twinkle.mid")
