#!/usr/bin/python
# -*- coding: utf-8 -*-

# import generici
import sys
sys.path.insert(0, "..")
from ublib.models.CommesseMacchinario import CommesseMacchinario
from ublib.models.AnalisiMacchinario import AnalisiMacchinario
from ublib.models.DatiMacchinario import DatiMacchinario
from enum import Enum
from threading import Thread
import datetime 
import time


class Machine(Thread):
	''' Classe che estende i thread che rappresenta una macchina
	'''
	def __init__(self, _id, _db_conn = None, config_connessione='',config_commesse='', config_analisi='', config_dati='', sleep_time=5.0):
		''' configurazione macchina
			client se già connessa (la macchina ha un metodo connect())
			db_conn se già connesso
		'''
		Thread.__init__(self)
		self.id			= _id
		self.db_conn	= _db_conn
		self.connected 	= False
		self.config_connessione = config_connessione
		self.config_commesse = config_commesse
		self.config_analisi = config_analisi
		self.config_dati = config_dati
		self.sleep_time = sleep_time

	def run(self):
		'''funzione necessaria ai thread per funzionare'''
		self.start_connector(sleep_time = self.sleep_time)

	def start_connector(self, stop=False, sleep_time = 1):
		''' Avvia la connessione con la macchina e cicla finchè necessario
			quando termina il ciclo, disconnette la macchina
		'''
		self.connect()
		self.cycle(stop, sleep_time)
		self.disconnect()

	def cycle(self, stop=False, sleep_time = 5):
		commessa_attiva = CommesseMacchinario()
		machine_data = AnalisiMacchinario()
		# ciclo finchè non mi viene detto di fermarmi
		while (not stop):
			
			if (not self.connected):
				print("macchina {} non connessa".format(self.id))
				# riprovo a connettermi al macchinario
				time.sleep(sleep_time)
				self.connect()
				continue

			# leggo lo stato della macchina, se la macchina è spenta o non connessa faccio un nuovo ciclo
			machine_data = self.find_machine_data()
			if (not machine_data):
				time.sleep(sleep_time)
				# riprovo a connettermi al macchinario
				self.connect()
				continue

			commessa_attuale = self.find_commessa_attiva()

			# se è presente una commessa, ma è quella già attiva, controllo che non sia terminata
			if (commessa_attuale and commessa_attuale == commessa_attiva):
				# se è terminata la salvo a db
				if (self.close_commessa_condition(commessa_attiva,machine_data)):
					print("la macchina ha finito di lavorare")
					self.set_db_data(self.update_internal_data_before_save_to_db(commessa_attiva,machine_data))
					commessa_attiva = CommesseMacchinario()

			# se è presente una commessa, ma non ce ne è una attiva, la imposto
			elif (commessa_attuale and not commessa_attiva):
				print("è arrivata una nuova commessa, non ne avevo di attive")
				commessa_attiva = self.generate_internal_data(commessa_attuale)
				self.set_machine_data(commessa_attiva)
				print('commessa attiva:', commessa_attiva.co_commessa)
				print('articolo:', commessa_attiva.co_descrizioneArticolo)

			# se è presente una commessa, ma è diversa da quella attiva, la cambio
			elif (commessa_attuale and commessa_attuale != commessa_attiva):
				print("è arrivata una nuova commessa, ne avevo già una in canna")
				self.set_db_data(self.update_internal_data_before_save_to_db(commessa_attiva,machine_data))
				commessa_attiva = self.generate_internal_data(commessa_attuale)
				print('commessa attiva:', commessa_attiva.co_commessa)
				print('articolo:', commessa_attiva.co_descrizioneArticolo)
				self.set_machine_data(commessa_attiva)

			# se non è presente una commessa, e ce ne era una attiva (chiusa quindi da app), la chiudo da qui
			elif (not commessa_attuale and commessa_attiva):
				print("la commessa è stata chiusa da app")
				self.set_db_data(self.update_internal_data_before_save_to_db(commessa_attiva,machine_data))
				commessa_attiva = CommesseMacchinario()

			# se non è presente una commessa, e non ce ne era una attiva, non faccio niente
			else:
				print("\nnothing to do\n")

			self.end_cycle(commessa_attiva,machine_data)

			time.sleep(sleep_time)


