#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mp
import sys
import os
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import colors as pltcolors

class Config:
    function: str      # franke, cos, eggholder
    mesh: str          # turbine, halton
    rbf: str           # gauss-45, c2-10, c2-5
    
    include_iter: bool # True, False
    repr_h: float


preCICE_orange = "#F36221"
preCICE_lightblue = "#9ECEEC"
preCICE_blue = "#0065BD"
preCICE_green = "#A1B119"
preCICE_lightgreen = "#E4ED94"
preCICE_red = "#C91B36"
preCICE_yellow = "#ffcf4a"

###### HELPERS ######

def get_grid_resolutions(config: Config):
    if config.mesh == "halton":
        return [0.168, 0.084, 0.042, 0.021, 0.0105, 0.00525, 0.002625]
    elif config.mesh == "turbine":
        return [0.03, 0.02, 0.01, 0.006, 0.004] # 0.008 (5310), 0.009 (4302) fehlt
    else:
        raise f"unknown mesh: config.mesh={config.mesh}"


def get_grid_sizes(config: Config):
    if config.mesh == "halton":
        return [9, 25, 81, 289, 1089, 4225, 16641]
    elif config.mesh == "turbine":
        return [438, 924, 3458, 9588, 21283] # 0.008 (5310), 0.009 (4302) fehlt
    else:
        raise f"unknown mesh: config.mesh={config.mesh}"


def read_greedy_values_file(plot_path: str):
    return pd.read_csv(f"{plot_path}/greedy_values.csv").sort_values(by="mesh A", ascending=False)


def read_statistics_file(plot_path: str):
    return pd.read_csv(f"{plot_path}/statistics.csv").sort_values(by="mesh A", ascending=False)


def set_properties(config: Config, data_field: str):
    plt.grid(True, which="major", color="gainsboro", linestyle="dotted", linewidth=1)
    plt.rc("legend",fontsize="small")
    
    # x-Achse
    plt.gca().xaxis.set_inverted(True)
    plt.xscale("log")
    plt.xlabel("$h$")
    plt.gca().set_xticks(get_grid_resolutions(config))
    if data_field == "used centers":
        plt.xlabel("$N$")
        plt.gca().set_xticklabels(get_grid_sizes(config))
    else:
        plt.gca().set_xticklabels(get_grid_resolutions(config))
        
    # y-Achse
    ylabel = data_field
    if data_field == "relative-l2":
        ylabel = "error (RMSE)"
    elif "computeMappingTime" == data_field:
        ylabel = "comupte time ($\mu s$)"
    elif "mapDataTime" == data_field:
        ylabel = "mapping time ($\mu s$)"
    if data_field != "used centers": 
        plt.yscale("log")
    else:
        plt.gca().set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        plt.gca().yaxis.set_major_formatter(mp.ticker.PercentFormatter(decimals=0))
    plt.ylabel(ylabel)


def greedy_name_to_float(name: str, greedy_method: str):
    mapping_prefix = f"{greedy_method.lower()}_"
    name = name.replace(mapping_prefix, "")
    name = name.str.replace("1e", "")
    return name.replace("1e", "").astype(float)


def greedy_name_to_tolerance_latex(name: str, greedy_method: str):
    mapping_prefix = f"{greedy_method.lower()}_"
    name = name.replace(mapping_prefix, "").replace("1e", "10^{")
    if "10^{" in name:
        name += "}"
    return name


###### PLOTS ######

