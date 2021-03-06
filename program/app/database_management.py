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
    db_path = 'app/J1_prediction.db'  # データベース名指定，この指定でappフォルダ内にDBを作れる．
    #db_path = 'J1_prediction.db'  # データベース名指定，この指定でappフォルダ内にDBを作れる．

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

    def DF_to_db(self, df: pd.DataFrame, column_list: list):
        self.df = df
        self.column_list = column_list

        conn = sqlite3.connect(self.db_path)
        #self.DF.to_sql('Gamba_Osaka', g.db, if_exists='append', index=None)
        #self.DF.to_sql('Gamba_Osaka', conn, if_exists='append', index=None)
        self.df.to_sql('Tosu', conn, if_exists='append', index=None)
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

    def get_team_name(self, select_name: str) -> str:
        self.select_name: str = select_name

        if self.select_name == 'G大阪':
            db_name: str = 'Gamba_Osaka'

        elif self.select_name == '浦和レッズ':
            db_name: str = 'Urawa'

        elif self.select_name == '鹿島アントラーズ':
            db_name: str = 'Kashima'

        elif self.select_name == '川崎フロンターレ':
            db_name: str = 'Kawasaki'

        elif self.select_name == 'FC東京':
            db_name: str = 'FC_Tokyo'

        elif self.select_name == 'サンフレッチェ広島':
            db_name: str = 'Hiroshima'

        elif self.select_name == '横浜FM':
            db_name: str = 'Yokohama_FM'

        elif self.select_name == 'ヴィッセル神戸':
            db_name: str = 'Kobe'

        elif self.select_name == 'サガン鳥栖':
            db_name: str = 'Tosu'

        elif self.select_name == 'ベガルタ仙台':
            db_name: str = 'Sendai'

        return db_name

    def get_data(self, team_name: str, column_list: list) -> pd.DataFrame:
        self.team_name: str = team_name
        self.column_list: list = column_list

        """select_team = 'Gamba_Osaka'

        if team_name == 'G大阪':
            select_team = 'Gamba_Osaka'
            """

        # SELECT文で全部とってくる．
        select_sql: str = 'SELECT * FROM {0}'.format(self.team_name)

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
