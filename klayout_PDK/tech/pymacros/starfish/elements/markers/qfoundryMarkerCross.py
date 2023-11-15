
# Enter your Python code here

from kqcircuits.elements.markers.marker import Marker
from kqcircuits.pya_resolver import pya
from kqcircuits.util.parameters import Param, pdt
from kqcircuits.elements.element import Element
from kqcircuits.defaults import default_marker_type

class QfoundryMarkerCross(Marker):
    """The PCell declaration for the Standard Marker.
    """
    
    # Overriding some parameters os thta they dont get displayed in the PCell
    a = Param(pdt.TypeDouble, "Width of center conductor", 10, unit="μm", hidden=True)
    b = Param(pdt.TypeDouble, "Width of gap", 6, unit="μm", hidden=True)
    n = Param(pdt.TypeInt, "Number of points on turns", 64, hidden=True)
    r = Param(pdt.TypeDouble, "Turn radius", 100, unit="μm", hidden=True)
    margin = Param(pdt.TypeDouble, "Margin of the protection layer", 5, unit="μm", hidden=True)
    face_ids = Param(pdt.TypeList, "Chip face IDs list", ["1t1", "2b1", "1b1", "2t1"], hidden=True)
    protect_opposite_face = Param(pdt.TypeBoolean, "Add opposite face protection too", False,hidden=True)
    
    positive = Param(pdt.TypeBoolean, "Marker for positive lithography", default=False,hidden=False)
    diagonal_squares = Param(pdt.TypeInt, "Number of diagonal squares in the marker", 0)
    
    def build(self):
        self.produce_geometry()
    
    
    
       
    def produce_geometry(self):
        """Produce common marker geometry."""

        layer_gap = self.get_layer("base_metal_gap_wo_grid")
        layer_pads = self.get_layer("airbridge_pads")
        layer_flyover = self.get_layer("airbridge_flyover")
        layer_gap_for_ebl = self.get_layer("base_metal_gap_for_EBL")
        layer_protection = self.get_layer("ground_grid_avoidance")

        def insert_to_main_layers(shape):
            self.cell.shapes(layer_gap).insert(shape)
            self.cell.shapes(layer_gap_for_ebl).insert(shape)
            if not self.window:
                self.cell.shapes(layer_flyover).insert(shape)
        
        # protection for the box
        protection_box = pya.DBox(
            pya.DPoint(220, 220),
            pya.DPoint(-220, -220)
        )
        self.cell.shapes(layer_protection).insert(protection_box)

        # make corners
        corner = pya.DPolygon([
            pya.DPoint(100, 100),
            pya.DPoint(10, 100),
            pya.DPoint(10, 80),
            pya.DPoint(80, 80),
            pya.DPoint(80, 10),
            pya.DPoint(100, 10),
        ])
        inner_corners = [pya.DTrans(rot) * corner for rot in [0, 1, 2, 3]]
        outer_corners = [pya.DCplxTrans(2, rot * 90., False, pya.DVector()) * corner for rot in [0, 1, 2, 3]]
        corners = pya.Region([s.to_itype(self.layout.dbu) for s in inner_corners + outer_corners])
        
        self.inv_corners = pya.Region([protection_box.to_itype(self.layout.dbu)])
        self.inv_corners -= corners
        self.cell.shapes(layer_pads).insert(self.inv_corners - pya.Region(sqr_uni.to_itype(self.layout.dbu)))
       
       
        
       
       
        
        if not self.positive:
          area = pya.DBox(
            pya.DPoint(240, 240),
            pya.DPoint(-240, -240)
          )
          sqr_uni = pya.DBox(
              pya.DPoint(10, 10),
              pya.DPoint(-10, -10),
          )
          ncorners = pya.Region(area).merged()-corners.merged()
          insert_to_main_layers(ncorners)
        else:
          insert_to_main_layers(corners)
          # center box
          sqr_uni = pya.DBox(
              pya.DPoint(10, 10),
              pya.DPoint(-10, -10),
          )
          insert_to_main_layers(sqr_uni)

        

        # window for airbridge flyover layer
        aflw = pya.DPolygon([
            pya.DPoint(800, 800),
            pya.DPoint(800, 10),
            pya.DPoint(80, 10),
            pya.DPoint(80, 2),
            pya.DPoint(2, 2),
            pya.DPoint(2, 80),
            pya.DPoint(10, 80),
            pya.DPoint(10, 800)
        ])
        if self.window:
            for alpha in [0, 1, 2, 3]:
                self.cell.shapes(layer_flyover).insert(pya.DTrans(alpha) * aflw)

        # marker diagonal
        sqr = pya.DBox(
            pya.DPoint(10, 10),
            pya.DPoint(2, 2),
        )
        self.diagonals = pya.Region()
        for i in range(5, 5 + self.diagonal_squares):
            ds = pya.DCplxTrans(3, 0, False, pya.DVector(50 * i - 3 * 6, 50 * i - 3 * 6)) * sqr
            insert_to_main_layers(ds)
            self.cell.shapes(layer_pads).insert(ds)
            self.diagonals += ds.to_itype(self.layout.dbu)
            self.cell.shapes(layer_protection).insert(
                pya.DCplxTrans(20, 0, False, pya.DVector(50 * i - 20 * 6, 50 * i - 20 * 6)) * sqr)
