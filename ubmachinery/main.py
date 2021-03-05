#!/usr/bin/python
# -*- coding: utf-8 -*-

from ublib.sql_connection import connect_to_db
from ublib.OpcUa_Machine import OpcUa_Machine
from config import prod_flag, prod_db_config, dev_db_config, config_siver


if __name__=="__main__":
	print("Controllo ambiente...")
	db_config = None
	if (prod_flag):
		db_config = prod_db_config
		print("Sono in produzione")
	else:
		db_config = dev_db_config
		print("Sono in dev")

	db_conn = connect_to_db(db_config)
	
	siver_machine = OpcUa_Machine(
		1,
		db_conn,
		{
			'address': 'esempio'
			,'usr':'esempio'
			,'pwd': 'esempio'
		},
		{
			'table_name':'commesse_siver',
			'table_fields':{
				'co_id': None
				,'co_idmacchinario': None
				,'co_dataOrdine': None
				,'co_numeroOrdine': None
				,'co_commessa': {'address':200, 'bit':None, 'datatype':'string', 'length':8}
				,'co_cliente': None
				,'co_dataConsegna': None
				,'co_codiceArticolo': {'address':208, 'bit':None, 'datatype':'string', 'length':8}
				,'co_descrizioneArticolo': None
				,'co_qtaDaProdurre': {'address':216, 'bit':None, 'datatype':'int', 'length':1}
				,'co_qtaProdotta': None
				,'co_note': None
				,'co_flInviato': None
			}
		},
		{
			'table_name':'analisi_siver',
			'table_fields':{
				'an_id': None
				,'an_idmacchinario': None
				,'an_idcommessa': {'address':200, 'bit':None, 'datatype':'string', 'length':8}
				,'an_qtaprodotta': None
				,'an_dataInizio': None
				,'an_dataFine': None
				,'an_tempoEffettivo': None
				,'an_timestamp': None
				,'an_flLettura': None
			}
		},
		{
			'table_name':'dati_siver',
			'table_fields':{
				'an_id': None
				,'an_idmacchinario': None
				,'an_idcommessa': {'address':200, 'bit':None, 'datatype':'string', 'length':8}
				,'an_velocitaTrasportatore': {'address':8, 'bit':None, 'datatype':'float', 'length':2}
				,'an_contenitoreAinServizio': {'address':64, 'bit':2, 'datatype':'boolean', 'length':1}
				,'an_contenitoreBinServizio': {'address':64, 'bit':3, 'datatype':'boolean', 'length':1}
				,'an_cambioColore': {'address':64, 'bit':4, 'datatype':'boolean', 'length':1}
				,'an_puliziaAinCorso': {'address':64, 'bit':5, 'datatype':'boolean', 'length':1}
				,'an_puliziaBinCorso': {'address':64, 'bit':6, 'datatype':'boolean', 'length':1}
				,'an_livelloMinimoA': {'address':64, 'bit':11, 'datatype':'boolean', 'length':1}
				,'an_livelloMinimoB': {'address':64, 'bit':12, 'datatype':'boolean', 'length':1}
				,'an_timestamp': None
			}
		}
		)
	siver_machine.start()

	# non chiudo il programma finchè ho almeno una macchina che sta andando
	siver_machine.join()
