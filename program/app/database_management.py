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


class DBMS:
    db_path = 'app/Gamba_Osaka.db'  # データベース名指定，この指定でappフォルダ内にDBを作れる．

    def __init__(self):
        pass

    def make_db(self):
        if 'db' not in g:
            g.db = sqlite3.connect(self.db_path)
            return g.db

    # classの中だけで使いたいので，_を付けている．
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        return conn

    def DF_to_db(self, DF, column_list):
        self.DF = DF
        self.column_list = column_list

        conn = sqlite3.connect(self.db_path)
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

    def get_data(self, team_name, column_list):
        self.team_name = team_name
        self.column_list = column_list

        select_team = 'Gamba_Osaka'

        if team_name == 'G大阪':
            select_team = 'Gamba_Osaka'

        # SELECT文で全部とってくる．
        select_sql = 'SELECT * FROM {0}'.format(select_team)

        # 同じクラス内のメソッドを実行したい．
        conn = self._get_conn()

        cur = conn.cursor()

        cur.row_factory = sqlite3.Row

        corsor = cur.execute(select_sql)

        all_column = corsor.description

        # .fetchall()で，全てのデータをとってくる．
        alldata = corsor.fetchall()

        # print("discription =", all_column)
        # print(type(all_column[1]))
        # print(all_column[1])

        # list()でタプルをリストに変換する．
        all_column = list(all_column)
        # print("all_column =", all_column)

        conn.close()

        alldata = pd.DataFrame(alldata, columns=self.column_list)

        return alldata
