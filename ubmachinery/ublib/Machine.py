#!/usr/bin/python
# -*- coding: utf-8 -*-

# import generici
import sys
sys.path.insert(0, "..")
import os
from enum import Enum
from threading import Thread
import datetime 
import time

# per connessione con database
from ublib.sql_connection import *

# per connessione tramite TCP-IP/Ethernet
import socket

# per connessione con modbus
# from ublib.plc_connection import plc_connect, plc_disconnect

# per connessione con modbus
from ublib.modbus_connection import modbus_connect, modbus_disconnect, read, write

# per connessione opc-ua
from opcua import ua
from opcua import Client
from opcua.common import ua_utils

from random import random, randint


SLEEP_TIME = 5.000

class Machine(Thread):
	''' Classe che estende i thread che rappresenta una macchina
	'''
	def __init__(self, _config, _client = None, _db_conn = None):
		''' configurazione macchina
			client se già connessa (la macchina ha un metodo connect())
			db_conn se già connesso
		'''
		Thread.__init__(self)
		self.id			= _config['db_config']['idMacchinario']
		self.client	 	= _client
		self.config	 	= _config
		self.db_conn	= _db_conn
		self.connected 	= False

	def run(self):
		'''funzione necessaria ai thread per funzionare'''
		self.start_connector(interval = SLEEP_TIME)

	def start_connector(self, stop=False, interval = 1):
		''' Avvia la connessione con la macchina e cicla finchè necessario
			quando termina il ciclo, disconnette la macchina
		'''
		self.connect()
		self.cycle(stop, interval)
		self.disconnect()

	def cycle(self, stop=False, interval = 1, sleep_time = 5):
		commessa_attiva = {'co_id':None}
		machine_data = None
		# ciclo finchè non mi viene detto di fermarmi
		while (not stop):
			
			if (not self.connected):
				print("macchina {} non connessa".format(self.id))
				# riprovo a connettermi al macchinario
				time.sleep(interval)
				self.connect()
				continue

			# leggo lo stato della macchina, se la macchina è spenta o non connessa faccio un nuovo ciclo
			machine_data = self.find_machine_data(sleep_time)
			if (not machine_data):
				time.sleep(interval)
				# riprovo a connettermi al macchinario
				self.connect()
				continue

			commessa_attuale = self.find_commessa_attiva(sleep_time)

			# se è presente una commessa, ma è quella già attiva, controllo che non sia terminata
			if (commessa_attuale and commessa_attuale['co_id'] == commessa_attiva['co_id']):
				# se è terminata la salvo a db
				if (self.close_commessa_condition(commessa_attiva,machine_data)):
					print("la macchina ha finito di lavorare")
					self.set_db_data(self.update_internal_data_before_save_to_db(commessa_attiva,machine_data))
					commessa_attiva = {'co_id':None}

			# se è presente una commessa, ma non ce ne è una attiva, la imposto
			elif (commessa_attuale and not commessa_attiva['co_id']):
				print("è arrivata una nuova commessa, non ne avevo di attive")
				commessa_attiva = self.generate_internal_data(commessa_attuale)
				self.set_machine_data(commessa_attiva)
				print('commessa attiva:', commessa_attiva['co_commessa'])
				print('articolo:', commessa_attiva['co_descrizioneArticolo'])

			# se è presente una commessa, ma è diversa da quella attiva, la cambio
			elif (commessa_attuale and commessa_attuale['co_id'] != commessa_attiva['co_id']):
				print("è arrivata una nuova commessa, ne avevo già una in canna")
				self.set_db_data(self.update_internal_data_before_save_to_db(commessa_attiva,machine_data))
				commessa_attiva = self.generate_internal_data(commessa_attuale)
				print('commessa attiva:', commessa_attiva['co_commessa'])
				print('articolo:', commessa_attiva['co_descrizioneArticolo'])
				self.set_machine_data(commessa_attiva)

			# se non è presente una commessa, e ce ne era una attiva (chiusa quindi da app), la chiudo da qui
			elif (not commessa_attuale and commessa_attiva['co_id']):
				print("la commessa è stata chiusa da app")
				self.set_db_data(self.update_internal_data_before_save_to_db(commessa_attiva,machine_data))
				commessa_attiva = {'co_id':None}

			# se non è presente una commessa, e non ce ne era una attiva, non faccio niente
			else:
				print("\nnothing to do\n")

			# in ogni caso, in ogni ciclo scrivo i dati del macchinario nella tabella di analisi
			dati_analisi = machine_data.copy()
			dati_analisi['an_idcommessa'] = commessa_attiva['co_id']
			dati_analisi['an_idmacchinario'] = self.id
			insert(self.db_conn, 'dati_siver', dati_analisi)

			time.sleep(interval)


