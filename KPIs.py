# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 09:56:20 2024

@author: user
"""
import numpy as np
import pandas as pd

def get_CAGR(DF):
    df = DF.copy()  # 複製數據
    df["return"] = df["Adj Close"].pct_change()  # 計算每日收益率
    df["cum return"] = (1 + df["return"]).cumprod()  # 計算累積收益率
    n = len(df) / 252  # 計算年份數（假設一年有 252 個交易日）
    CAGR = (df["cum return"].iloc[-1])**(1/n) - 1  # 計算 CAGR
    return CAGR

def get_volatility(DF):
    df = DF.copy()  # 複製數據
    df["return"] = df["Adj Close"].pct_change()  # 計算每日收益率
    vol = df["return"].std() * np.sqrt(252)  # 計算年度波動率
    return vol

def get_MDD(DF):    
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change()  # 計算每日收益率
    df["cum return"] = (1 + df["return"]).cumprod()  # 計算累積收益率
    df["max cum return"] = df["cum return"].cummax()  # 計算累積收益率中的最大值
    df["drawdown"] = df["max cum return"] - df["cum return"]  # 計算回撤
    MDD = (df["drawdown"]/df["max cum return"]).max()  # 計算最大回撤
    return MDD

def get_calmar(DF):
    df = DF.copy()
    cal = get_CAGR(df) / get_MDD(df)  # 卡馬比率 = CAGR / 最大回撤
    return cal

def get_sharpe(DF, rf):
    df = DF.copy()
    sharpe = (get_CAGR(df) - rf) / get_volatility(df)  # 計算夏普比率
    return sharpe

def get_sortino(DF, rf):
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change()  # 計算每日收益率
    negative_return = np.where(df["return"] < 0, df["return"], 0)  # 選取負收益率
    negative_vol = pd.Series(negative_return[negative_return != 0]).std() * np.sqrt(252)  # 計算負波動率
    sortino = (get_CAGR(df) - rf) / negative_vol  # 計算索提諾比率
    return sortino
