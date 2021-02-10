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
import lightgbm as lgb

from numpy.random import choice
from sklearn.neighbors import KernelDensity


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

    def data_transform(self, data: pd.DataFrame) -> [pd.DateOffset, list, list]:
        self.data = data

        # 試合結果の列：0or1or2（DF.valuesでnumpy配列にする．）
        #all_results = self.data['result'].values.tolist()
        all_results: list = self.data['home score'].values.tolist()
        #print(all_results)
        #print(len(all_results))

        # Unnamed: 0も抜く，# 他にも不要なデータ抜く
        stats_data: pd.DataFrame = self.data.drop(['Unnamed: 0', 'result', 'home score', 'away score',
                                                   'team', 'season', 'Opponent'], axis=1
                                                  )
        # 列名を取得．
        feature_name: list = stats_data.columns.tolist()

        #print(stats_data)
        all_data: pd.DataFrame = stats_data

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

    def make_model(self, all_data: pd.DataFrame, all_results: list, feature_name: list) -> object:
        self.all_data = all_data
        self.all_results = all_results
        self.feature_name = feature_name

        score_count = max(self.all_results) + 1  # max()で最大得点数を取得する．
        #print("score count =", score_count)

        # LightGBMのデータセット作成．
        lgb_train = lgb.Dataset(self.all_data, self.all_results)

        # https://cocoinit23.com/lightgbm-cannot-use-dataset-instance-for-prediction-please-use-raw-data-instead/
        # ↑は学習時の表示をなくすために参考にしたサイト．

        # LightGBM のハイパーパラメータ
        lgbm_params = {
            # 多値分類問題
            'objective': 'multiclass',
            # クラス数は 3
            # クラス数はscoreの種類に合わせる．
            'num_class': score_count,
            'verbose': -1,
            'max_depth': 7
        }  # 'verbose': -1 とすることで学習のログを消せる．

        # 'max_depth': 3
        # 上記のパラメータでモデルを学習する
        model: object = lgb.train(lgbm_params, lgb_train, valid_sets=lgb_train, verbose_eval=False)
        # verbose_eval=False とすることで学習のログを消せる．

        return model  # modelを返す．

    def _make_model(self, all_data, all_results, feature_name):
        self.all_data = all_data
        self.all_results = all_results
        self.feature_name = feature_name

        # XGBoostのモデル作成
        train_data = xgb.DMatrix(self.all_data, label=self.all_results, feature_names=self.feature_name)

        param = {'max_depth': 10, 'eta': 1, 'objective': 'multi:softmax', 'num_class': 3}

        num_round = 10
        bst_model = xgb.train(param, train_data, num_round)

        return bst_model  # modelを返す．

    def make_test_data(self, all_data: pd.DataFrame, n_samples: int, feature_name: list) -> pd.DataFrame:
        self.all_data = all_data
        self.n_samples = n_samples
        self.feature_name = feature_name

        test_data_DF: pd.DataFrame = pd.DataFrame()

        for row in self.all_data:  # 列でfor文回したい．
            # row = チーム名になる
            np_sub_df: np.array = self.all_data[row].values  # 一つの列のデータ抜き出した．np.array

            # KDEで確率密度関数を推定（今回はdefault）
            kde_model = KernelDensity(kernel='gaussian').fit(np_sub_df[:, None])

            random_sample = kde_model.sample(n_samples)

            # flatten()で一次元にして，tolist()でlistにする．
            random_sample_list: list = random_sample.flatten().tolist()

            series_sample: pd.Series = pd.Series(random_sample_list)

            test_data_DF: pd.DataFrame = pd.concat([test_data_DF, series_sample], axis=1)

            # print(test_data_DF)

        #print(test_data_DF)
        # 列名を設定．
        test_data_DF.columns = self.feature_name

        return test_data_DF

    def _make_test_data(self, all_data, n_samples, feature_name):
        self.all_data = all_data
        self.n_samples = n_samples
        self.feature_name = feature_name
        #print("all data =", self.all_data)

        test_data_DF = pd.DataFrame()

        for row in self.all_data:  # 列でfor文回したい．
            # row = チーム名になる
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

        # 列名を設定．
        test_data_DF.columns = self.feature_name

        #print(test_data_DF)

        return test_data_DF

    def predictin(self, model: object, test_DF: pd.DataFrame) -> list:
        self.model = model
        self.test_DF = test_DF

        #np_test = self.test_DF.values  # np.arrayにする．

        #test_data = lgb.Dataset(np_test)
        #print(test_data)

        all_pred = self.model.predict(self.test_DF, num_iteration=model.best_iteration)
        #print(all_pred)
        all_pred_max: np.array = np.argmax(all_pred, axis=1)  # 最尤と判断したクラスの値にする
        #print(all_pred_max)
        all_pred_max: list = all_pred_max.tolist()

        return all_pred_max

    def feature_importance(self, model: object, feature_name: list, team_name: str) -> None:
        self.model = model
        self.feature_name = feature_name
        self.team_name = team_name

        # ------------プロット用-----------------
        fig = plt.figure(figsize=(9, 7))
        plt.rcParams["xtick.direction"] = "in"
        plt.rcParams["ytick.direction"] = "in"
        plt.rcParams['xtick.major.width'] = 1.2
        plt.rcParams['ytick.major.width'] = 1.2
        plt.rcParams['axes.linewidth'] = 1.2
        plt.rcParams['grid.linestyle'] = '--'
        plt.rcParams['grid.linewidth'] = 0.3
        plt.rcParams["legend.markerscale"] = 2
        plt.rcParams["legend.fancybox"] = False
        plt.rcParams["legend.framealpha"] = 1
        plt.rcParams["legend.edgecolor"] = 'black'
        # ----------------------------------------

        # 特徴量重要度の算出方法 'gain'(推奨) : トレーニングデータの損失の減少量を評価
        f_importance = np.array(model.feature_importance(importance_type='gain'))  # 特徴量重要度の算出
        f_importance = f_importance / np.sum(f_importance)  # 正規化(必要ない場合はコメントアウト)
        df_importance = pd.DataFrame({'feature': self.feature_name, 'importance': f_importance})
        df_importance = df_importance.sort_values('importance', ascending=False)  # 降順ソート

        # データフレームを綺麗に出力する関数
        import IPython

        def display(*dfs, head=True):
            for df in dfs:
                IPython.display.display(df.head() if head else df)

        display(df_importance)

        # 特徴量重要度を棒グラフでプロットする関数
        def plot_feature_importance(df):
            n_features = len(df)  # 特徴量数(説明変数の個数)
            df_plot = df.sort_values('importance')  # df_importanceをプロット用に特徴量重要度を昇順ソート
            f_importance_plot = df_plot['importance'].values  # 特徴量重要度の取得
            plt.barh(range(n_features), f_importance_plot, align='center')
            cols_plot = df_plot['feature'].values  # 特徴量の取得
            plt.yticks(np.arange(n_features), cols_plot, fontsize=12)  # x軸,y軸の値の設定
            plt.xlabel('Feature importance', fontsize=14)  # x軸のタイトル
            plt.ylabel('Feature', fontsize=14)  # y軸のタイトル

        # 特徴量重要度の可視化
        plot_feature_importance(df_importance)
        plt.title(self.team_name, fontsize=18)
        plt.tight_layout()
        plt.savefig("feature_importance_{0}.pdf".format(self.team_name))
        #plt.grid()
        plt.show()

    def _predictin(self, model, test_DF):
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

        #print(pred)
        #print(y_test)

        return accuracy