#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON CICLO
#---------------------------------------------------------------------------------------------------------
	def change_commessa_condition(self,commessa_attiva,machine_data):
		return False


	def close_commessa_condition(self,commessa_attiva,machine_data):
		if machine_data and commessa_attiva:
			return machine_data['an_qtaprodotta'] >= commessa_attiva['co_qtaDaProdurre']
		return False


	def generate_internal_data(self,commessa_attiva=None):
		''' ritorna un dizionario pronto per essere riempiti con i dati del ciclo
		'''
		commessa_attiva['co_dataInizio'] = datetime.datetime.now(datetime.timezone.utc)
		return commessa_attiva


	def update_internal_data_before_save_to_db(self,commessa_attiva,machine_data):
		return_data = {}
		return_data['an_idcommessa'] = commessa_attiva['co_id']
		return_data['an_idmacchinario'] = self.id
		return_data['an_dataInizio'] = commessa_attiva['co_dataInizio'].strftime("%Y-%m-%d %H:%M:%S")
		data_fine = datetime.datetime.now(datetime.timezone.utc)
		return_data['an_dataFine'] = data_fine.strftime("%Y-%m-%d %H:%M:%S")
		return_data['an_qtaprodotta'] = commessa_attiva['co_qtaDaProdurre']
		return_data['an_tempoEffettivo'] = (data_fine - commessa_attiva['co_dataInizio']).seconds * 1000 # tempo in millisecondi
		return return_data


	def find_commessa_attiva(self, sleep_time):
		commessa_attiva = self.get_db_data()
		if (not commessa_attiva):
			print("nessuna commessa attiva per {}".format(self.id))
			time.sleep(sleep_time)
			return None
		return commessa_attiva


	def find_machine_data(self,sleep_time):
		machine_data = self.get_machine_data()
		if (not machine_data):
			print("macchina {}: errore nell'estrazione dei dati".format(self.id))
			self.connected = False
			time.sleep(sleep_time)
			return None
		return machine_data


#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON DATABASE
#---------------------------------------------------------------------------------------------------------
	def get_db_data(self, nome_tabella_config=""):
		''' Legge lo stato della macchina
		'''
		try:
			commesse = select(self.db_conn,nome_tabella_config,self.get_fields(nome_tabella_config),'co_flInviato=1 AND co_idmacchinario='+self.id).response
			commessa_attiva = None
			if (commesse and len(commesse) > 0): 
				commessa_attiva = commesse[0]
			return commessa_attiva
		except Exception as e:
			print("Errore in get_db_data per ", self.id," - ",e)
			return False


	def set_db_data(self, values, nome_tabella_scrittura_config="", nome_tabella_commesse_config=""):
		''' Invio dati al macchinario
		'''
		try:
			# salvo i dati di lavorazione
			print(values)
			insert(self.db_conn, nome_tabella_scrittura_config, values)

			# aggiorno lo stato della commessa e la metto come terminata
			result = update(self.db_conn,nome_tabella_commesse_config,'co_id='+str(values['an_idcommessa'])+' AND co_idmacchinario='+self.id,{'co_flInviato':2, 'co_qtaProdotta':values['an_qtaprodotta']})

			return True
		except Exception as e:
			print("Errore in set_machine_data per ", self.id," - ",e)
			return False
				
	
	def get_fields(self, nome_tabella=None):
		''' ciclo i filtri del config e li metto insieme con virgolette e ",", tolgo l'ultima virgola
		'''
		return ", ".join(self.config['fields'][nome_tabella].keys())


