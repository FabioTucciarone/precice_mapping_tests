#!/usr/bin/env python3
import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import sys
import os
import numpy as np


def get_mesh_res(description: str):
    if "coarse" in description:
        return "0.02"
    elif "fine" in description:
        return "0.008"
    else:
        return "?"


def get_test_function(description: str):
    if "cos" in description:
        return "$0.8 + \cos(15(x+y+z))$"
    elif "franke" in description:
        return "franke3d"
    else:
        return "?"
    

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
             (f"test/radius/data/cos", "statistics.csv", "additional.csv")] # (f"test/radius/data/franke3d", "statistics.csv", "additional.csv")

    for case in paths:
        
        case_path, stats_file_name, add_file_name = case

        statistics = pd.read_csv(f"{case_path}/{stats_file_name}")
        additional = pd.read_csv(f"{case_path}/{add_file_name}")
        
        statistics['rbf'] = statistics.apply(lambda row: row.mapping.split("_")[0], axis=1)
        statistics['radius'] = statistics.apply(lambda row: row.mapping.split("_")[1], axis=1).astype('float64')
        
        additional['rbf'] = additional.apply(lambda row: row.mapping.split("_")[0], axis=1)
        additional['radius'] = additional.apply(lambda row: row.mapping.split("_")[1], axis=1).astype('float64')
    
        
        fig: Figure = plt.figure()
        
        fig.suptitle(get_test_function(case_path))
        
        for i, mesh_resolution in enumerate(["coarse"]): # coarse und ggf andere stehen in statistics.csv
            for j, rbf in enumerate(["gaussian", "wendlandC4"]):
                
                err_axs: Axes  = fig.add_subplot(221 + 2*i + j)
                cond_axs: Axes = fig.add_subplot(221 + 2*i + j, sharex=err_axs, frame_on=False)
                
                filtered_stats = statistics.loc[(statistics["rbf"] == rbf) & (statistics["mesh A"] == mesh_resolution)].sort_values(by="radius", ascending=False).reindex()
                filtered_add   = additional.loc[(additional["rbf"] == rbf) & (additional["mesh A"] == mesh_resolution)].sort_values(by="radius", ascending=False).reindex()
                
                filtered_stats = filtered_stats.loc[filtered_add["llt-success"] == 1]
                filtered_add   = filtered_add.loc[filtered_add["llt-success"] == 1]

                rcond       = np.pow(10.0, filtered_add['100-log-rcond'] / 100.0)
                loocv_error = np.pow(10.0, filtered_add['1000-log-loocv_error'] / 1000.0)
                sum_error   = np.pow(10.0, filtered_add['1000-log-sum_error'] / 1000.0) / 1e3

                err_axs.plot(filtered_stats['radius'], filtered_stats['relative-l2'], marker="o", label="relative-l2")
                err_axs.plot(filtered_stats['radius'], filtered_stats['weighted-relative-l2'], marker="o", label="weighted-relative-l2")
                err_axs.plot(filtered_stats['radius'], loocv_error, marker="o", label="loocv_error")
                err_axs.plot(filtered_stats['radius'], sum_error, marker="o", label="sum_error")
                
                cond_axs.plot(filtered_add['radius'], 1 / rcond, marker="x", linestyle="dotted", color="red", label="condition number")
                #err_axs.plot(filtered_add['radius'], filtered_add['llt-success'] + 1e-3, marker=".", linestyle="none", color="grey", label="LLT success")
                
                cond_axs.set_xscale("log")
                cond_axs.set_yscale("symlog")
                #cond_axs.grid(which="major", color="lightgrey", linestyle="dotted")
                cond_axs.yaxis.tick_right()
                cond_axs.yaxis.set_label_position('right') 
                
                err_axs.set_title(f"{mesh_resolution} ($h={get_mesh_res(mesh_resolution)}$), rbf={rbf}")
                err_axs.set_xscale("log")
                err_axs.set_yscale("symlog")
                err_axs.grid(which="major", color="lightgrey", linestyle="dotted")
                err_axs.set_xlabel("radius")
                
                if j == 0:
                    err_axs.set_ylabel("relative $l_2$")
                else:
                    cond_axs.set_ylabel("condition number")
                
                time_handles,   labels = err_axs.get_legend_handles_labels()
                memory_handles, labels = cond_axs.get_legend_handles_labels()
    
                fig.legend(handles=time_handles + memory_handles, ncol=4, loc='outside lower center')
                
                
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