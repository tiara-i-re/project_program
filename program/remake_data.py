#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 12/15/2020 14:01:27 
@author: Taira
"""

import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_path = "data/GambaOsaka_re.csv"

DF = pd.read_csv(file_path, sep=',')  # read_csvで読み込んだデータはDataFrameである．

print(DF)
print(type(DF))
print(DF.columns)

score_column = DF['スコア']  # スコアの列を取り出す． スコアはstr型なので，それをハイフンで切り離し，点を比べて勝ち負け引き分けのラベルをつける．
print(score_column)

score_column[1]
print(score_column[1])
print(type(score_column[1]))

# ---------------------------------------------------

print(score_column[1].split('-'))

split_score = score_column[1].split('-')  # .splitでハイフンでスコアを切り離し，その結果がリストに入っている．
print(split_score)
print(type(split_score))

home_score = split_score[1]
print(home_score)
print(type(home_score))

home_score = int(split_score[1])  # int()で，str型の数字を整数方にする．
print(home_score)
print(type(home_score))

# ---------------------------------------------------

home_score_column = []
away_score_column = []
result_column = []

for i in range(len(score_column)):  # スコア列の行数だけfor回す
    score = score_column[i]
    print(score)

    split_score_list = score.split('-')
    print(split_score_list)

    home_score = split_score_list[0]
    away_score = split_score_list[1]

    home_score_column.append(home_score)
    away_score_column.append(away_score)

    if home_score > away_score:
        result_column.append('win')

    elif home_score < away_score:
        result_column.append('lose')

    elif home_score == away_score:
        result_column.append('draw')


print(home_score_column)
print(away_score_column)
print(result_column)

series_home_score = pd.Series(home_score_column, name='home score')
series_away_score = pd.Series(away_score_column, name='away score')
series_result = pd.Series(result_column, name='result')

print(series_home_score)
print(type(series_home_score))
#exit()

# concatでくっつける
new_score_DF = pd.concat([series_result, series_home_score, series_away_score], axis=1)


from typing import Union, Optional

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

#DF.head()
#new_score_DF.head()

new_DF = insert_columns(DF, new_score_DF, after='相手')

print(new_DF)

new_DF = new_DF



