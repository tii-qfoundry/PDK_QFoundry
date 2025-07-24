import pya
from numpy import tan, cos, sin, radians, linspace, sign, linspace
from math import pi

# Parametric Manhattan Josephson Junction
# Copyright: TII QRC/QFoundry 2023
# Juan E. Villegas, Nov. 2023

from kqcircuits.util.symmetric_polygons import polygon_with_vsym
from qfoundry.junctions.utils import arc, draw_junction, draw_pad, draw_patch, draw_pad
from qfoundry.utils import _add_shapes

def draw_patch_openning(finger_size, conn_width, heigth, angle, inner_angle, gap=2) -> pya.DPolygon:
    size = finger_size
    _angle = radians(angle)
    _inner_angle = radians(inner_angle)
    
    def patch_points(heigth, size, angle,rot=0, round = True):
        end_x = size*cos(angle)
        end_y = size*sin(angle)
    
        polygon = pya.DTrans(0,False, end_x, end_y) * pya.DPolygon([
            pya.DPoint(-conn_width/2-gap, 0),
            pya.DPoint(-conn_width/2-gap, heigth+gap),
            pya.DPoint(conn_width/2+gap, heigth+gap),
            pya.DPoint(conn_width/2+gap, 0),
        ])
        if True:
            polygon = polygon.round_corners(1, 1, 32)
        return polygon
        
    patch = pya.DTrans(0,False,0, -1) * (patch_points(heigth=heigth, size=size,angle=_angle))
    
    return patch
    
