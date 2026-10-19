import numpy as np

from ..particles import Particles, render_sprites, rng
from .base import ParticleEffect

DURATION = 6.0
# nuvola = cerchi (dx, dy, raggio) attorno al suo centro
CLOUD = np.array([(-90, 10, 45), (-40, -15, 55), (20, -25, 60), (80, 0, 48), (0, 20, 50), (-60, 25, 40), (55, 25, 42)])
CLOUD_COLOR = (185, 185, 190)
DROP_COLOR = (235, 200, 170)


class RainCloud(ParticleEffect):
    """Una nuvoletta segue la tua testa e ti piove addosso."""
    label, gesture = "Nuvola di pioggia", "Thumb_Down"

    def __init__(self):
        super().__init__()
        self.start, self.pos = -1e9, None

    def make_particles(self):
        return Particles("drop", gravity=(0, 300))

    def trigger(self, ctx, hand):
        self.start = ctx.now

    def active(self, now):
        return now - self.start < DURATION or super().active(now)

    def render(self, ctx, out):
        elapsed = ctx.now - self.start
        fade = min(elapsed / 0.5, (DURATION - elapsed) / 0.5, 1.0)  # dissolvenza in entrata/uscita
        if fade > 0:
            ext = ctx.person_extent
            w = ctx.mask.shape[1]
            target = np.array([ext[2], max(ext[0] - 90, 70)] if ext else [w / 2, 80], np.float32)
            self.pos = target if self.pos is None else self.pos + (target - self.pos) * min(1.0, ctx.dt * 6)
            n = int(ctx.dt * 220) + 1
            drops = np.column_stack([self.pos[0] + rng.uniform(-110, 110, n), np.full(n, self.pos[1] + 30)])
            vel = np.column_stack([rng.uniform(-15, 15, n), rng.uniform(550, 750, n)])
            self.particles.emit(drops, vel, life=0.9, size=rng.integers(12, 22, n), color=DROP_COLOR)
        else:
            self.pos = None
        out = super().render(ctx, out)  # gocce dietro la nuvola
        if fade > 0:
            out = render_sprites(out, self.pos[0] + CLOUD[:, 0], self.pos[1] + CLOUD[:, 1], CLOUD[:, 2],
                                 CLOUD_COLOR, 0.95 * fade, "circle")
        return out
