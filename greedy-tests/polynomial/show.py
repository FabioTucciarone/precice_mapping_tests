#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mp
import sys
import os.path


preCICE_orange = "#F36221"
preCICE_lightblue = "#9ECEEC"
preCICE_blue = "#0065BD"
preCICE_green = "#A1B119"
preCICE_lightgreen = "#E4ED94"
preCICE_red = "#C91B36"

def format_plot(test_function, plot_name):
    ylabels = {"centres": "centres used", "time": "mapping time ($\mu s$)", "error": "error (RMSE)"}
    meshes = [0.03, 0.02, 0.01, 0.006, 0.004]
    plt.xscale("log")
    plt.gca().set_xticks(meshes)
    plt.gca().set_xticklabels(meshes)
    plt.xlabel("$h$")
    plt.xlim(0.035, 0.0035)
    plt.grid(True, which="major", color="gainsboro", linestyle="dotted", linewidth=1)
    
    plt.yscale("log")
    plt.xticks(rotation=25, ha='right')
    
    if plot_name == "centres":
        plt.gca().minorticks_off()
        plt.gca().set_yticks([1,2,5,10,20,50,100])
        plt.gca().set_xticklabels([438, 924, 3458, 9588, 21283])
        plt.xlabel("$N$")
        
        plt.gca().yaxis.set_major_formatter(mp.ticker.PercentFormatter(decimals=0))
        
    if test_function == "eggholder" and plot_name == "error":
        plt.gca().set_yticks([4, 6, 10])
        plt.gca().set_yticklabels([4, 6, 10])
        
    plt.ylabel(ylabels[plot_name])
    

def main(plot_path: str):
    
    for test_function in ["franke", "eggholder"]:
        stats_file  = pd.read_csv(os.path.join(plot_path, f"statistics_{test_function}.csv")).sort_values(by="mesh A", ascending=False)
        greedy_file = pd.read_csv(os.path.join(plot_path, f"greedy_values_{test_function}.csv")).sort_values(by="mesh A", ascending=False)
        
        colors = {"f": {"A": preCICE_lightblue, "B": preCICE_blue},
                "P": {"A": preCICE_orange,    "B": preCICE_red},
                "direct": preCICE_green}
        
        linestyles = {"off": "dashed", "sep": "solid"}
        markers    = {"off": "o",      "sep": "D"}
        
        franke_tols    = {"f": {"A": "10^{-7}",        "B": "10^{-9}"},
                          "P": {"A": "4 \cdot 10^{-4}","B": "3.2 \cdot 10^{-5}"}}
        eggholder_tols = {"f": {"A": "810",            "B": "175"},
                          "P": {"A": "4 \cdot 10^{-4}","B": "3.2 \cdot 10^{-5}"}}
        
        tolerances = {"franke": franke_tols, "eggholder": eggholder_tols}
        
        time_field = "mapDataTime"
        
        for method in ["f", "P"]:
            for p in ["off", "sep"]:
                for t in ["A", "B"]:
                    mapping_type = f"{method}_C2-0.5_poly-{p}_tol-{t}"
                    tol_string   = tolerances[test_function][method][t]
                    label        = f"${method}$-greedy, $\\tau={tol_string}$" if p == "sep" else None
                            
                    stats  = stats_file[stats_file["mapping"].str.contains(mapping_type)]
                    greedy = greedy_file[greedy_file["mapping"].str.contains(mapping_type)]
                        
                    plt.subplot(1,3,1)
                    plt.plot(greedy["mesh A"], (greedy["n"] / greedy["N"]) * 100, color=colors[method][t], linestyle=linestyles[p], marker=markers[p], markersize=5, label=label)
                    format_plot(test_function, "centres")
                            
                    plt.subplot(1,3,2)
                    plt.plot(stats["mesh A"], stats[time_field], color=colors[method][t], linestyle=linestyles[p], marker=markers[p], markersize=5, label=label)
                    format_plot(test_function, "time")

                    plt.subplot(1,3,3)
                    plt.plot(stats["mesh A"], stats["relative-l2"], color=colors[method][t], linestyle=linestyles[p], marker=markers[p], markersize=5, label=label)
                    format_plot(test_function, "error")
        
        
        for p in ["off", "sep"]:
            mapping_type = f"direct_C2-0.5_poly-{p}"
            label        = f"global-direct" if p == "sep" else None
                    
            stats  = stats_file[stats_file["mapping"].str.contains(mapping_type)]
                    
            plt.subplot(1,3,2)
            plt.plot(stats["mesh A"], stats[time_field], color=colors["direct"], linestyle=linestyles[p], marker=markers[p], markersize=5, label=label)
            format_plot(test_function, "time")

            plt.subplot(1,3,3)
            plt.plot(stats["mesh A"], stats["relative-l2"], color=colors["direct"], linestyle=linestyles[p], marker=markers[p], markersize=5, label=label)
            format_plot(test_function, "error")
        
        
        plt.gcf().legend(*plt.gca().get_legend_handles_labels(), ncol=3, loc='outside lower center')
        
        plt.gcf().tight_layout()
        plt.subplots_adjust(bottom=0.32, wspace=0.36)
        
        plt.savefig(f"poly-{test_function}.pdf")
        plt.show()
    
    
if __name__ == "__main__":
    
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "figure.figsize": [8.5, 4],
        "font.size": 13,
        "legend.fontsize": 12,
        "lines.markersize": 5
    })
    
    plot_path = os.path.join("test", "polynomial", "data")
    if len(sys.argv) == 2:
        plot_path = os.path.join(plot_path, sys.argv[1])
    
    main(plot_path)

    