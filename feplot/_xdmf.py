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

import numpy as np
from meshio import Mesh
from meshio.xdmf import TimeSeriesReader
from xml.etree import ElementTree as ET


class XDMFReader(TimeSeriesReader):
    """TimeSeriesReader wrapper class"""

    def __init__(self, filename):
        super().__init__(filename)

    def get_mesh(self):
        """Return meshio mesh"""
        return Mesh(*self .read_points_cells())

    def get_scalars_info(self):
        """Get informations about scalars"""
        _, point_data, cell_data = self.read_data(0)
        def _size(v): return np.product(np.array(v.shape)[1:])
        return dict(point_data_scalars=list(point_data.keys()),
                    point_data_sizes=[_size(v) for v in point_data.values()],
                    cell_data_scalars=list(cell_data.keys()),
                    cell_data_sizes=[_size(v[0]) for v in cell_data.values()])

    def get_steps(self):
        """Get time steps"""
        _tree = ET.parse(self.filename)
        _root = _tree.getroot()
        _steps = _root.findall('.//Time')
        step_values = [_s.get('Value') for _s in _steps]
        return step_values

