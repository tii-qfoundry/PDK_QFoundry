# Enter your Python code here
import pya 
from qfoundry.elements.BenasqueBridge import BenasqueBridge

class BridgeQubit(pya.PCellDeclarationHelper):
  """
  A qubit based on an airbridge structure.
  
  The BridgeQubit consists of:
  - A BenasqueBridge airbridge as the central element
  - Landing pads on the bottom layer
  - Bridge body on the top layer with catenary-shaped profile
  """
  
  def __init__(self):
        super(BridgeQubit, self).__init__()
        self.set_parameters()
        
  def display_text_impl(self):
        return "BridgeQubit: A qubit based on an airbridge structure."
  
  def coerce_parameters_impl(self):
        # Ensure physical constraints are met
        if self.waist_width > self.land_width:
            self.waist_width = self.land_width
            
        if self.island_length> self.length:
            self.island_length = self.length
        
        if self.gap < 0.5:
            self.gap = 0.5
            
        if self.length < self.land_length * 2:
            self.length = self.land_length * 2

  def produce_impl(self):
        self._create_bridge_qubit() 
        
  def _add_shapes(self, shapes, layer):
        """Merge shapes into a region and add it to layer."""
        if type(shapes) == list:
          region = pya.Region(array=shapes).merged()
        else:
          region = pya.Region(shapes).merged()
        self.cell.shapes(layer).insert(region)
        return region  
         
  def set_parameters(self):
        # Layer parameters
        self.param("l1_layer", self.TypeLayer, "Layer Top Pads (Landing Pads)", 
                   default = pya.LayerInfo(146, 1))
        self.param("l2_layer", self.TypeLayer, "Layer Top (Bridge Body)", 
                   default = pya.LayerInfo(147, 1))

        self.param("l0_layer", self.TypeLayer, "Layer Bttom (Second Island)", 
                   default = pya.LayerInfo(130, 1))
        
        # Geometric parameters
        self.param("length", self.TypeDouble, "Total bridge length [um]", 
                   default = 82.0)
        self.param("waist_width", self.TypeDouble, "Bridge width at waist [um]", 
                   default = 300.0)
        self.param("land_width", self.TypeDouble, "Landing pad width [um]", 
                   default = 340.0)
        self.param("land_length", self.TypeDouble, "Landing pad length [um]", 
                   default = 20.0)
        self.param("gap", self.TypeDouble, "Gap around landing pads [um]", 
                   default = 1.0)
        
        # Bottom layer (second island) parameters
        self.param("island_length", self.TypeDouble, "Bottom island length [um]", 
                   default = 60.0)
        self.param("island_width", self.TypeDouble, "Bottom island width [um]", 
                   default = 340.0)
        self.param("island_gap", self.TypeDouble, "Gap around bottom island and frame edge [um]", 
                   default = 2.0)
        
        self.param("gal", self.TypeLayer, "Ground grid avoidance layer", default = pya.LayerInfo(133, 1), hidden=True)

        # Catenary curve parameter
        self.param("curve_a", self.TypeDouble, "Curve 'a' parameter, y = w/2*cosh(x/a)", 
                   default = 15.0, hidden=False)
        
        # Optional rounded corners
        self.param("round_path", self.TypeBoolean, "Round landing pad edges", 
                   default=True, hidden=False)
        self.param("pad_radius", self.TypeDouble, "Corner radius [um]", 
                   default = 5.0, hidden=False)
        
  def _create_bridge_qubit(self):
        """Create the bridge qubit structure using BenasqueBridge."""
        dbu = self.layout.dbu
        
        # First, draw the bottom island (l0_layer)
        self._draw_bottom_island()
        
        # Get the BenasqueBridge PCell, a fallback to draw it here can be useful 
        bridge_lib = pya.Library.library_by_name("qfoundry", self.layout.library().technology)
        if bridge_lib is None:
            # If library not found, create bridge directly
            raise RuntimeError("QFoundry library not found")
        
        if True:
            # Create instance using PCell
            param_dict = {
                "l1_layer": self.l1_layer,
                "l2_layer": self.l2_layer,
                "waist_width": self.waist_width,
                "gap": self.gap,
                "land_width": self.land_width,
                "land_length": self.land_length,
                "length": self.length,
                "curve_a": self.curve_a,
                "round_path": self.round_path,
                "pad_radius": self.pad_radius
            }
            
            # Create PCell variant
            bridge_cell = self.layout.create_cell(pcell_name = "BenasqueBridge", params = param_dict)
            
            if bridge_cell:
                # Insert instance at origin
                self.cell.insert(pya.CellInstArray(bridge_cell.cell_index(), pya.Trans()))
            else:
                # Fallback to direct creation
                raise RuntimeError("Failed to create bridge cell")
        else:
            # Fallback to direct creation
            raise RuntimeError("BenasqueBridge PCell not found")

  def _draw_bottom_island(self, offset = 0.0):
        """Draw a bottom island using negative lithography on the l0_layer.
        
        This creates a frame with the island area and landing pads subtracted out.
        The frame extends island_gap distance beyond the bridge bounding box.
        For negative lithography, the pattern drawn is what will be removed.
        """
        dbu = self.layout.dbu
        round_rad = self.pad_radius + offset

        # Create the island shape (this will be subtracted)
        half_length = (self.island_length) / 2.0
        half_width = (self.island_width) / 2.0
        
        island_cutout = pya.DPolygon([
            pya.DPoint(-half_length, -half_width),
            pya.DPoint(half_length, -half_width),
            pya.DPoint(half_length, half_width),
            pya.DPoint(-half_length, half_width),
        ])
        
        if self.round_path and round_rad > 0:
            island_cutout = island_cutout.round_corners(round_rad, round_rad, 36)

        # Create landing pad cutouts (these will also be subtracted)
        length = self.length
        land_length = self.land_length
        land_gap = self.gap
        island_gap = self.island_gap
        # Landing pad positions (same as in BenasqueBridge)
        landing_sta = self._draw_landing(pya.DPoint(-length/2 - land_length/2, 0), offset=0.0)
        landing_end = self._draw_landing(pya.DPoint(+length/2 + land_length/2, 0), offset=0.0)

        # Calculate frame size based on bridge bounding box plus gap
        # Bridge bounding box goes from landing pad edges plus land_width
        bridge_half_length = (length) / 2.0 + land_length + land_gap
        bridge_half_width = self.land_width / 2.0 + land_gap
        
        # Frame extends island_gap beyond the bridge bounding box
        half_frame_length = bridge_half_length + island_gap
        half_frame_width = bridge_half_width + island_gap
        
        frame_polygon = pya.DPolygon([
            pya.DPoint(-half_frame_length, -half_frame_width),
            pya.DPoint(half_frame_length, -half_frame_width),
            pya.DPoint(half_frame_length, half_frame_width),
            pya.DPoint(-half_frame_length, half_frame_width),
        ])
        if self.round_path and island_gap > 0:
            frame_polygon = frame_polygon.round_corners(round_rad + island_gap , round_rad + island_gap, 64)

        # Use region operations to subtract island and landing pads from frame (negative lithography)
        frame_region = pya.Region(frame_polygon.to_itype(dbu))
        island_region = pya.Region(island_cutout.to_itype(dbu))
        landing_sta_region = pya.Region(landing_sta.to_itype(dbu))
        landing_end_region = pya.Region(landing_end.to_itype(dbu))
        
        # Subtract all cutouts from the frame
        negative_pattern = frame_region - island_region - landing_sta_region - landing_end_region
        
        # Add the result to the layer
        self.cell.shapes(self.l0_layer).insert(negative_pattern)

  def _draw_landing(self, center=pya.DPoint(0, 0), offset=0.0):  
        """Draw a landing pad at the specified position."""
        width = self.land_width + offset * 2
        length = self.land_length + offset * 2
        round_rad = self.pad_radius + offset
        
        # Create rectangular polygon
        polygon = pya.DPolygon([
            pya.DPoint(length/2, width/2),
            pya.DPoint(length/2, -width/2),
            pya.DPoint(-length/2, -width/2),
            pya.DPoint(-length/2, width/2),
        ])
        
        # Apply rounding if enabled
        if self.round_path and round_rad > 0:
            polygon = polygon.round_corners(round_rad, round_rad, 36)
        
        # Transform to center position
        land_polygon = pya.DTrans(0, False, center.x, center.y) * polygon
        
        

        return land_polygon


if __name__ == "__main__":
    # Test the BridgeQubit PCell
    from qfoundry.scripts import reload_library
    from qfoundry.utils import test_pcell
    reload_library()

    pcell_decl = BridgeQubit
    pcell_params = {
        "length": 82.0,
        "waist_width": 300.0,
        "land_width": 340.0,
        "land_length": 20.0,
        "gap": 1.0,
        "curve_a": 80,
        "round_path": True,
        "pad_radius": 10.0,
        "island_length": 60.0,
        "island_width": 320.0,
        "island_gap": 20.0
    }
    pcell_trans = pya.Trans(pya.Trans.R0, 0.0, 0.0)

    test_pcell(pcell_decl, pcell_params, pcell_trans)
