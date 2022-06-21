import sys
from decimal import *
import datetime


def make_file(inf: str, outf: str) -> None:


    with open(inf, "r") as f:
        lines = f.read().split("\n")[:-1]

    plus_one = lambda a: a + datetime.timedelta(minutes=1)
    cache = lambda rest: "{}" + f",{','.join(rest)}"

    tfmt = "%Y-%m-%d %H:%M"

    ts_str, *rest = lines[0].split(",")

    next_ts = plus_one(datetime.datetime.strptime(ts_str, tfmt))
    cache_line = cache(rest)
    output = [lines[0]]

    for line in lines[1:]:
        ts_str, *rest = line.split(",")
        ts = datetime.datetime.strptime(ts_str, tfmt)
        close_ts = plus_one(ts)
        while next_ts < ts:
            output.append(cache_line.format(next_ts.strftime(tfmt)))
            next_ts = plus_one(next_ts)
        output.append(line)
        next_ts = plus_one(ts)
        cache_line = cache(rest)
        
    with open(outf, "w") as f:
        f.write("\n".join(output))
        f.write("\n")

inf = sys.argv[1]
outf = sys.argv[2]
make_file(inf, outf)
