from pymusic import Note, Track, Song, export_wav, export_midi
from pymusic.play import play
from pymusic.rhythm import quarter, half

melody = Track("Melody", instrument=0)

notes = [
    Note("C4"), Note("C4"), Note("G4"), Note("G4"),
    Note("A4"), Note("A4"), Note("G4"),
    Note("F4"), Note("F4"), Note("E4"), Note("E4"),
    Note("D4"), Note("D4"), Note("C4"),
]
durations = [
    quarter, quarter, quarter, quarter,
    quarter, quarter, half,
    quarter, quarter, quarter, quarter,
    quarter, quarter, half,
]

for note, dur in zip(notes, durations):
    melody.add(note.with_duration(dur))

song = Song("Twinkle Twinkle", bpm=100)
song.add_track(melody)

print(song)
export_wav(song, "twinkle.wav")
export_midi(song, "twinkle.mid")
print("Saved twinkle.wav and twinkle.mid")

print("Playing...")
play(song)