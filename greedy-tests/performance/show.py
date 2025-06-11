#!/usr/bin/env python3
import polars as pl
import pandas as pd
import sys

def main(argv):

    statistics = pl.read_csv(argv[1])
    print(statistics.select("relative-l2", "median(abs)","mapDataTime", "computeMappingTime"))

if __name__ == "__main__":
   main(sys.argv)