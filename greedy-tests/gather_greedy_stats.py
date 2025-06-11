import pandas as pd
import numpy as np
import csv
import argparse
import json
import os
import sys
import os.path

def parse_args(argv):
    parser = argparse.ArgumentParser(description="Gathers stats after a run")
    parser.add_argument(
        "-o",
        "--outdir",
        default="cases",
        help="Directory where to find the test suite.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="greedy_values.csv",
        help="The resulting CSV file containing all stats.",
    )
    parser.add_argument(
        "-nc",
        "--name_constraint",
        default="",
        help="String that must be included in the case name.",
    )
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv[1:])
    
    assert os.path.isdir(args.outdir)
    
    stats_collection = [["mapping", "mesh A", "mesh B", "N", "n"]]
    
    for case_dir_name in os.listdir(args.outdir):
        if args.name_constraint == "" or args.name_constraint in case_dir_name:
            
            case_dir = os.path.join(args.outdir, case_dir_name, "consistent")
            if not os.path.isdir(case_dir):
                print(f"{os.path.join(args.outdir, case_dir_name)}: not a case directory, skipping")
                continue
                
            for mesh_dir_name in os.listdir(case_dir):
                
                case_results_dir = os.path.join(case_dir, mesh_dir_name, "1-1") # TODO: "1-1" assumption
                profiling_json   = os.path.join(case_results_dir, "profiling.json") 
                profiling_csv    = os.path.join(case_results_dir, "profiling.csv")
                
                if not os.path.isfile(profiling_json):
                    continue
                assert os.system(f"precice-profiling export --output {profiling_csv} {profiling_json}") == 0
                
                pd.set_option('display.max_rows', None)
                statistics   = pd.read_csv(profiling_csv)
                row_selector = (statistics["participant"] == "B") & (statistics["event"].str.contains("advance/map\.greedy\.mapData", regex=True) )
                
                if len(statistics[row_selector]["data"]) != 1:
                    print(f"{case_dir_name}: no greedy data found, skipping")
                    continue
                
                print(f"{case_dir_name}: {statistics[row_selector]['data']}")
                
                greedy_data_json = str(statistics[row_selector]["data"].iloc[0]).replace("\'", "\"")
                greedy_data      = json.loads(greedy_data_json)
                
                print(f"{case_dir_name}: greedy data = {greedy_data_json}")
                
                mapping = case_dir_name
                meshA   = mesh_dir_name.split("-")[0]
                meshB   = mesh_dir_name.split("-")[1]
                N       = greedy_data["inSize"]
                n       = greedy_data["basisSize"]
                stats_collection.append([mapping, meshA, meshB, N, n])
    
    with open(args.file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(stats_collection)

if __name__ == "__main__":
   main(sys.argv)
