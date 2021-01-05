import requests
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np


url = "https://www.football-lab.jp/g-os/match/?year=2019"
url = "https://www.football-lab.jp/g-os/match/?year={0}".format(2019)  # format使ってURL指定可能．

#url = "https://www.football-lab.jp/uraw/match/?year=2019"
#url = "https://www.football-lab.jp/uraw/match/?year=2018"

html = urlopen(url)

soup = BeautifulSoup(html, 'html.parser')


title = soup.title.string
#print("title =", title)

table = soup.find_all("tr")  # th列に情報が入っている（thはtrの中にある．）

#print(table)


header = soup.find_all(class_="thline")
#print(header)


header_list = []
for row in header:
    header_list.append(row.get_text())


header_list = sorted(set(header_list), key=header_list.index)
print(header_list)

#print(type(header_list))

results = []
for row in table:
    tmp = []
    #print(row)
    for item in row.find_all("td"):  # tdの要素を抜き出して，回す．
        #tmp.append(row)
        tmp.append(item.get_text())  # get_text()で，文字を取り出す．
        #print(item.get_text())

    results.append(tmp)



DF = pd.DataFrame(results)
#print(df)
DF = DF.iloc[2:, :]
DF = DF.reset_index()
DF = DF.drop(DF.columns[[0, 3]], axis=1)  # 曜日列を削除
#print(DF)
#DF.columns(header_list)
new_df = pd.DataFrame(DF.values[0:], columns=header_list)
#DF.rename(columns=header_list)
print(new_df)


# -------------------------------------------------------

exhibition_date = new_df['開催日']  # 開催日の列を抜き出す．
H_or_A = new_df['']  # HomeまたはAwayの列を抜き出す．

print(exhibition_date)  # 開催日の列
print(H_or_A)  # HomeまたはAwayの列



# 上記の情報を元に，試合ごとの細かいスタッツデータを抜き出す．

split_date = exhibition_date.str.split('.', expand=True)  # 開催日を月と日に分ける．(=split_date)
print(split_date)

feature_name_ver02 = ["パス", "クロス", "スローイン", "タックル", "ドリブル"]
ex_rsults = []


for m_and_d, h_or_a in zip(exhibition_date, H_or_A):
    split_date = m_and_d.split('.')  # 開催日を月と日に分ける．
    #print(split_date)
    #print("h_or_a =", h_or_a)

    month = split_date[0]  # 月．
    date = split_date[1]  # 日．

    if len(month) == 1:  # 月が一桁の場合は前に0を付けて01のようにしなくてはならない．
        month = "0" + month

    if len(date) == 1:
        date = "0" + date

    #print(month)
    #print(type(month))

    ex_url = "https://www.football-lab.jp/g-os/report/?year={0}&month={1}&date={2}".format(
        2019, month, date
    )

    # URLのHTMLソースを取得．
    ex_html = urlopen(ex_url)
    ex_soup = BeautifulSoup(ex_html, 'html.parser')

    table = ex_soup.find_all(class_="statsTbl6")  # スタッツデータの入った表を取得．

    results = []
    for row in table:
        #print(row)
        tmp = []
        for item in row.find_all("td"):
            if len(tmp) == 8:  # 1行の長さに制限して改行する．
                results.append(tmp)
                tmp = []
                tmp.append(item.get_text())

            else:
                tmp.append(item.get_text())

        #results.append(tmp)  # これで最後のボール支配率が入る．

    results = np.array(results)
    #print(results)
    DF = pd.DataFrame(results)

    DF = DF.T  # DataFrameの転置．
    #print(DF)
    DF.columns = DF.iloc[0]  # 0行目に入っているヘッダーを抜き出し，そのままDFのヘッダーにする．
    DF = DF.reindex(DF.index.drop(0))  # ヘッダーを設定した後，その行を削除する．

    ex_DF = DF.iloc[:, 8:]  # 欲しいデータのDF
    # 特定の列以降を持ってくるようにしたら上手く行った．
    # DF.drop(DF.iloc[:, 0:8], axis=1) これをするとクロスとかが2つとも抜けてしまう．
    print(ex_DF)

    ex_DF = ex_DF.drop(["シュート", "チャンス構築率"], axis=1)

    feature_columns = ["Goal expectation", "Shots on target", "Shots by PK", "Passes", "Acc. passes",
                       "Crosses", "Acc. Crosses", "Direct FK", "Indirect FK", "CK", "throw-ins",
                       "Acc. throw-ins", "Dribbles", "Acc. Dribbles", "Tackles", "Acc. Tackles",
                       "Clearances", "Interceptions", "Offsides", "Yellow cards", "Red cards", "Entries of 30m line",
                       "Entries of Penalty area", "Total running distance", "Sprints", "Attack times"]
    # print(feature_columns)

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
                #print(per)
                ex_list.append(H_number)
                ex_list.append(per)

            elif stats_name == "総走行距離":
                dis = H_number.split('m')[0]  # 走行距離からmを外したい．
                ex_list.append(dis)

            else:
                ex_list.append(H_number)

        if h_or_a == "A":
            if stats_name in feature_name_ver02:  # ["パス", "クロス", "スローイン", "タックル", "ドリブル"]の中のどれかであれば．
                split_first = A_per.split('(')  # 一回目分割，(のところでする．()で囲まれたものを取り出したかったが無理らしい・・・
                split_second = split_first[1].split('%')  # 2回目の分割，%のところでする．
                per = split_second[0]
                #print(per)
                ex_list.append(A_number)
                ex_list.append(per)

            elif stats_name == "総走行距離":
                dis = A_number.split('m')[0]  # 走行距離からmを外したい．
                ex_list.append(dis)

            else:
                ex_list.append(A_number)

    ex_rsults.append(ex_list)
    print(ex_list)

