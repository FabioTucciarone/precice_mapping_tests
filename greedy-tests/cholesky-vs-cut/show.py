#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mp
import os
import sys

preCICE_orange = "#F36221"
preCICE_lightblue = "#9ECEEC"
preCICE_blue = "#0065BD"
preCICE_green = "#A1B119"


def collect_method_stats(statistics: pd.DataFrame, method: str):
    method_selector = statistics["mapping"].str.contains(method)
    method_stats    = statistics[method_selector].copy()
    
    if method == "direct":
        return method_stats
    
    method_stats["centers-percent"] = method_stats["mapping"].str.replace(f"{method}-", "").astype(int)
    method_stats["mapping"]         = method_stats["mapping"].str.replace("-[0-9]+", "")
    method_stats.sort_values("centers-percent", inplace=True)
    
    return method_stats


def get_methods(statistics: pd.DataFrame):
    return statistics["mapping"].str.replace("-[0-9]+", "", regex=True).drop_duplicates().to_list()


def build_figure(data_path: str, colors: dict, time_column: str):
        
    time_stats_path   = os.path.join(data_path, "statistics.csv")
    memory_stats_path = os.path.join(data_path, "memory.csv")
    
    fig = plt.figure()
    
    for show_PUM in [False, True]:
        
        time_axes = fig.add_subplot(121 + 1*show_PUM, label="time")
        memory_axes = fig.add_subplot(121 + 1*show_PUM, label="memory", frame_on=False, sharex=time_axes)
        
        memory_axes.grid(True, which="major", axis="y", color="gainsboro", linestyle="dotted", linewidth=1)
        time_axes.grid(True, which="major", axis="y", color="gainsboro", linestyle="dotted", linewidth=1)
        time_axes.grid(True, which="major", axis="x", color="gainsboro", linestyle="dotted", linewidth=1)
        
        if os.path.isfile(time_stats_path):
            times_csv = pd.read_csv(time_stats_path)
            mapping_methods = get_methods(times_csv)
    
            time_axes.set_ylabel("compute time ($ms$)" if time_column == "computeMappingTime" else "mapping time ($ms$)")
            time_axes.yaxis.tick_left()
            time_axes.yaxis.set_label_position('left') 
            time_axes.xaxis.set_major_formatter(mp.ticker.PercentFormatter(decimals=0))
            
            for method in mapping_methods:
                method_time_stats = collect_method_stats(times_csv, method)
                time_ms = method_time_stats[time_column] / 1000.0
                
                method_label = method.replace("cut","inv").replace("P-", "$P$-").replace("f-", "$f$-") + " (time)"
                
                if show_PUM:
                    time_axes.plot(method_time_stats["relative-l2"], time_ms, marker="o", color=colors[method], linestyle="solid", label=method_label)
                    time_axes.set_xscale("log")
                    time_axes.set_yscale("log")
                    if method == "direct":
                        time_axes.axhline(y=time_ms.iloc[0], color=colors[method], linestyle='dotted')
                elif not "PUM" in method:
                    time_axes.ticklabel_format(axis="y", style="sci", scilimits=(0,3))
                    if "P-" in method:
                        time_axes.plot(method_time_stats["centers-percent"], time_ms, marker="o", color=colors[method], linestyle="solid", label=method_label)
                    else:
                        time_axes.plot([100], time_ms, marker="o", color=colors[method], linestyle="solid", label=method_label)
                        time_axes.axhline(y=time_ms.iloc[0], color=colors[method], linestyle='dotted')
                        
            if show_PUM:
                time_axes.set_xlabel("error (RMSE)")
            else:
                time_axes.set_xlabel("centres used")
        
        else:
            print(f"\"{time_stats_path}\": no timing data found.")
            return
  
        memory_axes.set_ylabel("memory ($GB$)")
        memory_axes.yaxis.tick_right()
        memory_axes.yaxis.set_label_position('right') 
            
        for method in mapping_methods:
            method_time_stats = collect_method_stats(times_csv, method)
            
            method_label = method.replace("cut","inv").replace("P-", "$P$-").replace("f-", "$f$-") + " (mem)"
        
            memory_column = "peakMemB"
            if os.path.isfile(memory_stats_path):
                memory_csv = pd.read_csv(memory_stats_path)
                method_mem_stats = collect_method_stats(memory_csv, method)
                method_mem_stats = pd.merge(method_time_stats, method_mem_stats, how="left", on=["mapping"]).dropna()
                memory_column = "memory"
                centers_column = "centers-percent_x"
            else:
                print("No external memory.csv found: plotting \"peakMemB\" from ASTE.")
                method_mem_stats = method_time_stats
                centers_column = "centers-percent"
                
            memory_gb = method_mem_stats[memory_column] / 1000.0
            
            if show_PUM:
                memory_axes.plot(method_mem_stats["relative-l2"], memory_gb, marker="D", color=colors[method], linestyle="dotted", label=method_label)
                time_axes.set_xscale("log")
                memory_axes.set_yscale("log")
                if method == "direct":
                        memory_axes.axhline(y=memory_gb.iloc[0], color=colors[method], linestyle='dotted')
            elif not "PUM" in method:
                if "P-" in method:
                    memory_axes.plot(method_mem_stats[centers_column], memory_gb, marker="D", color=colors[method], linestyle="dotted", label=method_label)
                else:
                    memory_axes.plot([100], memory_gb, marker="D", color=colors[method], linestyle="solid", label=method_label)
                    memory_axes.axhline(y=memory_gb.iloc[0], color=colors[method], linestyle='dotted') 
            
            if show_PUM:
                time_axes.set_xlabel("error (RMSE)")
            else:
                time_axes.set_xlabel("centres used")
        
        time_handles,   labels = time_axes.get_legend_handles_labels()
        memory_handles, labels = memory_axes.get_legend_handles_labels()
    
    plt.gcf().legend(handles=time_handles+memory_handles, ncol=4, loc='outside lower center')
    
    return fig
    

def main():
    
    data_path = os.path.join("test", "cholesky-vs-cut", "data")
    if len(sys.argv) == 2:
        data_path = os.path.join(data_path, sys.argv[1])
        
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "figure.figsize": [8.5, 4.5],
        "font.size": 13,
        "legend.fontsize": 12,
        "lines.markersize": 5
    })    
    colors = { "P-cholesky": preCICE_orange, "P-cut": preCICE_blue, "PUM": preCICE_lightblue, "direct": preCICE_green}
    
    for time_column in ["computeMappingTime", "mapDataTime"]:
        fig = build_figure(data_path, colors, time_column)
        
        fig.tight_layout()
        fig.subplots_adjust(bottom=0.28, wspace=0.4)
        
        plt.savefig(f"cut-vs-cholesky-{time_column}.pdf")
        plt.show()
        
     
if __name__ == "__main__":
    main()
    
    
    