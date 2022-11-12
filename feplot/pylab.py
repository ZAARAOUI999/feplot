
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

import felupe as fem

import matplotlib.pyplot as plt
from matplotlib import rcParams, tri, ticker
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.mplot3d.axes3d import Axes3D

from .tools import quatplot, polyplot

rcParams['pgf.texsystem'] = 'pdflatex'
rcParams.update({'font.family': 'serif', 'font.size': 10,
                 'axes.labelsize': 12, 'axes.titlesize': 13, 'figure.titlesize': 13})


class Plotter():
    """
    A simple plot helper for FElupe library.
    """

    def __init__(self):
        super().__init__()
        self.show_mesh = True
        self.show_min_max = True
        self.deformed = True
        self.n_ticks = 8
        self.grid = False
        self._ax = None
        self.data = dict()

    def plot(self, field, values, component: int = 0,
             update: bool = True, **kwds):
        """Plot results"""
        axes = ['x', 'y', 'z']
        args = ['deformed', 'show_mesh', 'show_min_max', 'grid', 'n_ticks']
        for arg in args:
            if arg in kwds:
                setattr(self, arg, kwds[arg])
        if 'label' in kwds:
            label = kwds.get('label')
        else:
            label = '?'
        if update:
            self.data['region'] = field.region
            self.data['mesh'] = field.region.mesh.copy()
            self.data['points'] = self.data.get('mesh').points
            self.data['cells'] = self.data.get('mesh').cells

        # get fields dimension
        dim = self.data.get('points').shape[-1]

        # get displacements
        _du = fem.project(field.fields[0].extract(
            grad=False), self.data.get('region'))
        if self.deformed:
            # add dispalacements to the reference points coordinates
            self.data.get('points')[:, :dim] += _du[:, :dim]

        if dim == 3:
            values, fig, _ax = self.plot3d(self.data.get('points'), self.data.get('cells'),
                                           axes, values, component)
            self._ax = _ax
        else:
            values, fig, _ax = self.plot2d(self.data.get('points'), self.data.get('cells'),
                                           axes, values, component)
            self._ax = _ax
        self.colorbar(fig, _ax, label=label, span=[values.min(), values.max()])

    def plot2d(self, *args):
        """Plot 2D results"""
        points, cells, axes, values, component = args
        # make a 2d figure
        _ax = plt.figure().add_subplot()
        # setting plot labels
        _ax.set_xlabel(axes[0]+'$\\longrightarrow$')
        _ax.set_ylabel(axes[1]+'$\\longrightarrow$')
        # get specified component from the given data
        if component < 0:
            values = values.mean(-1)
        else:
            values = values[:, component]
        # Delaunay triangulation of all points.
        triang = tri.Triangulation(points[:, 0], points[:, 1])
        # remove unwanted triangles
        mask = tri.TriAnalyzer(triang).get_flat_tri_mask(
            min_circle_ratio=.1, rescale=False)
        triang.set_mask(mask)
        # plot interpolated data
        fig = _ax.tricontourf(triang, values, cmap='turbo', levels=128)
        if self.show_mesh:
            # plot mesh edges
            quatplot(points[:, 0], points[:, 1], cells,
                     _ax, color='k', facecolor='none')
        return values, fig, _ax

    def plot3d(self, *args):
        """Plot 3D results"""
        points, cells, axes, values, component = args
        # make a 3d figure
        _ax = plt.figure().add_subplot(projection='3d')
        # setting plot labels
        _ax.set_xlabel(axes[0]+'$\\longrightarrow$')
        _ax.set_ylabel(axes[1]+'$\\longrightarrow$')
        _ax.set_zlabel(axes[2]+'$\\longrightarrow$')
        # get specified component from the given data
        if component < 0:
            values = values.mean(-1)
        else:
            values = values[:, component]
        _c = 'none'
        if self.show_mesh:
            _c = 'k'
        fig = polyplot(points, cells, values, _ax, c=_c)
        return values, fig, _ax

    def plot_displacement(self, field, label: str = '', component: int = 0, **kwds):
        """Plot field displacements"""
        # update data
        self.data['region'] = field.region
        self.data['mesh'] = field.region.mesh.copy()
        self.data['points'] = self.data.get('mesh').points
        self.data['cells'] = self.data.get('mesh').cells
        # get displacements
        values = fem.project(field.fields[0].extract(
            grad=False), self.data.get('region'))
        self.plot(field, values, component, update=False, label=label, **kwds)

    def colorbar(self, fig, _ax, label: str, span: list, **kwds):
        """Add a colorbar"""
        args = ['grid', 'n_ticks']
        for arg in args:
            if arg in kwds:
                setattr(self, arg, kwds[arg])
        # set colorbar
        c_axis = inset_axes(_ax, width='5%', height='50%',
                            loc='center left', borderpad=-10)
        _c = plt.gcf().colorbar(fig, cax=c_axis, pad=1)
        _c.ax.yaxis.set_ticks_position('right')
        if self.grid:
            _c.ax.yaxis.grid(True, color='k')
        # set colorbar title
        if self.show_min_max:
            label += '\nmin: %.1e\nmax: %.1e\n' % (span[0], span[1])
        _c.ax.set_title(x=0, label=label, verticalalignment='top',
                        horizontalalignment='left', fontproperties={'size': 10})
        # set colorbar ticks
        tick_locator = ticker.MaxNLocator(nbins=self.n_ticks)
        _c.locator = tick_locator
        _c.update_ticks()

    def xy_view(self, _ax=None):
        """Set view orientation to XY"""
        if not _ax:
            axis = self._ax
        else:
            axis = _ax
        if isinstance(axis, Axes3D):
            axis.set_proj_type('ortho')  # set projection type to orthoganale
            axis.view_init(90, -90)  # xy view
            axis.set_zticks([])  # hide z-axis ticks

    def yz_view(self, _ax=None):
        """Set view orientation to YZ"""
        if not _ax:
            axis = self._ax
        else:
            axis = _ax
        if isinstance(axis, Axes3D):
            axis.set_proj_type('ortho')  # set projection type to orthoganale
            axis.view_init(0, 0)  # yz view
            axis.set_xticks([])  # hide x-axis ticks

    def xz_view(self, _ax=None):
        """Set view orientation to XZ"""
        if not _ax:
            axis = self._ax
        else:
            axis = _ax
        if isinstance(axis, Axes3D):
            axis.set_proj_type('ortho')  # set projection type to orthoganale
            axis.view_init(0, -90)  # xz view
            axis.set_yticks([])  # hide y-axis ticks

    def hide_grid(self, _x: bool = True, _y: bool = True, _z: bool = True):
        """Hide gridlines"""
        if isinstance(self._ax, Axes3D):
            axes = {'x': _x, 'y': _y, 'z': _z}
            for axis in axes.items():
                if axis[1]:
                    getattr(
                        self._ax, axis[0]+'axis').set_pane_color((1., 1., 1., 0.))
                    getattr(
                        self._ax, axis[0]+'axis')._axinfo['grid']['color'] = (1., 1., 1., 0.)
