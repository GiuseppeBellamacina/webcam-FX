from .confetti import Confetti
from .hearts import Hearts
from .hologram import Hologram
from .raincloud import RainCloud
from .teleport import Teleport
from .timestop import TimeStop


def default_effects():
    """Registro degli effetti. L'ordine e' l'ordine di disegno: prima chi cambia mondo/persona,
    poi il teletrasporto (che rimuove la persona), infine le particelle sopra a tutto.
    Il tasto numerico N attiva l'N-esimo effetto della lista."""
    return [TimeStop(), Hologram(), Teleport(), Confetti(), Hearts(), RainCloud()]
