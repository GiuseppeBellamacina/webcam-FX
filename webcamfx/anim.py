def smoothstep(p):
    p = min(max(p, 0.0), 1.0)
    return p * p * (3 - 2 * p)


class Toggle:
    """Stato on/off con transizione animata; invertirlo a meta' riparte dal punto corrente."""

    def __init__(self, duration):
        self.duration, self.on, self._start = duration, False, -1e9

    def flip(self, now):
        p = min((now - self._start) / self.duration, 1.0)
        self._start = now - (1 - p) * self.duration
        self.on = not self.on

    def value(self, now):
        """0 = spento, 1 = acceso, in mezzo = transizione."""
        p = smoothstep((now - self._start) / self.duration)
        return p if self.on else 1 - p
