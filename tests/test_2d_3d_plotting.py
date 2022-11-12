import felupe as fem
import numpy as np

from feplot.pylab import Plotter


def test_2d():
    #2D plot
    #Get some data from FElupe
    m1 = fem.Rectangle(b=(10,10), n=20) #Create mesh
    r1 = fem.RegionQuad(m1) #Create region
    f1 = fem.FieldsMixed(r1, n=1) #Create field
    mat1 = fem.NeoHooke(mu=1, bulk=1) #Create material
    s1 = fem.SolidBody(mat1, f1) #Create solidbody
    bounds, _ = fem.dof.uniaxial(f1,right=10, clamped=True) #Set boundaries conditions
    move = fem.math.linsteps([0,15],5) #Create move steps
    ramp = {bounds['move']:move} # Create ramp
    step = fem.Step([s1], ramp, bounds) #Create step
    job = fem.Job([step]) #Create job
    job.evaluate(verbose=False) #Run job

    #Plot results
    pl = Plotter()
    pl.plot_displacement(f1, label='U$_1$', component=0)

def test_3d():
    #3D plot
    #Get some data from FElupe
    m1 = fem.Cube(b=(10,10,10), n=10) #Create mesh
    r1 = fem.RegionHexahedron(m1) #Create region
    f1 = fem.FieldsMixed(r1, n=1) #Create field
    mat1 = fem.NeoHooke(mu=1, bulk=1) #Create material
    s1 = fem.SolidBody(mat1, f1) #Create solidbody
    bounds, _ = fem.dof.uniaxial(f1,right=10, clamped=True) #Set boundaries conditions
    move = fem.math.linsteps([0,15],5) #Create move steps
    ramp = {bounds['move']:move} # Create ramp
    step = fem.Step([s1], ramp, bounds) #Create step
    job = fem.Job([step]) #Create job
    job.evaluate(verbose=False) #Run job

    #Plot results
    pl = Plotter()
    pl.plot_displacement(f1, label='U$_1$', component=0)

def main():
    test_2d()
    test_3d()

if __name__=='__main__':
    main()

