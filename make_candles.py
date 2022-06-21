import os
from decimal import *

def make_candles(blk:int, inf: str, outf: str) -> None:
    deci = lambda a: Decimal(a)
    start, high, low = [deci(a) for a in [0, 0, 0]]
    tick = 1
    p = ""
    with open(inf, "r") as infbuff, open(outf, "w") as outfbuff:
        for line in infbuff:
            ts, o, h, l, c = line.strip().split(",")
            o, h, l, c = [deci(x) for x in [o, h, l, c]]
            if tick == 1:
                start = o
                low = l
                high = h
            else:
                if l < low: low = l
                if h > high: high = h
            
            if tick == blk:
                p = ts
                tick = 1
                outfbuff.write(f"{p},{start:.5f},{high:.5f},{low:.5f},{c:.5f}\n")
            else:
                tick += 1

def make_indicator_candles(inf: str, outf: str, periods_sma1: int, periods_sma2: int, smoothing: int) -> None:
    deci = lambda a: Decimal(a)
    avg = lambda x: sum(x) / len(x)
    start, high, low, last_hopen, last_hclose = [deci(a) for a in [0, 0, 0, 0, 0]]
    first_line = True
    first_ema1 = True
    first_ema2 = True
    sma1_period_closes = []
    sma2_period_closes = []
    sma1 = 0
    sma2 = 0
    ema1 = 0
    ema2 = 0
    macd = 0
    direction = "none"
    with open(inf, "r") as infbuff, open(outf, "w") as outfbuff:
        for line in infbuff:
            safe_line = line.strip()
            ts, o, h, l, c = safe_line.split(",")
            o, h, l, c = [deci(x) for x in [o, h, l, c]]
            hclose = ((o+h+l+c)/4)
            if first_line:
                hopen = ((o+c)/2)
                first_line = False
            else:
                hopen = (last_hopen + last_hclose) / 2
            sma1_period_closes.append(hclose)
            sma2_period_closes.append(hclose)
            if len(sma1_period_closes) == periods_sma1:
                sma1 = avg(sma1_period_closes)
                sma1_period_closes.pop(0)
            if len(sma2_period_closes) == periods_sma2:
                sma2 = avg(sma2_period_closes)
                sma2_period_closes.pop(0)
            if ema1 != 0:
                prev_ema1 = ema1
                multiplier1 = deci(smoothing/(periods_sma1 + 1))
                ema1 = (hclose * multiplier1) + (prev_ema1 * (1 - (multiplier1)))
            if ema2 != 0:
                prev_ema2 = ema2
                multiplier2 = deci(smoothing/(periods_sma2 + 1))
                ema2 = (hclose * multiplier2) + (prev_ema2 * (1 - (multiplier2)))
            if sma1 != 0 and first_ema1 == True:
                ema1 = sma1
                first_ema1 = False
            if sma2 != 0 and first_ema2 == True:
                ema2 = sma2
                first_ema2 = False
            if ema1 != 0 and ema2 != 0:
                macd = deci(ema1 - ema2)
                direction = "down" if macd < 0 else "up"  
            outfbuff.write(f"{safe_line},{hopen:.5f},{hclose:.5f},{sma1:.5f},{sma2:.5f},{ema1:.5f},{ema2:.5f},{macd:.5f},{direction}\n")
            last_hopen = hopen
            last_hclose = hclose


timeframes = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 30, 32, 36, 40, 45, 48, 60, 72, 80, 90, 96, 120, 144, 160, 180, 240]
macd_combos = [[12,26,9],[9,20,7],[8,17,6],[6,13,5],[5,10,4],[4,9,3]]
for l in macd_combos:
    s,e,m = l
    for n in timeframes:
        p = n
        tmp_file = f'output/tmp-{s}-{e}-{m}_{p}mins.csv'
        make_candles(p, "input/fixed.csv", tmp_file)
        make_indicator_candles(tmp_file, f'output/{s}-{e}-{m}_{p}mins.csv', s, e, m)
        os.remove(tmp_file)
