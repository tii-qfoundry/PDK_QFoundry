
# Enter your Python code here
import pya 
from numpy import cosh, arccosh, linspace

class BenasqueBridge(pya.PCellDeclarationHelper):
  def __init__(self):
        super(BenasqueBridge, self).__init__()
        self.set_parameters()
        
  def display_text_impl(self):
        return "BenasqueBridge: A wide landing airbridge."
  
  def coerce_parameters_impl(self):
        pass

  def produce_impl(self):
        self._benasqueBridge() 
        
  def _add_shapes(self, shapes, layer):
        """Merge shapes into a region and add it to layer."""
        if type(shapes) == list:
          region:pya.Region = pya.Region(array=shapes).merged()
        else:
          region:pya.Region = pya.Region(shapes).merged()
        self.cell.shapes(layer).insert(region)
        return region  
         
  def set_parameters(self):
        self.param("l1_layer", self.TypeLayer, "Layer Bottom", default = pya.LayerInfo(146, 1))
        self.param("l2_layer", self.TypeLayer, "Layer Top", default = pya.LayerInfo(147, 1))
        self.param("waist_width", self.TypeDouble, "w, the airbridge width at its waist[um]", default = 10.0)
        self.param("gap", self.TypeDouble, "Airbridge landing gap [um]", default = 1)
        self.param("land_width", self.TypeDouble, "Airbridge width at landing [um]", default = 40)
        self.param("land_length", self.TypeDouble, "Landing path length [um]", default = 16)
        self.param("length", self.TypeDouble, "Airbridge length [um]", default = 60)
        self.param("curve_a", self.TypeDouble, "Curve 'a' parameter, y = w/2*cosh(x/a)", default = 15.0, hidden=False)
        self.param("round_path", self.TypeBoolean, "Pad has round edges", default=True, hidden=True)
        self.param("pad_radius", self.TypeDouble, "Airbridge length [um]", default = 5.0, hidden=True)
        
            
  def _draw_landing(self, center=pya.DPoint(0, 0), offset = 0.0):  
        width= self.land_width + offset*2
        length = self.land_length + offset*2
        round_rad = self.pad_radius + offset
        
        def landing_points(length, width):
            
            polygon = pya.DTrans(0,False, 0, 0)*pya.DTrans(0,False, 0, 0) * pya.DPolygon([
                pya.DPoint(length/2, width/2),
                pya.DPoint(length/2, -width/2),
                pya.DPoint(-length/2,-width/2),
                pya.DPoint(-length
                /2, width/2),
            ])
            
            if self.round_path:
              polygon = polygon.round_corners(round_rad, round_rad, 36)
            return polygon

        land_polygon = pya.DTrans(0,False,center.x,center.y) * (
                                  landing_points( length=length,
                                                  width=width))
        return land_polygon
        
  def _draw_bridge(self)-> [pya.Polygon]:
        length = self.length
        width= self.land_width + self.gap*2
        w = self.waist_width
        
        land_length = self.land_length
        offset = self.gap
        # Draw landing pads
        landing_sta = self._draw_landing(pya.DPoint(-length/2-land_length/2, 0),offset=offset)
        landing_end = self._draw_landing(pya.DPoint(+length/2+land_length/2, 0),offset=offset) 
        h = w/2
        
        a = w/2 if self.curve_a <=1e-4 else self.curve_a
        
        x_0 = (length+self.land_length)/2
        x_end = arccosh(width/2.0/h)*a
        num_points = 20
                
        x_array=linspace(-x_end, x_end, num=num_points+1)
        
        points = [pya.DPoint(-x_0, width/2)]
        points += [pya.DPoint(x, h*cosh(x/a)) for x in x_array]
        points += [pya.DPoint(x_0, width/2)]
        points += [pya.DPoint(x_0, -width/2)]
        points += [pya.DPoint(x, -h*cosh(x/a)) for x in x_array[::-1]]
        points += [pya.DPoint(-x_0, -width/2)]
        
        polygon = pya.DTrans(0,False, 0, 0)*pya.DPolygon(points)
        shapes = [landing_sta, landing_end, polygon]
        
        return [shape.to_itype(self.layout.dbu) for shape in shapes ]
  
  def _benasqueBridge(self):
        dbu = self.layout.dbu
        length = self.length
        land_length = self.land_length
        # Draw landing pads
        landing_sta = self._draw_landing(pya.DPoint(-length/2-land_length/2, 0)).to_itype(dbu)
        landing_end = self._draw_landing(pya.DPoint(+length/2+land_length/2, 0)).to_itype(dbu)
        self._add_shapes(landing_sta, self.l1_layer) 
        self._add_shapes(landing_end, self.l1_layer) 
        bridge_shapes = self._draw_bridge()
        self._add_shapes(bridge_shapes, self.l2_layer)
        
        
        

if __name__ == "__main__":
    # You need to reload the library to see the changes in the PCell 
    from qfoundry.scripts.utils import test_pcell
    from qfoundry.scripts.library import PDK_Lib
    PDK_Lib()

    pcell_decl = BenasqueBridge
    pcell_params = {
              "length":60.0, 
              }
    pcell_trans = pya.Trans(pya.Trans.R0, 0.0, 0.0)

    test_pcell(pcell_decl, pcell_params, pcell_trans)