#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON CICLO
#---------------------------------------------------------------------------------------------------------
	def close_commessa_condition(self,commessa_attiva:CommesseMacchinario,machine_data:AnalisiMacchinario):
		if machine_data and commessa_attiva:
			return machine_data.an_qtaProdotta >= commessa_attiva.co_qtaDaProdurre
		return False


	def end_cycle(self,commessa_attiva:CommesseMacchinario,machine_data:AnalisiMacchinario):
		''' Cosa deve fare la macchina alla terminazione di ogni ciclo'''
		try:
			_ = 1/0
		except Exception as _:
			print("Errore in end_cycle per ", self.id," - non implementato")
			return False


	def generate_internal_data(self,commessa_attiva:CommesseMacchinario=None) -> CommesseMacchinario:
		''' ritorna un dizionario pronto per essere riempiti con i dati del ciclo
		'''
		commessa_attiva.co_dataInizio = datetime.datetime.now(datetime.timezone.utc)
		return commessa_attiva


	def update_internal_data_before_save_to_db(self,commessa_attiva:CommesseMacchinario,machine_data:AnalisiMacchinario) -> AnalisiMacchinario:
		return_data = AnalisiMacchinario()
		return_data.an_idcommessa = commessa_attiva.co_id
		return_data.an_idmacchinario = self.id
		return_data.an_dataInizio = commessa_attiva.co_dataInizio.strftime("%Y-%m-%d %H:%M:%S")
		data_fine = datetime.datetime.now(datetime.timezone.utc)
		return_data.an_dataFine = data_fine.strftime("%Y-%m-%d %H:%M:%S")
		return_data.an_qtaProdotta = machine_data.an_qtaProdotta
		return_data.an_tempoEffettivo = (data_fine - commessa_attiva.co_dataInizio).seconds * 1000 # tempo in millisecondi
		return return_data


	def find_commessa_attiva(self) -> CommesseMacchinario:
		commessa_attiva = self.get_db_data()
		if (not commessa_attiva):
			print("nessuna commessa attiva per {}".format(self.id))
			return None
		return commessa_attiva


	def find_machine_data(self) -> AnalisiMacchinario:
		machine_data = self.get_machine_data()
		if (not machine_data):
			print("macchina {}: errore nell'estrazione dei dati".format(self.id))
			self.connected = False
			return None
		return machine_data


#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON DATABASE
#---------------------------------------------------------------------------------------------------------
	def get_db_data(self) -> CommesseMacchinario:
		''' Legge lo stato della macchina
		'''
		try:
			_ = 1/0
			return CommesseMacchinario()
		except Exception as _:
			print("Errore in get_machine_data per ", self.id," - non implementato")
			return False


	def set_db_data(self, values:AnalisiMacchinario) -> bool:
		''' Invio dati al macchinario
		'''
		try:
			_ = 1/0
			return True
		except Exception as _:
			print("Errore in get_machine_data per ", self.id," - non implementato")
			return False


#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON MACCHINA
#---------------------------------------------------------------------------------------------------------
	def read_variable(self,variable):
		try:
			_ = 1/0
		except Exception as _:
			print("Errore in read_variable per ", self.id," - non implementato")
			return False


	def write_variable(self,variable,value):
		try:
			_ = 1/0
		except Exception as _:
			print("Errore in write_variable per ", self.id," - non implementato")
			return False

	
	def get_machine_data(self) -> AnalisiMacchinario:
		''' Legge lo stato della macchina
		'''
		try:
			_ = 1/0
		except Exception as _:
			print("Errore in get_machine_data per ", self.id," - non implementato")
			return None


	def set_machine_data(self, data):
		''' Invio dati al macchinario
		'''
		try:
			_ = 1/0
		except Exception as _:
			print("Errore in set_machine_data per ", self.id," - non implementato")
			return False


	def connect(self):
		''' In base al protocollo specificato nel config del macchinario, connette la macchina
			Ritorna un handler per la connessione con il macchinario
		'''
		try:
			_ = 1/0
		except Exception as _:
			print("Errore in connect per ", self.id," - non implementato")
			return False


	def disconnect(self):
		''' In base al protocollo specificato nel config del macchinario, disconnette la macchina
		'''
		try:
			_ = 1/0
		except Exception as _:
			print("Errore in disconnect per ", self.id," - non implementato")
			return False


class Stati_Macchina(Enum):
	''' Possibili stati in cui una macchina si può trovare
	'''
	in_lavorazione = 1
	spenta = 0
	allarme = 2
	setup = 3
	non_connessa = 4


class Stati_Commessa(Enum):
	''' Possibili stati in cui una commessa si può trovare
	'''
	commessa_attiva = 1
	commessa_terminata = 2
	nessuna_commessa = 3