# AG5 V20.4 ELITE FILTERED - CODE: final_v20_4_elite_filtered.py
import pandas as pd, yfinance as yf, time
CODE_NAME = "final_v20_4_elite_filtered.py"
print(f"[CODE: {CODE_NAME}]")

df=pd.DataFrame()
for _ in range(3):
    try:
        tmp=yf.download("GC=F", period="60d", interval="15m", progress=False, auto_adjust=True)
        if isinstance(tmp.columns, pd.MultiIndex):
            tmp.columns = tmp.columns.get_level_values(0)
        if len(tmp)>500:
            df=tmp.reset_index(drop=False)
            break
    except: time.sleep(2)

close,high,low,open_=df['Close'],df['High'],df['Low'],df['Open']
tr1=high-low
tr2=(high-close.shift(1)).abs()
tr3=(low-close.shift(1)).abs()
tr=pd.concat([tr1,tr2,tr3],axis=1).max(axis=1)
atr=tr.rolling(14).mean()
atr_sma=atr.rolling(50).mean()
close_h4=close.rolling(16).mean()
ema50_h4=close_h4.ewm(span=50, adjust=False).mean()
ema200_h4=close_h4.ewm(span=200, adjust=False).mean()
ema50_m15=close.ewm(span=50, adjust=False).mean()
ema200_m15=close.ewm(span=200, adjust=False).mean()
p_friction=0.85
min_target=p_friction*2.2
trades=[]; valid_buy=0; in_pos=False; entry=sl=tp=0; bar_entry=0; last_sig=-999
for i in range(200, len(df)):
    if pd.isna(atr.iloc[i]) or pd.isna(ema200_h4.iloc[i]): continue
    atr_i=float(atr.iloc[i])
    if atr_i<=0: continue
    h4_bull = float(close_h4.iloc[i]) > float(ema50_h4.iloc[i]) > float(ema200_h4.iloc[i])
    m15_bull = float(ema50_m15.iloc[i]) > float(ema200_m15.iloc[i])
    vol_ok = atr_i > float(atr_sma.iloc[i])*1.0 if not pd.isna(atr_sma.iloc[i]) else True
    bull_fvg = float(low.iloc[i]) > float(high.iloc[i-2]) and float(close.iloc[i-1]) > float(open_.iloc[i-1]) if i>=2 else False
    bull_ob = float(close.iloc[i-2]) < float(open_.iloc[i-2]) and float(close.iloc[i-1]) > float(open_.iloc[i-1]) and float(close.iloc[i-1]) > float(high.iloc[i-2]) if i>=2 else False
    bos_ok = float(close.iloc[i]) > float(high.iloc[i-32:i-1].max()) if i>=32 else True
    retest_ok = abs(float(close.iloc[i]) - float(low.iloc[i-2])) < atr_i*0.5 if bull_ob else abs(float(close.iloc[i]) - (float(high.iloc[i-2])+float(low.iloc[i]))/2) < atr_i*0.5 if bull_fvg else False
    long_cond = h4_bull and m15_bull and (bull_fvg or bull_ob) and atr_i>min_target and vol_ok and bos_ok and retest_ok and (i-last_sig>16)
    if h4_bull and (bull_fvg or bull_ob): valid_buy+=1
    if not in_pos and long_cond:
        in_pos=True; entry=float(close.iloc[i]); sl=entry-atr_i*1.2; tp=entry+atr_i*2.4; bar_entry=i; last_sig=i
    elif in_pos:
        if float(high.iloc[i])>=tp or float(low.iloc[i])<=sl or i-bar_entry>=64:
            exit_price=tp if float(high.iloc[i])>=tp else sl if float(low.iloc[i])<=sl else float(close.iloc[i])
            trades.append(exit_price-entry); in_pos=False
if trades:
    wins=sum(1 for x in trades if x>0); win_rate=wins/len(trades)*100; gp=sum(x for x in trades if x>0); gl=abs(sum(x for x in trades if x<0))+1e-9; pf=gp/gl
    print(f"[{CODE_NAME}] rows={len(df)} Valid={valid_buy} Trades={len(trades)} Win={win_rate:.2f}% PF={pf:.2f}")
    open("RESULTS_AG5.md","w",encoding="utf-8").write(f"# {CODE_NAME} Result\n- CODE: {CODE_NAME}\n- rows: {len(df)}\n- Valid: {valid_buy}\n- Trades: {len(trades)}\n- Win: {win_rate:.2f}%\n- PF: {pf:.2f}\n")
else:
    print(f"[{CODE_NAME}] no trades")
