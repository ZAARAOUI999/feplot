
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

import copy

MESH_TYPE_MAPPING = {
    'MeshTet1': 'tetra_sk',
    'MeshTet2': 'tetra10',
    'MeshHex1': 'hexahedron_sk',
    'MeshHex2': 'hexahedron27',
    'MeshWedge1': 'wedge',
    'MeshTri1': 'triangle',
    'MeshTri2': 'triangle6',
    'MeshTri1DG': 'triangle',
    'MeshQuad1': 'quad',
    'MeshQuad2': 'quad9',
    'MeshLine1': 'line',
}

class SKMesh:
    """Get points, cells and cell_type from skfem mesh"""
    def __init__(self, mesh):
        super().__init__()
        self.points = mesh.doflocs.T
        self.cells = mesh.t.T
        type_ = f'{type(mesh)}'
        self.cell_type = MESH_TYPE_MAPPING[type_[type_.rindex('.')+1:type_.rindex('\'')]]
    
    def copy(self):
        """Return a copy of the mesh data"""
        return copy.deepcopy(self)