#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON MACCHINA
#---------------------------------------------------------------------------------------------------------
	def get_machine_data(self, old_data=None, nome_tabella_config=""):
		''' Legge lo stato della macchina
		'''
		if not old_data:
			old_data = dict()
		try:
			if self.config['connection_type'] == 'snap7':
				for field in self.config['fields'][nome_tabella_config].keys():
					# ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
					if (self.config['fields'][nome_tabella_config][field]):
						old_data[field] = read(self.client,self.config['fields'][nome_tabella_config][field])
			if self.config['connection_type'] == 'opc-ua':
				for field in self.config['fields'][nome_tabella_config].keys():
					# ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
					if (self.config['fields'][nome_tabella_config][field]):
						old_data[field] = self.client.get_node(self.config['fields'][nome_tabella_config][field]).get_value()
			if self.config['connection_type'] == 'modbus':
				for field in self.config['fields'][nome_tabella_config].keys():
					# ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
					if (self.config['fields'][nome_tabella_config][field]):
						old_data[field] = read(self.client,self.config['fields'][nome_tabella_config][field])
			return old_data
		except Exception as e:
			print("Errore in get_machine_data per ", self.id," - ",e)
			return False


	def set_machine_data(self, data, nome_tabella_config=""):
		''' Invio dati al macchinario
		'''
		try:
			if self.config['connection_type'] == 'snap7':
				for field in self.config['fields'][nome_tabella_config].keys():
					# ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
					if (self.config['fields'][nome_tabella_config][field]):
						write(self.client,self.config['fields'][nome_tabella_config][field],data[field])
			if self.config['connection_type'] == 'opc-ua':
				for field in self.config['fields'][nome_tabella_config].keys():
					# ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
					if (self.config['fields'][nome_tabella_config][field]):
						node = self.client.get_node(self.config['fields'][nome_tabella_config][field])
						data_type = node.get_data_type_as_variant_type()
						node.set_value(ua_utils.string_to_variant(str(data[field]),data_type))
			if self.config['connection_type'] == 'modbus':
				for field in self.config['fields'][nome_tabella_config].keys():
					# ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
					if (self.config['fields'][nome_tabella_config][field]):
						write(self.client,self.config['fields'][nome_tabella_config][field],data[field])

			return True
		except Exception as e:
			print("Errore in set_machine_data per ", self.id," - ",e)
			return False


	def connect(self):
		''' In base al protocollo specificato nel config del macchinario, connette la macchina
			Ritorna un handler per la connessione con il macchinario
		'''
		try:
			if self.config['connection_type'] == 'snap7':
				client = plc_connect(self.config['connection_config'])
				if (client):	self.connected = True
			if self.config['connection_type'] == 'modbus':
				client = modbus_connect(self.config['connection_config'])
				if (client):	self.connected = True
			if self.config['connection_type'] == 'opc-ua':
				client = Client(self.config['connection_config']['address'])
				if (self.config['connection_config']['usr']):
					client.set_user(self.config['connection_config']['usr'])
				if (self.config['connection_config']['pwd']):
					client.set_password(self.config['connection_config']['pwd'])
				client.connect()
			if self.config['connection_type'] == 'ethernet':
				client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if self.config['connection_type'] == 'file':
				client = self.config['connection_config']['folder']
			self.client = client
		except TimeoutError:
			print("TimeoutError")
			return False
		except ConnectionRefusedError as e:
			print("ConnectionRefusedError:", e)
			return False
		except ConnectionResetError as e:
			print("ConnectionResetError: ", e)
			return False
		except Exception as e:
			print("Errore in connection_to_machine", e)
		return True


	def disconnect(self):
		''' In base al protocollo specificato nel config del macchinario, disconnette la macchina
		'''
		try:
			if self.config['connection_type'] == 'snap7':
				plc_disconnect(self.client)
			if self.config['connection_type'] == 'modbus':
				modbus_disconnect(self.client)
			if self.config['connection_type'] == 'opc-ua':
				self.client.disconnect()
			if self.config['connection_type'] == 'file':
				# nothing to do
				pass
		except TimeoutError:
			print("TimeoutError")
			return False
		except ConnectionRefusedError as e:
			print("ConnectionRefusedError:", e)
			return False
		except ConnectionResetError as e:
			print("ConnectionResetError: ", e)
			return False
		except Exception as e:
			print("Errore in connection_to_machine", e)
			return False
		return True


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