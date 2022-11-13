
import felupe as fem
from feplot.pylab import Plotter
from feplot.tools import plot_model


def create_field_and_boundaries(region):
    field = fem.FieldsMixed(region, n=1)
    # Set BCs
    boundaries, _ = fem.dof.uniaxial(field, right=(
        region.mesh.points[:, 0].max()), clamped=True)
    return field, boundaries


def test():
    # Create regions
    r1 = fem.RegionQuad(fem.Rectangle(b=(25, 25), n=10))
    r2 = fem.RegionHexahedron(fem.Cube(b=(25, 25, 25), n=5))
    regions = [r1, r2]
    # Plot BCs & Loads
    for region in regions:
        field, boundaries = create_field_and_boundaries(region)
        plot_model(field, boundaries, show_load=True, show_bc=False)
        plot_model(field, boundaries, show_load=False, show_bc=True)


def main():
    test()


if __name__ == "__main__":
    main()
