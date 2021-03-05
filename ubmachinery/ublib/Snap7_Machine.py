

#!/usr/bin/python
# -*- coding: utf-8 -*-

from Costumer_Machine import Costumer_Machine

# per connessione opc-ua
from opcua import ua
from opcua import Client
from opcua.common import ua_utils



class OpcUa_Machine(Costumer_Machine):
	''' Classe che estende i thread che rappresenta una macchina con scambio dati OPC-UA'''

#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON MACCHINA
#---------------------------------------------------------------------------------------------------------
	def read_variable(self,variable):
		try:
			return self.client.get_node(variable).get_value()
		except Exception as e:
			print("Errore in read_variable per ", self.id," - ", e)
			return False


	def write_variable(self,variable,value):
		try:
			node = self.client.get_node(variable)
			data_type = node.get_data_type_as_variant_type()
			node.set_value(ua_utils.string_to_variant(str(value),data_type))
			return True
		except Exception as e:
			print("Errore in write_variable per ", self.id," - ", e)
			return False


	def get_machine_data(self, old_data=None, nome_tabella_config=""):
		''' Legge lo stato della macchina
		'''
		if not old_data:
			old_data = dict()
		try:
			for field in self.config_dati.keys():
				# ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
				if (self.config_dati[field]):
					old_data[field] = self.read_variable(self.config_dati[field])
			return old_data
		except Exception as e:
			print("Errore in get_machine_data per ", self.id," - ",e)
			return False


	def set_machine_data(self, data, nome_tabella_config=""):
		''' Invio dati al macchinario
		'''
		try:
			for field in self.config_commesse.keys():
				# ci potrebbero essere dei valori che voglio tenere nel config ma che non voglio leggere dal macchinario
				if (self.config_commesse[field]):
					self.write_variable(self.config_commesse[field], data[field])
			return True
		except Exception as e:
			print("Errore in set_machine_data per ", self.id," - ",e)
			return False


	def connect(self):
		''' In base al protocollo specificato nel config del macchinario, connette la macchina
			Ritorna un handler per la connessione con il macchinario
		'''
		try:
			client = Client(self.config_connessione['address'])
			if (self.config_connessione['usr']):
				client.set_user(self.config_connessione['usr'])
			if (self.config_connessione['pwd']):
				client.set_password(self.config_connessione['pwd'])
			client.connect()
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
			self.client.disconnect()
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