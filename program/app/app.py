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

teams = ["▼Select", "G大阪", "C大阪", "浦和レッズ", "鹿島アントラーズ", "川崎フロンターレ", "FC東京",
         "名古屋グランパス", "柏レイソル", "サンフレッチェ広島", "横浜FM", "ヴィッセル神戸", "北海道コンサドーレ札幌",
         "清水エスパルス", "サガン鳥栖", "ベガルタ仙台", "湘南ベルマーレ", "大分トリニータ", "横浜FC"]

predict_class = ["▼Select", "Win", "Lose", "Draw"]


@app.route("/", methods=['GET', 'POST'])
def predict():
    message = ["Select Home team.", "Select Away team", "Select your prediction game result of home team."]

    if request.method == 'POST':
        hometeam = request.form['hometeam']
        awayteam = request.form['awayteam']
        pred_class = request.form['pred_class']

        # predictionクラスのインスタンス作成
        p = prediction.Prediction()

        # チーム名，予測結果をプロパティで設定する．
        p.home_team = hometeam
        p.away_team = awayteam
        p.predict_class = pred_class

        p.print_team_name()

        file_path = "data/GambaOsaka_2019.csv"
        gamba_2019 = pd.read_csv(file_path, sep=',')

        # カラムリストを取得．
        column_list = gamba_2019.columns

        # database_managementクラスのインスタンス作成
        d = database_management.DBMS()

        #conn = d.get_conn()
        #print("conn =", conn)

        #data = d.DF_to_db(gamba_2019, column_list)

        data = d.get_data(p.home_team, column_list)

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
        title="Let's J1 League prediction",
        message=message,
        teams=teams,
        predict_class=predict_class,
    )


@app.route("/result", methods=['GET', 'POST'])
def result_print():
    message = ['accuracy score is...  ', 'The prediction game result you select is：',
               'The Home team you select is：', 'The Away team you select is：']

    if request.method == 'POST':

        # accuracyなどの値を他のリクエストから受け取り．sessionで受け取り．
        accuracy = str(session.get('accuracy', None))  # float型をstr型に変換して文字列で表示する．
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
    # 実行されたら，http://127.0.0.1:5000　に接続．
    app.run(debug=True, host='127.0.0.1', threaded=True)

    #< button class ="button", type="submit", value="team,predict_class", onClick="setTF(this.form.showbutton,'visible')" > Predict < / button >
    #< button class ="button", name='showbutton', formaction="http://127.0.0.1:5000/result", style='visibility:hidden' > Show result < / button >
