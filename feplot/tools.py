
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
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from scipy.spatial import Delaunay, distance, ConvexHull as conv
from matplotlib import collections
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def quatplot(_u, _v, cells, _ax, **kwargs):
    """Plot a 2D mesh"""
    _uv = np.c_[_u, _v]
    verts = _uv[cells]
    mesh = collections.PolyCollection(verts, **kwargs)
    _ax.add_collection(mesh)
    _ax.autoscale()


def ratio(p):

    p1, p2, p3 = p
    a = distance.euclidean(p1, p2)
    b = distance.euclidean(p2, p3)
    c = distance.euclidean(p3, p1)
    s = np.sum([a, b, c])
    ri = np.sqrt((s-a)*(s-b)*(s-c)/s)
    ro = (a*b*c)/(np.sqrt((a+b-c)*(a-b+c)*(-a+b+c)*(a+b+c)))
    ar = 2 * ro / ri
    return abs(ar)


def polyplot(points, cells, values, _ax, update=True, method=2, **kwargs):
    """Plot a 3D mesh"""
    polys = []
    new_values = []
    if method == 2:
        #########################################################################
        new_points = [points[np.sort(cell)] for cell in cells]
        triangs = [Delaunay(points) for points in new_points]
        hulls = [triang.convex_hull for triang in triangs]
        polys = [list(points[hull]) for points, hull in zip(new_points, hulls)]
        new_values = [list(values[np.sort(cell)][hull])
                      for cell, hull in zip(cells, hulls)]  # [mask]
        #########################################################################
        polys = np.array(polys).reshape(-1, 3, 3)
        new_values = np.array(new_values).reshape(-1, 3).mean(1)

    else:
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
    if update:
        new_values = np.array(new_values)
        if method == 1:
            new_values = new_values.mean(1)
        mesh.set_array(new_values)
    _ax.add_collection3d(mesh)
    ###### Don't remove this till I get where is the problem!!!########
    _ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=0.0001, marker='o',
                c='k', cmap='turbo')
    ###################################################################
    _ax.relim()
    return mesh


def plot_2d_boundary(_ax, points):
    """Plot mesh boundaries"""
    hull = conv(points)
    _x, _y = points[hull.vertices, 0], points[hull.vertices, 1]
    _x = np.append(_x, _x[0])
    _y = np.append(_y, _y[0])
    _ax.plot(_x, _y, c='k')
    _ax.set_aspect('equal')


def plot_3d_boundary(_ax, mesh):
    """Plot mesh boundaries"""
    points = mesh.points
    cells = mesh.cells
    values = np.zeros(shape=points.shape)
    polyplot(points, cells, values, _ax, update=False, c='none')


def plot_model(field, bounds, show_load=True, show_bc=True, **kwds):
    """Plot model"""
    dim = field.region.mesh.points.shape[1]
    if dim == 2:
        _ax = plt.figure().add_subplot()
        plot_2d_model(_ax, field, bounds, show_load=show_load, show_bc=show_bc)
    elif dim == 3:
        _ax = plt.figure().add_subplot(projection="3d")
        plot_3d_model(_ax, field, bounds, show_load=show_load, show_bc=show_bc)


