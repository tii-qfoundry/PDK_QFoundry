import pya
from numpy import tan, cos, sin, radians, linspace, sign, linspace
from math import pi

# Parametric Manhattan Josephson Junction
# Copyright: TII QRC/QFoundry 2023
# Juan E. Villegas, Nov. 2023

from kqcircuits.util.symmetric_polygons import polygon_with_vsym
from qfoundry.junctions.utils import arc, draw_junction, draw_pad, draw_patch, draw_patch_openning
from qfoundry.utils import _add_shapes

NEGATIVE_LAYERS = [
    pya.LayerInfo(1, 0),
    pya.LayerInfo(130, 1),
]


    
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
        self.param("conn_width", self.TypeDouble, "Connector pad width", default=5.0, hidden=False)
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
            finger_shapes = draw_junction(angle = self.angle, 
                                          inner_angle = self.inner_angle, 
                                          junction_width_b = self.junction_width_b, 
                                          junction_width_t = self.junction_width_t, 
                                          finger_size = self.finger_size, 
                                          mirror_offset = self.mirror_offset, 
                                          offset_compensation = self.offset_compensation, 
                                          finger_overshoot = self.finger_overshoot, 
                                          finger_overlap = self.finger_overlap, 
                                          bottom_lead_comp = 0, center = pya.DPoint(0, 0), dbu = dbu)
            conn_shapes = self.draw_connectors(pya.DPoint(0, 0))
            layer_jj = self.layout.layer(self.l_layer)
            _add_shapes(self.cell, finger_shapes, layer_jj)
            _add_shapes(self.cell, conn_shapes, layer_jj)

            # Capacitor
            if self.draw_cap:
                cap_shape = draw_pad(self.cap_w, self.cap_h, self.cap_gap, dbu = dbu)
                _angle = radians(self.angle)
                patch_open_shape = []
                patch_shape = []
                
                metal_neg = pya.Box(-(self.cap_w+80)/dbu/2, -(self.cap_h+40+self.cap_gap/2)/dbu,
                                    (self.cap_w+80)/dbu/2, (self.cap_h+40+self.cap_gap/2)/dbu)

                region_pos = pya.Region(cap_shape).merged()
                region_neg = pya.Region(metal_neg).merged()- pya.Region(cap_shape).merged()
            else:
                # If no capacitor is drawn, we still need to define the regions
                region_pos = pya.Region()
                region_neg = pya.Region()
                
            # Patches
            if self.draw_patch:
                # Use the updated draw_patch function
                patch_shape = draw_patch(
                    self.finger_size, 
                    self.cap_gap, 
                    self.conn_width, 
                    self.conn_height, 
                    self.angle, 
                    self.inner_angle, 
                    self.patch_scratch, 
                    self.patch_clearance,
                    center=pya.DPoint(0, 0), 
                    dbu=dbu
                )
                
                # Patch opening in base metal layer
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
                region_pos = region_pos - pya.Region(patch_open_shape).merged()
                region_neg = region_neg + pya.Region(patch_open_shape).merged()
            
            # Label handling
            if self.draw_cap:
                trans = pya.Trans(pya.Trans.R0, (-self.cap_w/2+10)/dbu, (self.cap_h-10)/dbu)     
                cell_label = self.layout.create_cell("TEXT", "Basic", {"text":self.label, "mag":20,"layer": pya.LayerInfo(1, 0) })
                cell_instance_lbl = pya.CellInstArray(cell_label.cell_index(),trans)
            else:
                cell_instance_lbl = pya.CellInstArray(pya.CellIndex(0), trans)
            
            # Add shapes to the layout
            layer_cap = self.layout.layer(self.cap_layer)

            # Apply layer logic based on lithography type
            if layer_cap in [self.layout.layer(layer) for layer in NEGATIVE_LAYERS]: 
                # Negative lithography: use separate layers for positive and negative regions
                layer_add = self.layout.layer(pya.LayerInfo(131, 1))
                self.cell.shapes(layer_add).insert(region_pos) 
                self.cell.shapes(layer_cap).insert(region_neg)
                self.cell.insert(cell_instance_lbl)    
            else:
                # Positive lithography: insert label and subtract from positive region
                self.cell.insert(cell_instance_lbl)
                # Flatten and subtract the label region from region_pos if needed
                self.cell.shapes(layer_cap).insert(region_pos)

            # Add patch shapes to patch layer
            layer_patch = self.layout.layer(self.patch_layer)
            _add_shapes(self.cell, patch_shape, layer_patch)


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
    reload_library()

    pcell_decl = Manhattan
    pcell_params = {
              "junction_width_t":0.1, 
              "junction_width_b":0.2, 
              "angle": 0.,
              "draw_cap":True,
              "patch_scratch":True,}
    pcell_trans = pya.Trans(pya.Trans.R0, 0.0, 0.0)

    test_pcell(pcell_decl, pcell_params, pcell_trans)
