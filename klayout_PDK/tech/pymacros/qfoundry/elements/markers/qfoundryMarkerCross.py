
# Enter your Python code here

from kqcircuits.elements.markers.marker import Marker
from kqcircuits.pya_resolver import pya
from kqcircuits.util.parameters import Param, pdt
from kqcircuits.elements.element import Element
from kqcircuits.defaults import default_marker_type


Marker.marker_type_choices = [
    'Marker Standard',
    'Qfoundry Marker Cross'
]

class QfoundryMarkerCross(Marker):
    """The PCell declaration for the Standard Marker.
    """
    
    # Overriding some parameters so that they dont get displayed in the PCell
    a = Param(pdt.TypeDouble, "Width of center conductor", 10, unit="μm", hidden=True)
    b = Param(pdt.TypeDouble, "Width of gap", 6, unit="μm", hidden=True)
    n = Param(pdt.TypeInt, "Number of points on turns", 64, hidden=True)
    r = Param(pdt.TypeDouble, "Turn radius", 100, unit="μm", hidden=True)
    margin = Param(pdt.TypeDouble, "Margin of the protection layer", 20, unit="μm", hidden=True)
    face_ids = Param(pdt.TypeList, "Chip face IDs list", ["1t1", "2b1", "1b1", "2t1"], hidden=True)
    protect_opposite_face = Param(pdt.TypeBoolean, "Add opposite face protection too", False,hidden=True)
    
    positive = Param(pdt.TypeBoolean, "Marker for positive lithography", default=False,hidden=False)
    n_items = Param(pdt.TypeInt, "Number of markers (side)", default=2,hidden=False)
    
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
            pya.DPoint(50, 50),
            pya.DPoint(-50, -50)
        )
        self.cell.shapes(layer_protection).insert(protection_box)

        # make corners
        corner = pya.DPolygon([
            pya.DPoint(50, 50),
            pya.DPoint(25, 50),
            pya.DPoint(25, 40),
            pya.DPoint(40, 40),
            pya.DPoint(40, 25),
            pya.DPoint(50, 25),
        ])
        
        inner_corners = [pya.DCplxTrans(0.5, rot * 90., False, pya.DVector()) * corner for rot in [0, 1, 2, 3]]
        inner_box = pya.DBox(
            pya.DPoint(-15, -15),
            pya.DPoint(15, 15),
        )
        
        corner = pya.DPolygon([
            pya.DPoint(95, 95),
            pya.DPoint(25, 95),
            pya.DPoint(25, 85),
            pya.DPoint(85, 85),
            pya.DPoint(85, 25),
            pya.DPoint(95, 25),
        ])
        
        outer_corners = [pya.DCplxTrans(0.5, rot * 90., False, pya.DVector()) * corner for rot in [0, 1, 2, 3]]
        region_corners = pya.Region([s.to_itype(self.layout.dbu) for s in inner_corners + outer_corners])
        
        sqr = pya.DPolygon([
            pya.DPoint(-2, 0),
            pya.DPoint(0, 2),
            pya.DPoint(2, 0),
            pya.DPoint(0, -2),
        ])
        outer_corners = [pya.DCplxTrans(0.5, rot * 90., False, pya.DVector()) * corner for rot in [0, 1, 2, 3]]
        
        corner = pya.DPolygon([
            pya.DPoint(0, 0),
            pya.DPoint(0, 10),
            pya.DPoint(4, 10),
            pya.DPoint(4, 6),
            pya.DPoint(2, 6),
            pya.DPoint(2, 2),
            pya.DPoint(6, 2),
            pya.DPoint(6, 4),
            pya.DPoint(10, 4),
            pya.DPoint(10, 0),
            pya.DPoint(0, 0),
        ])
        cross = [pya.DCplxTrans(1, rot * 90., False, pya.DVector()) * corner for rot in [0, 1, 2, 3]]
        
        
        region_corners = pya.Region([s.to_itype(self.layout.dbu) for s in inner_corners + outer_corners])
        region_cross = pya.Region([s.to_itype(self.layout.dbu) for s in cross])
        
        inner_region = pya.Region(inner_box.to_itype(self.layout.dbu))
        inner_region -= region_cross
        inner_region +=  pya.Region(sqr.to_itype(self.layout.dbu))
        
        self.inv_corners = pya.Region([protection_box.to_itype(self.layout.dbu)])
        self.inv_corners -= inner_region
        self.inv_corners -= region_corners
        marker_step = 100
        t = pya.Trans(pya.DVector(0,0).to_itype(self.layout.dbu))
        for i in range(self.n_items):
          for j in range(self.n_items):
            self.cell.shapes(layer_gap).insert(self.inv_corners.transform(t))
            t = pya.Trans(pya.DVector(-marker_step, 0).to_itype(self.layout.dbu))
          t = pya.Trans(pya.DVector((self.n_items-1)*marker_step, marker_step).to_itype(self.layout.dbu))
            
       
       
        
