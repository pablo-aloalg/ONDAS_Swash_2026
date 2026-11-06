import numpy as np
import matplotlib.pyplot as plt

def reef_profile(dx, h0, Slope1, Slope2, Wreef, Wfore, bCrest, emsl):
    '''
        Reef morphologic profile (Pearson et al. 2017)

        dx:   bathymetry mesh resolution at x axes (m)
        h0:      offshore depth (m)
        Slope1:  fore shore slope
        Slope2:  inner shore slope
        Wreef:   reef bed width (m)
        Wfore:   flume length before fore toe (m)
        bCrest:  beach heigh (m)
        emsl:    mean sea level (m)

        return depth data values
    '''

    # flume length
    W_inner = bCrest / Slope2
    W1 = int(h0 / Slope1)

    # sections length
    x1 = np.arange(0, Wfore,   dx)
    x2 = np.arange(0, W1,      dx)
    x3 = np.arange(0, Wreef,   dx)
    x4 = np.arange(0, W_inner, dx)

    # curve equation
    y_fore = np.zeros(len(x1)) + [h0]
    y1 = - Slope1 * x2 + h0
    y2 = np.zeros(len(x3)) + [0]
    y_inner = - Slope2 * x4

    # overtopping cases: an inshore plane beach to dissipate overtopped flux
    plane = 0.005 * np.arange(0, len(y_inner), 1) + y_inner[-1]

    # concatenate depth
    depth = np.concatenate([y_fore, y1 ,y2, y_inner, plane]) + emsl
    x = np.arange(0,len(depth),1)
    return x, -depth


def linear_profile(h0, Ltotal, Wconst=0.0, slope=None, hFinal=None, dx=1.0):

    if slope is None and hFinal is None:
        raise ValueError("Either slope or hFinal must be provided.")
    if slope is not None and hFinal is not None:
        raise ValueError("Provide only one of slope or hFinal, not both.")

    
    # Total number of points
    N = int(Ltotal / dx) + 1
    x = np.linspace(0, Ltotal, N)
    z = np.zeros_like(x)
    
    # Index where the slope starts
    idx_slope_start = int(Wconst / dx)
    
    # Constant depth section
    z[:idx_slope_start] = h0
    
    # Linear section
    x_slope = x[idx_slope_start:]
    
    if slope is not None:
        z[idx_slope_start:] = h0 + slope * (x_slope - Wconst)
    else:
        # compute slope automatically
        slope_auto = (hFinal - h0) / (Ltotal - Wconst)
        z[idx_slope_start:] = h0 + slope_auto * (x_slope - Wconst)
    
    return x, z