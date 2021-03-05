#!/usr/bin/python
# -*- coding: utf-8 -*-

from ublib.Costumer_Machine import Costumer_Machine


class Specific_Machine(Costumer_Machine): 

	def get_db_data(self, nome_tabella_config=""):
		''' Legge a db se ci sono delle commesse da avviare in macchina
		'''
		return super().get_db_data("commesse_allevi")


	def set_db_data(self, data, nome_tabella_scrittura_config="", nome_tabella_commesse_config=""):
		''' Invio dati al database
		'''
		return super().set_db_data(data,"analisi_allevi","commesse_allevi")


	def get_machine_data(self, old_data=None, nome_tabella_config=""):
		''' Legge lo stato della macchina
		'''
		return super().get_machine_data(old_data,"analisi_allevi")


	def set_machine_data(self, data, nome_tabella_config=""):
		''' Invio dati al macchinario
		'''
		return super().set_machine_data(data,"commesse_allevi")
				










