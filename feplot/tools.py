
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
import matplotlib.path as mpath

from scipy.spatial import ConvexHull as conv
from matplotlib import collections
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


hex_mask = np.array([[0, 1, 2, 3], [0, 1, 5, 4],
                     [1, 2, 6, 5], [2, 3, 7, 6],
                     [0, 3, 7, 4], [4, 5, 6, 7]])

hex_mask_sk = np.array([[7, 4, 2, 6], [4, 1, 0, 2],
                        [1, 5, 3, 0], [5, 7, 6, 3],
                        [7, 4, 1, 5], [6, 2, 0, 3]])

tetra_mask = np.array([[0, 1, 2], [0, 2, 3],
                      [0, 3, 1], [1, 2, 3]])

tetra_mask_sk = np.array([[1, 2, 3], [0, 2, 3],
                          [0, 1, 3], [0, 1, 2]])

tri_mask = np.array([0, 1, 2])

tri6_mask = np.array([0, 1, 2, 3, 4, 5])

quad_mask = np.array([0, 1, 2, 3])

quad9_mask = np.array([0, 1, 2, 3])

line_mask = np.array([0, 1])

MASK = {'line': line_mask,
        'triangle': tri_mask,
        'triangle6': tri6_mask,
        'quad': quad_mask,
        'quad9': quad9_mask,
        'tetra': tetra_mask,
        'tetra_sk': tetra_mask_sk,
        'hexahedron': hex_mask,
        'hexahedron_sk': hex_mask_sk}


def line_plot(mesh, values=None, ax=None, cmap='coolwarm', linewidth=3, alpha=1.0):
    """ plot line gradient"""
    p = mesh.points

    values = np.asarray(values)
    if p.shape[1] == 1:
        p = np.column_stack([p, values.reshape(p.shape[0], -1)])
    segments = p[:, :2][mesh.cells]
    values = values.reshape(p.shape[0], -1).mean(1)[mesh.cells].mean(1)
    lc = collections.LineCollection(segments, array=values, cmap=cmap,
                                    linewidth=linewidth, alpha=alpha)
    ax.add_collection(lc)
    ax.set_aspect('equal')

    return lc


def surface_plot(mesh, values, _ax, **kwargs):
    """Plot a 2D mesh"""
    verts = mesh.points[mesh.cells[:, MASK[mesh.cell_type]]]
    _mesh = collections.PolyCollection(verts, edgecolors=kwargs.pop('c'),
                                       cmap='coolwarm', linewidths=.5)
    condition = verts.shape[0]*verts.shape[1] == values.shape[0]
    if condition:
        _mesh.set_array(values.reshape(-1, mesh.cells.shape[1]).mean(1))
    else:
        _mesh.set_array(values[mesh.cells[:, MASK[mesh.cell_type]]].mean(1))

    _ax.add_collection(_mesh)
    _ax.set_aspect('auto')
    _ax.autoscale()
    return _mesh


def volume_plot(mesh, values, _ax, update=True, **kwargs):
    """Plot a 3D mesh"""
    _m = mesh.copy()
    points = _m.points
    cells = _m.cells
    cell_type = _m.cell_type
    # Convert points array to cells points array
    points = points[cells]
    # Get cell type mask
    if cell_type in ['hexahedron', 'hexahedron_sk']:
        d = 4
    elif cell_type in ['tetra', 'tetra_sk']:
        d = 3
    # Get polygons
    polys = points[:, MASK[mesh.cell_type]].reshape(-1, d, 3)
    print(len(cells), values.shape, polys.shape)
    # Project values
    values = values[cells[:, MASK[mesh.cell_type]]].reshape(-1, d).mean(1)
    print(values.shape)
    # Create matplotlib mesh
    _mesh = Poly3DCollection(polys, linewidths=.5, edgecolor=kwargs.pop('c'),
                             closed=True, cmap='coolwarm', zsort='average',
                             facecolor='grey')
    _ax.add_collection3d(_mesh)

    if update:
        _mesh.set_array(values)
    _ax.set_xlim(mesh.points[:, 0].min(), mesh.points[:, 0].max())
    _ax.set_ylim(mesh.points[:, 1].min(), mesh.points[:, 1].max())
    _ax.set_zlim(mesh.points[:, 2].min(), mesh.points[:, 2].max())

    return _mesh


def plot_2d_boundary(_ax, points):
    """Plot mesh boundaries"""
    hull = conv(points)
    _x, _y = points[hull.vertices, 0], points[hull.vertices, 1]
    _x = np.append(_x, _x[0])
    _y = np.append(_y, _y[0])
    _ax.plot(_x, _y, c='k')
    _ax.set_aspect('equal')


def plot_3d_boundary(_ax, mesh, c='k'):
    """Plot mesh boundaries"""
    values = np.zeros(shape=mesh.points.shape)
    volume_plot(mesh, values, _ax, update=False, c=c)


def plot_model(field, bounds, show_load=True, show_bc=True, **kwds):
    """Plot model"""
    dim = field.region.mesh.points.shape[1]
    if dim == 2:
        _ax = plt.figure().add_subplot()
        plot_2d_model(_ax, field, bounds, show_load=show_load, show_bc=show_bc)
    elif dim == 3:
        _ax = plt.figure().add_subplot(projection="3d")
        plot_3d_model(_ax, field, bounds, show_load=show_load, show_bc=show_bc)
    _ax.grid(False)


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
