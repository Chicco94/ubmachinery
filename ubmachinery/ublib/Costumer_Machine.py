#!/usr/bin/python
# -*- coding: utf-8 -*-

from ublib.Machine import Machine, Stati_Commessa, Stati_Macchina, datetime

# per connessione con database
from sql_connection import insert,update,select

class Costumer_Machine(Machine):
	''' Qui ci vanno tutte le personalizzazioni comuni a tutte le macchine del cliente, ad esempio 
		la lettura a db o la condizione di chiusura di commessa potrebbe essere unica per tutte le macchine
	'''
#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON DB
#---------------------------------------------------------------------------------------------------------
	def get_db_data(self):
		''' Legge a db se ci sono delle commesse da avviare in macchina
		'''
		try:
			commesse = select(
				self.db_conn,
				self.config_commesse['table_name'],
				','.join(self.config_commesse['table_fields'].keys()),
				'co_flInviato=1 AND co_idmacchinario='+self.id
				).response
			commessa_attiva = None
			if (commesse and len(commesse) > 0): 
				commessa_attiva = commesse[0]
			return commessa_attiva
		except Exception as e:
			print("Errore in get_db_data per ", self.id," - ",e)
			return False


	def set_db_data(self, values):
		''' Invio dati al database
		'''
		try:
			# salvo i dati di lavorazione
			insert(self.db_conn, self.config_analisi['table_name'], values)

			# aggiorno lo stato della commessa e la metto come terminata
			update(self.db_conn, self.config_commesse['table_name'],'co_id='+str(values['an_idcommessa'])+' AND co_idmacchinario='+self.id,{'co_flInviato':2, 'co_qtaProdotta':values['an_qtaprodotta']})

			return True
		except Exception as e:
			print("Errore in set_machine_data per ", self.id," - ",e)
			return False


#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON CICLO
#---------------------------------------------------------------------------------------------------------	
	def end_cycle(self,commessa_attiva,machine_data):
		''' Cosa deve fare la macchina alla terminazione di ogni ciclo'''
		try:
			dati_analisi = machine_data.copy()
			dati_analisi['an_idcommessa'] = commessa_attiva['co_id']
			dati_analisi['an_idmacchinario'] = self.id
			insert(self.db_conn, self.config_dati['table_name'], dati_analisi)
		except Exception as _:
			print("Errore in end_cycle per ", self.id," - ", e)
			return False
