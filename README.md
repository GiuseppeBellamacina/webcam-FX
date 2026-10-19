# Webcam FX

Effetti webcam attivati dai gesti, inviati a **OBS Virtual Camera** (selezionabile in Teams/Meet).

```
uv run main.py              # --camera 1 se l'indice 0 e' la virtual cam
uv run check.py             # self-check senza webcam
```

Tasti: `1`..`6` attivano gli effetti, `b` cattura lo sfondo tra 3s (esci dall'inquadratura), `q` esce.

| Gesto | Effetto |
|---|---|
| ✋ palmo | Tempo fermo (on/off) |
| ☝️ indice su | Ologramma (on/off) |
| ✌️ V | Teletrasporto (on/off) |
| 👍 pollice su | Coriandoli |
| 🤟 rock | Cuori |
| 👎 pollice giu | Nuvola di pioggia |

## Struttura

```
webcamfx/
  app.py          loop: webcam -> percezione -> sfondo -> gesti -> effetti -> output
  perception.py   modelli MediaPipe (maschera persona + mani)
  gestures.py     classificazione gesti + debounce (GestureTrigger)
  background.py   sfondo senza persona
  context.py      FrameContext: cio' che un effetto puo' leggere
  particles.py    Particles + render_sprites (block, circle, heart, drop) condivisi
  anim.py         Toggle con transizione reversibile
  camera.py       webcam, OBS Virtual Camera, anteprima
  effects/
    base.py       Effect, ToggleEffect, ParticleEffect
    __init__.py   default_effects(): registro e ordine di disegno
```

## Aggiungere un effetto

1. Crea `webcamfx/effects/mio.py` estendendo:
   - `ToggleEffect` per un effetto on/off: implementa `apply(ctx, out, t)` (t = avanzamento 0..1 della transizione);
   - `ParticleEffect` per un effetto a particelle: implementa `make_particles()` e `trigger(ctx, hand)`;
   - `Effect` per qualunque altra cosa.
2. Imposta `label` e `gesture` (`Victory`, `Thumb_Up`, `Thumb_Down`, `Open_Palm`, `Closed_Fist`, `Pointing_Up`, `ILoveYou`).
3. Aggiungilo alla lista in `default_effects()`.

`render` deve restituire un nuovo array senza modificare `out`. Il pugno chiuso (`Closed_Fist`) e' ancora libero.
