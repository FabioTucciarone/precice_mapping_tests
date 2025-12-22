#!/usr/bin/env python3
import polars as pl
import pandas as pd
import matplotlib as mp
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
        return "$f=0.8 + \cos(20(x+y+z))$"
    elif "franke" in description:
        return "$f= $ franke3d"
    else:
        return "?"
    

# HACKY SOLUTION FOR CONSERVATIVE ERROR MEASURES
# Shitty code that probably doesn't work. Also requires hacky state of preCICE and aste.

def main(argv):
    
    paths = []
    
    paths = [(f"test/radius/data/franke3d", "statistics.csv", "additional.csv"),
             (f"test/radius/data/cos", "statistics.csv", "additional.csv")]

    for case in paths:
        
        case_path, stats_file_name, add_file_name = case

        statistics = pd.read_csv(f"{case_path}/{stats_file_name}")
        additional = pd.read_csv(f"{case_path}/{add_file_name}")
        
        other_statistics = statistics.loc[~statistics['mapping'].str.contains("_")]
        other_additional = additional.loc[~additional['mapping'].str.contains("_")]
        
        statistics = statistics.drop(other_statistics.index)
        additional = additional.drop(other_additional.index)
        
        statistics['rbf'] = statistics.apply(lambda row: row.mapping.split("_")[0], axis=1)
        statistics['radius'] = statistics.apply(lambda row: row.mapping.split("_")[1], axis=1).astype('float64')
        
        additional['rbf'] = additional.apply(lambda row: row.mapping.split("_")[0], axis=1)
        additional['radius'] = additional.apply(lambda row: row.mapping.split("_")[1], axis=1).astype('float64')
    
        
        fig: Figure = plt.figure()
        
        fig.suptitle(f"{get_test_function(case_path)}")
        
        for j, rbf in enumerate(["gaussian", "wendlandC4"]):
            
            filtered_stats = statistics.loc[(statistics["rbf"] == rbf) & (statistics["mesh A"] == "coarse")].sort_values(by="radius", ascending=False).reindex()
            filtered_add   = additional.loc[(additional["rbf"] == rbf) & (additional["mesh A"] == "coarse")].sort_values(by="radius", ascending=False).reindex()
            
            radius_range = 0.06
            
            filtered_stats = filtered_stats.loc[(filtered_add["llt-success"] == 1) & (filtered_stats["radius"] < radius_range)]
            filtered_add   = filtered_add.loc[(filtered_add["llt-success"] == 1) & (filtered_stats["radius"] < radius_range)]

            rcond       = np.pow(10.0, filtered_add['100-log-rcond'] / 100.0)
            loocv_error = np.pow(10.0, filtered_add['1000-log-loocv_error'] / 1000.0)
            sum_error   = np.clip(np.pow(10.0, filtered_add['1000-log-sum_error'] / 1000.0), 1e-14, 1e10)
            
            loocv_error_vs = np.pow(10.0, other_additional['1000-log-loocv_error'] / 1000.0)
            sum_error_vs   = np.clip(np.pow(10.0, other_additional['1000-log-sum_error'] / 1000.0), 1e-14, 1e10)
            
            ########################################################################
            
            err_axs: Axes  = fig.add_subplot(321 + j)
            err_axs.set_xscale('log')
            err_axs.set_xticks([0.005, 0.01, 0.02, 0.05])
            err_axs.get_xaxis().set_major_formatter(mp.ticker.ScalarFormatter())
            cond_axs: Axes = fig.add_subplot(321 + j, sharex=err_axs, frame_on=False)
            
            cond_axs.set_yscale("log")
            err_axs.set_yscale("log")

            err_axs.plot(filtered_stats['radius'], np.abs(filtered_stats['relative-l2']),          color="tab:blue", marker="o", label="standard RMSE")
            err_axs.plot(filtered_stats['radius'], np.abs(filtered_stats['weighted-relative-l2']), color="tab:orange", marker="o", label="weighted RMSE")
            cond_axs.plot(filtered_add['radius'], 1 / rcond, marker="x", linestyle="dotted", color="red", label="condition")
            
            err_axs.axhline(y=np.abs(other_statistics['relative-l2']).iloc[0], color="tab:blue", marker="+", linestyle="dotted", label="volume-splines")
            err_axs.axhline(y=np.abs(other_statistics['weighted-relative-l2']).iloc[0], color="tab:orange", marker="+", linestyle="dotted", label="volume-splines")

            err_handles,  labels = err_axs.get_legend_handles_labels()
            cond_handles, labels = cond_axs.get_legend_handles_labels()
            err_axs.legend(handles=err_handles + cond_handles, loc="upper left", fontsize=9)
            cond_axs.yaxis.tick_right()
            cond_axs.yaxis.set_label_position('right') 

            ###########################################################################
            
            loocv_err_axs: Axes  = fig.add_subplot(323 + j, sharex=err_axs)
            sum_err_axs: Axes  = fig.add_subplot(323 + j, sharex=loocv_err_axs, frame_on=False)
            
            loocv_err_axs.set_yscale("log")
            sum_err_axs.set_yscale("log")
            
            loocv_err_axs.plot(filtered_stats['radius'], loocv_error,     color="tab:blue", marker="o", label="LOOCV")
            sum_err_axs.plot(filtered_stats['radius'], np.abs(sum_error), color="tab:orange", marker="o", label="sum difference")
            loocv_err_axs.axhline(y=np.abs(loocv_error_vs).iloc[0], color="tab:blue", marker="+", linestyle="dotted", label="volume-splines")
            sum_err_axs.axhline(y=np.abs(sum_error_vs).iloc[0], color="tab:orange", marker="+", linestyle="dotted", label="volume-splines")
            
            loocv_err_handles, labels = loocv_err_axs.get_legend_handles_labels()
            sum_err_handles,   labels = sum_err_axs.get_legend_handles_labels()
            sum_err_axs.legend(handles=loocv_err_handles + sum_err_handles, loc="lower left", fontsize=9)
            loocv_err_axs.yaxis.tick_right()
            loocv_err_axs.yaxis.set_label_position('right') 
            
            ###########################################################################
            
            fft_axs: Axes  = fig.add_subplot(325 + j, sharex=err_axs)
            min_max_axs: Axes  = fig.add_subplot(325 + j, sharex=fft_axs, frame_on=False)
            
            fft_axs.set_yscale("log")
            min_max_axs.set_yscale("log")
            
            fft_axs.plot(filtered_stats['radius'], np.abs(filtered_stats['aste-fft-diff']),    color="tab:blue", marker="o", label="fft-diff")
            min_max_axs.plot(filtered_stats['radius'], np.abs(filtered_stats['min-max-diff']), color="tab:orange", marker="o", label="min-max-diff")
            fft_axs.axhline(y=np.abs(other_statistics['aste-fft-diff']).iloc[0], color="tab:blue", marker="+", linestyle="dotted", label="volume-splines")
            min_max_axs.axhline(y=np.abs(other_statistics['min-max-diff']).iloc[0], color="tab:orange", marker="+", linestyle="dotted", label="volume-splines")

            fft_handles,     labels = fft_axs.get_legend_handles_labels()
            min_max_handles, labels = min_max_axs.get_legend_handles_labels()
            fft_axs.legend(handles=fft_handles + min_max_handles, loc="upper left", fontsize=9)
            min_max_axs.yaxis.tick_right()
            min_max_axs.yaxis.set_label_position('right') 
            
            #######################################################################
            
            if j == 0:
                err_axs.set_ylabel("RMSE")
                fft_axs.set_ylabel("FFT difference")
                sum_err_axs.set_ylabel("sum difference")
            else:
                loocv_err_axs.set_ylabel("LOOCV")
                cond_axs.set_ylabel("condition number")
                min_max_axs.set_ylabel("min-max coeff")
                
            err_axs.set_title(f"$h=0.02$, rbf$=${rbf}")
            min_max_axs.set_xlabel("radius")
            

                
        fig.savefig(f"{case_path}-conservative.pdf")
        fig.show()
        
    plt.show(block=True)


if __name__ == "__main__":
    
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "font.size": 12,
        "legend.fontsize": 12,
        "lines.markersize": 5,
        "figure.subplot.top": 0.93,
        "figure.subplot.bottom": 0.1,
        "figure.subplot.wspace": 0.36,
        "figure.subplot.left": 0.12,
        "figure.subplot.hspace": 0.25,
        "figure.figsize": (9, 9)
    })
    
    main(sys.argv)