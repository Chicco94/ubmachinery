#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder # Per leggere
from pymodbus.payload import BinaryPayloadBuilder # Per scrivere
import struct

def read_all(client,list_of_variables):
	''' 
	'''
	try:
		res_dict = dict()
		for key,variable in list_of_variables.items():
			res_dict[key]  = read(client,variable)
		return res_dict
	except Exception as e:
		print(e)
		return None

		

def read(client,variable):
	''' Lettura standard
			- client: client già connesso
			- variable: variabile così composta (address, datatype, length)
	'''
	try:
		registers = client.read_holding_registers(variable['address'],variable['length'])
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
		print(e)
		return None



def write(client,variable,value):
	''' Lettura standard
			- client: client già connesso
			- variable: variabile così composta (area,dn_number,byte,bit,datatype)
			- value: value to be written
	'''
	try:
		builder = BinaryPayloadBuilder()
		if variable['datatype']=='float':
			return False
		if variable['datatype']=='int':
			return client.write_multiple_registers(variable['address'],[value])
		if variable['datatype']=='boolean':
			return False
		if variable['datatype']=='string':
			# Pulisco il campo
			builder.add_string('\x00'*variable['length']*2)
			client.write_multiple_registers(variable['address'],builder.to_registers())
			# Scrivo il valore richiesto
			builder = BinaryPayloadBuilder()
			builder.add_string(value)
			return client.write_multiple_registers(variable['address'],builder.to_registers())
	except Exception as e:
		print(e)
		return None
	

def modbus_connect(config):
	address = config["address"]
	port = config["port"]
	unit_id = config["unit_id"]
	try:
		client = ModbusClient()
		client.host(address)
		client.port(port)
		client.unit_id(unit_id)
		client.open()
		if (client.is_open()):
			print("Connessione con client stabilita")
			return client
		else:
			print("Connessione non riuscita")
			return None
	except Exception as e:
		print(e)
		return None



def modbus_disconnect(client):
	try:
		client.close()
		print("Connessione con client terminata")
		return 0
	except Exception as e:
		print(e)
		return None

##
##def string_to_hex(stringa):
##	'''
##	Funzione che riceve una stringa e ne calcola la lunghezza convertendola poi in esadecimale.
##	Infine ritorna l'esadecimale calcolato con la stringa \x davanti.
##	'''
##	l_str=len(stringa)
##	l_hex=hex(l_str).split('x')[-1]
##	if (len(l_hex)==1):
##		return "\\x0"+l_hex
##	else:
##		return "\\x"+l_hex
##
##



	
