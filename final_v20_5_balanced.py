# CODE: final_v20_5_balanced.py - Pine V20.3 (70,25,25,20,15,15,1,2,1.5,4,64,0.2,0.5,0.1,32)
import pandas as pd, yfinance as yf, time
CODE_NAME="final_v20_5_balanced.py"
print(f"[CODE: {CODE_NAME}]")
df=pd.DataFrame()
for _ in range(3):
    try:
        tmp=yf.download("GC=F", period="60d", interval="15m", progress=False, auto_adjust=True)
        if isinstance(tmp.columns, pd.MultiIndex): tmp.columns=tmp.columns.get_level_values(0)
        if len(tmp)>500: df=tmp.reset_index(drop=False); break
    except: time.sleep(2)
close,high,low,open_=df['Close'],df['High'],df['Low'],df['Open']
tr=pd.concat([high-low,(high-close.shift(1)).abs(),(low-close.shift(1)).abs()],axis=1).max(axis=1)
atr=tr.rolling(14).mean(); atr_sma=atr.rolling(50).mean()
close_h4=close.rolling(16).mean(); ema50_h4=close_h4.ewm(span=50).mean(); ema200_h4=close_h4.ewm(span=200).mean()
ema50_m15=close.ewm(span=50).mean()
trades=[]; valid_buy=0; in_pos=False; entry=sl=tp=0; bar_entry=0; last_sig=-999
for i in range(200, len(df)):
    if pd.isna(atr.iloc[i]) or pd.isna(ema200_h4.iloc[i]): continue
    atr_i=float(atr.iloc[i])
    h4_bull=float(close_h4.iloc[i])>float(ema50_h4.iloc[i])>float(ema200_h4.iloc[i])
    m15_bull=float(close.iloc[i])>float(ema50_m15.iloc[i])
    vol_ok=atr_i>float(atr_sma.iloc[i])*0.85 if not pd.isna(atr_sma.iloc[i]) else True
    bull_fvg=float(low.iloc[i])>float(high.iloc[i-2]) if i>=2 else False
    bull_ob=float(close.iloc[i-2])<float(open_.iloc[i-2]) and float(close.iloc[i-1])>float(open_.iloc[i-1]) if i>=2 else False
    retest_ok=abs(float(close.iloc[i])-float(low.iloc[i-2]))<atr_i*0.8 if bull_ob else abs(float(close.iloc[i])-(float(high.iloc[i-2])+float(low.iloc[i]))/2)<atr_i*0.8 if bull_fvg else False
    long_cond=h4_bull and m15_bull and (bull_fvg or bull_ob) and atr_i>0.85*2.0 and vol_ok and retest_ok and (i-last_sig>8)
    if h4_bull and (bull_fvg or bull_ob): valid_buy+=1
    if not in_pos and long_cond: in_pos=True; entry=float(close.iloc[i]); sl=entry-atr_i*1.0; tp=entry+atr_i*2.0; bar_entry=i; last_sig=i
    elif in_pos:
        if float(high.iloc[i])>=tp or float(low.iloc[i])<=sl or i-bar_entry>=64:
            exit_price=tp if float(high.iloc[i])>=tp else sl if float(low.iloc[i])<=sl else float(close.iloc[i]); trades.append(exit_price-entry); in_pos=False
wins=sum(1 for x in trades if x>0); print(f"[{CODE_NAME}] rows={len(df)} Valid={valid_buy} Trades={len(trades)} Win={wins/len(trades)*100:.2f}% PF={sum(x for x in trades if x>0)/(abs(sum(x for x in trades if x<0))+1e-9):.2f}" if trades else f"[{CODE_NAME}] no trades")
open("RESULTS_AG5.md","w").write(f"# {CODE_NAME}\nCODE: {CODE_NAME}\nrows: {len(df)}\nTrades: {len(trades)}\n")
