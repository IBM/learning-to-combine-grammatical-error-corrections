from typing import NamedTuple

from span import Span


class Edit(NamedTuple):
    start: int
    end: int
    cat: str
    cor: str
    coder: str
    origLine: str

    @property
    def span(self):
        return Span(self.start, self.end)

    @property
    def len(self):
        return self.span.end - self.span.start

    def __str__(self):
        return self.origLine
