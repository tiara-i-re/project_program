#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 12/13/2020 16:30:33 
@author: Taira
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

from app import prediction
from app import database_management

import sqlite3  # sqlite3標準モジュールをインポート
from flask import Flask, g, request, render_template, current_app, session

app = Flask(__name__)  # Flaskクラスのインスタンス生成
app.secret_key = 'hogehoge'  # これを設定しないといけない．

# 2015~　J1に在籍しているチーム．
teams: list = ["G大阪", "浦和レッズ", "鹿島アントラーズ", "川崎フロンターレ", "FC東京",
               "サンフレッチェ広島", "横浜FM", "ヴィッセル神戸", "サガン鳥栖", "ベガルタ仙台",
               ]

"""
teams: list = ["G大阪", "C大阪", "浦和レッズ", "鹿島アントラーズ", "川崎フロンターレ", "FC東京",
               "名古屋グランパス", "柏レイソル", "サンフレッチェ広島", "横浜FM", "ヴィッセル神戸",
               "北海道コンサドーレ札幌", "清水エスパルス", "サガン鳥栖", "ベガルタ仙台", "湘南ベルマーレ",
               "大分トリニータ", "横浜FC"
               ]
"""


predict_class: list = ["Win", "Lose", "Draw"]


@app.route("/", methods=['GET', 'POST'])
def predict():
    message: list = ["・Select Home team.", "・Select Away team.",
                     "・Select your prediction game result of home team."
                     ]

    if request.method == 'POST':
        hometeam: str = request.form['hometeam']
        awayteam: str = request.form['awayteam']
        pred_class: str = request.form['pred_class']

        # predictionクラスのインスタンス作成
        p = prediction.Prediction()

        # チーム名，予測結果をプロパティで設定する．（str型）
        p.home_team = hometeam
        p.away_team = awayteam
        p.predict_class = pred_class

        #print("predict_class =", p.predict_class)

        #p.print_team_name()

        file_path = "data/g-os_all_data.csv"  # 相対パス(run.pyからが基準)

        # --------------------------------------------------------------
        # まずはガンバから．
        g_os = pd.read_csv(file_path, sep=',')

        # カラムリストを取得．
        column_list: list = g_os.columns.tolist()
        #print(column_list)

        # database_managementクラスのインスタンス作成
        d = database_management.DBMS()

        #conn = d.get_conn()
        #print("conn =", conn)

        #data = d.DF_to_db(g_os, column_list)
        #print(data)
        #exit()

        # ブラウザ表記のチーム名とデータベースでのチーム名が異なるため．
        home_db_name: str = d.get_team_name(p.home_team)
        away_db_name: str = d.get_team_name(p.away_team)

        # データベース接続
        start = time.time()
        # -----------------------------------------------------------------
        home_data: pd.DataFrame = d.get_data(home_db_name, column_list)
        # -----------------------------------------------------------------
        elapsed_time = time.time() - start
        print("database connection time:{0}".format(round(elapsed_time, 2)) + "[sec]")
        away_data: pd.DataFrame = d.get_data(away_db_name, column_list)


        #print("Sucsssfull database creation!!")

        #X_train, y_train, X_test, y_test, feature_name = p.data_transform(data)
        # pd.DataFrame, list, list
        home_all_data, home_all_results, feature_name = p.data_transform(home_data)
        away_all_data, away_all_results, feature_name = p.data_transform(away_data)

        start = time.time()
        # -----------------------------------------------------------------
        home_bst_model = p.make_model(home_all_data, home_all_results, feature_name)
        # -----------------------------------------------------------------
        elapsed_time = time.time() - start
        print("model building time:{0}".format(round(elapsed_time, 2)) + "[sec]")
        away_bst_model = p.make_model(away_all_data, away_all_results, feature_name)

        # -----------------------------------------------
        #p.feature_importance(home_bst_model, feature_name)
        # -----------------------------------------------

        n_samples = 10000  # シミュレーション回数

        H_test_data: pd.DataFrame = p.make_test_data(home_all_data, n_samples, feature_name)
        A_test_data: pd.DataFrame = p.make_test_data(away_all_data, n_samples, feature_name)

        start = time.time()
        # -----------------------------------------------------------------
        H_pred: pd.DataFrame = p.predictin(home_bst_model, H_test_data)
        # -----------------------------------------------------------------
        elapsed_time = time.time() - start
        print("prediction time:{0}".format(round(elapsed_time, 2)) + "[sec]")
        A_pred: pd.DataFrame = p.predictin(away_bst_model, A_test_data)

        #print("H_pred =", H_pred)
        #print("A_pred =", A_pred)

        # 勝ち=2，引き分け=1，負け=0とする．
        pred_list: list = []

        for H_result, A_result in zip(H_pred, A_pred):
            if H_result == A_result:
                pred_list.append(1)

            elif H_result > A_result:
                pred_list.append(2)

            elif H_result < A_result:
                pred_list.append(0)

        pred_len = len(pred_list)

        # list.count()で要素を数える．count() https://note.nkmk.me/python-collections-counter/ を参考．
        win_count = pred_list.count(2)
        draw_count = pred_list.count(1)
        lose_count = pred_list.count(0)

        # round()で小数点以下第一位にする　https://hibiki-press.tech/python/round_ceil_floor/903 を参考
        win_per = round((win_count / pred_len) * 100.0, 2)
        draw_per = round((draw_count / pred_len) * 100.0, 2)
        lose_per = round((lose_count / pred_len) * 100.0, 2)

        #print("win_per = {0}%".format(win_per))
        #print("draw_per = {0}%".format(draw_per))
        #print("lose_per = {0}%".format(lose_per))

        per_list = [win_per, lose_per, draw_per]

        max_index = per_list.index(max(per_list))  # .index(max())で最大値のindexを取得．
        true_result = predict_class[max_index]

        if true_result == p.predict_class:
            final_message = "・Your prediction is correct!!!"

        else:
            final_message = "・Your prediction is incorrect..."

        # https://www.366service.com/jp/qa/8d411aca7775c7835c7e6619ad241dbf　を参考にした
        session['win_per'] = win_per
        session['draw_per'] = draw_per
        session['lose_per'] = lose_per
        session['hometeam'] = hometeam
        session['awayteam'] = awayteam
        session['pred_class'] = pred_class
        session['final_message'] = final_message
        # sessionで，異なるリクエストにおいても値を受け渡しできるようにしている．

    return render_template(
        "index.html",
        title="J1 League prediction",
        message=message,
        teams=teams,
        predict_class=predict_class,
    )


@app.route("/result", methods=['GET', 'POST'])
def result_print():
    message = ['・The Home team you select is：', '・The Away team you select is：',
               '・The prediction game result you select is：'
               ]

    if request.method == 'POST':

        # win_perなどの値を他のリクエストから受け取り．sessionで受け取り．
        win_per = str(session.get('win_per', None))  # float型をstr型に変換して文字列で表示する．
        draw_per = str(session.get('draw_per', None))
        lose_per = str(session.get('lose_per', None))
        hometeam = session.get('hometeam', None)
        awayteam = session.get('awayteam', None)
        pred_class = session.get('pred_class', None)
        final_message = session.get('final_message', None)

        return render_template(
            "result_print.html",
            title='Prediction result',
            message=message,
            win_per=win_per,
            draw_per=draw_per,
            lose_per=lose_per,
            home_team=hometeam,
            away_team=awayteam,
            pred_class=pred_class,
            final_message=final_message
        )


if __name__ == "__main__":
    # 実行されたら，http://127.0.0.1:5000　に接続．
    app.run(debug=True, host='127.0.0.1', threaded=True)
