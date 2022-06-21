import datetime
from decimal import *


def make_log(level: int):
    def msg_severity(s: int):
        def echo(a):
            if s > level:
                print(a)
        return echo
    return msg_severity

log = make_log(3)
debug = log(1)
info = log(2)
avg_pip = 1.7
chart_drivers = []
fast_macd_drivers =[]    
med_macd_drivers =[]    
slow_macd_drivers =[]    

def candles(p: int, p_macd: list) -> list:
    with open(f"output/{p_macd[0]}-{p_macd[1]}-{p_macd[2]}_{p}mins.csv") as f:
        lines = f.read().split("\n")[:-1]
    output = []
    for line in lines:
        ts, o, h, l, c, ho, hc, sma1, sma2, ema1, ema2, macd, d = line.strip().split(",")
        output.append([datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M"), Decimal(c), d])
    return output

def write_trade_data(candle, change, trading_time, f_macd, m_macd, s_macd):
    with open(f"output/{f_macd[0]}-{f_macd[1]}-{f_macd[2]}_{m_macd[0]}-{m_macd[1]}-{m_macd[2]}_{s_macd[0]}-{s_macd[1]}-{s_macd[2]}_{str(f)}-{str(m)}-{str(s)}.csv", "a") as trade_data:
        trade_data.write(f"{trading_time} - {candle[0]},{candle[2]},{float(change*10000)-avg_pip}\n")

def simulate_combo(fast_p: int, med_p: int, slow_p: int, f_macd: list, m_macd: list, s_macd: list) -> Decimal:
    total = Decimal(0)
    trading = False
    trading_dir = ""
    trading_price = Decimal(0)

    info("getting data...")
    fast = candles(fast_p, f_macd)
    med = candles(med_p, m_macd)
    slow = candles(slow_p, s_macd)
    med_i =  -1
    med_rng = len(med) - 1
    slow_i = -1
    slow_rng = len(slow) - 1
    entries = 0
    wins = 0
    info("begining simulation...")
    for candle in fast:
        if med_i + 1 > med_rng or slow_i + 1 > slow_rng:
            break
        if candle[0] >= med[med_i + 1][0]:
            med_i += 1
        if candle[0] >= slow[slow_i + 1][0]:
            slow_i += 1

        debug("")
        debug("candle")
        debug(candle)
        if trading:
            if candle[2] == med[med_i][2] and candle[2] != trading_dir:
                info("==exiting trade==")
                info(candle)
                trading = False
                current_total = total
                current_closing_candle = med[med_i] if candle[0] == med[med_i][0] else candle
                change = ( (candle[1] - trading_price) * (1 if trading_dir == "up" else -1) )
                total = total + change 
                write_trade_data(current_closing_candle, change, trading_time, f_macd, m_macd, s_macd)
                wins += (1 if total > current_total else 0)
                if slow[slow_i][2] != trading_dir:
                    info("==reentering trade==")
                    trading = True
                    entries += 1
                    trading_dir = candle[2]
                    trading_price = candle[1]
                    trading_time = candle[0]
        else:
            if candle[2] == med[med_i][2] and candle[2] == slow[slow_i][2]:
                info("==entering trade==")
                info(candle)
                trading = True
                entries += 1
                trading_time = candle[0]
                trading_dir = candle[2]
                trading_price = candle[1]


    if trading:
        info("==exiting trading cause we're out of time")
        info(candle)
        total = total + ( (fast[-1][1] - trading_price) * (1 if trading_dir == "up" else -1) )

    return total, entries, wins

with open("./FAST_MACD.csv", "r") as fast, open("./MED_MACD.csv", "r") as medium, open("./SLOW_MACD.csv", "r") as slow:
    for line in fast:
        fast_add = line.strip().split(",")
        fast_macd_drivers.append(fast_add)
    for line in medium:
        med_add = line.strip().split(",")
        med_macd_drivers.append(med_add)
    for line in slow:
        slow_add = line.strip().split(",")
        slow_macd_drivers.append(slow_add)

with open("./drivers.csv", "r") as driver_list:
    for line in driver_list:
        chart_driver_add = line.strip().split(",")
        chart_drivers.append(chart_driver_add)

for fm in fast_macd_drivers:
    for mm in med_macd_drivers:
        for sm in slow_macd_drivers:
            for f, m, s in chart_drivers:
                info(f"=== trading {str(f)}, {str(m)}, {str(s)}")
                chg, cnt, wins = simulate_combo(f, m, s, fm, mm, sm)
                pips = float(chg * 10000) - (avg_pip * cnt)
                info("==== total ====")
                info(chg)
                info("==== done ====")
                print(f"{str(fm)[0]}-{str(fm[1])}-{str(fm[2])},{str(mm)[0]}-{str(mm[1])}-{str(mm[2])},{str(sm)[0]}-{str(sm[1])}-{str(sm[2])},{str(mm)},{str(sm)},{str(f)},{str(m)},{str(s)},{cnt},{pips:.2f}, {wins}")
