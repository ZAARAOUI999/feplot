
"""
    FEPlot
    Created November 2022
    Copyright (C) Mohamed ZAARAOUI

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import numpy as np

from scipy.spatial import Delaunay
from matplotlib import collections
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def quatplot(_u, _v, cells, _ax, **kwargs):
    """Plot a 2D mesh"""
    _uv = np.c_[_u,_v]
    verts= _uv[cells]
    mesh = collections.PolyCollection(verts, **kwargs)
    _ax.add_collection(mesh)
    _ax.autoscale()

def polyplot(points, cells, values, _ax, **kwargs):
    """Plot a 3D mesh"""
    polys = []
    new_values = []
    for cell in cells:
        new_points = points[np.sort(cell)]
        triang = Delaunay(new_points)
        hull = triang.convex_hull
        poly = new_points[hull]
        polys.extend(list(poly))
        new_values.extend(list(values[np.sort(cell)][hull]))
    mesh = Poly3DCollection(polys, linewidths=.5, edgecolor=kwargs.pop('c'),
                                closed=True, cmap='turbo', zsort='average',
                                facecolor='grey')
    new_values = np.array(new_values)
    mesh.set_array(new_values.mean(1))
    _ax.add_collection3d(mesh)
    ###### Don't remove this till I get where is the problem!!!########
    _ax.scatter(points[:,0],points[:,1],points[:,2], s=0.0001, marker='o',
               c='k', cmap='turbo')
    ###################################################################
    _ax.relim()
    return mesh
