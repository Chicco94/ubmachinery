#!/usr/bin/python
# -*- coding: utf-8 -*-
from opcua import ua
from opcua import Client
from opcua.common import ua_utils


def opcua_read_all(client,list_of_variables):
    ''' 
    '''
    try:
        res_dict = dict()
        for key,variable in list_of_variables.items():
            res_dict[key]  = read(client, variable)
        return res_dict
    except Exception as e:
        print("Errore gestito opcua", e)
        return None

        

def opcua_read(client,variable):
    ''' Lettura standard
            - client: client già connesso
            - variable: variabile così composta ("ns=x;s=address")
    '''
    try:
        return client.get_node(variable).get_value()
    except Exception as e:
        print("Errore gestito opcua", e)
        return None


def opcua_write(plc,variable,value):
    ''' Lettura standard
            - plc: client già connesso
            - variable: variabile così composta (area,dn_number,byte,bit,datatype)
            - value: value to be written
    '''
    try:
        node = self.client.get_node(variable)
        data_type = node.get_data_type_as_variant_type()
        return node.set_value(ua_utils.string_to_variant(value,data_type))
    except Exception as e:
        print("Errore gestito opcua", e)
        return None

    

def opcua_connect(config):
    print(config)
    try:
        client = Client(config['connection_config']['address'])
        if (config['connection_config']['usr']):
            client.set_user(config['connection_config']['usr'])
        if (config['connection_config']['pwd']):
            client.set_password(config['connection_config']['pwd'])
        client.connect()
    except Exception as e:
        print("Errore gestito opcua", e)
        return None



def opcua_disconnect(client):
    try:
        client.disconnect()
        print("Connessione con opcua terminata")
        return 0
    except Exception as e:
        print("Errore gestito opcua", e)
        return None



    
