#!/usr/bin/env python3
import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import sys
import os
import numpy as np

def main(argv):
    
    paths = []
    
    # if len(argv) > 1:
    #     if not os.path.exists(argv[1]):
    #         raise f'Path "{os.path.abspath(argv[1])}" not found.'
    #     paths.append( ("console arg", argv[1]) )
    # else:
    #     for file_name in os.listdir("test/radius/data"):
    #         if not os.path.isdir(file_name):
    #             paths.append( (file_name, f"test/radius/data/{file_name}") )
                
    paths = [(f"test/radius/data/franke3d", "statistics.csv", "additional.csv"),
             (f"test/radius/data/cos", "statistics.csv", "additional.csv")]

    for case in paths:
        
        case_path, stats_file_name, add_file_name = case

        statistics = pd.read_csv(f"{case_path}/{stats_file_name}")
        additional = pd.read_csv(f"{case_path}/{add_file_name}")
        
        statistics['rbf'] = statistics.apply(lambda row: row.mapping.split("_")[0], axis=1)
        statistics['radius'] = statistics.apply(lambda row: row.mapping.split("_")[1], axis=1).astype('float64')
        
        additional['rbf'] = additional.apply(lambda row: row.mapping.split("_")[0], axis=1)
        additional['radius'] = additional.apply(lambda row: row.mapping.split("_")[1], axis=1).astype('float64')
    
        
        fig: Figure = plt.figure()
        
        fig.suptitle(case_path)
        
        for i, mesh_resolution in enumerate(["coarse", "fine"]):
            for j, rbf in enumerate(["gaussian", "wendlandC4"]):
                
                err_axs: Axes  = fig.add_subplot(221 + 2*i + j)
                cond_axs: Axes = fig.add_subplot(221 + 2*i + j, sharex=err_axs, frame_on=False)
                
                filtered_stats = statistics.loc[(statistics["rbf"] == rbf) & (statistics["mesh A"] == mesh_resolution)].sort_values(by="radius", ascending=False)
                filtered_add   = additional.loc[(additional["rbf"] == rbf) & (additional["mesh A"] == mesh_resolution)].sort_values(by="radius", ascending=False)

                rcond = np.pow(10.0, filtered_add['100-log-rcond'] / 100.0) # filtered_add['condition-factor'] / 10 * np.pow(2.0, filtered_add['condition-exp'])

                err_axs.plot(filtered_stats['radius'], filtered_stats['relative-l2'], marker="o", color="blue", label="error")
                cond_axs.plot(filtered_add['radius'], 1 / rcond, marker="x", linestyle="dotted", color="red", label="reciprocal condition")
                err_axs.plot(filtered_add['radius'], filtered_add['llt-success'] + 1e-3, marker=".", linestyle="none", color="grey", label="llt success")
                
                cond_axs.set_xscale("log")
                cond_axs.set_yscale("log")
                cond_axs.grid(which="major", color="lightgrey", linestyle="dotted")
                cond_axs.yaxis.tick_right()
                cond_axs.yaxis.set_label_position('right') 
                
                err_axs.set_title(f"{mesh_resolution}, {rbf}")
                err_axs.set_xscale("log")
                err_axs.set_yscale("log")
                err_axs.grid(which="major", color="lightgrey", linestyle="dotted")
                err_axs.set_xlabel("radius")
                
                if j == 0:
                    err_axs.set_ylabel("relative $l_2$")
                else:
                    cond_axs.set_ylabel("reciprocal condition")
                
                time_handles,   labels = err_axs.get_legend_handles_labels()
                memory_handles, labels = cond_axs.get_legend_handles_labels()
    
                fig.legend(handles=time_handles+memory_handles, ncol=4, loc='outside lower center')
                
                # Manuelle Punkte
                if mesh_resolution == "fine" and rbf == "wendlandC4":
                    # Bayes Opt:
                    err_axs.plot(9.2714e-01, 0.000005, marker="D", color="green")
                    err_axs.annotate("BO", (9.2714e-01, 0.000005))
                    # Bisection:
                    err_axs.plot(8.8041e-01, 0.000005, marker="D", color="green")
                    err_axs.annotate("Bi", (8.8041e-01, 0.000005))
                    # Iterative:
                    err_axs.plot(1.0020e+00, 0.000005, marker="D", color="green")
                    err_axs.annotate("It", (1.0020e+00, 0.000005))
                    
                if mesh_resolution == "fine" and rbf == "gaussian":
                    # Bayes Opt:
                    err_axs.plot(5.6346e-02, 0.00215189, marker="D", color="green")
                    err_axs.annotate("BO", (5.6346e-02, 0.00215189))
                    # Bisection:
                    err_axs.plot(7.2194e-02, 0.0005269536, marker="D", color="green")
                    err_axs.annotate("Bi", (7.2194e-02, 0.0005269536))
                    # Iterative:
                    err_axs.plot(5.6346e-02, 0.00215189, marker="D", color="green")
                    err_axs.annotate("It", (5.6346e-02, 0.00215189))
                    
                
        fig.show()
        fig.savefig(f"{stats_file_name}.pdf")
        
    plt.show(block=True)


if __name__ == "__main__":
    
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "font.size": 12,
        "legend.fontsize": 12,
        "lines.markersize": 5,
        "figure.subplot.bottom": 0.13,
        "figure.subplot.wspace": 0.285,
        "figure.subplot.left": 0.12,
        "figure.subplot.hspace": 0.25,
        "figure.figsize": (9, 9)
    })
    
    main(sys.argv)