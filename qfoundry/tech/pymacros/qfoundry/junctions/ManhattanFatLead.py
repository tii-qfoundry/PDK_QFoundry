import pya
from numpy import cos, sin, arctan,tan, radians, linspace, sign, linspace, pi
from math import pi

from kqcircuits.util.symmetric_polygons import polygon_with_vsym
from qfoundry.junctions.utils import arc, draw_junction, draw_pad, draw_patch_openning, draw_patch
from qfoundry.utils import _add_shapes, _substract_shapes

NEGATIVE_LAYERS = [
    pya.LayerInfo(1, 0),
    pya.LayerInfo(130, 1),
]

class ManhattanFatLead(pya.PCellDeclarationHelper):

    def __init__(self):
        super(ManhattanFatLead, self).__init__()
        self.set_paramters()

    def display_text_impl(self):
        return "ManhattanFatLead: A parameteric manhattan josephson junction"

    def coerce_parameters_impl(self):
        if(self.angle < -15):
            self.angle = -15
        elif(self.angle > 15):
            self.angle = 15
        self.overlap = self.conn_width
        

    def produce_impl(self):
        self.produceManhattanFatLead()
  
    def set_paramters(self):
        self.param("l_layer", self.TypeLayer, "Layer", default = pya.LayerInfo(2, 0))
        choices = [("Single Junction",0),("SQUID Pair",1), ("SQUID Reflected",2)]
        self.param("junction_type", self.TypeList, "Junction Type", choices=choices, default=0)
        self.param("squid_spacing", self.TypeDouble, "Spacing between SQUID junctions", default=20.0, unit="μm")
        self.param("angle", self.TypeDouble, "Junction angle", default = 0.0)
        
        self.param("inner_angle", self.TypeDouble, "Angle between junction pads", default = 90.0)
        self.param("junction_width_t", self.TypeDouble, "Top junction width", default = 0.3, unit="μm",hidden=False)
        self.param("junction_width_b", self.TypeDouble, "Bottom junction width", default = 0.3, unit="μm",hidden=False)

        self.param("finger_overshoot",self.TypeDouble, "Length of fingers after the junction.", default=2.0, unit="μm", hidden=False)
        self.param("finger_size",self.TypeDouble, "Length of fingers (without overshoot).", default=5.0, unit="μm")
        
        self.param("round_pad", self.TypeBoolean, "Pad has round edges", default=False, hidden=True)
        self.param("pad_radius", self.TypeDouble, "Pad edge radius", default=2.0, hidden=True)
        
        self.param("conn_width", self.TypeDouble, "Connector lead width", default=9.0, hidden=False)
        self.param("conn_height", self.TypeDouble, "Connector lead height inside the probe (capacitor)", default=10.0, hidden=False)
        self.param("draw_cap", self.TypeBoolean, "Include test pad", default=False)
        self.param("draw_patch", self.TypeBoolean, "Include patches", default=False)
        self.param("patch_scratch", self.TypeBoolean, "Draw 45 deg scratches as patch", default=False, hidden=True)
        self.param("patch_layer", self.TypeLayer, "Patch Layer", default = pya.LayerInfo(4, 0), hidden=True)
        self.param("patch_gap", self.TypeDouble, "Patch gap", default=1.0, hidden = False)
        
        self.param("patch_clearance", self.TypeDouble, "Patch clearance", default=5.0, hidden = True)
        self.param("cap_gap", self.TypeDouble, "Capacitor gap", default=20.0)
        self.param("cap_w", self.TypeDouble, "Capacitor width", default=200.0,hidden=False)
        self.param("cap_h", self.TypeDouble, "Capacitor height", default=200.0,hidden=False)
        self.param("cap_layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("offset_compensation",self.TypeDouble, "Compensation for top junction.", default=0.0, unit="μm",hidden=True)
        self.param("mirror_offset",self.TypeDouble, "Length of fingers (without overshoot).", default=False, unit="μm",hidden=True)
        self.param("label",self.TypeString, "Label", default="",hidden=False)

    def produceManhattanFatLead(self): 
            """Draws the Manhattan junction"""
            dbu = self.layout.dbu
            jj_layer = self.layout.layer(self.l_layer)
            _angle = radians(self.angle)
            _inner_angle = radians(self.inner_angle)
            size = self.finger_size
            conn_height= self.conn_height
            conn_width = self.conn_width
            
            #Junction
            
            if self.junction_type == 0:
                finger_shapes = draw_junction(self.angle, self.inner_angle, self.junction_width_b, self.junction_width_t, self.finger_size, self.mirror_offset, self.offset_compensation, self.finger_overshoot, 
                  finger_overlap = self.conn_width, 
                  center = pya.DPoint(0, 0), dbu=dbu)
                _add_shapes(self.cell, finger_shapes, jj_layer)
            else:  # SQUID cases
                center1 = pya.DPoint(-self.squid_spacing / 2, 0)
                finger_shapes1 = draw_junction(self.angle, self.inner_angle, self.junction_width_b, self.junction_width_t, self.finger_size, self.mirror_offset, self.offset_compensation, self.finger_overshoot, 
                    finger_overlap = self.conn_width, 
                    center = center1, dbu=dbu,
                    bottom_lead_comp = -self.conn_width/2
                    )
                
                angle2 = self.angle-180 if self.junction_type == 2 else self.angle
                inner_angle2 = 180+self.inner_angle if self.junction_type == 2 else self.inner_angle
                if self.junction_type == 2:
                  extension = self.squid_spacing/cos(radians(self.angle))-2*conn_width-size
                  bottom_lead_comp = -extension+self.squid_spacing*sin(radians(self.angle))+self.finger_size
                  finger_size2 = extension
                  print(finger_size2, 'um, angle = ', self.angle)
                else:
                  bottom_lead_comp = self.squid_spacing*tan(radians(self.angle))
                  finger_size2 = self.finger_size
                  
                center2 = pya.DPoint(self.squid_spacing / 2, self.squid_spacing*tan(radians(angle2)))
                
                finger_shapes2 = draw_junction(angle2, inner_angle2, 
                                               self.junction_width_b, 
                                               self.junction_width_t, 
                                               finger_size2, 
                                               self.mirror_offset, 
                                               self.offset_compensation, 
                                               self.finger_overshoot,
                                               finger_overlap = self.conn_width,
                                               center = center2, dbu=dbu,
                                               bottom_lead_comp = bottom_lead_comp-   self.conn_width/2
                                            )
                _add_shapes(self.cell, finger_shapes1, jj_layer)
                _add_shapes(self.cell, finger_shapes2, jj_layer)
                
                # Connecting loop for SQUID uses the capacitors as the loop path
            
            
            # Connector leads
            self.top_dx = (size+conn_width/2)*cos(_angle)
            self.top_dy = (size+conn_width/2)*sin(_angle)
            self.top_lead_height = conn_height+self.cap_gap/2-self.top_dy+0
            
            bottom_finger_angle = _angle - _inner_angle
            self.bot_dx = size*sin(bottom_finger_angle+pi/2)
            self.bot_dy = -size*cos(bottom_finger_angle+pi/2)
            self.bot_lead_height = -(conn_height + self.cap_gap/2)
            
               
            if self.junction_type != 0:
                dx2 = (finger_size2 + bottom_lead_comp)*sin(_angle)
                dy2 = (self.squid_spacing)*tan(_angle)

                conn_shapes = self.draw_connectors(center = pya.DPoint(-self.squid_spacing / 2, 0), 
                                                   draw_top = True, 
                                                   draw_bot = True,
                                                   offsets = {'top_dx': self.top_dx, 
                                                               'top_dy': self.top_dy, 
                                                               'bot_dx': self.bot_dx, 
                                                               'bot_dy': self.bot_dy},
                                                    lead_height={'top': self.top_lead_height+self.top_dy, 
                                                                'bot': self.bot_lead_height})
                conn_shapes2 = self.draw_connectors(center = pya.DPoint(self.squid_spacing / 2, 0), 
                                                    draw_top=True if self.junction_type == 1 else False, 
                                                    draw_bot=True,
                                                    offsets = {'top_dx': self.top_dx, 
                                                               'top_dy': self.top_dy + dy2, 
                                                               'bot_dx': self.bot_dx +dx2, 
                                                               'bot_dy': self.bot_dy},
                                                    lead_height={'top': self.top_lead_height+ self.top_dy, 
                                                                 'bot': self.bot_lead_height})
                                                    
                # ompensate the y offset in the bottom-right lead
                # Compensate the x ioffset in the bottom-right lead
                # conn_shapes2 = [conn_shapes2[0], 
                #                 conn_shapes2[1]*pya.DTrans(0, False, dx2/dbu, 0)]
                                
                _add_shapes(self.cell, conn_shapes, jj_layer)
                _add_shapes(self.cell, conn_shapes2, jj_layer)
            else:
                conn_shapes = self.draw_connectors(pya.DPoint(0, 0),
                                                   draw_top=True, draw_bot=True,
                                                   lead_height={'top': self.top_lead_height+ self.top_dy, 
                                                                'bot': self.bot_lead_height},
                                                    offsets = {'top_dx': self.top_dx, 
                                                               'top_dy': self.top_dy,
                                                               'bot_dx': self.bot_dx,
                                                               'bot_dy': self.bot_dy})
                _add_shapes(self.cell, conn_shapes, jj_layer)
            
            # Pads
            if self.draw_cap:
                cap_shape = draw_pad(self.cap_w, self.cap_h, self.cap_gap, dbu)
                patch_open_shape = []
                patch_shape = []
                # Patches
                if self.draw_patch:
                    # Patch opening in base metal layer
                    center = pya.DPoint(0, 0)
                   
                    if self.junction_type != 0:
                        
                        center1 = pya.DPoint(-self.squid_spacing / 2, 0)
                        center2 = pya.DPoint(self.squid_spacing / 2, 0)

                        patch_top = draw_patch_openning(
                            self.finger_size + self.conn_width / 2,
                            self.conn_width,
                            self.top_lead_height,
                            self.angle,
                            self.inner_angle,
                            gap=self.patch_gap
                        )

                        patch_bot = draw_patch_openning(
                            self.finger_size,
                            self.conn_width,
                            abs(self.bot_lead_height+size*cos(_angle)),
                            self.angle - self.inner_angle,
                            self.inner_angle,
                            gap=self.patch_gap,
                            direction=-1
                        )

                        patch_open_shape = [
                            (pya.DTrans(0, False, center1.x, center1.y + self.patch_gap) * patch_top).to_itype(dbu),
                            (pya.DTrans(0, False, center1.x, center1.y + self.patch_gap) * patch_bot).to_itype(dbu),
                            (pya.DTrans(0, False, center2.x+dx2, center2.y + self.patch_gap) * patch_bot).to_itype(dbu)
                        ]
                        if self.junction_type == 1:
                            patch_open_shape.append(
                                (pya.DTrans(0, False, center2.x, center2.y + self.patch_gap) * patch_top).to_itype(dbu)
                            )
                    else: 
                        patch_top = draw_patch_openning(
                            self.finger_size+self.conn_width/2, # This dimension size extends to the center of the connector
                            self.conn_width, 
                            self.top_lead_height, 
                            self.angle, 
                            self.inner_angle, 
                            gap = self.patch_gap
                        )
                        
                        patch_bot = draw_patch_openning(
                            self.finger_size, 
                            self.conn_width, 
                            abs(self.bot_lead_height+size*cos(_angle)), 
                            self.angle-self.inner_angle, 
                            self.inner_angle,   
                            gap = self.patch_gap,
                            direction = -1
                        )

                        patch_open_shape = [
                        (pya.DTrans(0, False, center.x,center.y+self.patch_gap) * patch_top).to_itype(dbu),
                        (pya.DTrans(0, False, center.x,center.y+self.patch_gap) * patch_bot).to_itype(dbu)
                        ]
                    
                layerm = self.layout.layer(self.cap_layer)
                
                  
                
                label_trans = pya.Trans(pya.Trans.R0, (-self.cap_w/2+10)/dbu, (self.cap_h-10)/dbu)     
                cell_label = self.layout.create_cell("TEXT", "Basic", {"text":self.label, "mag":20,"layer": pya.LayerInfo(1, 0) })
                cell_instance_lbl = pya.CellInstArray(cell_label.cell_index(),label_trans)
                
                metal_neg = pya.Box(-(self.cap_w+80)/dbu/2, -(self.cap_h+40+self.cap_gap/2)/dbu,
                                      (self.cap_w+80)/dbu/2, (self.cap_h+40+self.cap_gap/2)/dbu)
                                      
                region_pos = pya.Region(cap_shape).merged() - pya.Region(patch_open_shape).merged()
                region_neg = pya.Region(metal_neg).merged()- pya.Region(cap_shape).merged() + pya.Region(patch_open_shape).merged()
                
                if self.cap_layer in NEGATIVE_LAYERS  : 
                  layer_add = self.layout.layer(pya.LayerInfo(131, 1))
                  self.cell.shapes(layer_add).insert(region_pos) 
                  self.cell.shapes(layerm).insert(region_neg)
                  self.cell.insert(cell_instance_lbl)    
                else:
                  # Convert cell_instance_lbl to a region
                    self.cell.insert(cell_instance_lbl).flatten()
                    # Subtract the label region from region_pos if label_region is not empt
                    
                    self.cell.shapes(layerm).insert(region_pos)
                  #self.cell.shapes(layerm).insert(region_pos) 
                  
                layer = self.layout.layer(self.patch_layer)
                _add_shapes(self.cell, patch_shape, layer)
  

    def draw_connectors(self, center=pya.DPoint(0, 0), draw_top=True, draw_bot=True, 
          offsets = {'top_dx': 0, 'top_dy': 0, 'bot_dx': 0, 'bot_dy': 0},
          lead_height={'top': 5, 'bot': 5}):
        dbu = self.layout.dbu
        _angle = radians(self.angle)
        conn_width = self.conn_width
        
        rounding_params = {
            "rinner": 10,  # inner corner rounding radius
            "router": 10,  # outer corner rounding radius
            "n": 64,  # number of point per rounded corner
        }
        
        def connector_points(heigth, width, angle, rot=0, round = False, offsets = {'dx': 0, 'dy': 0}):
            x0 = width/2.
            y0 = width/2.*tan(angle)
            
            if round:
                return arc(heigth/2.0, width/2.0, angle, rot)
            else:
                return pya.DTrans(rot,False, offsets['dx'], 0)*pya.DPolygon([
                    pya.DPoint(-x0, -y0 + offsets['dy']),
                    pya.DPoint(x0, y0 + offsets['dy']),
                    pya.DPoint(x0, heigth),
                    pya.DPoint(-x0, heigth),
                ])

        conn_shapes = []
        if draw_top:
            conn_top = pya.DTrans(0,False,0, 0) * connector_points(
                                heigth=lead_height['top'],
                                width=conn_width,
                                angle=_angle,
                                offsets = {'dx': offsets['top_dx'], 
                                           'dy': offsets['top_dy']},
                                )
            conn_shapes.append((pya.DTrans(0, False, center.x,center.y) * conn_top).to_itype(dbu))

        if draw_bot:
            conn_bot = pya.DTrans(0,False,0, 0) * connector_points(
                            heigth=lead_height['bot'],
                            width=conn_width,
                            angle=_angle,
                            offsets = {'dx': offsets['bot_dx'], 
                                       'dy': offsets['bot_dy']},
                            )
            conn_shapes.append((pya.DTrans(0, False, center.x,center.y) * conn_bot).to_itype(dbu))
        
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
