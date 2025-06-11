#!/usr/bin/env python3
import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import sys

def main(argv):
    
    stat_path = "test/performance/testcase/statistics.csv"
    if (not sys.path.exists(stat_path)):
        stat_path = "test/performance/data/statistics.csv"
    if len(argv) > 1:
        stat_path = argv[1]   

    statistics = pd.read_csv(stat_path)
    
    statistics['rbf'] = statistics.apply(lambda row: row.mapping.split("_")[0], axis=1)
    statistics['radius'] = statistics.apply(lambda row: row.mapping.split("_")[1], axis=1).astype('float64')
    
    axs: Axes; fig: Figure
    fig, axs= plt.subplots(2, 2, sharex=True)
    
    for i, mesh_resolution in enumerate(["coarse", "fine"]):
        for j, rbf in enumerate(["gaussian", "wendlandC4"]):
            
            filtered_stats = statistics.loc[(statistics["rbf"] == rbf) & (statistics["mesh A"] == mesh_resolution)].sort_values(by="radius", ascending=False)

            axs[i, j].plot(filtered_stats['radius'], filtered_stats['relative-l2'], marker="o")
            
            axs[i, j].set_title(f"{mesh_resolution}, {rbf}")
            axs[i, j].set_xscale("log")
            axs[i, j].set_yscale("log")
            axs[i, j].set_xlabel("radius")
            axs[i, j].set_ylabel("relative $l_2$")
            axs[i, j].grid(which="major", color="lightgrey")
            
    plt.show()
    plt.savefig(f"shape-param-comparison.pdf")


if __name__ == "__main__":
    
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "font.size": 12,
        "legend.fontsize": 12,
        "lines.markersize": 5,
        "figure.subplot.bottom": 0.13,
        "figure.subplot.wspace": 0.27,
        "figure.subplot.left": 0.12,
        "figure.subplot.hspace": 0.18,
        "figure.figsize": (8.5, 8.5)
    })
    
    main(sys.argv)