#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 12/13/2020 18:04:16 
@author: Taira
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import mglearn
import graphviz

import xgboost as xgb

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


class Prediction:
    def __init__(self, home, away, pred_class):
        self.home = home
        self.away = away
        self.pred_class = pred_class

    def print_team_name(self):
        print("hometeam =", self.home)
        print("awayteam =", self.away)
        print('predict result =', self.pred_class)

    def data_transform(self, data):
        self.data = data

        # DF.valuesでnumpy配列にする．
        results = self.data['result'].values

        # Unnamed: 0も抜く
        stats_DF = self.data.drop(['Unnamed: 0', 'result'], axis=1)
        # 他にも不要なデータ抜く
        stats_data = stats_DF.drop(['team', 'season', 'Opponent'], axis=1)
        feature_name = stats_data.columns

        stats_data = stats_data.values

        # 17節までを学習データにする．
        X_train = stats_data[:17]
        y_train = results[:17]

        # 18節以降をテストデータにする．
        X_test = stats_data[17:]
        y_test = results[17:]

        return X_train, y_train, X_test, y_test, feature_name

    def prediction(self, X_train, y_train, X_test, y_test, feature_name):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.feature_name = feature_name

        dtrain = xgb.DMatrix(self.X_train, label=self.y_train, feature_names=self.feature_name)
        dvalid = xgb.DMatrix(self.X_test, label=self.y_test, feature_names=self.feature_name)

        param = {'max_depth': 10, 'eta': 1, 'objective': 'multi:softmax', 'num_class': 3}

        num_round = 10
        bst = xgb.train(param, dtrain, num_round)

        pred = bst.predict(dvalid)

        accuracy = accuracy_score(self.y_test, pred)

        print(pred)
        print(y_test)

        return accuracy






