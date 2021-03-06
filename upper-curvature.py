#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 15:56:40 2022

@author: utkarsh
"""

import MDAnalysis as mda
from membrane_curvature.base import MembraneCurvature
from MDAnalysisData import datasets
import matplotlib.pyplot as plt
import more_itertools as mit
import nglview as nv
import numpy as np
from scipy import ndimage
import argparse
import sys

trajectory = sys.argv[1]
topology = sys.argv[2]
universe = mda.Universe(topology, trajectory)
P_headgroups = universe.select_atoms('name P31')
from MDAnalysis.analysis.leaflet import LeafletFinder

# Lsys = LeafletFinder(universe, 'name PO4', cutoff=20)
Lsys = LeafletFinder(universe, 'name P31')


upper_leaflet = Lsys.groups(0) # upper leaflet
lower_leaflet = Lsys.groups(1) # lower leafet

#leaflets = ['Lower', 'Upper']

#upper_leaflet_P = upper_leaflet.select_atoms("name P31")
#lower_leaflet_P = lower_leaflet.select_atoms("name P31")

sel_upper = " ".join([str(r) for r in upper_leaflet.residues.resids])
sel_lower = " ".join([str(r) for r in lower_leaflet.residues.resids])

upper_string = "resid {} and name P31".format(sel_upper)
lower_string = "resid {} and name P31".format(sel_lower)


#curvature calculation

MembraneCurvature(universe,         # universe
                  select='name P31',  # selection of reference
                  n_x_bins=10,       # number of bins in the x dimension
                  n_y_bins=10,       # number of bins in the y_dimension
                  wrap=True)        # wrap coordinates to keep atoms in the main unit cell

curvature_upper_leaflet = MembraneCurvature(universe,
                                            select=upper_string,
                                            n_x_bins=10,
                                            n_y_bins=10,
                                            wrap=True).run()

curvature_lower_leaflet = MembraneCurvature(universe,
                                            select=lower_string,
                                            n_x_bins=10,
                                            n_y_bins=10,
                                            wrap=True).run()

surface_upper_leaflet = curvature_upper_leaflet.results.average_z_surface
surface_lower_leaflet = curvature_lower_leaflet.results.average_z_surface
mean_upper_leaflet = curvature_upper_leaflet.results.average_mean
mean_lower_leaflet = curvature_lower_leaflet.results.average_mean
gaussian_upper_leaflet = curvature_upper_leaflet.results.average_gaussian
gaussian_lower_leaflet = curvature_lower_leaflet.results.average_gaussian


#plots by leaflet

def plots_by_leaflet(results):
    """
    Generate figure with of surface, $H$ and $K$
    as subplots.
    """


    cms=["YlGnBu_r", "bwr", "PiYG"]
    units=['$Z$ $(\AA)$','$H$ (??$^{-1})$', '$K$ (??$^{-2})$']
    titles = ['Surface', 'Mean Curvature', 'Gaussian Curvature']

    fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(7,4), dpi=200)
    for ax, mc, title, cm, unit in zip((ax1, ax2, ax3), results, titles, cms, units):
        mc = ndimage.zoom(mc,3, mode='wrap', order=1)
        bound = max(abs(np.min(mc)), abs(np.max(mc)))
        if np.min(mc) < 0 < np.max(mc):
            im = ax.contourf(mc, cmap=cm, levels=40, alpha=0.95, vmin=-bound, vmax=+bound)
            tcs = [np.min(mc), 0, np.max(mc)]
        else:
            im = ax.contourf(mc, cmap=cm, levels=40, alpha=0.95)
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=12)
        ax.axis('off')
        cbar=plt.colorbar(im, ticks=[np.min(mc), 0, np.max(mc)] if np.min(mc) < 0 < np.max(mc) else [np.min(mc), np.max(mc)], ax=ax, orientation='horizontal', pad=0.05, aspect=15)
        cbar.ax.tick_params(labelsize=7, width=0.5)
        cbar.set_label(unit, fontsize=9, labelpad=2)
    plt.tight_layout()
    fig.savefig("upper_curvature.png")

#upper leaflet
results_upper = [surface_upper_leaflet,
           mean_upper_leaflet,
           gaussian_upper_leaflet]
plots_by_leaflet(results_upper)
