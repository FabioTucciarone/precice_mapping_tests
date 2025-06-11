#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib as mp
import numpy as np


preCICE_blue = "#0065BD"


def w_c0(r):
    return (1 - r)**2 * (r <= 1)

def w_c2(r):
    return (1 - r)**4 * (4*r + 1) * (r <= 1)
    
def w_c4(r):
    return (1 - r)**6 * (35*r**2 + 18*r + 3) * (r <= 1)
    
def w_c6(r):
    return (1 - r)**8 * (32*r**3 + 25*r**2 + 8*r + 1) * (r <= 1)
  
def w_c8(r):
    return (1.0 - r)**10 * (1287.0 * r**4 + 1350.0 * r**3 + 630.0 * r**2 + 150.0 * r + 15) * (r <= 1)
    
    
def w_c(alpha, x, rho):
    r = np.abs(x) / rho
    if alpha == 0:
        return w_c0(r)
    if alpha == 2:
        return w_c2(r)
    if alpha == 4:
        return w_c4(r)
    if alpha == 6:
        return w_c6(r)
    if alpha == 8:
        return w_c8(r)
    else:
        raise "alpha ∈ {0,2,4,6,8}"


def main():
    
    x = np.linspace(-1, 1, 1000)

    for alpha in range(0, 10, 2):
        plt.subplot(1, 5, int(alpha/2) + 1)
        plt.plot(x, w_c(alpha, x, 1), color=preCICE_blue, label="$w_{" + str(alpha) + ", 1}(\|x\|)$")
        plt.xlabel("$x$")
        plt.yticks([round(y, 1) for y in np.linspace(0, w_c(alpha, 0, 1), 4)])
        plt.grid(True, which="both", axis="both", color="gainsboro", linestyle="dotted", linewidth=1)
        plt.title("$w_{" + str(alpha) + ", 1}(x)$")
        
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.22, wspace=0.3, hspace=0.164)

    plt.savefig(f"wendland-functions.pdf")

    plt.show()
        
    
if __name__ == "__main__":
    
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "figure.figsize": [8.5, 2.3],
        "font.size": 14,
        "axes.titlesize": 14,
        "legend.fontsize": 10
    })
    
    main()