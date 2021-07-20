

#!/usr/bin/python
# -*- coding: utf-8 -*-

from ublib.Costumer_Machine import Costumer_Machine

# per connessione opc-ua
from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder # Per leggere
from pymodbus.payload import BinaryPayloadBuilder # Per scrivere



class OpcUa_Machine(Costumer_Machine):
	''' Classe che estende i thread che rappresenta una macchina con scambio dati OPC-UA'''

#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON MACCHINA
#---------------------------------------------------------------------------------------------------------
	def read_variable(self,variable):
		try:
			registers = self.client.read_holding_registers(variable['address'],variable['length'])
			decoder = BinaryPayloadDecoder.fromRegisters(registers)
			if variable['datatype']=='float':
				return decoder.decode_32bit_float()
			if variable['datatype']=='int':
				return registers[0]
			if variable['datatype']=='boolean':
				return int("{0:b}".format(registers[0])[variable['bit']])
			if variable['datatype']=='string':
				return decoder.decode_string(variable['length']*2).decode('utf-8').replace('\x00','')
			raise Exception
		except Exception as e:
			print("Errore in read_variable per ", self.id," - ", e)
			return False


	def write_variable(self,variable,value):
		try:
			builder = BinaryPayloadBuilder()
			if variable['datatype']=='float':
				return False
			if variable['datatype']=='int':
				return self.client.write_multiple_registers(variable['address'],[value])
			if variable['datatype']=='boolean':
				return False
			if variable['datatype']=='string':
				# Pulisco il campo
				builder.add_string('\x00'*variable['length']*2)
				self.client.write_multiple_registers(variable['address'],builder.to_registers())
				# Scrivo il valore richiesto
				builder = BinaryPayloadBuilder()
				builder.add_string(value)
				return self.client.write_multiple_registers(variable['address'],builder.to_registers())
			raise Exception
		except Exception as e:
			print("Errore in write_variable per ", self.id," - ", e)
			return False


	def connect(self):
		''' In base al protocollo specificato nel config del macchinario, connette la macchina
			Ritorna un handler per la connessione con il macchinario
		'''
		try:
			address = self.config["address"]
			port = self.config["port"]
			unit_id = self.config["unit_id"]

			self.client = ModbusClient()
			self.client.host(address)
			self.client.port(port)
			self.client.unit_id(unit_id)
			self.client.open()
			if (self.client.is_open()):
				print("Connessione con client stabilita")
				return True
			else:
				print("Connessione non riuscita")
			return False
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


	def disconnect(self):
		''' In base al protocollo specificato nel config del macchinario, disconnette la macchina
		'''
		try:
			self.client.close()
			return True
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