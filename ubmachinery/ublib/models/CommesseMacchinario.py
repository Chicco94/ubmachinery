from dataclasses import dataclass
from datetime import datetime

@dataclass(init=True)
class CommesseMacchinario:
    co_id: int
    co_idmacchinario: int
    co_commessa: str = None
    co_numeroOrdine: int = None
    co_cliente: str = None
    co_dataOrdine: datetime = None
    co_dataConsegna: datetime = None
    co_codiceArticolo: str = None
    co_descrizioneArticolo: str = None
    co_qtaDaProdurre: int = None
    co_qtaProdotta: int = 0
    co_note: str = None
    co_flInviato: int = None

    co_dataInizio: datetime = None

    def __eq__(self, o: object) -> bool:
        return self.co_id == o.co_id

    def __ne__(self, o: object) -> bool:
        return self.co_id != o.co_id