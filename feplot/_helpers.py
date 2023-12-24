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

import os

def icon_file(filename):
    icon_file = os.path.dirname(os.path.realpath(__file__)) 
    icon_file += f"\\icons\\{filename}.png"
    return icon_file
        
def update_mesh(mesh, du):
    """Update mesh points coordinates"""
    mesh.points += du
    return mesh

def update_menu(parent):
    """update main menu"""
    _file, _view, _tools = parent.main_menu.actions()
    parent.main_menu.removeAction(_view)
    parent.main_menu.removeAction(_tools)
    _file_menu = _file.menu()
    # _view_menu = _view.menu()
    # _tools_menu = _tools.menu()
    _file_menu.removeAction(_file_menu.actions()[1])
    # for _action in _view_menu.actions():
    #     _view_menu.removeAction(_action)
    # for _action in _tools_menu.actions():
    #     _tools_menu.removeAction(_action)
