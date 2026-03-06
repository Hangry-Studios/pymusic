whole = 4.0
half = 2.0
quarter = 1.0
eighth = 0.5
sixteenth = 0.25
beat = quarter
dotted_half = 3.0
dotted_quarter = 1.5
dotted_eighth = 0.75
triplet_quarter = 2 / 3
triplet_eighth = 1 / 3


class Pattern:
    def __init__(self, durations):
        self.durations = list(durations)

    def apply(self, notes):
        n = len(self.durations)
        return [note.with_duration(self.durations[i % n]) for i, note in enumerate(notes)]

    def repeat(self, times):
        return Pattern(self.durations * times)

    def __add__(self, other):
        return Pattern(self.durations + other.durations)

    def __repr__(self):
        return f'Pattern({self.durations})'
