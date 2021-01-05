#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 01/04/2021 01:52:13 
@author: Taira
"""

import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import requests
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup


#url = "https://www.football-lab.jp/g-os/match/?year=2019"

# 変数urlでサイトのURLを指定．
url = "https://www.football-lab.jp/g-os/report/?year=2020&month=12&date=16"

# URLのHTMLソースを取得．
html = urlopen(url)

soup = BeautifulSoup(html, 'html.parser')

header = soup.find_all(class_="dsktp c")

header_list = []
for row in header:
    header_list.append(row.get_text())
print(header_list)


table = soup.find_all(class_="statsTbl6")  # スタッツデータの入った表を取得．
#print(table)

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

results = np.array(results)
print(results)
DF = pd.DataFrame(results)
DF.to_csv("example.csv")
exit()


