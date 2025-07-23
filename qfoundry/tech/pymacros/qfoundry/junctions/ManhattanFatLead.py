import pya
from numpy import cos, sin, tan, radians, linspace, sign, linspace
from math import pi

# Parametric Manhattan Josephson Junction
# Copyright: TII QRC/QFoundry 2023
# Juan E. Villegas, Nov. 2023

from kqcircuits.util.symmetric_polygons import polygon_with_vsym
from qfoundry.junctions.utils import arc, draw_junction, draw_pad, draw_patch_openning, draw_patch
from qfoundry.utils import _add_shapes

class ManhattanFatLead(pya.PCellDeclarationHelper):

    def __init__(self):
        super(ManhattanFatLead, self).__init__()
        self.set_paramters()

    def display_text_impl(self):
        return "ManhattanFatLead: A parameteric manhattan josephson junction"

    def coerce_parameters_impl(self):
        if(self.angle < -60):
            self.angle = -60
        elif(self.angle > 60):
            self.angle = 60
        self.overlap = self.conn_width
        

    def produce_impl(self):
        self.produceManhattanFatLead()
  
    def set_paramters(self):
        self.param("l_layer", self.TypeLayer, "Layer", default = pya.LayerInfo(2, 0))
        self.param("angle", self.TypeDouble, "Junction angle", default = 0.0)
        
        self.param("inner_angle", self.TypeDouble, "Angle between junction pads", default = 90.0)
        self.param("junction_width_t", self.TypeDouble, "Top junction width", default = 0.3, unit="μm",hidden=False)
        self.param("junction_width_b", self.TypeDouble, "Bottom junction width", default = 0.3, unit="μm",hidden=False)
        self.param("junction_y_offset", self.TypeDouble, "Vertical Offset of the junction position", default = 0.0, unit="μm",hidden=False)    
        self.param("finger_overshoot",self.TypeDouble, "Length of fingers after the junction.", default=2.0, unit="μm", hidden=False)
        self.param("finger_size",self.TypeDouble, "Length of fingers (without overshoot).", default=5.0, unit="μm")
        self.param("round_pad", self.TypeBoolean, "Pad has round edges", default=False, hidden=True)
        self.param("pad_radius", self.TypeDouble, "Pad edge radius", default=2.0, hidden=True)
        self.param("conn_width", self.TypeDouble, "Connector lead width", default=5.0, hidden=True)
        self.param("conn_height", self.TypeDouble, "Connector lead height inside the probe (capacitor)", default=5.0, hidden=False)
        self.param("draw_cap", self.TypeBoolean, "Include test pad", default=False)
        self.param("draw_patch", self.TypeBoolean, "Include patches", default=False)
        self.param("patch_scratch", self.TypeBoolean, "Draw 45 deg scratches as patch", default=False)
        self.param("patch_layer", self.TypeLayer, "Patch Layer", default = pya.LayerInfo(4, 0))
        self.param("patch_gap", self.TypeDouble, "Patch gap", default=2.0, hidden = True)
        self.param("patch_clearance", self.TypeDouble, "Patch clearance", default=5.0)
        self.param("cap_gap", self.TypeDouble, "Capacitor gap", default=20.0)
        self.param("cap_w", self.TypeDouble, "Capacitor width", default=200.0,hidden=False)
        self.param("cap_h", self.TypeDouble, "Capacitor height", default=200.0,hidden=False)
        self.param("cap_layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("offset_compensation",self.TypeDouble, "Compensation for top junction.", default=0.0, unit="μm",hidden=True)
        self.param("mirror_offset",self.TypeDouble, "Length of fingers (without overshoot).", default=False, unit="μm",hidden=True)
        self.param("label",self.TypeString, "Label", default="QFOUNDRY",hidden=True)



    def produceManhattanFatLead(self): 
            """Draws the Manhattan junction"""
            dbu = self.layout.dbu
            jj_layer = self.layout.layer(self.l_layer)
            _angle = radians(self.angle)
            #Junction
            finger_shapes = draw_junction(self.angle, self.inner_angle, self.junction_width_b, self.junction_width_t, self.finger_size, self.mirror_offset, self.offset_compensation, self.finger_overshoot, 
              finger_overlap = self.conn_width, 
              center = pya.DPoint(0, 0), dbu=dbu)
            _add_shapes(self.cell, finger_shapes, jj_layer)
            
            
            # Connector leads
            conn_shapes = self.draw_connectors(pya.DPoint(0, 0))
            _add_shapes(self.cell, conn_shapes, jj_layer)
            
            
            # Pads
            if self.draw_cap:
                top_dx = self.conn_width*cos(_angle)/2
                cap_shape = draw_pad(self.cap_w, self.cap_h, self.cap_gap, dbu)
                patch_open_shape = []
                patch_shape = []
                # Patches
                if self.draw_patch:
                    patch_open_shape = draw_patch_openning( self.finger_size, 
                                                            self.conn_width, 
                                                            self.conn_height, 
                                                            self.angle, 
                                                            self.inner_angle, 
                                                            self.cap_gap, 
                                                            gap = self.patch_gap, 
                                                            center = pya.DPoint(0, 0),
                                                            dbu = dbu)
                    patch_shape = draw_patch(self.finger_size, self.cap_gap, self.conn_width, self.conn_height, self.angle, self.inner_angle, self.patch_scratch, self.patch_clearance, center = pya.DPoint(0, 0), dbu = dbu)
                
                layerm = self.layout.layer(pya.LayerInfo(1, 0))
                
                trans = pya.Trans(pya.Trans.R0, (-self.cap_w/2+10)/dbu, (self.cap_h-10)/dbu)     
                cell_label = self.layout.create_cell("TEXT", "Basic", {"text":self.label, "mag":20,"layer": pya.LayerInfo(1, 0) })
                cell_instance_lbl = pya.CellInstArray(cell_label.cell_index(),trans)
                self.cell.insert(cell_instance_lbl)  

                
                metal_neg = pya.Box(-(self.cap_w+80)/dbu/2, -(self.cap_h+40+self.cap_gap/2)/dbu,
                                    (self.cap_w+80)/dbu/2, (self.cap_h+40+self.cap_gap/2)/dbu)
                
                layer_add = self.layout.layer(pya.LayerInfo(131, 1))
                
                region_pos = pya.Region(cap_shape).merged() - pya.Region(patch_open_shape).merged()
                self.cell.shapes(layer_add).insert(region_pos) 
                    
                region_neg = pya.Region(metal_neg).merged()- pya.Region(cap_shape).merged() + pya.Region(patch_open_shape).merged()
                self.cell.shapes(layerm).insert(region_neg)  
                
                layer = self.layout.layer(self.patch_layer)
                _add_shapes(self.cell, patch_shape, layer)  
  

    def draw_connectors(self, center=pya.DPoint(0, 0)):
        dbu = self.layout.dbu
        gap = self.cap_gap
        size = self.finger_size
        _angle = radians(self.angle)
        _inner_angle = radians(self.inner_angle)
        
        top_lead_height = self.conn_height+self.cap_gap/2
        bot_lead_height = max(gap/2.-size, 0.) + self.conn_height
        conn_width = self.conn_width
        
        bot_dy = size*cos(_angle)
        
        rounding_params = {
            "rinner": 10,  # inner corner rounding radius
            "router": 10,  # outer corner rounding radius
            "n": 64,  # number of point per rounded corner
        }
        
        def connector_points(heigth, width, angle, rot=0, round = False):
            x0 = width/2.
            y0 = width/2.*tan(angle)
            
            if round:
                return arc(heigth/2.0, width/2.0, angle, rot)
            else:
                return pya.DTrans(rot,False, 0, 0)*pya.DPolygon([
                    pya.DPoint(-x0, -heigth/2.0-y0),
                    pya.DPoint(x0, -heigth/2.0+y0),
                    pya.DPoint(x0, heigth/2.0),
                    pya.DPoint(-x0, heigth/2.0),
                ])

        top_dx = conn_width*cos(_angle)/2
        top_dy = top_lead_height/2+(size+conn_width/2)*sin(_angle)
        conn_top = pya.DTrans(0,False,size*cos(_angle)+top_dx, top_dy) * (connector_points(
                            heigth=top_lead_height,
                            width=conn_width,
                            angle=_angle))
                        
        conn_bot = pya.DTrans(0,False,size*sin(_angle), -bot_lead_height/2-bot_dy) * (connector_points(
                        heigth=bot_lead_height,
                        width=conn_width,
                        angle=0))
                        
        conn_shapes = [ (pya.DTrans(0, False, center.x,center.y) * conn_top).to_itype(dbu),
                            (pya.DTrans(0, False, center.x,center.y) * conn_bot).to_itype(dbu)]
        
        return conn_shapes

if __name__ == "__main__":
    from qfoundry.scripts import reload_library
    from qfoundry.utils import test_pcell
    reload_library()
    
    pcell_decl = ManhattanFatLead
    pcell_params = {
              "junction_width_t":0.1, 
              "junction_width_b":0.2, 
              "angle": 0.,
              "draw_cap":False,
              "patch_scratch":False,}
    pcell_trans = pya.Trans(pya.Trans.R0, 0.0, 0.0)

    test_pcell(pcell_decl, pcell_params, pcell_trans)
