#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 01/02/2021 00:11:39 
@author: Taira
"""

import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


file_path = "data/GambaOsaka_2019.csv"  # 相対パス(run.pyからが基準)
gamba_2019 = pd.read_csv(file_path, sep=',')

#print(gamba_2019)

# DF.valuesでnumpy配列にする．
results = gamba_2019['result'].values

# .dropで不要なデータを削除する，列名をリストで指定可能，axis=1で列方向．''でHかAが消える
new_df = gamba_2019.drop(['Unnamed: 0', 'result', 'team', 'season', 'Opponent'], axis=1)

feature_name = new_df.columns
stats_data = new_df.values

Chance_create = new_df['Chance create'].values.tolist()
print(Chance_create)

AGI = new_df['AGI'].values.tolist()
plt.hist(AGI, color='c', bins=len(AGI), rwidth=0.5)
plt.show()

exit()


home_score = new_df['home score'].values.tolist()
plt.hist(home_score)
plt.show()

exit()





sorted_Chance_create = sorted(Chance_create)
print(sorted_Chance_create)

plt.plot(sorted_Chance_create)
plt.show()

plt.hist(sorted_Chance_create)
plt.show()
