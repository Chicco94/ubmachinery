#!/usr/bin/python
# -*- coding: utf-8 -*-

from ublib.Costumer_Machine import Costumer_Machine, read, write


class Siver_Machine(Costumer_Machine):

	def get_db_data(self, nome_tabella_config="commesse_siver"):
		''' Legge a db se ci sono delle commesse da avviare in macchina
		'''
		return super().get_db_data(nome_tabella_config)


	def set_db_data(self, data, nome_tabella_scrittura_config="analisi_siver", nome_tabella_commesse_config="commesse_siver"):
		''' Invio dati al database
		'''
		return super().set_db_data(data,nome_tabella_scrittura_config,nome_tabella_commesse_config)


	def get_machine_data(self, old_data=None, nome_tabella_config="analisi_siver"):
		''' Legge lo stato della macchina
		'''
		return super().get_machine_data(old_data,nome_tabella_config)


	def set_machine_data(self, data, nome_tabella_config="commesse_siver"):
		''' Invio dati al macchinario
		'''
		# in questo blocco viene anche modificato l'id transazione
		return super().set_machine_data(data,nome_tabella_config)

	def close_commessa_condition(self,commessa_attiva,machine_data):
		''' verifico se la quantità da raggiungere è stata raggiunta
		'''
		return False