#!/usr/bin/python
# -*- coding: utf-8 -*-
import snap7
import snap7.client
from snap7.snap7types import *
from snap7.util import *
import struct


def read_all(plc,list_of_variables):
	''' 
	'''
	try:
		res_dict = dict()
		for key,variable in list_of_variables.items():
			res_dict[key]  = read_memory(
								plc,
								variable['area'],
								variable['db_number'],
								variable['byte'],
								variable['bit'],
								variable['datatype'],
								variable['length'] if variable['datatype'] == 'string' else 10
								)
		return res_dict
	except snap7.snap7exceptions.Snap7Exception as e:
		print("Errore gestito snap", e)

		

def read(plc,variable, length=None):
	''' Lettura standard
			- plc: client già connesso
			- variable: variabile così composta (area,dn_number,byte,bit,datatype)
	'''
	try:
		return read_memory(
					plc,
					variable['area'],
					variable['db_number'],
					variable['byte'],
					variable['bit'],
					variable['datatype'],
					variable['length'] if variable['datatype'] == 'string' else 10
					)
	except snap7.snap7exceptions.Snap7Exception as e:
		print("Errore gestito snap", e)
		return None


		
def read_memory(plc,area, db_number,byte,bit,datatype, length=None):
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



def write(plc,variable,value):
	''' Lettura standard
			- plc: client già connesso
			- variable: variabile così composta (area,dn_number,byte,bit,datatype)
			- value: value to be written
	'''
	try:
		return write_memory(
					plc,
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


		
def write_memory(plc,area,db_number,byte,bit,datatype,value,length=None):
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
	

def plc_connect(config):
	address = config["address"]
	rack	= config["rack"]
	slot	= config["slot"]
	tcpport = config["tcpport"]
	try:
		client = snap7.client.Client()
		client.connect(
			address  = address
			,rack	= rack
			,slot	= slot
			,tcpport = tcpport
		)
		if (client.get_connected()):
			print("Connessione con plc stabilita")
			return client
		else:
			print("Connessione non riuscita")
			return None
	except snap7.snap7exceptions.Snap7Exception as e:
		print("Errore gestito snap", e)
		return None



def plc_disconnect(plc):
	try:
		plc.disconnect()
		plc.destroy()
		print("Connessione con plc terminata")
		return 0
	except snap7.snap7exceptions.Snap7Exception as e:
		print("Errore gestito snap", e)
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



	
