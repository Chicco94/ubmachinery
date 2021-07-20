from dataclasses import dataclass
from datetime import datetime

@dataclass(init=True)
class DatiMacchinario:
    id: int
    idmacchinario: int
    qtaProdotta: int
    tempoEsecuzione: datetime
    tempoFermo: datetime
    tempoSetup: datetime = None
    idinput: int = None

