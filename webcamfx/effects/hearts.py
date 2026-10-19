import numpy as np

from ..particles import Particles, rng
from .base import ParticleEffect

COLORS = np.array([(90, 60, 240), (150, 100, 255), (120, 40, 200), (180, 150, 255)], np.float32)


class Hearts(ParticleEffect):
    """Cuori che salgono ondeggiando dalla mano."""
    label, gesture = "Cuori", "ILoveYou"

    def make_particles(self):
        return Particles("heart", gravity=(0, -40), drag=0.5, wobble=30)

    def trigger(self, ctx, hand):
        n = 30
        pos = ctx.anchor(hand) + rng.uniform(-40, 40, (n, 2))
        vel = np.column_stack([rng.uniform(-80, 80, n), rng.uniform(-260, -140, n)])
        self.particles.emit(pos, vel, life=rng.uniform(2.5, 3.5, n), size=rng.integers(24, 48, n),
                            color=COLORS[rng.integers(0, len(COLORS), n)], delay=rng.uniform(0, 1.2, n))