ex_rsults = np.array(ex_rsults)
ex_DF_all = pd.DataFrame(ex_rsults)

ex_DF_all.columns = feature_columns  # これが抜き出したかったデータの入ったDataFrame．

ex_DF_all.to_csv("ex_DF_all.csv")


#exit()

# -------------------------------------------------------


# .dropで不要なデータを削除する，列名をリストで指定可能，axis=1で列方向．''でHかAが消える
new_df = new_df.drop(['節', '', '開催日', '会場', '観客数', '天候', '得点者', '指揮官'], axis=1)
print(new_df)
print(new_df.columns)

feature_name = ['Opponent', 'Score', 'AGI', 'KAGI', 'Chance create',
                'Total shots', 'Acc. Shots', 'Ball possession',
                'Offence CBP', 'Pass CBP', 'Capture P', 'Defence P']

new_df.columns = feature_name

print(new_df)
#exit()



after_split = pd.DataFrame()

for row in new_df:  # rowは列名になる．
    series_row = new_df[row]  # 列名で抜き出し．

    # panda.seriesのstr.split('文字')で指定文字を削除可能，%がついていれば，2列に別れる．expand=Trueは，リストではなくDFにしてくれる．
    series_row = series_row.str.split('%', expand=True)

    # splitした後に，そのcolumnの長さが2であれば，後ろの方を削除する．
    if len(series_row.columns) == 2:
        series_row = series_row.drop(series_row.columns[1], axis=1)

    # 用意しておいた空のDFと結合
    after_split = pd.concat([after_split, series_row], axis=1)

# データ整形前と同じcolumnを設定する．
after_split.columns = new_df.columns
print(after_split)


# --------['スコア']を，ホーム，アウェイの点数と勝敗引き分けがわかるように変形--------

score_column = after_split['Score']  # スコアの列を取り出す． スコアはstr型なので，それをハイフンで切り離し，点を比べて勝ち負け引き分けのラベルをつける．
print(score_column)

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

    # 勝ち=3，引き分け=1，負け=0とする．
    if home_score > away_score:
        #result_column.append('win')
        result_column.append(0)

    elif home_score < away_score:
        #result_column.append('lose')
        result_column.append(2)

    elif home_score == away_score:
        #result_column.append('draw')
        result_column.append(1)

series_home_score = pd.Series(home_score_column, name='home score')
series_away_score = pd.Series(away_score_column, name='away score')
series_result = pd.Series(result_column, name='result')

# concatでくっつける
new_score_DF = pd.concat([series_result, series_home_score, series_away_score], axis=1)

from typing import Union, Optional


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


new_DF = insert_columns(after_split, new_score_DF, after='Opponent')
# ['スコア']の列を削除
new_DF = new_DF.drop(['Score'], axis=1)
print(new_DF)

# ---------------------------------------------------

# チーム名とシーズンを入れたい，listで足し合わせておいてDataFrameにするのが速いらしい
team = []
season = []

for i in range(len(new_DF)):
    print(i)
    team += ['G大阪']
    season += ['2019']

team_and_season_DF = pd.DataFrame(data={'team': team, 'season': season}, columns=['team', 'season'])
print(team_and_season_DF)

# ---------------------------------------------------



# ---------------------------------------------------

# concatでくっつける
new_DF = pd.concat([team_and_season_DF, new_DF], axis=1)

new_DF = pd.concat([new_DF, ex_DF_all], axis=1)

print(new_DF)

new_DF.to_csv("new_DF.csv")
#new_DF.to_csv("data/GambaOsaka_2019.csv")

exit()


#new_df.to_csv("GambaOsaka.csv")
#new_df.to_csv("Urawa.csv")
#new_df.to_csv("Urawa_2018.csv")


#print(new_df.iloc[])


exit()