def plot_2d_model(_ax, field, bounds, show_load, show_bc):
    """Plot 2D model"""
    mesh = field.region.mesh.copy()
    points = mesh.points
    plot_2d_boundary(_ax, points)
    axis = ['x', 'y', 'z']
    selected_field = field.fields[0]
    for bound in bounds:
        field = bounds[bound].field
        if field == selected_field:
            bc_mask = bounds[bound].mask
            bc_points = bounds[bound].points
            bc_skip = list(bounds[bound].skip)
            bc_value = bounds[bound].value

            for i, skip in enumerate(bc_skip):
                cent = mesh.points[bc_points]
                if cent.shape[1] == 2:
                    cent = np.column_stack([cent, np.zeros(cent.shape[0])])
                direction = np.zeros(shape=cent.shape, like=cent)
                if skip == 1:
                    if np.array([bc_value]).ravel().all() == 0:
                        if show_bc:
                            direction[..., i] = abs(
                                np.max(mesh.points[..., i])-np.min(mesh.points[..., i]))/10
                            _ax.quiver(cent[:, 0], cent[:, 1], direction[:, 0],
                                       direction[:, 1], color='blue', label=bound+'[skip_%s=1]' % (axis[i]))
                    else:
                        if show_load:
                            direction[..., i] = abs(
                                np.max(mesh.points[..., i])-np.min(mesh.points[..., i]))/10
                            _ax.quiver(cent[:, 0], cent[:, 1], direction[:, 0], direction[:, 1],
                                       color='green', label=bound+'[skip_%s=1]' % (axis[i]))
                elif skip == 0:
                    if np.array([bc_value]).ravel().all() == 0:
                        if show_bc:
                            direction[..., i] = abs(
                                np.max(mesh.points[..., i])-np.min(mesh.points[..., i]))/10
                            _ax.quiver(cent[:, 0], cent[:, 1], direction[:, 0], direction[:,
                                       1], color='red', label=bound+'[skip_%s=0]' % (axis[i]))
                    else:
                        if show_load:
                            direction[..., i] = abs(
                                np.max(mesh.points[..., i])-np.min(mesh.points[..., i]))/10
                            _ax.quiver(cent[:, 0], cent[:, 1], direction[:, 0], direction[:, 1],
                                       color='orange', label=bound+'[skip_%s=0]' % (axis[i]))
    add_model_legend(show_load, show_bc)


def plot_3d_model(ax, field, bounds, show_load, show_bc):
    """Plot 3D model"""
    mesh = field.region.mesh.copy()
    points = mesh.points
    plot_3d_boundary(ax, mesh)
    axis = ['x', 'y', 'z']
    selected_field = field.fields[0]
    for bound in bounds:
        field = bounds[bound].field
        if field == selected_field:
            bc_mask = bounds[bound].mask
            bc_points = bounds[bound].points
            bc_skip = list(bounds[bound].skip)
            bc_value = bounds[bound].value

            for i, skip in enumerate(bc_skip):
                cent = mesh.points[bc_points]
                direction = np.zeros(shape=cent.shape, like=cent)
                if skip == 1:
                    if np.array([bc_value]).ravel().all() == 0:
                        if show_bc:
                            direction[..., i] = abs(
                                np.max(mesh.points[..., i])-np.min(mesh.points[..., i]))/10
                            plt.gca().quiver(cent[:, 0], cent[:, 1], cent[:, 2], direction[:, 0], direction[:,
                                                                                                            1], direction[:, 2], color='blue', label=bound+'[skip_%s=1]' % (axis[i]))
                    else:
                        if show_load:
                            direction[..., i] = abs(
                                np.max(mesh.points[..., i])-np.min(mesh.points[..., i]))/10
                            plt.quiver(cent[:, 0], cent[:, 1], cent[:, 2], direction[:, 0], direction[:, 1],
                                       direction[:, 2], color='green', label=bound+'[skip_%s=1]' % (axis[i]))
                elif skip == 0:
                    if np.array([bc_value]).ravel().all() == 0:
                        if show_bc:
                            direction[..., i] = abs(
                                np.max(mesh.points[..., i])-np.min(mesh.points[..., i]))/10
                            plt.quiver(cent[:, 0], cent[:, 1], cent[:, 2], direction[:, 0], direction[:, 1],
                                       direction[:, 2], color='red', label=bound+'[skip_%s=0]' % (axis[i]))
                    else:
                        if show_load:
                            direction[..., i] = abs(
                                np.max(mesh.points[..., i])-np.min(mesh.points[..., i]))/10
                            plt.quiver(cent[:, 0], cent[:, 1], cent[:, 2], direction[:, 0], direction[:, 1],
                                       direction[:, 2], color='orange', label=bound+'[skip_%s=0]' % (axis[i]))
    add_model_legend(show_load, show_bc)


def add_model_legend(show_load=True, show_bc=True):
    """Add model plot's legend"""
    patches = []
    if show_bc:
        patches.append(mpatches.Patch(color='red', label='BC [skip=0]'))
        patches.append(mpatches.Patch(color='blue', label='BC [skip=1]'))
    if show_load:
        patches.append(mpatches.Patch(color='orange', label='Load [skip=0]'))
        patches.append(mpatches.Patch(color='green', label='Load [skip=1]'))
    plt.gca().legend(handles=patches, loc='center left',
                     bbox_to_anchor=(1.04, 0.5), borderaxespad=2)
