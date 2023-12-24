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
