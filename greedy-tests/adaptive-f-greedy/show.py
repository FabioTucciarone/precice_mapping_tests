#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import matplotlib as mp
import sys
import json
import yaml
import os
from cycler import cycler


preCICE_orange = "#F36221"
preCICE_lightblue = "#9ECEEC"
preCICE_blue = "#0065BD"
preCICE_green = "#A1B119"
preCICE_lightgreen = "#E4ED94"
preCICE_red = "#C91B36"


def parse_greedy_data_json(df_row):
    if "data" in df_row and df_row["data"] == df_row["data"]:
        data = json.loads(df_row["data"].replace("\'", "\""))
        return { "N": data["inSize"], "n": data["basisSize"] }
    else: 
        return { "N": 1, "n": 1 }
    
def set_properties(ax: Axes, label):
    ax.grid(True, which="major", color="gainsboro", linestyle="dotted", linewidth=1)
    ax.set_ylabel(label)
    ax.tick_params('x', labelbottom=False)
    if label == "mapping time ($\mu s$)":
        ax.grid(True, which="major", color="gainsboro", linestyle="dotted", linewidth=1)
        ax.set_yscale("log")
    if label == "used centers":
        ax.yaxis.set_major_formatter(mp.ticker.PercentFormatter(decimals=0))
    #ax.set_yticks(ax.get_yticks())


def combine_input_files(events_csv, statistics_csv, print_details=False):
    if print_details:
        pd.set_option('display.max_rows', None)
        row_selector = (events_csv["participant"] == "B") & events_csv["event"].str.contains("(map\..*greedy\.(solve|update)|map\.(rbf|pou)\.mapData)", regex=True)
        events = events_csv[row_selector]
        print(events[["event", "duration"]])
    
    row_selector = (events_csv["participant"] == "B") & events_csv["event"].str.contains("(map\..*greedy\.mapData|map\.(rbf|pou)\.mapData)", regex=True)
    events = events_csv[row_selector]
    
    applied_df = events.apply(parse_greedy_data_json, axis='columns', result_type='expand')
    statistics = pd.concat([events, applied_df], axis='columns')
    statistics = statistics.reset_index()
    statistics["relative-l2"] = list(statistics_csv["relative-l2"])
    statistics = statistics.drop([len(statistics)-1], axis=0) # letzter Zeitschritt aus irgendeinem Grund verschoben
    statistics["t"] = (statistics.index.astype(int) + 1) # * plot_info['time-step-size']
    
    if print_details:
        print(statistics[["t", "n", "N", "duration", "relative-l2"]])
    
    return statistics


def show_statistics(axs: list[Axes], statistics, label, linestyle, marker):
    axs[0].plot(statistics["t"], statistics["duration"], marker=marker, linestyle=linestyle, markersize=4, label=label)
    set_properties(axs[0], "mapping time ($\mu s$)")

    axs[1].plot(statistics["t"], (statistics["n"] / statistics["N"]) * 100, marker=marker,linestyle=linestyle, markersize=4, label=label)
    set_properties(axs[1], "used centers")
                
    axs[2].plot(statistics["t"], statistics["relative-l2"], marker=marker, linestyle=linestyle, markersize=4, label=label)
    set_properties(axs[2], "error (RMSE)")
                
    axs[2].set_xticks(statistics["t"])
    axs[2].tick_params('x', labelbottom=True)
                
    axs[2].set_xlabel("time steps")
    
    average_duration = np.average(statistics["duration"])
    average_error = np.average(statistics["relative-l2"])
    print(f"   average duration = {average_duration}")
    print(f"   average error    = {average_error}")


def load_statistics(case_path):
    events_path     = os.path.join(case_path, "profiling.csv")
    statistics_path = os.path.join(case_path, "statistics.csv")
        
    if not (os.path.isfile(events_path) or os.path.isfile(statistics_path)):
        print(f"\"{os.path.isfile(events_path)}\" or \"{os.path.isfile(statistics_path)}\": no data found, skipping")
        return None
        
    events_csv     = pd.read_csv(events_path)
    statistics_csv = pd.read_csv(statistics_path)
                
    return combine_input_files(events_csv, statistics_csv, print_details=False)


def load_yaml_info(info_yaml_path):
    if not os.path.isfile(info_yaml_path):
        print(f"\"{info_yaml_path}\": Plotting information not found.")
        return None
    with open(info_yaml_path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(f"\"{info_yaml_path}\": YAML Error: \n {exc}")
            return None


def build_figure(plot_path, colors, linestyles, markers):
    
    if len(os.listdir(plot_path)) > 0:
        
        fig, axs = plt.subplots(nrows=3, ncols=1, sharex=True)
        
        for j in range(0, 3):
            axs[j].set_prop_cycle(cycler(color=colors))
        
        i = 0
        case_dirs = os.listdir(plot_path)
        case_dirs.sort()
        
        for case_dir in case_dirs:
            case_path = os.path.join(plot_path, case_dir)
    
            if os.path.isdir(case_path) and not case_dir.startswith("."):
                print(f"Found case: \"{case_dir}\"")
                sub_case_dirs = os.listdir(case_path)
                sub_case_dirs.sort()
                
                for sub_case_dir in sub_case_dirs:
                    sub_case_path = os.path.join(case_path, sub_case_dir)
                    
                    if os.path.isdir(sub_case_path) and not sub_case_dir.startswith("."):
                        print(f" > sub-case: \"{sub_case_dir}\"")
                        
                        statistics = load_statistics(sub_case_path)
                        if statistics is None:
                            continue
                        
                        combined_name = f"{sub_case_dir}" if case_dir == "all" else f"{case_dir}: {sub_case_dir}"
                        show_statistics(axs, statistics, f"{combined_name}", linestyles[i % len(linestyles)], markers[i % len(markers)])
                i += 1
            
                for j in range(0, 3):
                    axs[j].set_prop_cycle(cycler(color=colors))

        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, ncol=5, loc='outside lower center')
        
    else:
        print(f"Showing results at default path.")
        
        fig, axs = plt.subplots(nrows=3, ncols=1, sharex=True)
        
        case_path  = os.path.join(plot_path, "data") #TODO LÖSEN
        statistics = load_statistics(case_path)
        if statistics is None:
            print(f"\"{case_path}\": no data found, skipping")
            return
        
        show_statistics(axs, statistics, "Latest", "solid", "o")
        
    return fig
    

def  main():
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "figure.figsize": [8.5, 6.5],
        "font.size": 13,
        "legend.fontsize": 12
    })
   
    colors     = [preCICE_orange, preCICE_blue, preCICE_lightblue, preCICE_green, preCICE_red, preCICE_lightgreen]
    linestyles = ["solid", "dashed", "dotted", "dashdot"]
    markers    = ["o", "v", "d", "h", "s", "P"]
    
    plot_path = os.path.join("test", "adaptive-f-greedy", "data")
    if len(sys.argv) == 2:
        plot_path = os.path.join(plot_path, sys.argv[1])
        
    fig = build_figure(plot_path, colors, linestyles, markers)
    
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.138)
    
    name = plot_path.split("/")[-1].split("thesis-")[-1]
    
    plt.savefig(f"adaptive-{name}.pdf")
    plt.show() 
    
    
if __name__ == "__main__":
    main()