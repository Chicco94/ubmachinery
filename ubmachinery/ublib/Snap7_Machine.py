

#!/usr/bin/python
# -*- coding: utf-8 -*-

from ublib.Costumer_Machine import Costumer_Machine

# per connessione snap7
import snap7
import snap7.client
from snap7.types import *
from snap7.util import *
import struct



class Snap7_Machine(Costumer_Machine):
	''' Classe che estende i thread che rappresenta una macchina con scambio dati snap7'''

#---------------------------------------------------------------------------------------------------------
#								INTERAZIONI CON MACCHINA
#---------------------------------------------------------------------------------------------------------
	def read_variable(self,variable):
		''' Lettura standard
			- plc: client già connesso
			- variable: variabile così composta (area,dn_number,byte,bit,datatype)
		'''
		try:
			return self.read_memory(
						self.client,
						variable['area'],
						variable['db_number'],
						variable['byte'],
						variable['bit'],
						variable['datatype'],
						variable['length'] if variable['datatype'] == 'string' else 10
						)
		except snap7.snap7exceptions.Snap7Exception as e:
			print("Errore gestito snap", e)
			return False
		except Exception as e:
			print("Errore in read_variable per ", self.id," - ", e)
			return False

	def read_memory(self,plc,area, db_number,byte,bit,datatype, length=None):
		''' Legge un area di memoria:
				- plc: client già connesso
				- db_number: numero db
				- byte: indirizzo di lettura
				- bit: bit specifico di lettura
				- datatype: tipo standar snap7
			Ritorna valore letto
		'''
		try:
			if datatype == 'string':
					return plc.read_area(areas[area],db_number,byte,length).decode('utf-8')
			result = plc.read_area(areas[area],db_number,byte,datatype)
			if datatype == S7WLBit:
					return get_bool(result,0,bit)
			if datatype == S7WLByte:
					return get_int(result,0)
			if datatype == S7WLWord:
					return struct.unpack('>i',plc.db_read(db_number,byte,4))[0]
			if datatype == S7WLReal:
					return get_real(result,0)
			if datatype == S7WLDWord:
					return get_dword(result,0)
			
		except snap7.snap7exceptions.Snap7Exception as e:
			print("Errore gestito snap", e)
			return None


	def write_variable(self,variable,value):
		try:
			return self.write_memory(
						self.client,
						variable['area'],
						variable['db_number'],
						variable['byte'],
						variable['bit'],
						variable['datatype'],
						value,
						variable['length'] if variable['datatype'] == 'string' else 10
						)
		except snap7.snap7exceptions.Snap7Exception as e:
			print("Errore gestito snap", e)
			return None

	def write_memory(self,plc,area,db_number,byte,bit,datatype,value,length=None):
		''' Legge un area di memoria:
				- plc: client già connesso
				- db_number: numero db
				- byte: indirizzo di lettura
				- bit: bit specifico di lettura
				- datatype: tipo standar snap7
				- value: valore da inserire
			Ritorna True se andato a buon fine, False altrimeti
		'''
		if datatype == 'string':
			# pulisco l'area di memoria prima di scrivere
			plc.write_area(areas[area],db_number,byte,(b'\x00'*length))
			plc.write_area(areas[area],db_number,byte,bytearray(str(value),'utf-8'))
			return True
		result = plc.read_area(areas[area],db_number,byte,datatype)
		if datatype == S7WLBit:
			set_bool(result,0,bit,value)
		if datatype == S7WLByte:
			set_int(result, 0, value)
		if datatype == S7WLWord:
			plc.write_area(areas[area],db_number,byte,struct.pack('>i',int(value)))
			return True
		if datatype == S7WLReal:
			set_real(result, 0, value)
		if datatype == S7WLDWord:
			set_dword(result, 0, value)
		plc.write_area(areas[area],db_number,byte,result)
		return True


	def connect(self):
		''' In base al protocollo specificato nel config del macchinario, connette la macchina
			Ritorna un handler per la connessione con il macchinario
		'''
		address = self.config["address"]
		rack	= self.config["rack"]
		slot	= self.config["slot"]
		tcpport = self.config["tcpport"]
		try:
			self.client = snap7.client.Client()
			self.client.connect(
				address  = address
				,rack	= rack
				,slot	= slot
				,tcpport = tcpport
			)
			if (self.client.get_connected()):
				print("Connessione con plc stabilita")
				return True
			else:
				print("Connessione non riuscita")
				return None
		except snap7.snap7exceptions.Snap7Exception as e:
			print("Errore gestito snap", e)
			return None


	def disconnect(self):
		''' In base al protocollo specificato nel config del macchinario, disconnette la macchina
		'''
		try:
			self.client.disconnect()
			self.client.destroy()
			print("Connessione con plc terminata")
			return True
		except snap7.snap7exceptions.Snap7Exception as e:
			print("Errore gestito snap", e)
			return None
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