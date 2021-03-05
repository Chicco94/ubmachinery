#!/usr/bin/python
# -*- coding: utf-8 -*-

from ublib.Machine import Machine, Stati_Commessa, Stati_Macchina, ua_utils, read, write, select, update, insert, datetime


class Costumer_Machine(Machine):
	''' Qui ci vanno tutte le personalizzazioni comuni a tutte le macchine del cliente, ad esempio 
		la lettura a db o la condizione di chiusura di commessa potrebbe essere unica per tutte le macchine
	'''
#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON DB
#---------------------------------------------------------------------------------------------------------
	def get_db_data(self, nome_tabella_config=""):
		''' Legge a db se ci sono delle commesse da avviare in macchina
		'''
		return super().get_db_data(nome_tabella_config)


	def set_db_data(self, values, nome_tabella_scrittura_config="", nome_tabella_commesse_config=""):
		''' Invio dati al database
		'''
		return super().set_db_data(values, nome_tabella_scrittura_config, nome_tabella_commesse_config)


#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON CICLO
#---------------------------------------------------------------------------------------------------------
	def change_commessa_condition(self,commessa_attiva,machine_data):
		''' Cambio commessa se me ne arriva una nuova da gestionale oppure quella attuale risulta terminata
		'''
		return super().change_commessa_condition(commessa_attiva,machine_data)
	
	def close_commessa_condition(self,commessa_attiva,machine_data):
		''' verifico se la quantità da raggiungere è stata raggiunta
		'''
		return super().close_commessa_condition(commessa_attiva,machine_data)


	def generate_internal_data(self,commessa_attiva=None):
		''' ritorna un dizionario pronto per essere riempiti con i dati del ciclo
		'''
		return super().generate_internal_data(commessa_attiva)


	def update_internal_data_before_save_to_db(self,commessa_attiva,machine_data):
		''' aggiorna i dati del ciclo prima di salvarli a db
		'''
		# Personalizzazione macchina siver
		return super().update_internal_data_before_save_to_db(commessa_attiva,machine_data)
