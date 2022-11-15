
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


def arrow_3d(_ax, length=1, width=0.05, head=0.2, headwidth=2,
             theta_x=0, theta_z=0, offset=(0, 0, 0), **kwargs):  # stackoverflow
    """Add 3D arrow"""
    _w = width
    _h = head
    _hw = headwidth
    theta_x = np.deg2rad(theta_x)
    theta_z = np.deg2rad(theta_z)

    _a = np.array([[0, 0], [_w, 0], [_w, (1-_h)*length],
                   [_hw*_w, (1-_h)*length], [0, length]])

    _r, theta = np.meshgrid(_a[:, 0], np.linspace(0, 2*np.pi, 30))
    _z = np.tile(_a[:, 1], _r.shape[0]).reshape(_r.shape)
    _x = _r*np.sin(theta)
    _y = _r*np.cos(theta)

    rot_x = np.array([[1, 0, 0], [0, np.cos(theta_x), -np.sin(theta_x)],
                      [0, np.sin(theta_x), np.cos(theta_x)]])
    rot_z = np.array([[np.cos(theta_z), -np.sin(theta_z), 0],
                      [np.sin(theta_z), np.cos(theta_z), 0], [0, 0, 1]])

    b_1 = np.dot(rot_x, np.c_[_x.flatten(), _y.flatten(), _z.flatten()].T)
    b_2 = np.dot(rot_z, b_1)
    b_2 = b_2.T+np.array(offset)
    _x = b_2[:, 0].reshape(_r.shape)
    _y = b_2[:, 1].reshape(_r.shape)
    _z = b_2[:, 2].reshape(_r.shape)
    _ax.plot_surface(_x, _y, _z, **kwargs)
