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

def make_indicator_candles(inf: str,outf: str,periods_sma: int,periods_ema1: int,periods_ema2: int,smoothing: int) -> None:
    deci = lambda a: Decimal(a)
    avg = lambda x: sum(x) / len(x)
    start, high, low = [deci(a) for a in [0, 0, 0]]
    first_line = True
    first_ema1 = True
    first_ema2 = True
    sma_period_closes = []
    ema1_period_closes = []
    ema2_period_closes = []
    sma = 0
    sma1 = 0
    sma2 = 0
    ema1 = 0
    ema2 = 0
    macd = 0
    macd_direction = "none"
    sma_direction = "none" 
    pa_direction = "none"
    direction = "none"
    with open(inf, "r") as infbuff, open(outf, "w") as outfbuff:
        for line in infbuff:
            safe_line = line.strip()
            ts, o, h, l, c = safe_line.split(",")
            o, h, l, c = [deci(x) for x in [o, h, l, c]]
            sma_period_closes.append(c)
            ema1_period_closes.append(c)
            ema2_period_closes.append(c)
            if len(sma_period_closes) == periods_sma:
                sma = avg(sma_period_closes)
                sma_period_closes.pop(0)
            if len(ema1_period_closes) == periods_ema1:
                sma1 = avg(ema1_period_closes)
                ema1_period_closes.pop(0)
            if len(ema2_period_closes) == periods_ema2:
                sma2 = avg(ema2_period_closes)
                ema2_period_closes.pop(0)
            if ema1 != 0:
                prev_ema1 = ema1
                multiplier1 = deci(smoothing/(periods_ema1 + 1))
                ema1 = (c * multiplier1) + (prev_ema1 * (1 - (multiplier1)))
            if ema2 != 0:
                prev_ema2 = ema2
                multiplier2 = deci(smoothing/(periods_ema2 + 1))
                ema2 = (c * multiplier2) + (prev_ema2 * (1 - (multiplier2)))
            if sma1 != 0 and first_ema1 == True:
                ema1 = sma1
                first_ema1 = False
            if sma2 != 0 and first_ema2 == True:
                ema2 = sma2
                first_ema2 = False
            if ema1 != 0 and ema2 != 0:
                macd = deci(ema1 - ema2) * 150
                macd_direction = "down" if macd < 0 else "up" 
            sma_direction = "up" if c > sma else "down"
            pa_direction = "up" if c > o else "down"
            if macd_direction == "up" and sma_direction == "up" and pa_direction == "up":
                direction = "up"
            elif macd_direction == "down" and sma_direction == "down" and pa_direction == "down":
                direction = "down"
            else:
                direction = "none"
            outfbuff.write(f"{safe_line},{sma:.5f},{ema1:.5f},{ema2:.5f},{macd:.5f},{macd_direction}, {sma_direction}, {pa_direction}, {direction}\n")


timeframes = [1,5,10,15,20,60,90,120,180,240]
macd_combos = []
with open("./UM_MACD-Drivers.csv", "r")as candlesurf:
    for line in candlesurf:
        macd_combos.append(line.strip().split(","))

for l in macd_combos:
    s,e,m = l
    for n in timeframes:
        p = n
        tmp_file = f'output/tmp-{s}-{e}-{m}_{p}mins.csv'
        make_candles(p, "input/fixed.csv", tmp_file)
        make_indicator_candles(tmp_file, f'output/{s}-{e}-{m}_{p}mins.csv', int(s), int(e), int(m), 2)
        os.remove(tmp_file)
