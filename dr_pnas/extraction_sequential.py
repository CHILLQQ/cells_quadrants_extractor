"""This module contains functions for extracting every surface parameter defined
under dr/parameters from a given a surface.

`extract_parameters` does this for a single surface, while the family of 
`parallelized_extraction` functions use parallel processing to speed up computation
when calculating over multiple surfaces.

`construct_cache` is a helper function that calculates and caches several items
that the surface parameters rely on. For instance, to avoid recalculating the 
Fourier spectrum of a surface everytime we call a spatial parameter, we calculate it
once and then pass the cached value in as an argument to every spatial parameter
instead.

Note that extracting the parameters from a surface sometimes requires you to provide
information like the pixel separation distances (dx, dy) or configuration options like 
how many semicircles/radial lines to draw for spatial parameters (M).

!!!NOTE
this code is reduced so it does not include parallelized parts
it is also missing these libraries
import pathos.multiprocessing as mp
from functools import partial, reduce
it is needed to calculate surface parameters on google colab sequentially
"""

import numpy as np
import pandas as pd
from tqdm import tqdm

from dr_pnas.load import load_ascii
from dr_pnas.utils import (fit_and_subtract,
                      find_local_maxs,
                      find_local_mins,
                      find_summits,
                      construct_interpolator,
                      get_fourier_spectrum,
                      angular_amplitude_sum,
                      radial_amplitude_sum,
                      get_acf)
from dr_pnas.parameters import *


