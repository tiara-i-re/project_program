#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 12/08/2020 13:22:18 
@author: Taira
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import mglearn
import graphviz

import xgboost as xgb

from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


file_path = "data/GambaOsaka_2019.csv"

# read_csvで読み込んだデータはDataFrameである．
gamba_2019 = pd.read_csv(file_path, sep=',')

print(gamba_2019)

# DF.valuesでnumpy配列にする．
results = gamba_2019['result'].values

# ---------------------------------------------------

# Unnamed: 0も抜く
stats_DF = gamba_2019.drop(['Unnamed: 0', 'result'], axis=1)
#print(stats_DF)

# 他にも不要なデータ抜く
stats_data = stats_DF.drop(['team', 'season', 'Opponent'], axis=1)
feature_name = stats_data.columns
print(feature_name)

stats_data = stats_data.values
#print(stats_data)

#print(stats_data[0])
#print(stats_data[0][0])

#print(type(stats_data[0][0]))

# 17節までを学習データにする．
X_train = stats_data[:17]
y_train = results[:17]

# 18節以降をテストデータにする．
X_test = stats_data[17:]
y_test = results[17:]

dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_name)
dvalid = xgb.DMatrix(X_test, label=y_test, feature_names=feature_name)

print(dtrain)

#exit()

param = {'max_depth': 10, 'eta': 1, 'objective': 'multi:softmax', 'num_class': 3}

num_round = 10
bst = xgb.train(param, dtrain, num_round)

pred = bst.predict(dvalid)

print("勝ち=0，引き分け=1，負け=2とする．")
print("predict results =", pred)
print("y_test =", y_test)

from sklearn.metrics import accuracy_score

score = accuracy_score(y_test, pred)
print('score:{0:.4f}'.format(score))

#print(xgb.)

exit()

xgb.plot_importance(bst)
plt.tight_layout()
plt.show()

xgb.plot_tree(bst)
plt.tight_layout()
plt.show()


exit()

# -----------------これより下は，異なる-----------------------

cancer = load_breast_cancer()

X_train, X_test, y_train, y_test = train_test_split(cancer.data, cancer.target, stratify=cancer.target, random_state=42)

#tree = DecisionTreeClassifier(random_state=0)

#tree.fit(X_train, y_train)

#iris = load_iris()

#iris_data = pd.DataFrame(iris.data, columns=iris.feature_names)
#iris_target = pd.Series(iris.target)

#X_train, X_test, y_train, y_test = train_test_split(iris_data, iris_target, test_size=0.2, shuffle=True)


dtrain = xgb.DMatrix(X_train, label=y_train)
dvalid = xgb.DMatrix(X_test, label=y_test)

#dtest = xgb.DMatrix(df_test.values)

param = {'max_depth': 3, 'eta': 1, 'objective': 'multi:softmax', 'num_class': 3}

num_round = 10
bst = xgb.train(param, dtrain, num_round)

pred = bst.predict(dvalid)

print(pred)


from sklearn.metrics import accuracy_score

score = accuracy_score(y_test, pred)
print('score:{0:.4f}'.format(score))

graph1 = xgb.to_graphviz(bst)
graph1.format = 'png'
graph1.render('tree2')
xgb.plot_tree(bst)
plt.tight_layout()
plt.show()

exit()

xgb.plot_importance(bst)
plt.tight_layout()
plt.show()

#mglearn.plots.plot_animal_tree()
#plt.xlabel('Feature 0')
#plt.show()


