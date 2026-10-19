import cv2
import numpy as np

from ..context import person_extent
from ..particles import render_sprites
from .base import ToggleEffect

CYAN = np.array([240, 225, 90], np.float32)  # BGR
BLOCK = 12          # lato dei blocchi-particella in px
FEATHER = 18        # sfumatura del fronte di dissoluzione
TINT = 0.65         # quanto ciano nelle particelle (0 = colore originale)


def teleport(person, background, mask, t):
    """Dissolve la persona in blocchi ciano dal basso verso l'alto. t=0 intera, t=1 solo sfondo.
    Le particelle sono funzione deterministica di t, quindi l'animazione e' reversibile."""
    if t <= 0:
        return person
    if t >= 1:
        return background
    ext = person_extent(mask)
    if ext is None:
        return background
    h, w = mask.shape
    top, bottom, _ = ext
    span = max(bottom - top, 1)
    front = float(bottom - t * 2 * span)  # a t=1 e' sopra la testa di `span`

    # fronte frastagliato: rumore fisso per colonna
    rng = np.random.default_rng(0)
    jag = cv2.resize(rng.uniform(-1, 1, (1, w // 60 + 4)).astype(np.float32), (w, 1),
                     interpolation=cv2.INTER_CUBIC)[0] * 16
    yy = np.arange(h, dtype=np.float32)[:, None]
    a = mask * np.clip((front + jag - yy) / FEATHER, 0, 1)
    out = cv2.blendLinear(person, background, a, 1 - a)

    # bagliore ciano appena sopra il fronte (solo nella fascia interessata)
    y0, y1 = int(np.clip(front - FEATHER - 40, 0, h)), int(np.clip(front - FEATHER + 40, 0, h))
    if y1 > y0:
        band = out[y0:y1].astype(np.float32)
        glow = mask[y0:y1] * np.clip(1 - np.abs(front + jag - FEATHER - yy[y0:y1]) / 14, 0, 1) * 0.8
        out[y0:y1] = (band + (CYAN - band) * glow[..., None]).astype(np.uint8)

    # una particella per blocco della persona gia' sotto il fronte
    gh, gw = h // BLOCK, w // BLOCK
    cm = cv2.resize(mask, (gw, gh), interpolation=cv2.INTER_AREA)
    cc = cv2.resize(person, (gw, gh), interpolation=cv2.INTER_AREA) * (1 - TINT) + CYAN * TINT
    vx = rng.uniform(-1, 1, (gh, gw))
    vy = rng.uniform(-0.7, 0.25, (gh, gw))
    size = rng.integers(BLOCK // 2, BLOCK + 3, (gh, gw))
    cy = (np.arange(gh)[:, None] + 0.5) * BLOCK
    age = (cy - front) / span + rng.uniform(-0.15, 0.15, (gh, gw))  # 0 appena dissolto, 1 sparito
    gy, gx = np.nonzero((cm > 0.4) & (age > 0) & (age < 1))
    ag = age[gy, gx]
    xs = gx * BLOCK + vx[gy, gx] * ag * span * 0.6
    ys = gy * BLOCK + vy[gy, gx] * ag * span * 0.6
    return render_sprites(out, xs, ys, size[gy, gx], cc[gy, gx], (1 - ag) ** 0.7)


class Teleport(ToggleEffect):
    label, gesture, duration = "Teletrasporto", "Victory", 1.5

    def apply(self, ctx, out, t):
        return teleport(out, ctx.background, ctx.mask, t)
