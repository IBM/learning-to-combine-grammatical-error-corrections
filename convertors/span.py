from typing import NamedTuple


class Span(NamedTuple):
    start: int
    end: int

    @property
    def len(self):
        return self.end - self.start

    def __str__(self):
        return '(' + self.start + ',' + self.end + ')'
