import numpy as np

from ..particles import Particles, rng, spray
from .base import ParticleEffect

COLORS = np.array([(60, 60, 240), (60, 200, 255), (80, 220, 80), (255, 160, 40), (220, 80, 220), (255, 255, 255)], np.float32)


class Confetti(ParticleEffect):
    """Esplosione di coriandoli dalla mano."""
    label, gesture = "Coriandoli", "Thumb_Up"

    def make_particles(self):
        return Particles("block", gravity=(0, 900), drag=0.6, wobble=25)

    def trigger(self, ctx, hand):
        n = 300
        pos, vel = spray(n, ctx.anchor(hand), angles=(-np.pi * 0.9, -np.pi * 0.1), speed=(400, 1100))
        self.particles.emit(pos, vel, life=rng.uniform(1.8, 2.8, n), size=rng.integers(6, 13, n),
                            color=COLORS[rng.integers(0, len(COLORS), n)])
