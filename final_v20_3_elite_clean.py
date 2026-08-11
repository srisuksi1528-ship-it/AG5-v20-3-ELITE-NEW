# AG5 V20.3 ELITE FIXED TH55 BOS48 - M15 60d
import pandas as pd, yfinance as yf, time
df=pd.DataFrame()
for _ in range(3):
    try:
        tmp=yf.download("GC=F",period="60d",interval="15m",progress=False,auto_adjust=True)
        if isinstance(tmp.columns,pd.MultiIndex): tmp.columns=tmp.columns.get_level_values(0)
        if len(tmp)>300: df=tmp.reset_index(drop=True); break
    except: time.sleep(3)
if len(df)<200: raise SystemExit(f"rows {len(df)}")
close,high,low,open_=df['Close'],df['High'],df['Low'],df['Open']

p_thresh=55.0 # จาก 70 -> 55
p_bos_max=48 # จาก 32 -> 48
p_risk,p_reward=1.5,4.0
p_dur=48

ema50=close.ewm(50).mean(); ema200=close.ewm(200).mean()
tr=pd.concat([high-low,(high-close.shift(1)).abs(),(low-close.shift(1)).abs()],axis=1).max(axis=1)
atr=tr.rolling(14).mean()

ph=[False]*len(df); phv=[float('nan')]*len(df)
for i in range(5,len(df)-5):
    if high.iloc[i]==high.iloc[i-5:i+6].max(): ph[i+5]=True; phv[i+5]=float(high.iloc[i])

res=[]; bos_bar=-999; bos_lv=float('nan'); last=-999999
vb=0; w=l=0; tdir=0; sl=tp=float('nan'); tbar=-1

for i in range(len(df)):
    if ph[i]: res.insert(0,phv[i]); res=res[:3]
    rv=res[0] if res else float('nan')
    if __import__('pandas').isna(atr.iloc[i]): continue
    ai=float(atr.iloc[i])
    hc=float(close.iloc[i-1]); hf=float(ema50.iloc[i-1]); hs=float(ema200.iloc[i-1]) if not __import__('pandas').isna(ema200.iloc[i-1]) else hf
    regime=1 if hc>hs and hf>hs else -1
    body=abs(float(close.iloc[i]-open_.iloc[i])); disp=body>(ai*0.4)
    up=(float(high.iloc[i]-low.iloc[i])>0 and (float(close.iloc[i]-low.iloc[i])/(float(high.iloc[i]-low.iloc[i])))>0.6)
    brk=(rv==rv) and float(close.iloc[i])>(rv+ai*0.1)
    if brk and up and disp: bos_bar=i; bos_lv=rv
    valid=(i-bos_bar)<=p_bos_max and (i-bos_bar)>0
    retest=valid and bos_lv==bos_lv and abs(float(low.iloc[i]-bos_lv))<=ai*0.2 and float(close.iloc[i])>bos_lv
    score=0
    if regime==1 and float(close.iloc[i])>hf: score+=25
    if retest: score+=25
    elif valid: score+=17
    if disp and up: score+=20
    score+=30
    if score>=p_thresh and (i-last)>=3 and retest and regime==1: vb+=1; last=i
    if tdir!=0 and (float(high.iloc[i])>=tp or float(low.iloc[i])<=sl or (i-tbar)>=p_dur):
        if float(high.iloc[i])>=tp: w+=1
        else: l+=1
        tdir=0
    if tdir==0 and score>=p_thresh and retest and regime==1:
        tdir=1; sl=float(close.iloc[i])-(ai*p_risk); tp=float(close.iloc[i])+(ai*p_reward); tbar=i

trades=w+l; win=w*100/trades if trades else 0; pf=(w*p_reward)/(l*p_risk) if l>0 else 99
print(f"FIXED rows={len(df)} Buy={vb} Trades={trades} Win={win:.1f}% PF={pf:.2f}")
