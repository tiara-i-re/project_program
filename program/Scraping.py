#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 01/05/2021 18:29:15 
@author: Taira
鹿島2017年の20節のデータに走行距離の欠如などの不備があるので抜く．
神戸2019年の18節のデータに走行距離の欠如などの不備があるので抜く．
仙台2017年の20節のデータに走行距離の欠如などの不備があるので抜く．
"""

import requests
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup

from typing import Union, Optional

import pandas as pd
import numpy as np


# この関数はhttps://qiita.com/hoto17296/items/7a910c9ffe13691938a8を参考
def insert_columns(
        df: pd.DataFrame,
        data: Union[pd.Series, pd.DataFrame],
        *,
        before: Optional[str] = None,
        after: Optional[str] = None,
        allow_duplicates: bool = False,
        inplace: bool = False,
    ) -> pd.DataFrame:

    if not inplace:
        df = df.copy()

    if not (after is None) ^ (before is None):
        raise ValueError('Specify only "before" or "after"')

    if before:
        loc = df.columns.get_loc(before)
    else:
        loc = df.columns.get_loc(after) + 1

    if type(data) is pd.Series:
        df.insert(loc, data.name, data, allow_duplicates)
    elif type(data) is pd.DataFrame:
        for column in data.columns[::-1]:
            df.insert(loc, column, data[column], allow_duplicates)

    return df


if __name__ == "__main__":
    # チーム名でfor文回したい．
    """team_list = ['g-os', 'kasm', 'ka-f', 'c-os', 'y-fm', 'fctk', 'hiro', 'uraw', 'kobe', 'nago',
                 'send', 'tosu', 'shon', 'oita', 'sapp', 'shim', 'y-fc', 'kasw']"""

    # 2015~2020までJ1にいたチーム．セレッソJ2落ちとったやん．
    team_list = ['g-os', 'kasm', 'ka-f', 'y-fm', 'fctk', 'hiro', 'uraw', 'kobe',
                 'send', 'tosu']

    """
    team_list = ['y-fm', 'fctk', 'hiro', 'uraw', 'kobe',
                 'send', 'tosu']

    team_list = ['send', 'tosu']
    """


    #team_list = ['kasm']
    #team_list = ['fctk']
    #team_list = ['g-os']
    #team_list = ['kobe']

    for team in team_list:
        team_name = team

        # シーズンでfor文回したい．
        # season_list = [2014, 2015, 2016, 2017, 2018, 2019, 2020]
        season_list = [2015, 2016, 2017, 2018, 2019, 2020]  # シーズンリスト
        #season_list = [2019]

        All_DF = pd.DataFrame()  # 全てのデータを格納するDF

        for season in season_list:
            # --------------------ここから，「試合日程・結果」を抜き出す．---------------------------
            print("{0}の{1}シーズン".format(team_name, season))
            url = "https://www.football-lab.jp/{0}/match/?year={1}".format(team_name, season)  # format使ってURL指定可能．

            html = urlopen(url)
            soup = BeautifulSoup(html, 'html.parser')

            table = soup.find_all("tr")  # th列に情報が入っている（thはtrの中にある．）
            header = soup.find_all(class_="thline")

            header_list = []
            for row in header:
                header_list.append(row.get_text())

            header_list = sorted(set(header_list), key=header_list.index)

            results = []
            for row in table:  # tableでfor文回す．
                tmp = []
                for item in row.find_all("td"):  # tdの要素を抜き出して，回す．
                    tmp.append(item.get_text())  # get_text()で，文字を取り出す．

                results.append(tmp)
                #print(tmp)  # これは必要なprint()

            # resultsには最初の2列に空白のリストが入っている．

            # team_nameはstr型，seasonはint型．
            if team_name == 'kasm' and season == 2017:  # 鹿島2017年でここでエラーが出る．20節がおかしい．
                del results[21]

            if team_name == 'kobe' and season == 2019:  # 神戸2019年でここでエラーが出る．18節がおかしい．
                del results[19]

            if team_name == 'send' and season == 2017:  # 仙台2017年でここでエラーが出る．20節がおかしい．
                del results[21]

            DF = pd.DataFrame(results)

            DF = DF.iloc[2:, :]
            DF = DF.reset_index()
            DF = DF.drop(DF.columns[[0, 3]], axis=1)  # 曜日列を削除

            new_df = pd.DataFrame(DF.values[0:], columns=header_list)

            # -------------------次の準備-------------------
            exhibition_date = new_df['開催日']  # 開催日の列を抜き出す．
            H_or_A = new_df['']  # HomeまたはAwayの列を抜き出す．
            # ---------------------------------------------------

            new_df = new_df.drop([''], axis=1)  # 下で指揮官を抜きたいのに''に反応されてしまうので．

            columns = new_df.columns
            #print(columns)
            #print(False not in [i not in '指揮官' for i in columns])  # '指揮官'が含まれていれば，ここはTrueになる．
            # '指揮官'が含まれていない(not in)した中に，Falseが含まれていない(not in)がTrueになるため．

            # 2014年のデータに'指揮官'がないため．
            # "https://qiita.com/___xxx_/items/76a33ad7cfe64a5fe9d8"　←ここを参考にした．
            # False not in [i in '該当させたい文字列' for i in 検索したい文字列の入ったリスト]
            if (False not in [i not in '指揮官' for i in columns]) == True:
                # .dropで不要なデータを削除する，列名をリストで指定可能，axis=1で列方向．''でHかAが消える
                new_df = new_df.drop(['節', '開催日', '会場', '観客数', '天候', '得点者'], axis=1)

            elif (False not in [i not in '指揮官' for i in columns]) == False:
                new_df = new_df.drop(['節', '開催日', '会場', '観客数', '天候', '得点者', '指揮官'], axis=1)

            feature_name = ['Opponent', 'Score', 'AGI', 'KAGI', 'Chance create',
                            'Total shots', 'Acc. Shots', 'Ball possession',
                            'Offence CBP', 'Pass CBP', 'Capture P', 'Defence P']

            new_df.columns = feature_name

            after_split = pd.DataFrame()

            for row in new_df:  # rowは列名になる．
                series_row = new_df[row]  # 列名で抜き出し．

                # panda.seriesのstr.split('文字')で指定文字を削除可能，%がついていれば，2列に別れる．
                # expand=Trueは，リストではなくDFにしてくれる．
                series_row = series_row.str.split('%', expand=True)

                # splitした後に，そのcolumnの長さが2であれば，後ろの方を削除する．
                if len(series_row.columns) == 2:
                    series_row = series_row.drop(series_row.columns[1], axis=1)

                # 用意しておいた空のDFと結合
                after_split = pd.concat([after_split, series_row], axis=1)

            # データ整形前と同じcolumnを設定する．
            after_split.columns = new_df.columns

            # --------['スコア']を，ホーム，アウェイの点数と勝敗引き分けがわかるように変形--------

            # スコアの列を取り出す． スコアはstr型なので，それをハイフンで切り離し，点を比べて勝ち負け引き分けのラベルをつける
            score_column = after_split['Score']

            home_score_column = []
            away_score_column = []
            result_column = []

            for i in range(len(score_column)):  # スコア列の行数だけfor回す
                score = score_column[i]

                split_score_list = score.split('-')

                home_score = split_score_list[0]
                away_score = split_score_list[1]

                home_score_column.append(home_score)
                away_score_column.append(away_score)

                # 勝ち=2，引き分け=1，負け=0とする．
                if home_score > away_score:
                    result_column.append(2)

                elif home_score < away_score:
                    result_column.append(0)

                elif home_score == away_score:
                    result_column.append(1)

            series_home_score = pd.Series(home_score_column, name='home score')
            series_away_score = pd.Series(away_score_column, name='away score')
            series_result = pd.Series(result_column, name='result')

            # concatでくっつける
            new_score_DF = pd.concat([series_result, series_home_score, series_away_score], axis=1)

            new_DF = insert_columns(after_split, new_score_DF, after='Opponent')
            # ['スコア']の列を削除
            new_DF = new_DF.drop(['Score'], axis=1)

            # ---------------------------------------------------
            # チーム名とシーズンを入れたい，listで足し合わせておいてDataFrameにするのが速いらしい
            team_list = []
            season_list = []

            for i in range(len(new_DF)):
                team_list += ['{0}'.format(team_name)]
                season_list += ["{0}".format(season)]

            team_and_season_DF = pd.DataFrame(data={'team': team_list, 'season': season_list},
                                              columns=['team', 'season'])
            # concatでくっつける
            new_DF = pd.concat([team_and_season_DF, new_DF], axis=1)

            # --------------------ここまでで，「試合日程・結果」が抜き出せた．------------------------




            # --------------------ここから，「最新の試合結果」を抜き出す．---------------------------
            split_date = exhibition_date.str.split('.', expand=True)  # 開催日を月と日に分ける．(=split_date)

            feature_name_ver02 = ["パス", "クロス", "スローイン", "タックル", "ドリブル"]
            ex_results = []

            for m_and_d, h_or_a in zip(exhibition_date, H_or_A):
                split_date = m_and_d.split('.')  # 開催日を月と日に分ける．

                month = split_date[0]  # 月．
                date = split_date[1]  # 日．

                if len(month) == 1:  # 月が一桁の場合は前に0を付けて01のようにしなくてはならない．
                    month = "0" + month

                if len(date) == 1:
                    date = "0" + date

                ex_url = "https://www.football-lab.jp/{0}/report/?year={1}&month={2}&date={3}".format(
                    team_name, season, month, date
                )

                # URLのHTMLソースを取得．
                ex_html = urlopen(ex_url)
                ex_soup = BeautifulSoup(ex_html, 'html.parser')

                table = ex_soup.find_all(class_="statsTbl6")  # スタッツデータの入った表を取得．

                results = []
                for row in table:
                    # print(row)
                    tmp = []
                    for item in row.find_all("td"):
                        if len(tmp) == 8:  # 1行の長さに制限して改行する．
                            results.append(tmp)
                            tmp = []
                            tmp.append(item.get_text())

                        else:
                            tmp.append(item.get_text())

                results = np.array(results)
                ex_one_DF = pd.DataFrame(results)

                ex_one_DF = ex_one_DF.T  # DataFrameの転置．

                ex_one_DF.columns = ex_one_DF.iloc[0]  # 0行目に入っているヘッダーを抜き出し，そのままDFのヘッダーにする．
                ex_one_DF = ex_one_DF.reindex(ex_one_DF.index.drop(0))  # ヘッダーを設定した後，その行を削除する．

                ex_DF = ex_one_DF.iloc[:, 8:]  # 欲しいデータのDF

                columns = ex_DF.columns

                # 2019年以前ののデータに'ゴール期待値'がないため，# 泣く泣く"Goal expectation", ゴール期待値もぬく．
                if (False not in [i not in 'ゴール期待値' for i in columns]) == True:
                    ex_DF = ex_DF.drop(["シュート", "チャンス構築率"], axis=1)

                elif (False not in [i not in 'ゴール期待値' for i in columns]) == False:
                    ex_DF = ex_DF.drop(["シュート", "ゴール期待値", "チャンス構築率"], axis=1)

                ex_list = []  # 要素を追加していくリスト

                # ["パス", "クロス", "スローイン", "タックル", "ドリブル"]については数と成功率どちらも欲しい．
                for i in range(0, len(ex_DF.columns)):
                    stats_row = ex_DF.iloc[:, i]  # データ別の列．
                    stats_name = stats_row.name  # データの名前．

                    H_per = stats_row.iloc[1]  # [1]でHの時のパーセンテージ．
                    H_number = stats_row.iloc[2]  # [2]でHの時の数字．

                    A_per = stats_row.iloc[5]  # [5]でAの時のパーセンテージ．
                    A_number = stats_row.iloc[4]  # [4]でAの時の数字．

                    # HかAであったかを判断するためのif文．
                    if h_or_a == "H":
                        if stats_name in feature_name_ver02:  # ["パス", "クロス", "スローイン", "タックル", "ドリブル"]の中のどれかであれば．
                            split_first = H_per.split('(')  # 一回目分割，(のところでする．()で囲まれたものを取り出したかったが無理らしい・・・
                            split_second = split_first[1].split('%')  # 2回目の分割，%のところでする．
                            per = split_second[0]
                            # print(per)
                            ex_list.append(H_number)
                            ex_list.append(per)

                        elif stats_name == "総走行距離":
                            del_m = H_number.split('m')[0]  # 走行距離からmを外したい．
                            split = del_m.split(',')  # ,で分割して，結合することで,を取り除ける．
                            dis = split[0] + split[1]
                            ex_list.append(dis)

                        else:
                            ex_list.append(H_number)

                    if h_or_a == "A":
                        if stats_name in feature_name_ver02:  # ["パス", "クロス", "スローイン", "タックル", "ドリブル"]の中のどれかであれば．
                            split_first = A_per.split('(')  # 一回目分割，(のところでする．()で囲まれたものを取り出したかったが無理らしい・・・
                            split_second = split_first[1].split('%')  # 2回目の分割，%のところでする．
                            per = split_second[0]
                            # print(per)
                            ex_list.append(A_number)
                            ex_list.append(per)

                        elif stats_name == "総走行距離":
                            dis = A_number.split('m')[0]  # 走行距離からmを外したい．
                            split = del_m.split(',')  # ,で分割して，結合することで,を取り除ける．
                            dis = split[0] + split[1]
                            ex_list.append(dis)

                        else:
                            ex_list.append(A_number)

                print(ex_list)  # ここのprint()はいる．
                ex_results.append(ex_list)

            ex_results = np.array(ex_results)

            ex_DF_all = pd.DataFrame(ex_results)

            feature_columns = ["Shots on target", "Shots by PK", "Passes", "Acc. passes",
                               "Crosses", "Acc. Crosses", "Direct FK", "Indirect FK", "CK", "throw-ins",
                               "Acc. throw-ins", "Dribbles", "Acc. Dribbles", "Tackles", "Acc. Tackles",
                               "Clearances", "Interceptions", "Offsides", "Yellow cards", "Red cards",
                               "Entries of 30m line",
                               "Entries of Penalty area", "Total running distance", "Sprints", "Attack times"]

            ex_DF_all.columns = feature_columns  # これが抜き出したかったデータの入ったDataFrame．

            # --------------------ここまでで，「最新の試合結果」が抜き出せた．------------------------

            # concatでくっつける
            new_DF = pd.concat([new_DF, ex_DF_all], axis=1)

            All_DF = pd.concat([All_DF, new_DF], axis=0)

        All_DF.reset_index(drop=True, inplace=True)
        All_DF.to_csv("data/{0}_all_data.csv".format(team_name))
