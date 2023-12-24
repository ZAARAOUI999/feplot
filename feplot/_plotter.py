####################### - بــسم الله الرحمــان الرحيــم - #####################

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

import re
import pyvista as pv
import numpy as np
import vtk
from pyvista.plotting.renderer import make_legend_face, map_loc_to_pos
from pyvista.plotting.colors import Color
from pyvistaqt import BackgroundPlotter
from qtpy.QtWidgets import (QComboBox, QLabel, QPushButton, QSlider)
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QIcon

from ._helpers import *
from ._xdmf import XDMFReader

pv.set_plot_theme("document")


class Plotter(BackgroundPlotter):
    """VTK Plotter class"""

    def __init__(self, **kwargs):
        super().__init__(title='FEPlot', toolbar=False, editor=False,
                         **kwargs)
        self._mesh = None
        self._undeformed_mesh = None
        self._args = None
        self._mesh_actor = None
        self._legend_actor = None
        self.toolbar = None
        self.process = None
        self.substep_text = None
        self.current_substep = 0
        self.data_size = dict()
        self.steps = list()
        self.scalar_bar_args = {'title': 'U Magnitude\n', 'n_labels': 8,
                                'bold': False, 'title_font_size': 14,
                                'label_font_size': 12, 'font_family': 'courier',
                                'position_x': 0.05, 'height': 0.45, 'width': 0.07,
                                'position_y': 0.5, 'vertical': True,
                                'interactive': False}
        self._kwargs = dict(style='surface', scalar_bar_args=self.scalar_bar_args,
                            n_colors=128, cmap='turbo', show_edges=True, name='Mesh')
        self.legend_kwargs = dict(size=(0.1, 0.1), bcolor='w', loc='upper right',
                                  face=None, font_family='courier')
        
        self.add_axes()
        self.add_key_events()
        self.configure_menu()
        self.add_toolbar()
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.animate_frames)
        self.app_window.setWindowIcon(QIcon(icon_file('feplot')))
        self.app.setStyle('Fusion')
        
    def configure_menu(self):
        """Configure the main menu"""
        update_menu(self)

    def add_toolbar(self):
        """Add a toolbar"""
        self.toolbar = self.app_window.addToolBar('datasets')
        self.scalar_combo = QComboBox(self.app_window)
        self.component_combo = QComboBox(self.app_window)
        self.component_combo.setFixedWidth(63)
        _widgets = [QLabel("Scalar: "), self.scalar_combo,
                    QLabel("Component: "), self.component_combo]

        i = 0
        for _w in _widgets:
            self.toolbar.addWidget(_w)
            i += 1
            if i == 2:
                self.toolbar.addSeparator()

        self.scalar_combo.currentTextChanged.connect(self.update_components)
        self.component_combo.currentTextChanged.connect(self.update_data)
        self.add_slider()
        self.add_animation_tools()

    def add_slider(self):
        """Add time slider widget"""
        self.sl = QSlider(Qt.Horizontal)
        self.sl.setMinimum(0)
        self.sl.setMaximum(0)
        self.sl.setValue(0)
        self.sl.setSingleStep(1)
        self.sl.setFixedWidth(200)
        self.sl.setTickPosition(QSlider.TickPosition.NoTicks)
        self.sl.setTickInterval(5)
        self.sl.valueChanged.connect(self.load_time)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(QLabel('Substep: '))
        self.toolbar.addWidget(self.sl)

    def add_animation_tools(self):
        """Add animation control buttons"""
        self.btn_play = QPushButton(QIcon(icon_file('play')), '')
        self.btn_stop = QPushButton(QIcon(icon_file('stop')), '')
        self.btn_play.clicked.connect(self.animate)
        self.btn_stop.clicked.connect(self.stop_animation)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.btn_play)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.btn_stop)

    def add_key_events(self):
        """Add key events"""
        self.add_key_event('x', lambda: self.view_yz())
        self.add_key_event('y', lambda: self.view_xz())
        self.add_key_event('z', lambda: self.view_xy())
        self.add_key_event('h', lambda: self.toggle_widgets())
        self.add_key_event('m', lambda: self.show_edges())
        
    #pyvista modified add_legend function
    def add_legend(
        self,
        labels=None,
        bcolor=(0.5, 0.5, 0.5),
        border=False,
        size=(0.2, 0.2),
        name=None,
        loc='upper right',
        face='triangle',
        font_family='courier',
    ):
        """Add a legend to render window."""

        self._legend = vtk.vtkLegendBoxActor()
        self._legend.SetNumberOfEntries(len(labels))
        legend_face = make_legend_face(face)
        for i, (text, color) in enumerate(labels):
            self._legend.SetEntry(i, legend_face, text, Color(color).float_rgb)
        if loc is not None:
            x, y, size = map_loc_to_pos(loc, size, border=0.02)
            self._legend.SetPosition(x, y)
            self._legend.SetPosition2(size[0], size[1])
        self._legend.SetUseBackground(True)
        self._legend.SetBackgroundColor(Color(bcolor).float_rgb)
        self._legend.SetBorder(border)
        legend_text = self._legend.GetEntryTextProperty()
        legend_text.SetFontFamily(
            pv.tools.parse_font_family('courier'))
        self.add_actor(self._legend, reset_camera=False,
                       name=name, pickable=False)
        return self._legend

    def animate(self):
        """Start the animation"""
        self.btn_play.setDisabled(True)
        self.btn_stop.setDisabled(False)
        self.timer.start()

    def animate_frames(self):
        """play next animation frame"""
        if self.current_substep < len(self.steps):
            self.current_substep += 1
        else:
            self.current_substep = 0
        self.sl.setValue(self.current_substep)

    def stop_animation(self):
        """Stop the animation"""
        self.btn_stop.setDisabled(True)
        self.btn_play.setDisabled(False)
        self.timer.stop()

    def set_anti_aliasing(self, stats):
        """Enable/Disable anti-aliasing"""
        if stats:
            self.renderer.enable_anti_aliasing
        else:
            self.renderer.disable_anti_aliasing
        self.update()

    def read_mesh(self, mesh, data, *args, **kwargs):
        """Read mesh"""
        self._mesh = mesh
        self._undeformed_mesh = mesh
        # self.add_mesh(self._undeformed_mesh, opacity=0.3, name="undeformed_mesh")
        self._args = args
        self._kwargs.update(kwargs)
        for scalar, value in data.items():
            if scalar == 'Displacement':
                self._mesh = update_mesh(self._mesh, value)
        self._mesh_actor = self.add_mesh(
            self._mesh, *self._args, **self._kwargs)

    def read_xdmf(self, filename: str):
        """Read XDMF file"""
        self.reader = XDMFReader(filename)
        self.mesh = self.reader.get_mesh()
        self.steps = self.reader.get_steps()
        self.check_scalars(self.reader)
        self.update_components()
        self.update_slider(len(self.steps)-1)
        self._kwargs['interpolate_before_map'] = True
        self.load_time(0)

    def load_time(self, k):
        """ Load solution at value specified using the slider """
        if self.component_combo.currentText() != '':

            self.current_substep = k = int(k)
            t, point_data, cell_data = self.reader.read_data(k)
            scalar = self.scalar_combo.currentText()
            title = self.component_combo.currentText() + '\n '
            if scalar in point_data.keys():
                scalars = point_data[scalar]
                self._kwargs['preference'] = 'point'
            elif scalar in cell_data.keys():
                scalars = cell_data[scalar][0]
                self._kwargs['preference'] = 'cell'
            self._kwargs['scalars'] = scalars
            self.scalar_bar_args['title'] = title
            self._kwargs['scalar_bar_args'] = self.scalar_bar_args
            data = {'Displacement': point_data['Displacement']}
            if self._mesh_actor is None:
                self.read_mesh(self.mesh, data, **self._kwargs)
                self.update_view()
                self._legend_actor = self.add_legend([('Substep: %d' % int(k), 'k')],
                                                     **self.legend_kwargs)
            else:
                self.remove_legend()
                self._legend_actor = self.add_legend([('Substep: %d' % int(k), 'k')],
                                                     **self.legend_kwargs)
                _n = scalars.shape[0]
                _c = self.component_combo.currentIndex()
                data = scalars.reshape(_n, -1)[..., _c]
                mapper = self._mesh_actor.mapper
                mesh = mapper.dataset
                
                #force updating scalar map mode
                mapper.scalar_map_mode = self._kwargs['preference']
                
                if self._kwargs['preference'] == 'point':
                    mesh.point_data[scalar] = data
                else:
                    # mapper.scalar_map_mode = 'point'
                    # mapper.color_mode = 'map'
                    mesh.cell_data[scalar] = data
                    # c2p = vtk.vtkCellDataToPointData()
                    # c2p.SetInputData(mesh)
                    # c2p.Update()
                    # mesh = pv.UnstructuredGrid(c2p.GetOutput())
                mesh.set_active_scalars(scalar)
                old_title = list(
                    self._scalar_bars._scalar_bar_actors.keys())[0]
                self._scalar_bars._scalar_bar_actors[old_title].SetTitle(title)
                self.update_scalar_bar_range([data.min(), data.max()])
                mesh.points = self._mesh.points + point_data['Displacement']
                self.set_focus(mesh.center)
                self.update_view()

    def check_scalars(self, reader):
        """Update scalars and their data sizes"""
        self.scalar_combo.clear()
        (point_data_scalars, point_data_sizes, cell_data_scalars,
         cell_data_sizes) = self.reader.get_scalars_info().values()
        self.scalar_combo.addItems(point_data_scalars)
        self.data_size = dict(zip(point_data_scalars, point_data_sizes))
        self.scalar_combo.addItems(cell_data_scalars)
        self.data_size.update(dict(zip(cell_data_scalars, cell_data_sizes)))

    def update_components(self):
        """Update current scalar components"""
        if len(self.data_size) != 0:
            self.component_combo.clear()
            scalar = self.scalar_combo.currentText()
            _nc = self.data_size[scalar]
            self.component_combo.addItems(
                [re.sub('[^A-Z]', '', scalar) + f'{_i}' for _i in range(_nc)])

    def update_data(self):
        """Update current data"""
        if self.reader is not None:
            self.load_time(self.current_substep)

    def update_slider(self, max_value: int):
        self.sl.setMaximum(max_value)

    def show_edges(self, *args, **kwargs):
        """Show mesh edges"""
        prop = self._mesh_actor.prop
        prop.show_edges = not prop.show_edges
        self.render()

    def update_view(self):
        """Update view"""
        self.camera.view_angle = 45.0
        self.render()
