#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mp
import sys
import os.path


preCICE_orange = "#F36221"
preCICE_lightblue = "#9ECEEC"
preCICE_blue = "#0065BD"
preCICE_green = "#A1B119"


def collect_method_stats(statistics: pd.DataFrame):
    statistics["shape-param"] = statistics["mapping"].str.replace("(direct|f|P)_C[0-9]-", "", regex=True).astype(float)
    statistics["smoothness"]  = statistics["mapping"].str.replace("(direct|f|P)_C", "", regex=True).str.replace("-[0-9\.]+", "", regex=True).astype(float)
    statistics["mapping"]     = statistics["mapping"].str.replace("_C[0-9]-[0-9\.]+", "", regex=True)
    
    return statistics


def format_plot(graph, stats, plot_name):
    ylabels = {"centres": "centres used", "time": "global time ($\mu s$)", "error": "error (RMSE)"}
    
    if graph == "shape-param":
        plt.xlabel("support radius ($s$)")
    else:
        plt.xlabel("smootness ($C^\\alpha$)")

    plt.ylabel(ylabels[plot_name])
    plt.grid(True, which="major", color="gainsboro", linestyle="dotted", linewidth=1)
    
    if plot_name == "centres":
        plt.gca().yaxis.set_major_formatter(mp.ticker.PercentFormatter(decimals=0))
    else:
        plt.yscale("log")
        
    if graph == "shape-param":
        plt.xticks(stats[graph][1::2])
    else:
        plt.xticks(stats[graph])
        

def main(plot_path: str):

    stats_file  = pd.read_csv(os.path.join(plot_path, "statistics.csv")).sort_values(by="mesh A", ascending=False)
    greedy_file = pd.read_csv(os.path.join(plot_path, "greedy_values.csv")).sort_values(by="mesh A", ascending=False)
    stats_csv   = collect_method_stats(stats_file)
    greedy_csv  = collect_method_stats(greedy_file)
    
    markers = {"P": "o", "f": "D", "direct": "D"}
    colors = {"f": preCICE_blue, "P": preCICE_orange, "direct": preCICE_green}
    
    for graph in ["shape-param", "smoothness"]:
        
        stats_csv.sort_values(graph, inplace=True)
        greedy_csv.sort_values(graph, inplace=True)
        
        for j, method in enumerate(["P", "f", "direct"]):
            
            if graph == "shape-param":
                stats  = stats_csv[(stats_csv["mapping"] == method) & (stats_csv["shape-param"] != 0.4)]
                greedy = greedy_csv[(greedy_csv["mapping"] == method) & (greedy_csv["shape-param"] != 0.4)]
            else:
                stats  = stats_csv[(stats_csv["mapping"] == method) & (stats_csv["shape-param"] == 0.4)]
                greedy = greedy_csv[(greedy_csv["mapping"] == method) & (greedy_csv["shape-param"] == 0.4)]
                
            method_label = "global direct"
            if method == "f":
                method_label = "$f$-greedy, $\\tau=10^{-9}$"
            elif method == "P":
                method_label = "$P$-greedy, $\\tau=10^{-6}$"
            
            plt.subplot(1, 3, 1) 
            plt.plot(stats[graph], stats["relative-l2"], color=colors[method], marker=markers[method], markersize=5, label=f"{method_label}")
            format_plot(graph, stats, "error")
            
            plt.subplot(1, 3, 2) 
            plt.plot(stats[graph], stats["globalTime"], color=colors[method], marker=markers[method], markersize=5)
            format_plot(graph, stats, "time")
            
            plt.subplot(1, 3, 3) 
            if method != "direct":
                plt.plot(greedy[graph], greedy["n"] / greedy["N"] * 100, color=colors[method], marker=markers[method], markersize=5)
                format_plot(graph, stats, "centres")
            
        
        plt.gcf().legend(ncol=4, loc='outside lower center')
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.295, wspace=0.42, hspace=0.164)
        plt.savefig(f"{graph}.pdf")
         
        plt.show()


if __name__ == "__main__":
    
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "figure.figsize": [8.5, 3.5],
        "font.size": 14,
        "legend.fontsize": 13,
        "lines.markersize": 5
    })

    plot_path = os.path.join("test", "shape-param", "data")
    if len(sys.argv) == 2:
        plot_path = os.path.join(plot_path, sys.argv[1])
    
    main(plot_path)