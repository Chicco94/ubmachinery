#!/usr/bin/python
# -*- coding: utf-8 -*-

from ublib.sql_connection import connect_to_db
from Siver_Machine import Siver_Machine
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
    
    siver_connector = Siver_Machine(config_siver,None,db_conn)
    siver_connector.start()

    # non chiudo il programma finchè ho almeno una macchina che sta andando
    siver_connector.join()
