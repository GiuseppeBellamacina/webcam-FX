"""Sprite e particelle condivisi da tutti gli effetti."""
import cv2
import numpy as np

rng = np.random.default_rng()

_t = np.linspace(0, 2 * np.pi, 24)
_HEART = np.column_stack([16 * np.sin(_t) ** 3,
                          -(13 * np.cos(_t) - 5 * np.cos(2 * _t) - 2 * np.cos(3 * _t) - np.cos(4 * _t))]) / 17


def _block(ov, al, x, y, s, c, a):   # (x, y) = angolo in alto a sinistra
    ov[max(y, 0):y + s, max(x, 0):x + s] = c
    al[max(y, 0):y + s, max(x, 0):x + s] = a


def _circle(ov, al, x, y, s, c, a):  # (x, y) = centro, s = raggio
    cv2.circle(ov, (x, y), s, c.tolist(), -1)
    cv2.circle(al, (x, y), s, float(a), -1)


def _heart(ov, al, x, y, s, c, a):   # (x, y) = centro, s = larghezza
    pts = (_HEART * s / 2 + (x, y)).astype(np.int32)
    cv2.fillPoly(ov, [pts], c.tolist())
    cv2.fillPoly(al, [pts], float(a))


def _drop(ov, al, x, y, s, c, a):    # (x, y) = punta alta, s = lunghezza
    cv2.line(ov, (x, y), (x, y + s), c.tolist(), 2)
    cv2.line(al, (x, y), (x, y + s), float(a), 2)


SHAPES = {"block": _block, "circle": _circle, "heart": _heart, "drop": _drop}


def render_sprites(out, xs, ys, sizes, colors, alphas, shape="block"):
    """Disegna N sprite semitrasparenti su `out` con un'unica fusione finale."""
    h, w = out.shape[:2]
    xs, ys = np.asarray(xs).astype(int), np.asarray(ys).astype(int)
    sizes = np.broadcast_to(np.asarray(sizes, int), xs.shape)
    colors = np.broadcast_to(np.asarray(colors, np.float32), (len(xs), 3))
    alphas = np.broadcast_to(np.asarray(alphas, np.float32), xs.shape)
    # fuori schermo: per i blocchi uno slice negativo farebbe il giro della riga
    on = (xs > -sizes) & (ys > -sizes) & (xs < w + sizes) & (ys < h + sizes) & (alphas > 0)
    if not on.any():
        return out
    ov = np.zeros_like(out)
    al = np.zeros((h, w), np.float32)
    draw = SHAPES[shape]
    for x, y, s, c, a in zip(xs[on], ys[on], sizes[on], colors[on], alphas[on]):
        draw(ov, al, x, y, s, c, a)
    # ponytail: loop Python per sprite (qualche migliaio/frame regge); vettorizzare se servono di piu'
    return cv2.blendLinear(ov, out, al, 1 - al)


def spray(n, origin, angles, speed):
    """n posizioni nell'origine e velocita' a ventaglio (angoli in radianti, y verso il basso)."""
    ang = rng.uniform(*angles, n)
    spd = rng.uniform(*speed, n)
    return np.tile(np.asarray(origin, np.float32), (n, 1)), np.column_stack([np.cos(ang) * spd, np.sin(ang) * spd])


class Particles:
    """Sistema di particelle con gravita', attrito e oscillazione laterale; svaniscono a fine vita."""
    FIELDS = ("pos", "vel", "age", "life", "size", "color", "phase")

    def __init__(self, shape="block", gravity=(0.0, 0.0), drag=1.0, wobble=0.0):
        self.shape, self.gravity, self.drag, self.wobble = shape, np.asarray(gravity, np.float32), drag, wobble
        self.pos, self.vel = np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32)
        self.age, self.life, self.phase = (np.zeros(0, np.float32) for _ in range(3))
        self.size, self.color = np.zeros(0, int), np.zeros((0, 3), np.float32)

    def __len__(self):
        return len(self.age)

    def emit(self, pos, vel, life, size, color, delay=0.0):
        """Aggiunge len(pos) particelle; gli scalari valgono per tutte. `delay` ritarda la comparsa."""
        n = len(pos)
        new = {"pos": pos, "vel": vel, "age": -np.broadcast_to(delay, (n,)), "life": np.broadcast_to(life, (n,)),
               "size": np.broadcast_to(size, (n,)), "color": np.broadcast_to(color, (n, 3)),
               "phase": rng.uniform(0, 2 * np.pi, n)}
        for f in self.FIELDS:
            old = getattr(self, f)
            setattr(self, f, np.concatenate([old, np.asarray(new[f], old.dtype)]))

    def step(self, dt):
        live = self.age >= 0
        self.vel[live] += self.gravity * dt
        self.vel[live] *= self.drag ** dt
        self.pos[live] += self.vel[live] * dt
        self.age += dt
        keep = self.age < self.life
        for f in self.FIELDS:
            setattr(self, f, getattr(self, f)[keep])

    def render(self, out):
        live = self.age >= 0
        if not live.any():
            return out
        age, life = self.age[live], self.life[live]
        x = self.pos[live, 0] + self.wobble * np.sin(age * 4 + self.phase[live])
        return render_sprites(out, x, self.pos[live, 1], self.size[live], self.color[live],
                              1 - (age / life) ** 2, self.shape)
