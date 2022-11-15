
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

from .tools import surface_plot, volume_plot
from .entities import arrow_3d
rcParams['pgf.texsystem'] = 'pdflatex'
rcParams.update({'font.family': 'serif', 'font.size': 10,
                 'axes.labelsize': 10, 'axes.titlesize': 10,
                 'figure.titlesize': 10})


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
        self.axes = None

    def plot(self, field, values, component: int = 0,
             update: bool = True, **kwds):
        """Plot results"""
        # Clear everything
        plt.clf()
        # Update Plotter attributes
        args = ['deformed', 'show_mesh',
                'show_min_max', 'grid', 'n_ticks', 'axes']
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
            values, fig, _ax = self.plot3d(
                self.data.get('mesh'), values, component)
            self._ax = _ax
        else:
            values, fig, _ax = self.plot2d(
                self.data.get('mesh'), values, component)
            self._ax = _ax
        self.colorbar(fig, _ax, label=label, span=[values.min(), values.max()])

    def plot2d(self, *args):
        """Plot 2D results"""
        mesh, values, component = args
        # make a 2d figure
        _ax = plt.figure().add_subplot()
        # setting plot labels
        _ax.set_xlabel('x')
        _ax.set_ylabel('y')
        # get specified component from the given data
        if values.ndim > 1:
            if component < 0:
                values = values.mean(-1)
            else:
                values = values[:, component]
        if self.show_mesh:
            # plot mesh edges
            c = 'k'
        else:
            c = 'none'
        fig = surface_plot(mesh, values, _ax, c='k')
        return values, fig, _ax

    def plot3d(self, *args):
        """Plot 3D results"""
        mesh, values, component = args
        # make a 3d figure
        _ax = plt.figure().add_subplot(projection='3d')
        # setting plot labels
        _ax.set_xlabel('x')
        _ax.set_ylabel('y')
        _ax.set_zlabel('z')
        # get specified component from the given data
        if values.ndim > 1:
            if component < 0:
                values = values.mean(-1)
            else:
                values = values[:, component]
        _c = 'none'
        if self.show_mesh:
            _c = 'k'
        fig = volume_plot(mesh, values, _ax, c=_c)
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
            angles = 90, -90
            axis.set_proj_type('ortho')  # set projection type to orthoganale
            axis.view_init(*angles)  # xy view
            if self.axes is not None:
                self.axes.view_init(*angles)
            axis.set_zticks([])  # hide z-axis ticks

    def yz_view(self, _ax=None):
        """Set view orientation to YZ"""
        if not _ax:
            axis = self._ax
        else:
            axis = _ax
        if isinstance(axis, Axes3D):
            angles = 0, 0
            axis.set_proj_type('ortho')  # set projection type to orthoganale
            axis.view_init(*angles)  # yz view
            if self.axes is not None:
                self.axes.view_init(*angles)
            axis.set_xticks([])  # hide x-axis ticks

    def xz_view(self, _ax=None):
        """Set view orientation to XZ"""
        if not _ax:
            axis = self._ax
        else:
            axis = _ax
        if isinstance(axis, Axes3D):
            angles = 0, -90
            axis.set_proj_type('ortho')  # set projection type to orthoganale
            axis.view_init(*angles)  # xz view
            if self.axes is not None:
                self.axes.view_init(*angles)
            axis.set_yticks([])  # hide y-axis ticks

    def hide_grid(self, _x: bool = True, _y: bool = True, _z: bool = True):
        """Hide gridlines"""
        if isinstance(self._ax, Axes3D):
            self._ax.set_axis_off()
        else:
            self._ax.set_axis_off()

    def show_ruler(self, _x: bool = True, _y: bool = True, _z: bool = True):
        """Show ruler"""
        axes = {'x': _x, 'y': _y, 'z': _z}
        self._ax.set_axis_on()
        self._ax.grid(False)
        if isinstance(self._ax, Axes3D):
            for axis in axes.items():
                getattr(self._ax, 'w_'+axis[0] +
                        'axis').set_pane_color((1, 1, 1, 0))
                if not axis[1]:
                    getattr(self._ax, 'set_'+axis[0]+'ticklabels')([])
                    getattr(self._ax, 'w_' +
                            axis[0]+'axis').line.set_color((1, 1, 1, 0))
                    getattr(self._ax, 'set_'+axis[0]+'ticks')([])
                    getattr(self._ax, 'set_'+axis[0]+'label')('')

        else:
            self._ax.set_axis_off()

    def add_axes(self):
        """Add axes orientation plot"""
        rect = [0, 0, 0.2, 0.2]
        if isinstance(self._ax, Axes3D):
            # Create axes to handel orientation plot
            ax_inset = plt.gcf().add_axes(rect, anchor='NW', projection='3d')
            ax_inset.set_axis_off()
            directions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            colors = ['crimson', 'green', 'blue']
            axes = ['x', 'y', 'z']
            kwargs = dict(clip_on=False)
            # Add 3D arrows
            arrow_3d(ax_inset, theta_x=90, theta_z=90,
                     color='crimson', **kwargs)  # x
            arrow_3d(ax_inset, theta_x=270, color='limegreen', **kwargs)  # y
            arrow_3d(ax_inset, color='blue', **kwargs)  # z
            # Add axes annotations
            for i, dir_ in enumerate(directions):
                ax_inset.text(*dir_, axes[i], 'x', color=colors[i])
            ax_inset.set_proj_type('ortho')
            ax_inset.set_box_aspect([.1, .1, .1])
            self.axes = ax_inset