def runtime_vs_error(config: Config, plot_path: str):
    stats_file = read_statistics_file(plot_path)
    greedy_file = read_greedy_values_file(plot_path)

    methods = [["rbf-direct"]]
    colors  = {"rbf-direct": preCICE_green }
    markers = {"rbf-direct": "s"         }
    names   = {"rbf-direct": "direct"}
    
    methods += [["nearest-neighbour"]]
    colors["nearest-neighbour"]  = "darkgrey"
    markers["nearest-neighbour"] = "s"
    names["nearest-neighbour"]   = "nearest"

    maps = stats_file[stats_file["mapping"].str.contains("pum_")]["mapping"].drop_duplicates().sort_values(key=lambda x: x.str.replace("pum_M", "").astype(float)).to_list()
    methods += [maps]
    for map in maps:
        colors[map]  = preCICE_lightblue
        markers[map] = "d"
        t = map.split("_M")[1]
        names[map] = t
    
    maps = greedy_file[greedy_file["mapping"].str.contains("p-greedy_")]["mapping"].drop_duplicates().sort_values(key=lambda x: greedy_name_to_float(x.str, "p-greedy")).to_list()
    methods += [maps]
    for map in maps:
        colors[map]  = preCICE_orange
        markers[map] = "o"
        t = map.split("_")[1]
        names[map] = f"${greedy_name_to_tolerance_latex(map, 'p-greedy')}$"
    
    maps = greedy_file[greedy_file["mapping"].str.contains("f-greedy_")]["mapping"].drop_duplicates().sort_values(key=lambda x: greedy_name_to_float(x.str, "f-greedy")).to_list()
    methods += [maps]
    for map in maps:
        colors[map]  = preCICE_blue
        markers[map] = "o"
        t = map.split("_")[1]
        names[map] = f"${greedy_name_to_tolerance_latex(map, 'f-greedy')}$"
        
    stats_h = stats_file[stats_file["mesh A"] == config.repr_h].sort_values(by="mapDataTime", ascending=False)
    time_fields = ["computeMappingTime", "mapDataTime"] # TODO: peakMemB
    
    fig, axs = plt.subplots(1, len(time_fields), sharey=True)
    
    for i, time_field in enumerate(time_fields):
        for maps in methods:
            errors = []
            times = []
            for map in maps:
                stats = stats_h[stats_h["mapping"].str.contains(f"{map}$")]
                if len(stats) > 0:              
                    error = float(stats["relative-l2"].iloc[0])
                    time  = float(stats[time_field].iloc[0])
                    errors.append(error)
                    times.append(time)
                    
                    axs[i].text(time + 0.35 * time, error - 0.2 * error, names[map], fontsize = 10)
                    axs[i].set_yscale("log")
                    axs[i].set_xscale("log")
            
            axs[i].plot(times, errors, marker=markers[maps[0]], linestyle=(0, (1, 2)), color=colors[maps[0]], label=f"{names[maps[0]]}")

        time_label = "mapping time" if time_field == "mapDataTime" else "compute time"
        axs[i].set_xlabel(f"{time_label} ($\mu s$)")
        if i == 0:
            axs[i].set_ylabel(f"error (RMSE)")
        axs[i].grid(True, which="major", color="gainsboro", linestyle="dotted", linewidth=1)
    
    fig.subplots_adjust(wspace=0.095, bottom=0.2)
    fig.set_size_inches(8.5, 5)
    
    line_p_greedy = mp.lines.Line2D([0], [0], label="$P$-greedy", marker="o", color=preCICE_orange)
    line_f_greedy = mp.lines.Line2D([0], [0], label='$f$-greedy', marker="o", color=preCICE_blue)
    line_pum = mp.lines.Line2D([0], [0], label='PUM', marker="d", color=preCICE_lightblue)
    line_nearest = mp.lines.Line2D([0], [0], label='nearest-neighbour', marker="s", color="darkgrey")
    line_direct = mp.lines.Line2D([0], [0], label='global-direct', marker="s", color=preCICE_green)
        
    handles, labels = fig.axes[0].get_legend_handles_labels()
    handles.clear()
    handles.extend([line_p_greedy, line_f_greedy, line_pum, line_nearest, line_direct])
    fig.legend(handles=handles, ncol=5, loc='outside lower center')
    
    plt.savefig(f"error-vs-runtime.pdf")
    plt.show()   


