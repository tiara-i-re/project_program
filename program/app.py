#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 12/13/2020 16:30:33 
@author: Taira
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import prediction
import database_management

import sqlite3  # sqlite3標準モジュールをインポート
from flask import Flask, g, request, render_template, current_app, session

app = Flask(__name__)  # Flaskクラスのインスタンス生成
app.secret_key = 'hogehoge'  # これを設定しないといけない．

teams = ["▼選択してください", "G大阪", "C大阪", "浦和レッズ", "鹿島アントラーズ", "川崎フロンターレ", "FC東京",
         "名古屋グランパス", "柏レイソル", "サンフレッチェ広島", "横浜FM", "ヴィッセル神戸", "北海道コンサドーレ札幌",
         "清水エスパルス", "サガン鳥栖", "ベガルタ仙台", "湘南ベルマーレ", "大分トリニータ", "横浜FC"]

predict_class = ["▼選択してください", "勝ち", "負け", "引き分け"]


@app.route("/", methods=['GET', 'POST'])
def predict():
    message = ["ホームチームを選んでください", "アウェイチームを選んでください", "ホームチームの勝敗予想結果を選んでください"]
    if request.method == 'POST':
        hometeam = request.form['hometeam']
        awayteam = request.form['awayteam']
        pred_class = request.form['pred_class']

        p = prediction.Prediction(hometeam, awayteam, pred_class)
        p.print_team_name()

        file_path = "data/GambaOsaka_2019.csv"
        gamba_2019 = pd.read_csv(file_path, sep=',')

        # カラムリストを取得．
        column_list = gamba_2019.columns

        #print("gamba_2019 =", gamba_2019)

        d = database_management.DBMS()
        data = d.DF_to_db(gamba_2019, column_list)

        print("Sucsssfull database creation!!")

        X_train, y_train, X_test, y_test, feature_name = p.data_transform(data)

        accuracy = p.prediction(X_train, y_train, X_test, y_test, feature_name)
        print("accuracy =", accuracy)

        # https://www.366service.com/jp/qa/8d411aca7775c7835c7e6619ad241dbf　を参考にした
        session['accuracy'] = accuracy
        session['hometeam'] = hometeam
        session['awayteam'] = awayteam
        session['pred_class'] = pred_class
        # sessionで，異なるリクエストにおいても値を受け渡しできるようにしている．

    return render_template(
        "index.html",
        title="Let's prediction",
        message=message,
        teams=teams,
        predict_class=predict_class,
    )


@app.route("/result", methods=['GET', 'POST'])
def result_print():
    message = ['accuracy score is...  ', 'あなたのホームチームの勝敗予測結果は：', 'ホームチーム：', 'アウェイチーム：']
    if request.method == 'POST':

        # accuracyなどの値を他のリクエストから受け取り．sessionで受け取り．
        accuracy = str(session.get('accuracy', None))
        hometeam = session.get('hometeam', None)
        awayteam = session.get('awayteam', None)
        pred_class = session.get('pred_class', None)


        return render_template(
            "result_print.html",
            title='Sucsssfull prediction!',
            message=message,
            accuracy_score=accuracy,
            home_team=hometeam,
            away_team=awayteam,
            pred_class=pred_class
        )


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', threaded=True)  # 実行されたら
