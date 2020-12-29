import requests
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup


url = "https://www.football-lab.jp/g-os/match/?year=2019"
#url = "https://www.football-lab.jp/uraw/match/?year=2019"
#url = "https://www.football-lab.jp/uraw/match/?year=2018"

html = urlopen(url)
#print(html)
soup = BeautifulSoup(html, 'html.parser')
#print(soup)

#exit()

title = soup.title.string
#print("title =", title)

table = soup.find_all("tr")  # th列に情報が入っている

#print(table)

header = soup.find_all(class_="thline")
#print(header)

#exit()

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
    for item in row.find_all("td"):
        #tmp.append(row)
        tmp.append(item.get_text())

    results.append(tmp)

#print(results)
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


# .dropで不要なデータを削除する，列名をリストで指定可能，axis=1で列方向．''でHかAが消える
new_df = new_df.drop(['節', '', '開催日', '会場', '観客数', '天候', '得点者', '指揮官'], axis=1)
print(new_df)
print(new_df.columns)

feature_name = ['Opponent', 'Score', 'AGI', 'KAGI', 'Chance create',
                'Shoot', 'Shoot success rate', 'Possession rate', 'Offence CBP', 'Pass CBP', 'Capture P', 'Defence P']

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
    team += ['G大阪']
    season += ['2019']

team_and_season_DF = pd.DataFrame(data={'team': team, 'season': season}, columns=['team', 'season'])
print(team_and_season_DF)

# ---------------------------------------------------


# concatでくっつける
new_DF = pd.concat([team_and_season_DF, new_DF], axis=1)

print(new_DF)


new_DF.to_csv("data/GambaOsaka_2019.csv")

exit()


#new_df.to_csv("GambaOsaka.csv")
#new_df.to_csv("Urawa.csv")
#new_df.to_csv("Urawa_2018.csv")


#print(new_df.iloc[])


exit()
