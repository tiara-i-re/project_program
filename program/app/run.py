#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created on 12/30/2020 00:12:46 
@author: Taira
"""

from app.app import app

if __name__ == "__main__":
    # 実行されたら，http://127.0.0.1:5000　に接続．
    app.run(debug=True, host='127.0.0.1', threaded=True)
