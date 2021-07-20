from dataclasses import dataclass
from datetime import datetime

@dataclass(init=True)
class AnalisiMacchinario:
    an_id: int = None
    an_idmacchinario: int = None
    an_idcommessa: int = None
    an_qtaProdotta: int = 0
    an_dataInizio: datetime = None
    an_dataFine: datetime = None
    an_tempoEffettivo: datetime = None
    an_timestamp: int = None
    an_flLettura: int = 0

    def __eq__(self, o: object) -> bool:
        return self.an_id == o.an_id

    def __ne__(self, o: object) -> bool:
        return self.an_id != o.an_id