def compare_methods(config: Config, plot_path: str, greedy_method: str):

    # collect statistics

    stats_file  = read_statistics_file(plot_path)
    greedy_file = read_greedy_values_file(plot_path)
    
    mapping_prefix = f"{greedy_method.lower()}_"
    greedy_maps = greedy_file[greedy_file["mapping"].str.contains(mapping_prefix)]["mapping"].drop_duplicates().sort_values(key=lambda x: greedy_name_to_float(x.str, greedy_method)).to_list()

    # colors and markers

    color_base_names = [preCICE_lightblue, preCICE_lightgreen, preCICE_green, preCICE_yellow, preCICE_orange, preCICE_red]
    color_base = [pltcolors.hex2color(color_name) for color_name in color_base_names]
    color_map  = LinearSegmentedColormap.from_list("colormap", color_base, N=len(greedy_maps))

    colors     = { "rbf-direct": preCICE_blue,    "pum_M10": "tab:cyan", "pum_M100": "tab:cyan", "nearest-neighbour": "gray"              }
    markers    = { "rbf-direct": "v",             "pum_M10": "d",        "pum_M100": "d",        "nearest-neighbour": "v"                 }
    linestyles = { "rbf-direct": "solid",         "pum_M10": "solid",    "pum_M100": "solid",    "nearest-neighbour": "dashed"            }
    names      = { "rbf-direct": "global direct", "pum_M10": "PUM: 10",  "pum_M100": "PUM: 100", "nearest-neighbour": "nearest neighbour" }
    compare_maps  = ["pum_M10", "pum_M100", "nearest-neighbour", "rbf-direct"]
    
    error_name = "relative-l2"
    center_name = "used centers"
    
    for i, map in enumerate(greedy_maps):
        colors[map] = color_map(i)
        markers[map] = "o"
        linestyles[map] = "dotted"
        names[map] = f"$\\tau={greedy_name_to_tolerance_latex(map, greedy_method)}$"
        
    # plot generation
        
    fig, axs = plt.subplots(2, 2)
    
    for i, data_name in enumerate([error_name, center_name, "computeMappingTime", "mapDataTime"]):

        plt.subplot(2, 2, 1 + i)
        
        max_error = stats_file['relative-l2'].max()
        start = stats_file["mesh A"].max()
        
        if data_name == error_name:
            plt.plot(stats_file["mesh A"], max(max_error / start, 1) * stats_file["mesh A"],    linestyle="solid", color="lightgray", label=f"$h^1$")
            plt.plot(stats_file["mesh A"], max(max_error / start, 1) * (stats_file["mesh A"])**2, linestyle="solid", color="lightgray", label=f"$h^2$")
            plt.plot(stats_file["mesh A"], max(max_error / start, 1) * (stats_file["mesh A"])**3, linestyle="solid", color="lightgray", label=f"$h^3$")
        
        for map in greedy_maps + compare_maps:
            if map in greedy_maps and data_name == center_name:
                stats = greedy_file[greedy_file["mapping"].str.contains(f"{map}$")]
                plt.plot(stats["mesh A"], (stats["n"] / stats["N"]) * 100, marker=markers[map], linestyle=linestyles[map], color=colors[map], label=f"{names[map]}")
            elif data_name != center_name:
                stats = stats_file[stats_file["mapping"].str.contains(f"{map}$")]
                plt.plot(stats["mesh A"], stats[data_name], marker=markers[map], linestyle=linestyles[map], color=colors[map], label=f"{names[map]}")
            
            
            plt.grid(True, which="major", color="gainsboro", linestyle="dotted", linewidth=0.5)
            
            # x-Achse
            plt.gca().xaxis.set_inverted(True)
            plt.xscale("log")
            plt.xlabel("$h$")
            plt.gca().set_xticks(get_grid_resolutions(config))
            if data_name == center_name:
                plt.xlabel("$N$")
                plt.gca().set_xticklabels(get_grid_sizes(config))
            else:
                plt.gca().set_xticklabels(get_grid_resolutions(config))
                
            # y-Achse
            ylabel = data_name.replace("relative-l2", "error (RMSE)").replace("computeMappingTime", "comupte time ($\mu s$)").replace("mapDataTime", "mapping time ($\mu s$)")
            if data_name != "used centers": 
                plt.yscale("log")
            else:
                plt.gca().set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
                plt.gca().yaxis.set_major_formatter(mp.ticker.PercentFormatter(decimals=0))
            plt.ylabel(ylabel)

    # formatting
             
    handles, labels = fig.axes[0].get_legend_handles_labels()
    fig.legend(handles=handles, ncol=5, loc='outside lower center')
        
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.19, wspace=0.27, left=0.12, hspace=0.164)
    fig.set_size_inches(8.5, 8.8)
    
    plt.savefig(f"general-comparison-{greedy_method.replace('-greedy', '')}.pdf")
    plt.show()


def main():
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "font.size": 14,
        "legend.fontsize": 12,
        "lines.markersize": 5
    })
      
    plot_path = os.path.join("test", "overview", "data")
    if len(sys.argv) == 2:
        plot_path = os.path.join(plot_path, sys.argv[1])
    
    config = Config()
    config.mesh     = "turbine"
    config.include_iter = False
    config.repr_h = 0.006
    
    compare_methods(config, plot_path, "f-greedy")
    compare_methods(config, plot_path, "P-greedy")
    runtime_vs_error(config, plot_path)
    
    

if __name__ == "__main__":
   main()