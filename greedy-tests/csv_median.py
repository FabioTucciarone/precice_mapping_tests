#!/usr/bin/env python3
import pandas as pd
import argparse
import os
import sys
import os.path
import re 
import numbers

def parse_args(argv):
    parser = argparse.ArgumentParser(description="Gathers stats after a run")
    parser.add_argument(
        "-o",
        "--run_dir",
        default=".",
        help="Directory to generate the test suite in.",
    )
    parser.add_argument(
        "-b",
        "--base_name",
        default="statistics",
        help="The base name is the file name prefix before a numbering: statistics_1.csv, statistics_2.csv, ...",
    )
    return parser.parse_args(argv)


def median(x):
    if isinstance(x.loc[0], numbers.Number) and not x.isna().any():
        return x.median() 
    else:
        return x.loc[0]


def main(argv):
    args = parse_args(argv[1:])
    
    data_frames = []
    
    for file_name in os.listdir(args.run_dir):
        stats_regex  = re.compile(f"{args.base_name}_[0-9]+\.csv")
        
        if stats_regex.search(file_name):
            stats_df = pd.read_csv(os.path.join(args.run_dir, file_name))
            if "mapping" in stats_df:
                stats_df = stats_df.sort_values(by=["mapping"]).reset_index(drop=True)
            elif "step" in stats_df:
                stats_df = stats_df.sort_values(by=["step"]).reset_index(drop=True)
            data_frames.append(stats_df)
    
    statistics_avg = pd.concat([df.stack() for df in data_frames], axis=1).apply(median, axis=1).unstack()
    statistics_avg.to_csv(os.path.join(args.run_dir, f"{args.base_name}_med.csv"))
        
if __name__ == "__main__":
   main(sys.argv)
