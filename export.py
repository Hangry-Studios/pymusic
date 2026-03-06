"""Export — render a Song to WAV or MIDI files."""

from __future__ import annotations
import struct
import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .song import Song
    from .synth import Synth


# ---------------------------------------------------------------------------
# WAV export
# ---------------------------------------------------------------------------

def export_wav(
    song: "Song",
    path: str,
    synth: "Synth | None" = None,
    sample_rate: int = 44100,
) -> str:
    """
    Render *song* to a WAV file at *path*.

    Parameters
    ----------
    song : Song
        The song to render.
    path : str
        Output file path (should end in ``.wav``).
    synth : Synth, optional
        Synthesiser to use. Defaults to a sine-wave synth.
    sample_rate : int
        Samples per second.

    Returns
    -------
    str
        The output path.
    """
    from .synth import Synth
    from .chord import Chord
    from .note import _Rest

    if synth is None:
        synth = Synth("sine", sample_rate=sample_rate)

    # ------------------------------------------------------------------
    # Render each track to a time-indexed sample buffer
    # ------------------------------------------------------------------
    beat_sec = 60.0 / song.bpm
    total_sec = song.duration_seconds + 0.5   # small tail
    total_samples = int(total_sec * sample_rate)
    mix_buffer = [0.0] * total_samples

    for track in song.tracks:
        cursor = 0  # in samples
        for event in track:
            if isinstance(event, Chord):
                pcm = synth.render_chord(event, bpm=song.bpm)
            else:
                pcm = synth.render_note(event, bpm=song.bpm)

            # Convert bytes to int samples and add to mix
            n = len(pcm) // 2
            for i in range(n):
                idx = cursor + i
                if idx < total_samples:
                    sample = struct.unpack_from("<h", pcm, i * 2)[0]
                    mix_buffer[idx] += sample / 32768.0

            duration_sec = (
                event.duration if isinstance(event, (Chord, _Rest))
                else event.duration
            )
            cursor += int(duration_sec * beat_sec * sample_rate)

    # ------------------------------------------------------------------
    # Normalize
    # ------------------------------------------------------------------
    peak = max(abs(v) for v in mix_buffer) or 1.0
    if peak > 1.0:
        mix_buffer = [v / peak for v in mix_buffer]

    # ------------------------------------------------------------------
    # Write WAV
    # ------------------------------------------------------------------
    pcm_bytes = struct.pack(
        f"<{total_samples}h",
        *(int(max(-32768, min(32767, v * 32767))) for v in mix_buffer),
    )

    _write_wav(path, pcm_bytes, num_channels=1, sample_rate=sample_rate,
               bits_per_sample=16)
    return path


def _write_wav(
    path: str,
    pcm_data: bytes,
    num_channels: int = 1,
    sample_rate: int = 44100,
    bits_per_sample: int = 16,
) -> None:
    block_align = num_channels * bits_per_sample // 8
    byte_rate = sample_rate * block_align
    data_size = len(pcm_data)
    riff_size = 36 + data_size

    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", riff_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))            # chunk size
        f.write(struct.pack("<H", 1))             # PCM
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", block_align))
        f.write(struct.pack("<H", bits_per_sample))
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(pcm_data)


# ---------------------------------------------------------------------------
# MIDI export
# ---------------------------------------------------------------------------

def export_midi(song: "Song", path: str) -> str:
    """
    Export *song* as a standard MIDI file (.mid).

    Parameters
    ----------
    song : Song
        The song to export.
    path : str
        Output file path (should end in ``.mid``).

    Returns
    -------
    str
        The output path.
    """
    from .chord import Chord
    from .note import _Rest

    ticks_per_beat = 480
    tempo_us = int(60_000_000 / song.bpm)

    tracks_bytes = []

    for track in song.tracks:
        events = []  # list of (tick_offset, bytes)

        # Program change
        events.append((0, bytes([0xC0 | (track.channel & 0x0F), track.instrument & 0x7F])))

        cursor_ticks = 0
        for event in track:
            if isinstance(event, Chord):
                notes = list(event.notes)
                dur_ticks = int(event.duration * ticks_per_beat)
                vel = notes[0].velocity if notes else 64
                # Note-on for all notes
                for n in notes:
                    events.append((cursor_ticks, bytes([
                        0x90 | (track.channel & 0x0F),
                        n.midi & 0x7F,
                        vel & 0x7F,
                    ])))
                # Note-off for all notes
                for n in notes:
                    events.append((cursor_ticks + dur_ticks, bytes([
                        0x80 | (track.channel & 0x0F),
                        n.midi & 0x7F,
                        0,
                    ])))
                cursor_ticks += dur_ticks

            elif isinstance(event, _Rest):
                cursor_ticks += int(event.duration * ticks_per_beat)

            else:
                # Plain Note
                dur_ticks = int(event.duration * ticks_per_beat)
                events.append((cursor_ticks, bytes([
                    0x90 | (track.channel & 0x0F),
                    event.midi & 0x7F,
                    event.velocity & 0x7F,
                ])))
                events.append((cursor_ticks + dur_ticks, bytes([
                    0x80 | (track.channel & 0x0F),
                    event.midi & 0x7F,
                    0,
                ])))
                cursor_ticks += dur_ticks

        # Sort and encode with delta times
        events.sort(key=lambda x: x[0])
        track_data = io.BytesIO()
        prev_tick = 0
        for tick, msg in events:
            delta = tick - prev_tick
            prev_tick = tick
            track_data.write(_encode_vlq(delta))
            track_data.write(msg)
        # End of track
        track_data.write(b"\x00\xff\x2f\x00")

        td = track_data.getvalue()
        tracks_bytes.append(td)

    # ------------------------------------------------------------------
    # Assemble MIDI file
    # ------------------------------------------------------------------
    with open(path, "wb") as f:
        n_tracks = len(tracks_bytes) + 1  # +1 for tempo track

        # Header
        f.write(b"MThd")
        f.write(struct.pack(">I", 6))
        f.write(struct.pack(">H", 1))          # format 1
        f.write(struct.pack(">H", n_tracks))
        f.write(struct.pack(">H", ticks_per_beat))

        # Tempo track
        tempo_track = io.BytesIO()
        tempo_track.write(b"\x00\xff\x51\x03")
        tempo_track.write(struct.pack(">I", tempo_us)[1:])  # 3 bytes
        tempo_track.write(b"\x00\xff\x2f\x00")
        tt = tempo_track.getvalue()
        f.write(b"MTrk")
        f.write(struct.pack(">I", len(tt)))
        f.write(tt)

        # Instrument tracks
        for td in tracks_bytes:
            f.write(b"MTrk")
            f.write(struct.pack(">I", len(td)))
            f.write(td)

    return path


def _encode_vlq(value: int) -> bytes:
    """Encode an integer as a MIDI variable-length quantity."""
    result = []
    result.append(value & 0x7F)
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.reverse()
    return bytes(result)
