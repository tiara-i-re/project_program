#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 12/16/2020 12:50:28 
@author: Taira
"""

import pandas as pd
import numpy as np
import os

import sqlite3  # sqlite3標準モジュールをインポート
from flask import Flask, g, request, render_template, current_app

dbname = 'Gamba_Osaka.db'  # データベース名指定


class DBMS:
    def __init__(self):
        pass

    def make_db(self):
        if 'db' not in g:
            g.db = sqlite3.connect(dbname)
            return g.db

    def DF_to_db(self, DF, column_list):
        self.DF = DF
        self.column_list = column_list

        conn = sqlite3.connect(dbname)
        #self.DF.to_sql('Gamba_Osaka', g.db, if_exists='append', index=None)
        #self.DF.to_sql('Gamba_Osaka', conn, if_exists='append', index=None)
        conn.commit()

        # SELECT文で全部とってくる．
        select_sql = 'SELECT * FROM Gamba_Osaka'

        cur = conn.cursor()
        #cur = conn.cursor()
        cur.row_factory = sqlite3.Row

        corsor = cur.execute(select_sql)

        all_column = corsor.description

        # .fetchall()で，全てのデータをとってくる．
        alldata = corsor.fetchall()

        #print("discription =", all_column)
        #print(type(all_column[1]))
        #print(all_column[1])

        # list()でタプルをリストに変換する．
        all_column = list(all_column)
        #print("all_column =", all_column)

        conn.close()

        alldata = pd.DataFrame(alldata, columns=self.column_list)

        return alldata



    def get_data(self):


        pass



