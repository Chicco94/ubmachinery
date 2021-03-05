prod_flag = True

prod_db_config ={
	'user' : 'connettore',
	'password' : '4qP4X6ZW_@+Vrc^J',
	'host' : 'localhost',
	'port' : 3306,
	'database' : 'ubmachinery'
}

dev_db_config ={
	'user' : 'devdb',
	'password' : 'devdb',
	'host' : '192.168.50.179',
	'port' : 3306,
	'database' : 'ubmachinery_bemmex'
}


config_siver = {
	'connection_type': 'modbus' # snap7, opc-ua, modbus, file, ethernet
	,'db_config':{
		'idMacchinario': '9'
	}
	,'connection_config':{
		'address' : '192.168.0.26'
		,'port' : 502
		,'unit_id': 1
	}
	,'fields':{
		'commesse_siver': {
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
		,'analisi_siver':{
			'an_id': None
			,'an_idmacchinario': None
			,'an_idcommessa': {'address':200, 'bit':None, 'datatype':'string', 'length':8}
			,'an_qtaprodotta': None
			,'an_dataInizio': None
			,'an_dataFine': None
			,'an_tempoEffettivo': None
			,'an_velocitaTrasportatore': {'address':8, 'bit':None, 'datatype':'float', 'length':2}
			,'an_contenitoreAinServizio': {'address':64, 'bit':2, 'datatype':'boolean', 'length':1}
			,'an_contenitoreBinServizio': {'address':64, 'bit':3, 'datatype':'boolean', 'length':1}
			,'an_cambioColore': {'address':64, 'bit':4, 'datatype':'boolean', 'length':1}
			,'an_puliziaAinCorso': {'address':64, 'bit':5, 'datatype':'boolean', 'length':1}
			,'an_puliziaBinCorso': {'address':64, 'bit':6, 'datatype':'boolean', 'length':1}
			,'an_livelloMinimoA': {'address':64, 'bit':11, 'datatype':'boolean', 'length':1}
			,'an_livelloMinimoB': {'address':64, 'bit':12, 'datatype':'boolean', 'length':1}
			,'an_timestamp': None
			,'an_flLettura': None
		}
	}
}