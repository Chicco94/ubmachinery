#!/usr/bin/python
# -*- coding: utf-8 -*-

from ublib.Machine import Machine, Stati_Commessa, Stati_Macchina, datetime
from ublib.models.AnalisiMacchinario import AnalisiMacchinario
from ublib.models.CommesseMacchinario import CommesseMacchinario

# per connessione con database
from ublib.sql_connection import insert, update, select


class Costumer_Machine(Machine):
    """Qui ci vanno tutte le personalizzazioni comuni a tutte le macchine del cliente, ad esempio
    la lettura a db o la condizione di chiusura di commessa potrebbe essere unica per tutte le macchine
    """

    # ---------------------------------------------------------------------------------------------------------
    # 								INTERAZIONI CON DB
    # ---------------------------------------------------------------------------------------------------------
    def get_db_data(self) -> CommesseMacchinario:
        """Legge a db se ci sono delle commesse da avviare in macchina"""
        try:
            commesse = select(
                self.db_conn,
                self.config_commesse["table_name"],
                ",".join(self.config_commesse["table_fields"].keys()),
                "co_flInviato=1 AND co_idmacchinario=" + self.id,
            ).response
            commessa_attiva = None
            if commesse and len(commesse) > 0:
                commessa_attiva = CommesseMacchinario(*commesse[0])
            return commessa_attiva
        except Exception as e:
            print("Errore in get_db_data per ", self.id, " - ", e)
            return False

    def set_db_data(self, values: AnalisiMacchinario):
        """Invio dati al database"""
        try:
            # salvo i dati di lavorazione
            insert(self.db_conn, self.config_analisi["table_name"], values)

            # aggiorno lo stato della commessa e la metto come terminata
            update(
                self.db_conn,
                self.config_commesse["table_name"],
                "co_id="
                + str(values["an_idcommessa"])
                + " AND co_idmacchinario="
                + self.id,
                {"co_flInviato": 2, "co_qtaProdotta": values["an_qtaprodotta"]},
            )

            return True
        except Exception as e:
            print("Errore in set_machine_data per ", self.id, " - ", e)
            return False

    # ---------------------------------------------------------------------------------------------------------
    # 								INTERAZIONI CON CICLO
    # ---------------------------------------------------------------------------------------------------------
    def end_cycle(self, commessa_attiva, machine_data):
        """Cosa deve fare la macchina alla terminazione di ogni ciclo"""
        try:
            dati_analisi = machine_data.copy()
            dati_analisi["an_idcommessa"] = commessa_attiva["co_id"]
            dati_analisi["an_idmacchinario"] = self.id
            insert(self.db_conn, self.config_dati["table_name"], dati_analisi)
        except Exception as e:
            print("Errore in end_cycle per ", self.id, " - ", e)
            return False

    # ---------------------------------------------------------------------------------------------------------
    # 								INTERAZIONI CON MACCHINA
    # ---------------------------------------------------------------------------------------------------------
    def get_machine_data(self, old_data=None, nome_tabella_config=""):
        """Legge lo stato della macchina"""
        if not old_data:
            old_data = dict()
        try:
            for field in self.config_dati.keys():
                # ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
                if self.config_dati[field]:
                    old_data[field] = self.read_variable(self.config_dati[field])
            return old_data
        except Exception as e:
            print("Errore in get_machine_data per ", self.id, " - ", e)
            return False

    def set_machine_data(self, data, nome_tabella_config=""):
        """Invio dati al macchinario"""
        try:
            for field in self.config_commesse.keys():
                # ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
                if self.config_commesse[field]:
                    self.write_variable(self.config_commesse[field], data[field])
            return True
        except Exception as e:
            print("Errore in set_machine_data per ", self.id, " - ", e)
            return False
