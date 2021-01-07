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

from numpy.random import choice
from sklearn.model_selection import train_test_split


class Prediction:
    def __init__(self):
        self._home = "home"
        self._away = "away"
        self._pred_class = "predict_class"

    # ホームチームのプロパティ設定
    @property
    def home_team(self):
        return self._home

    @home_team.setter
    def home_team(self, home):
        self._home = home

    # アウェイチームのプロパティ設定
    @property
    def away_team(self):
        return self._away

    @away_team.setter
    def away_team(self, away):
        self._away = away

    # 予測の結果のラベルプロパティ設定
    @property
    def predict_class(self):
        return self._pred_class

    @predict_class.setter
    def predict_class(self, pred_class):
        self._pred_class = pred_class

    def print_team_name(self):
        print("hometeam =", self._home)
        print("awayteam =", self._away)
        print('predict result =', self._pred_class)

    def data_transform(self, data):
        self.data = data

        # 試合結果の列：0or1or2（DF.valuesでnumpy配列にする．）
        all_results = self.data['result'].values

        # Unnamed: 0も抜く，# 他にも不要なデータ抜く
        stats_data = self.data.drop(['Unnamed: 0', 'result', 'home score', 'away score',
                                     'team', 'season', 'Opponent'], axis=1
                                    )

        # 列名を取得．
        feature_name = stats_data.columns

        print(stats_data)
        all_data = stats_data

        #all_data = stats_data.values

        # 17節までを学習データにする．
        """
        X_train = stats_data[:17]
        y_train = results[:17]

        # 18節以降をテストデータにする．
        X_test = stats_data[17:]
        y_test = results[17:]
        """
        """
        return X_train, y_train, X_test, y_test, feature_name
        """
        return all_data, all_results, feature_name

    def make_model(self, all_data, all_results, feature_name):
        self.all_data = all_data
        self.all_results = all_results
        self.feature_name = feature_name

        train_data = xgb.DMatrix(self.all_data, label=self.all_results, feature_names=self.feature_name)

        param = {'max_depth': 10, 'eta': 1, 'objective': 'multi:softmax', 'num_class': 3}

        num_round = 10
        bst_model = xgb.train(param, train_data, num_round)

        return bst_model  # modelを返す．

    def make_test_data(self, all_data, n_samples, feature_name):
        self.all_data = all_data
        self.n_samples = n_samples
        self.feature_name = feature_name
        #print("all data =", self.all_data)

        test_data_DF = pd.DataFrame()

        for row in self.all_data:  # 列でfor文回したい．
            #print(row)
            sub_DF = self.all_data[row].values.tolist()  # 一つの列のデータ抜き出した．

            hist = np.histogram(sub_DF, bins=len(sub_DF))  # ヒストグラム作成．

            freq_list = hist[0].tolist()  # 頻度．
            values_list = hist[1].tolist()  # 実数値．

            # 頻度と実数値のリストの長さが異なるので合わせる．（https://www.sejuku.net/blog/70961 を参考）．
            bin_list = []
            for i in range(1, len(values_list)):
                bin_list.append((values_list[i - 1] + values_list[i]) / 2)

            # ここからchoice使う（下記参考）．
            """
            https://paper.hatenadiary.jp/entry/2017/07/20/000000#%E3%82%A2%E3%82%A4%E3%83%86%E3%83%A0%E3%81%94%E3%81%A8%E3%81%AE%E9%87%8D%E3%81%BF%E3%81%AB%E5%9F%BA%E3%81%A5%E3%81%84%E3%81%A6%E9%81%B8%E6%8A%9E
            """
            items = bin_list  # この中から重みを付けてランダムに持ってくる．
            distribution = np.array(freq_list, dtype=np.float64)
            distribution /= distribution.sum()

            all_pickup = choice(items, self.n_samples, p=distribution)  # これはリスト．

            series_pickup = pd.Series(all_pickup)

            test_data_DF = pd.concat([test_data_DF, series_pickup], axis=1)

        test_data_DF.columns = self.feature_name

        #print(test_data_DF)

        return test_data_DF

    def predictin(self, model, test_DF):
        self.model = model
        self.test_DF = test_DF

        # テストデータ作成（https://ohke.hateblo.jp/entry/2019/02/16/230000 を参考）．
        # https://qiita.com/predora005/items/19aebcf3aa05946c7cf4 を参考．
        test_data = xgb.DMatrix(self.test_DF)
        #test_data = xgb.DMatrix(self.test_DF, feature_names=self.feature_name)

        all_pred = self.model.predict(test_data)

        return all_pred

    def _prediction(self, X_train, y_train, X_test, y_test, feature_name):
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


