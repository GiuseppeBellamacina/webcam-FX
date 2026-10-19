from abc import ABC, abstractmethod

import numpy as np

from ..anim import Toggle
from ..particles import Particles


class Effect(ABC):
    """Un effetto: si attiva con un gesto (o con il tasto numerico) e disegna sul frame.
    `render` riceve l'output degli effetti precedenti e restituisce un NUOVO array (non modifica `out`)."""
    label = "?"          # nome mostrato nell'anteprima
    gesture = None       # nome gesto MediaPipe (vedi gestures.LABELS); None = solo da tastiera
    hold = 4             # rilevamenti consecutivi del gesto prima di scattare

    @abstractmethod
    def trigger(self, ctx, hand):
        """hand e' la Hand che ha fatto il gesto, None se attivato da tastiera."""

    @abstractmethod
    def render(self, ctx, out) -> np.ndarray:
        ...

    @abstractmethod
    def active(self, now) -> bool:
        """True se l'effetto sta disegnando qualcosa (evidenziato nell'anteprima)."""


class ToggleEffect(Effect):
    """Effetto on/off con transizione: le sottoclassi implementano solo `apply(ctx, out, t)`, t in (0, 1]."""
    duration = 0.6

    def __init__(self):
        self.state = Toggle(self.duration)

    def trigger(self, ctx, hand):
        self.state.flip(ctx.now)

    def active(self, now):
        return self.state.value(now) > 0

    def render(self, ctx, out):
        t = self.state.value(ctx.now)
        return self.apply(ctx, out, t) if t > 0 else out

    @abstractmethod
    def apply(self, ctx, out, t):
        ...


class ParticleEffect(Effect):
    """Effetto a particelle: le sottoclassi creano le particelle in `make_particles` e le emettono in `trigger`."""

    def __init__(self):
        self.particles = self.make_particles()

    @abstractmethod
    def make_particles(self) -> Particles:
        ...

    def active(self, now):
        return len(self.particles) > 0

    def render(self, ctx, out):
        self.particles.step(ctx.dt)
        return self.particles.render(out)
