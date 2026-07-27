"""Port PCell: bidirectional waveguide port marker.

Drawn on the PinRec layer (997/0) as two overlapping 1 um long paths
centered at the origin, spanning from x=-0.5 to x=0.5:
    - one path with the waveguide core width (default 15 um)
    - one path with the total waveguide width, core + 2*spacing
      (default spacing 7.5 um)

A bow tie made of two triangles meeting at the origin marks the port's
propagation axis (the port is bidirectional) and leaves a polygon vertex
at (0, 0) for snapping.
"""

import pya


class Port(pya.PCellDeclarationHelper):

    def __init__(self):
        super().__init__()
        self.set_parameters()

    def display_text_impl(self):
        return f"Port(w={self.wg_width:.1f}, gap={self.wg_gap:.1f})"

    def coerce_parameters_impl(self):
        self.wg_width = max(0.0, float(self.wg_width))
        self.wg_gap = max(0.0, float(self.wg_gap))
        self.marker_width = max(0.0, float(self.marker_width))

    def set_parameters(self):
        self.param("port_layer", self.TypeLayer, "Port layer",
                   default=pya.LayerInfo(997, 0))
        self.param("wg_width", self.TypeDouble,
                   "Waveguide core width [um]", default=15.0)
        self.param("wg_gap", self.TypeDouble,
                   "Waveguide gap, core to ground [um]", default=7.5)
        self.param("marker_width", self.TypeDouble,
                   "Bow-tie triangle base width [um]", default=2.0,
                    hidden = True)

    def produce_impl(self):
        p0 = pya.DPoint(-0.5, 0.0)
        p1 = pya.DPoint(0.5, 0.0)
        total_width = self.wg_width + 2.0 * self.wg_gap

        # Two nested paths, kept as separate Path shapes (not merged into a
        # Region) so both widths remain recoverable from the saved layout.
        self.cell.shapes(self.port_layer).insert(pya.DPath([p0, p1], self.wg_width))
        self.cell.shapes(self.port_layer).insert(pya.DPath([p0, p1], total_width))

        for tri in self._bowtie():
            self.cell.shapes(self.port_layer).insert(tri)

    def _bowtie(self):
        """Two triangles meeting at the origin: marks the port's direction
        (both ways, since the port is bidirectional) and gives a polygon
        vertex at (0, 0) for snapping."""
        l = 0.5
        w = self.marker_width / 2.0

        left = pya.DPolygon([
            pya.DPoint(-l, w),
            pya.DPoint(0.0, 0.0),
            pya.DPoint(-l, -w),
        ])
        right = pya.DPolygon([
            pya.DPoint(l, w),
            pya.DPoint(0.0, 0.0),
            pya.DPoint(l, -w),
        ])
        return [left, right]


# Local test block.
if __name__ == "__main__":
    from qfoundry.scripts.library import reload_library
    from qfoundry.utils import test_pcell

    reload_library()

    test_pcell(Port, {}, pya.Trans(pya.Trans.R0, 0, 0))
