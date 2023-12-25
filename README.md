<p align="center">
    <img width="400" height="378" src="https://github.com/ZAARAOUI999/feplot/assets/115699524/dc9fbd56-4061-43b7-a264-e9068591c3d4">
 </p>

 <h1 align="center">
     A visualization tool for FElupe
 </h1>
 
[![Generic badge](https://img.shields.io/badge/pypi-v0.1.13-<COLOR>.svg)](https://pypi.org/project/feplot/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10429725.svg)](https://doi.org/10.5281/zenodo.10429725) [![Downloads](https://static.pepy.tech/badge/feplot/month)](https://pepy.tech/project/feplot)
 
FEplot is based on the popular visualization library ```pyvista``` which is a comprehensive library for creating static, animated, and interactive visualizations in Python. The main aim of this package is to visualize [FElupe](https://github.com/adtzlr/felupe) results.

## Setup
To run this project, you can easily install it locally using pip:
```
pip install feplot
```
All is ready now, let's move on!

## How to Use

Starting with a quick example:

```python
import felupe as fem
from feplot import Plotter 

mesh = fem.Cube(n=6)
region = fem.RegionHexahedron(mesh)
field = fem.FieldContainer([fem.Field(region, dim=3)])

boundaries, loadcase = fem.dof.uniaxial(field, clamped=True)

umat = fem.OgdenRoxburgh(material=fem.NeoHooke(mu=1), r=3, m=1, beta=0)
solid = fem.SolidBodyNearlyIncompressible(umat, field, bulk=5000)

move = fem.math.linsteps([0, 1, 0, 1, 2, 1], num=5)
step = fem.Step(items=[solid], ramp={boundaries["move"]: move}, boundaries=boundaries)

job = fem.CharacteristicCurve(steps=[step], boundary=boundaries["move"])
job.evaluate(filename="result.xdmf")

p = Plotter()
p.read_xdmf("result.xdmf")

```

https://github.com/ZAARAOUI999/feplot/assets/115699524/19ac3be1-b829-44bd-82bc-20d0461452a8

# License
FEplot - A visualization tool for FElupe (C) 2023 Mohamed ZAARAOUI, Tunisia.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
