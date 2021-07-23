#!/usr/bin/python
# -*- coding: utf-8 -*-

import mysql.connector


class Response:
    def __init__(self, status, response=None, error=""):
        self.status = status
        self.response = response
        self.error = error


def connect_to_db(config):
    try:
        conn = mysql.connector.connect(**config)
        print("Connessione con database stabilita")
    except mysql.connector.Error as SQL_ERR:
        print("Errore nella connesione: ", SQL_ERR)
        return None
    return conn


def disconnect_from_db(connection):
    connection.close()
    print("Connessione con db terminata")
    return 0


def select(connection, table, fields="*", cond_where=""):
    """In caso di errore ritorna None
    per la condizione WHERE scrivere la stringa effettiva
    """
    query = (
        "SELECT "
        + fields
        + " FROM "
        + table
        + (" WHERE " + cond_where if cond_where else "")
    )
    try:
        connection.reconnect()
        mycursor = connection.cursor(dictionary=True)
        mycursor.execute(query)
        myresult = mycursor.fetchall()
        mycursor.close()
        return Response(True, myresult)
    except mysql.connector.Error as SQL_ERR:
        print("Errore SQL:", SQL_ERR, "\n", query)
        return Response(False, error="SQL_ERR")
    except Exception as GEN_ERR:
        print("Errore Generico:", GEN_ERR, "\n", query)
        return Response(False, error="GEN_ERR")


def insert(connection, table_name, dict_of_data):
    """Inserisce una lista di oggetti a database specificandone i campi"""

    try:
        connection.reconnect()
        mycursor = connection.cursor()
        placeholder = ", ".join(["%s"] * len(dict_of_data))
        query = "insert into `{table}` ({columns}) values ({values});".format(
            table=table_name, columns=",".join(dict_of_data.keys()), values=placeholder
        )
        mycursor.execute(query, list(dict_of_data.values()))
        connection.commit()
        mycursor.close()
        return (True, query)
    except Exception as e:
        print(e)
        print(query)
        return (False, e)


def update(connection, table, cond_where, campi):
    """Aggiorna i campi (dizionario campo:valore) della tabella che rispettano la condizione WHERE"""
    try:
        connection.reconnect()
        mycursor = connection.cursor()
        query = ["UPDATE " + table + " SET "]
        listacampi = []
        for colonna, valore in campi.items():
            listacampi.append(str(colonna) + "=" + str(valore))

        query.append(",".join(listacampi))

        if cond_where != "":
            query.append(" where " + cond_where)

        query = "".join(query)
        mycursor.execute(query)
        connection.commit()
        mycursor.close()
        return (True, query)
    except Exception as e:
        print(e)
        return (False, e)