class Manhattan(pya.PCellDeclarationHelper):

    def __init__(self):
        super(Manhattan, self).__init__()
        self.set_paramters()

    def display_text_impl(self):
        return "Manhattan: A parameteric manhattan josephson junction"

    def coerce_parameters_impl(self):
        if(self.angle < -60):
            self.angle = -60
        elif(self.angle > 60):
            self.angle = 60

    def produce_impl(self):
        self.produceManhattan()
  
    def set_paramters(self):
        self.param("l_layer", self.TypeLayer, "Layer", default = pya.LayerInfo(2, 0))
        self.param("angle", self.TypeDouble, "Junction angle", default = 0.0)
        
        self.param("inner_angle", self.TypeDouble, "Angle between junction pads", default = 90.0)
        self.param("junction_width_t", self.TypeDouble, "Top junction width", default = 0.3, unit="μm",hidden=False)
        self.param("junction_width_b", self.TypeDouble, "Bottom junction width", default = 0.3, unit="μm",hidden=False)
        self.param("junction_y_offset", self.TypeDouble, "Vertical Offset of the junction position", default = 0.0, unit="μm",hidden=False)    
        self.param("finger_overshoot",self.TypeDouble, "Length of fingers after the junction.", default=2.0, unit="μm", hidden=False)
        self.param("finger_overlap",self.TypeDouble, "Length of fingers inside the pads.", default=1.0, unit="μm",hidden=True)
        self.param("finger_size",self.TypeDouble, "Length of fingers (without overshoot).", default=10.0, unit="μm")
        
        self.param("round_pad", self.TypeBoolean, "Pad has round edges", default=True, hidden=True)
        self.param("pad_radius", self.TypeDouble, "Pad edge radius", default=2.0, hidden=True)
        self.param("conn_width", self.TypeDouble, "Connector pad width", default=5.0, hidden=True)
        self.param("conn_height", self.TypeDouble, "Connector pad height", default=20.0, hidden=False)

        # add separator
        self.param("draw_cap", self.TypeBoolean, "Include test pad", default=True)
        self.param("cap_gap", self.TypeDouble, "Capacitor gap", default=20.0)
        self.param("cap_w", self.TypeDouble, "Capacitor width", default=200.0,hidden=False)
        self.param("cap_h", self.TypeDouble, "Capacitor height", default=200.0,hidden=False)
        self.param("draw_patch", self.TypeBoolean, "Include patches", default=True)
        self.param("patch_scratch", self.TypeBoolean, "Draw 45 deg scratches as patch", default=False)
        self.param("patch_layer", self.TypeLayer, "Patch Layer", default = pya.LayerInfo(4, 0))
        self.param("patch_gap", self.TypeDouble, "Patch gap", default=2.0, hidden = True)
        self.param("patch_clearance", self.TypeDouble, "Patch clearance", default=5.0)

        
        self.param("cap_layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("offset_compensation",self.TypeDouble, "Compensation for top junction.", default=0.0, unit="μm",hidden=True)
        self.param("mirror_offset",self.TypeDouble, "Length of fingers (without overshoot).", default=False, unit="μm",hidden=True)
        self.param("label",self.TypeString, "Label", default="QFOUNDRY",hidden=True)

    def produceManhattan(self): 
            """Draws the Manhattan junction"""
            dbu = self.layout.dbu
            
            #Junction
            finger_shapes = draw_junction(self.angle, self.inner_angle, self.junction_width_b, self.junction_width_t, self.finger_size, self.mirror_offset, self.offset_compensation, self.finger_overshoot, self.finger_overlap, pya.DPoint(0, 0), dbu=dbu)
            conn_shapes = self.draw_connectors(pya.DPoint(0, 0))
            layer = self.layout.layer(self.l_layer)
            _add_shapes(self.cell, finger_shapes, layer)
            _add_shapes(self.cell, conn_shapes, layer)
            
            # Capacitor
            if self.draw_cap:
                cap_shape = draw_pad(self.cap_w, self.cap_h, self.cap_gap, dbu = dbu)
                _angle = radians(self.angle)
                patch_open_shape = []
                patch_shape = []
                # Patches
                if self.draw_patch:
                    center = pya.DPoint(0, 0)
                    top_height = self.conn_height+self.cap_gap/2-self.finger_size*sin(_angle)
                    patch_top = draw_patch_openning(
                        self.finger_size, 
                        self.conn_width, 
                        top_height, 
                        self.angle, 
                        self.inner_angle, 
                        gap = self.patch_gap
                    )
                    
                    bot_height = self.conn_height+self.cap_gap/2-self.finger_size*cos(_angle)
                    patch_bot = draw_patch_openning(
                        self.finger_size, 
                        self.conn_width, 
                        bot_height, 
                        self.angle-90, 
                        self.inner_angle,   
                        gap = self.patch_gap
                    )

                    patch_open_shape = [
                      (pya.DTrans(0, False, center.x,center.y) * patch_top).to_itype(dbu),
                      (pya.DTrans(0, False, center.x,center.y-bot_height) * patch_bot).to_itype(dbu)
                    ]

   
                
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
        size= self.finger_size
        _angle = radians(self.angle)
        conn_width = self.conn_width
        conn_height = self.conn_height
        _inner_angle = radians(self.inner_angle)
        
        rounding_params = {
            "rinner": 10,  # inner corner rounding radius
            "router": 10,  # outer corner rounding radius
            "n": 64,  # number of point per rounded corner
        }
        
        def connector_points(tip_w, width,angle, rot=0, conn_height = 20.0):
            dx = width/2*sin(angle)
            dy = width/2*cos(angle)
            
            end_x = size*cos(angle)
            end_y = size*sin(angle)
            
            polygon = pya.DTrans(0,False, end_x, end_y)*pya.DTrans(rot,False, 0, 0) * pya.DPolygon([
                pya.DPoint(tip_w/2, 0),
                pya.DPoint(conn_width/2, conn_width),
                pya.DPoint(conn_width/2, conn_height),
                pya.DPoint(-conn_width/2, conn_height),
                pya.DPoint(-conn_width/2, conn_width),
                pya.DPoint(-tip_w/2, 0)
            ])
            if self.round_pad:
              polygon = polygon.round_corners(self.pad_radius, self.pad_radius, 16)
            return polygon

        conn_top = pya.DTrans(0,False,0, -1) * (connector_points(tip_w=2.0,width=conn_width,angle=_angle,conn_height=conn_height+self.cap_gap/2.0-self.finger_size*sin(_angle)))
        conn_bot = pya.DTrans(0,False,0, 1) * (connector_points(tip_w=2.0,width=conn_width, angle=_angle-_inner_angle,rot=2,conn_height=conn_height+self.cap_gap/2.0+self.finger_size*sin(_angle-_inner_angle)))
        
        connector_shapes = [ (pya.DTrans(0, False, center.x,center.y) * conn_top).to_itype(dbu),
                            (pya.DTrans(0, False, center.x,center.y) * conn_bot).to_itype(dbu)]
        
        
        return connector_shapes
    
  
if __name__ == "__main__":
    # You need to reload the library to see the changes in the PCell 
    from qfoundry.scripts import reload_library
    from qfoundry.utils import test_pcell

    pcell_decl = Manhattan
    pcell_params = {
              "junction_width_t":0.1, 
              "junction_width_b":0.2, 
              "angle": 0.,
              "draw_cap":True,
              "patch_scratch":True,}
    pcell_trans = pya.Trans(pya.Trans.R0, 0.0, 0.0)

    test_pcell(pcell_decl, pcell_params, pcell_trans)
