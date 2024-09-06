# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import yfinance as yf

portfolios = []
print("請輸入您的資產組合")
asset = ""
while True:
    if asset == "q":
        break
    else:    
        asset = str(input())
        portfolios.append(asset)
portfolios.remove("q")
    
N = {}
total = 0
for stock in portfolios:
    n = int(input(f"lot for {stock}:"))
    N[stock] = n
    total += n

confidence_level = (int(input("設定confidence level(0~100(%)):")))/100
ret = {}
ohlc = {}

for stock in portfolios:
    temp = yf.download(stock, period="2y",interval="1d")
    temp.dropna(how="any", inplace=True)
    ohlc[stock] = temp
    ohlc[stock]["value"] = ohlc[stock]["Adj Close"] * N[stock] * 100
    ohlc[stock]["daily_ret"] = ohlc[stock]["Adj Close"].pct_change()
    ohlc[stock].drop(["Open", "High", "Low", "Close", "Volume"], axis=1, inplace=True)

scenario_n = [0]
for i in range(1, len(ohlc[stock]["Adj Close"])):
    scenario_n.append(i)
    
all_scenario = {}
lambda_ = 0.94
for stock in portfolios:
  ohlc[stock]["scenario_n"] = scenario_n
  ohlc[stock]["n days before"] = len(ohlc[stock]) - (ohlc[stock]["scenario_n"])
  ohlc[stock]["weight"] = (1-lambda_)*lambda_**(ohlc[stock]["n days before"]-1)
  ohlc[stock]["scenario result"] = ohlc[stock]["Adj Close"][-1]*(1+ohlc[stock]["daily_ret"])
  ohlc[stock]["scenario value"] = ohlc[stock]["scenario result"] * int(N[stock]) * 100
  ohlc[stock]["scenario loss"] = ohlc[stock]["value"][-1] - ohlc[stock]["scenario value"]
  ohlc[stock].set_index(["scenario_n"], inplace=True)
  ohlc[stock].dropna(how="any", inplace=True)

all_scenario = pd.DataFrame()
for stock in portfolios:
  all_scenario[stock] = ohlc[stock]["scenario loss"]
all_scenario["total loss"] = all_scenario.sum(axis=1)
all_scenario["n days before"] = ohlc[stock]["n days before"]
all_scenario["weight"] = ohlc[stock]["weight"]
all_scenario = all_scenario.sort_values(by="total loss")
all_scenario["accumalate weight"] = [0] * len(all_scenario)
all_scenario["accumalate weight"].iloc[0] = all_scenario["weight"].iloc[0]
for i in range(1, len(all_scenario)): 
    all_scenario["accumalate weight"].iloc[i] = all_scenario["accumalate weight"].iloc[i-1] +  all_scenario["weight"].iloc[i]

rest = all_scenario[all_scenario["accumalate weight"] > confidence_level]
tail_loss = all_scenario[all_scenario["accumalate weight"] <= confidence_level]
VaR = rest["total loss"].iloc[0]
tail_loss["probability"] = tail_loss["weight"]/confidence_level
ES = (tail_loss["probability"]*tail_loss["total loss"]).sum() + \
     rest["total loss"].iloc[0]*(1-tail_loss["probability"].sum())

print(f"VaR:{VaR}")
print(f"ES:{ES}")