def construct_cache(channel: np.array,
                    M: float,
                    interpolator=None) -> dict:
    """Constructs a cache of values useful for calculating the S parameters.

    Args:
        channel (np.array): An MxN channel.
        M (float): For use with several spatial parameters. See docs in `dr.parameters.spatial`
        for more details.
        interpolator (function, optional): An interpolation function called to
        provide interpolated values for the Fourier spectrum where necessary. If
        `None`, bilinear interpolation is used.

    Returns:
        dict: A cache of values containing:
            channel (np.array)
            fitted (np.array)
            spectrum (np.array)
            interpolator (function)
            angular_amplitudes (np.array)
            radial_amplitudes (np.array)
            acf (np.array)
            zero_lag_dix ((int, int))
            local_maxs (np.array)
            local_mins (np.array)
            summits (np.array) (not anymore actually)
    """
    cache = {}

    dim, _ = channel.shape

    # Channel and transformations
    cache['channel'] = channel
    cache['fitted'] = fit_and_subtract(channel)

    cache['spectrum'], cache['xf'], cache['yf'] = get_fourier_spectrum(
        cache['fitted'])

    if interpolator is None:
        cache['interpolator'] = construct_interpolator(cache['spectrum'])
    else:
        cache['interpolator'] = interpolator(cache['spectrum'])

    # Collections derived from Fourier spectrum
    cache['angular_amplitudes'] = [angular_amplitude_sum(spectrum=cache['spectrum'],
                                                         angle=i * np.pi / M,
                                                         interpolator=cache['interpolator'])
                                   for i in np.arange(0, M)]
    cache['radial_amplitudes'] = [radial_amplitude_sum(spectrum=cache['spectrum'],
                                                       radius=i,
                                                       interpolator=cache['interpolator'])
                                  for i in np.linspace(1, dim // 2, M // 2)]
    cache['acf'], cache['zero_lag_idx'] = get_acf(cache['spectrum'])

    # Local features
    cache['local_maxs'] = find_local_maxs(cache['fitted'])
    cache['local_mins'] = find_local_mins(cache['fitted'])

    # Currently, for parameter dependent on `summits`, we use local maximums instead
    # cache['summits'] = find_summits(cache['fitted'], S_z(cache['fitted']))

    return cache


def extract_parameters(channel: np.array,
                       dx: float,
                       dy: float,
                       M: int) -> pd.Series:
    """Extracts S parameters from a channel.

    Args:
        channel: An MxM channel.
        dx: The pixel separation distance along the x-dimension.
        dy: The pixel separation distance along the y-dimension.
        M: For use with several spatial parameters. See docs in
        `dr.parameters.spatial` for more details.

    Returns:
        A series containing the S parameters calculated on the given channel.
    """
    # Construct a cache containing useful calculations
    ######BE careful here. This /10 factor is added to match zoom.py
    ######If you calculate the surface params using zoom.py - comment it out!!
    ##channel = channel/10
    ##print("WORKS!")
    #####################
    cache = construct_cache(channel, M=M)

    #fitted = cache['fitted']
    fitted = channel  # because we don't need to fit for any channel except "height"
    print("No fitting here!")
    spectrum = cache['spectrum']

    # Parameters reused in calculating others
    s_q = S_q(fitted)
    s_2a = S_2a(fitted, dx=dx, dy=dy)
    s_3a = S_3a(fitted, dx=dx, dy=dy)


    parameters = {
        ## Amplitude parameters ##
        'S_a': S_a(fitted),
        'S_q': s_q,
        'S_sk': S_sk(fitted, std=s_q),
        'S_ku': S_ku(fitted, std=s_q),
        'S_z': S_z(fitted),
        'S_10z': S_10z(fitted,
                       local_maxs=cache['local_maxs'],
                       local_mins=cache['local_mins']),
        'S_v': S_v(fitted),
        'S_p': S_p(fitted),
        'S_mean': S_mean(channel),

        ## Hybrid parameters ##
        'S_sc': S_sc(fitted, dx=dx, dy=dy),
        'S_2a': s_2a,
        'S_3a': s_3a,
        'S_dr': S_dr(fitted, dx=dx, dy=dy, s_2a=s_2a, s_3a=s_3a),
        'S_dq': S_dq(fitted, dx=dx, dy=dy),
        'S_dq6': S_dq6(fitted, dx=dx, dy=dy),

        # Functional parameters ##
        'S_bi': S_bi(fitted, std=s_q),
        'S_ci': S_ci(fitted, dx=dy, dy=dy, std=s_q),
        'S_vi': S_vi(fitted, dx=dx, dy=dy, std=s_q),
        'S_pk': S_pk(fitted, dx=dx, dy=dy),
        'S_vk': S_vk(fitted),
        'S_k': S_k(fitted),
        'S_dc0-5': S_dc(fitted, l=0, h=5),
        'S_dc5-10': S_dc(fitted, l=5, h=10),
        'S_dc10-50': S_dc(fitted, l=10, h=50),
        'S_dc50-95': 0, #S_dc(fitted, l=50, h=95),
        'S_dc50-100': S_dc(fitted, l=50, h=100),

        ## Spatial parameters ##
        'S_ds': S_ds(fitted, dx=dx, dy=dy, summits=cache['local_maxs'])*1000000,
        'S_td': S_td(spectrum,
                     M=M,
                     amplitudes=cache['angular_amplitudes'],
                     interpolator=cache['interpolator']
                     ),
        'S_tdi': S_tdi(spectrum,
                       M=M,
                       amplitudes=cache['angular_amplitudes'],
                       interpolator=cache['interpolator']
                       ),
        'S_rw': S_rw(spectrum,
                     dx=dx,
                     M=M,
                     amplitudes=cache['radial_amplitudes'],
                     interpolator=cache['interpolator']),
        'S_rwi': S_rwi(spectrum,
                       M=M,
                       amplitudes=cache['radial_amplitudes'],
                       interpolator=cache['interpolator']),
        'S_hw': S_hw(spectrum,
                     dx=dx,
                     M=M,
                     amplitudes=cache['radial_amplitudes'],
                     interpolator=cache['interpolator']),
        'S_fd': S_fd(spectrum,
                     xf=cache['xf'],
                     M=M,
                     interpolator=cache['interpolator']),
        'S_cl20': S_cl(spectrum,
                       correlation=0.20,
                       dx=dx,
                       dy=dy,
                       acf=cache['acf'],
                       zero_lag_idx=cache['zero_lag_idx']),
        'S_cl37': S_cl(spectrum,
                       correlation=0.37,
                       dx=dx,
                       dy=dy,
                       acf=cache['acf'],
                       zero_lag_idx=cache['zero_lag_idx']),
        'S_tr20': S_tr(spectrum,
                       correlation=0.20,
                       dx=dx,
                       dy=dy,
                       acf=cache['acf'],
                       zero_lag_idx=cache['zero_lag_idx']),
        'S_tr37': S_tr(spectrum,
                       correlation=0.37,
                       dx=dx,
                       dy=dy,
                       acf=cache['acf'],
                       zero_lag_idx=cache['zero_lag_idx'])
    }
    return pd.Series(parameters)
