#!/usr/bin/env python3
import pandas as pd
import csv
import argparse
import json
import os
import sys
import os.path
import math

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
    parser.add_argument(
        "-er",
        "--event_regex",
        default="",
        help="Regex description of the event names containing the desired data.",
    )
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv[1:])
    
    is_conservative = False # TODO: auslesen
    
    all_keys: set = set()
    data_list: list[dict] = []
    
    assert os.path.isdir(args.outdir)
    
    for case_dir_name in os.listdir(args.outdir):
        if args.name_constraint == "" or args.name_constraint in case_dir_name:
            
            case_dir = os.path.join(args.outdir, case_dir_name, "conservative" if is_conservative else "consistent")
            if not os.path.isdir(case_dir):
                print(f" > {os.path.join(args.outdir, case_dir_name)}: not a case directory, skipping")
                continue
                
            for mesh_dir_name in os.listdir(case_dir):
                
                print(f"{case_dir}/{mesh_dir_name}")
                
                case_results_dir = os.path.join(case_dir, mesh_dir_name, "1-1") # TODO: "1-1" assumption
                profiling_json   = os.path.join(case_results_dir, "profiling.json") 
                profiling_csv    = os.path.join(case_results_dir, "profiling.csv")
                
                if not os.path.isfile(profiling_json):
                    print(f" > No profiling.json in \"{case_dir}/{mesh_dir_name}\"")
                    continue
                assert os.system(f"precice-profiling export --output {profiling_csv} {profiling_json}") == 0
                
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                statistics   = pd.read_csv(profiling_csv)
                row_selector = statistics["event"].str.contains(args.event_regex, regex=True)
                
                
                if len(statistics[row_selector]) < 1:
                    print(f" > {case_dir_name}: no data found, skipping")
                    continue
                
                # old event data format:
                # event_data_json = str(statistics[row_selector]["data"].iloc[0]).replace("\'", "\"")
                # event_data      = json.loads(event_data_json)
                
                event_data = dict()
                
                for key in statistics[row_selector].keys():
                    num_null_values = pd.isnull(statistics[row_selector][key]).sum()
                    if num_null_values == len(statistics[row_selector][key]) - 1:
                        for entry in statistics[row_selector][key]:
                            if not pd.isnull(entry):
                                event_data[key] = entry
                
                event_name = statistics[row_selector]['event'].iloc[0]
                mapping    = case_dir_name
                meshA      = mesh_dir_name.split("-")[0]
                meshB      = mesh_dir_name.split("-")[1]
                
                all_keys |= set(event_data.keys())
                data      = {"mapping": mapping, "mesh A": meshA, "mesh B": meshB, **event_data}
                
                data_list.append(data)
            
    key_list = ["mapping", "mesh A", "mesh B"] + list(all_keys)
    
    with open(args.file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, key_list)
        writer.writeheader()
        writer.writerows(data_list)


if __name__ == "__main__":
   main(sys.argv)
