import pya
from numpy import cos, sin, radians, linspace, sign, linspace
from math import pi

# Parametric Manhattan Josephson Junction
# Copyright: TII QRC/QFoundry 2023
# Juan E. Villegas, Nov. 2023

from kqcircuits.util.symmetric_polygons import polygon_with_vsym

class Manhattan(pya.PCellDeclarationHelper):

    def __init__(self):
        super(Manhattan, self).__init__()
        self.set_paramters()

    def display_text_impl(self):
        return "Manhattan: A parameteric manhattan josephson jucntion"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        self._Manhattan()
  
    def set_paramters(self):
        self.param("l_layer", self.TypeLayer, "Layer", default = pya.LayerInfo(2, 0))
        self.param("angle", self.TypeDouble, "Global angle of the junction pads", default = 0.0)
        self.param("inner_angle", self.TypeDouble, "Angle between junction pads", default = 90.0)
        self.param("junction_width_t", self.TypeDouble, "Top jucntion width", default = 0.3, unit="μm",hidden=False)
        self.param("junction_width_b", self.TypeDouble, "Bottom jucntion width", default = 0.3, unit="μm",hidden=False)
        self.param("junction_y_offset", self.TypeDouble, "Vertical Offset of the jucntion position", default = 0.0, unit="μm",hidden=False)    
        self.param("finger_overshoot",self.TypeDouble, "Length of fingers after the junction.", default=2.0, unit="μm", hidden=False)
        self.param("finger_overlap",self.TypeDouble, "Length of fingers inside the pads.", default=1.0, unit="μm",hidden=True)
        self.param("finger_size",self.TypeDouble, "Length of fingers (without overshoot).", default=10.0, unit="μm")
        self.param("round_pad", self.TypeBoolean, "Pad has round edges", default=True, hidden=True)
        self.param("pad_radius", self.TypeDouble, "Pad edge radius", default=2.0, hidden=True)
        self.param("conn_width", self.TypeDouble, "Connector pad width", default=5.0, hidden=True)
        self.param("conn_height", self.TypeDouble, "Connector pad height", default=20.0, hidden=False)
        self.param("draw_cap", self.TypeBoolean, "Include capacitor", default=True)
        self.param("draw_patch", self.TypeBoolean, "Include patches", default=True)
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


    def arc(r, start=0, stop=pi/2, n=64):
        """
            r: radius
            start/stop: angle in radians
            n: number of corners in full circle
        """
        n_steps = max(round(abs(stop - start) * n / (2 * pi)), 1)
        step = (stop - start) / n_steps
        r_corner = r / cos(step / 2)
        angles = linspace(start,stop,n_steps+2)
        points = []
        for alpha in angles:
            points.append(pya.DPoint(r_corner * cos(alpha), r_corner * sin(alpha)))
        return points

    def _draw_junction(self, center=pya.DPoint(0, 0)):
        _angle = radians(self.angle)
        _inner_angle = radians(self.inner_angle)

        ddb = self.junction_width_b
        ddt = self.junction_width_t
        size= self.finger_size
        
        if self.mirror_offset:
            ddt += self.offset_compensation * cos(_angle)
        else:
            ddb += self.offset_compensation * cos(_angle)
        
        def finger_points(size,width, angle):
            fo_x = (self.finger_overshoot) * cos(angle) 
            fo_y = self.finger_overshoot * sin(angle) 
            pl_x = (self.finger_overlap) * cos(angle)   
            pl_y = (self.finger_overlap) * sin(angle)   
            
            dx = width/2*sin(angle)
            dy = width/2*cos(angle)
            
            end_x = size*cos(angle)
            end_y = size*sin(angle)
            
            return [
                pya.DPoint(-dx-fo_x, +dy-fo_y),
                pya.DPoint(dx-fo_x, -dy-fo_y),
                pya.DPoint(end_x+dx+pl_x, end_y-dy+pl_y),
                pya.DPoint(end_x-dx+pl_x, end_y+dy+pl_y),
            ]

        finger_bottom = pya.DTrans(0, 0) * pya.DPolygon(finger_points(size,ddb,_angle-(_inner_angle)))
        finger_top = pya.DTrans(0, 0) * pya.DPolygon(finger_points(size,ddt, _angle))
        
        junction_shapes = [ (pya.DTrans(0, False, center.x,center.y) * finger_top).to_itype(self.layout.dbu),
                            (pya.DTrans(0, False, center.x,center.y) * finger_bottom).to_itype(self.layout.dbu)]
        
        return junction_shapes     
        
    def _draw_cap(self):
        cap_shape = []
        cap_h = self.cap_h
        rounding_params = {
            "rinner": 5,  # inner corner rounding radius
            "router": 10,  # outer corner rounding radius
            "n": 64,  # number of point per rounded corner
        }
        
        metal_cap_pts_left = [
            pya.DPoint(-self.cap_w / 2, self.cap_gap/2.0),
            pya.DPoint(-self.cap_w / 2, self.cap_gap/2.0+cap_h)
        ]
        
        metal_cap_shape = polygon_with_vsym(metal_cap_pts_left)
        self._round_corners_and_append(metal_cap_shape, cap_shape, rounding_params)
        self._round_corners_and_append(metal_cap_shape*pya.DTrans(2,False,0,0), cap_shape, rounding_params) 
        return cap_shape
        
    def _draw_patch_open(self, gap=2, center=pya.DPoint(0, 0)):
        size = self.finger_size
        conn_width = self.conn_width
        conn_height = self.conn_height
        _angle = radians(self.angle)
        _inner_angle = radians(self.inner_angle)
        
        def patch_points(heigth, size, angle,rot=0, round = True):
            end_x = size*cos(angle)
            end_y = size*sin(angle)
        
            polygon = pya.DTrans(0,False, end_x, end_y)*pya.DTrans(rot,False, 0, 0) * pya.DPolygon([
                pya.DPoint(-conn_width/2-gap, 0),
                pya.DPoint(-conn_width/2-gap, heigth+gap),
                pya.DPoint(conn_width/2+gap, heigth+gap),
                pya.DPoint(conn_width/2+gap, 0),
            ])
            if True:
                polygon = polygon.round_corners(1, 1, 64)
            return polygon
            
        patch_top = pya.DTrans(0,False,0, -1) * (patch_points(heigth=conn_height+self.cap_gap/2.0*cos(_angle),size=size,  angle=_angle))
        patch_bot = pya.DTrans(0,False,0, 1 ) * (patch_points(heigth=conn_height+self.cap_gap/2.0*sin(_angle),size=size,  angle=_angle-(_inner_angle),rot=2))
        
        patch_top = patch_top.round_corners(1, 1, 64)
        patch_bot = patch_bot.round_corners(1, 1, 64)
        
        return [(pya.DTrans(0, False, center.x,center.y) * patch_top).to_itype(self.layout.dbu),
                (pya.DTrans(0, False, center.x,center.y) * patch_bot).to_itype(self.layout.dbu)]

    def _draw_patch(self, patch_clearance=10.0, center=pya.DPoint(0, 0)):
        size = self.finger_size
        gap = self.cap_gap
        
        patch_width = patch_clearance*2+self.conn_width
        conn_height = self.conn_height
        _angle = radians(self.angle)
        _inner_angle = radians(self.inner_angle)
        
        def patch_points(heigth, size, angle,rot=0, round = False):
            end_x = size*cos(angle)
            end_y = size*sin(angle)
        
            span_y = heigth+patch_clearance+(end_y)*sign(end_y)
            
            polygon = pya.DTrans(0,False, end_x, 0)*pya.DTrans(rot,False, 0, 0) * pya.DPolygon([
                pya.DPoint(-patch_width/2, gap/2),
                pya.DPoint(patch_width/2, gap/2),
                pya.DPoint(patch_width/2, gap/2+span_y),
                pya.DPoint(-patch_width/2, gap/2+span_y),
            ])
            return polygon
        
        def patch_scratches(heigth, size, angle,rot=0, round = False):
            scratch_w = 0.5
            end_x = size*cos(angle)
            end_y = size*sin(angle)
        
            span_y = heigth+patch_clearance+(end_y)*sign(end_y)
            
            scratch_ang = abs(pi/4-abs(_angle))
            scratch_y1 = patch_width/2*sin(scratch_ang)
            scratch_x1 = patch_width/2
            y0 = gap/2+scratch_y1
            
            
            dy = scratch_w*cos(scratch_ang)
            dx = -scratch_w*sin(scratch_ang)
            
            polygon = pya.DTrans(0,False, end_x, 0)*pya.DTrans(rot,False, 0, 0) * pya.DPolygon([
                pya.DPoint(-scratch_x1+dx/2, y0-scratch_y1+dy/2),
                pya.DPoint(scratch_x1+dx/2, y0+scratch_y1+dy/2),
                pya.DPoint(scratch_x1-dx/2, y0+scratch_y1-dy/2),
                pya.DPoint(-scratch_x1-dx/2, y0-scratch_y1-dy/2),
            ])
            return polygon
        patches = []
        if self.patch_scratch:
            dy_arr = linspace(0.0,10.0,5)
            for dy in dy_arr:
              patches.append((pya.DTrans(0,False,center.x,dy) * (patch_scratches(heigth=conn_height,size=size,  angle=_angle))).to_itype(self.layout.dbu))
            for dy in dy_arr:
              patches.append((pya.DTrans(0,False,center.x, -dy) * (patch_scratches(heigth=conn_height,size=size,  angle=_angle-(_inner_angle),rot=2))).to_itype(self.layout.dbu))  
        else:    
            patches = [pya.DTrans(0,False,center.x, 0) * (
                        patch_points( heigth=conn_height-self.cap_gap/2.0*sin(_angle)+patch_clearance,
                                        size=size,  
                                        angle=_angle)
                        ).to_itype(self.layout.dbu),
                        pya.DTrans(0,False,center.x, 0) * (
                        patch_points( heigth=conn_height-self.cap_gap/2.0*cos(_angle)+patch_clearance,
                                        size=size,  
                                        angle=_angle-(_inner_angle),rot=2)
                        ).to_itype(self.layout.dbu)]

        return patches
                
    def _draw_connectors(self, center=pya.DPoint(0, 0)):
        
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
            end_x = size*cos(_angle)
            end_y = size*sin(_angle)
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
              polygon = polygon.round_corners(self.pad_radius, self.pad_radius, 64)
            return polygon

        conn_top = pya.DTrans(0,False,0, -1) * (connector_points(tip_w=2.0,width=conn_width,angle=_angle,conn_height=conn_height+self.cap_gap/2.0-self.finger_size*sin(_angle)))
        conn_bot = pya.DTrans(0,False,0, 1) * (connector_points(tip_w=2.0,width=conn_width, angle=_angle-_inner_angle,rot=2,conn_height=conn_height+self.cap_gap/2.0+self.finger_size*sin(_angle-_inner_angle)))
        
        connector_shapes = [ (pya.DTrans(0, False, center.x,center.y) * conn_top).to_itype(self.layout.dbu),
                            (pya.DTrans(0, False, center.x,center.y) * conn_bot).to_itype(self.layout.dbu)]
        
        # Add thick extensions
        
        return connector_shapes 
               
    def _round_corners_and_append(self, polygon, polygon_list, rounding_params):
            """Rounds the corners of the polygon, converts it to integer coordinates, and adds it to the polygon list."""
            polygon = polygon.round_corners(rounding_params["rinner"], rounding_params["router"], rounding_params["n"])
            polygon_list.append(polygon.to_itype(self.layout.dbu))  
            
    def _add_shapes(self, shapes, layer):
            """Merge shapes into a region and add it to layer."""
            region:pya.Region = pya.Region(shapes).merged()
            self.cell.shapes(layer).insert(region)
            return region    
            
    def _substract_shapes(self, shapesA, shapesB, layer):
            """Merge shapes into a region and add it to layer."""
            region = pya.Region(shapesA).merged()-pya.Region(shapesB).merged()
            self.cell.shapes(layer).insert(region)
            return region

    def _Manhattan(self): 
            """Draws the Manhattan junction"""
            dbu = self.layout.dbu
            
            #Junction
            finger_shapes = self._draw_junction(pya.DPoint(0, 0)) 
            conn_shapes = self._draw_connectors(pya.DPoint(0, 0))
            layer = self.layout.layer(self.l_layer)
            self._add_shapes(finger_shapes, layer)
            self._add_shapes(conn_shapes, layer)
            
            # Capacitor
            if self.draw_cap:
                cap_shape = self._draw_cap()
                patch_open_shape = []
                patch_shape = []
                # Patches
                if self.draw_patch:
                    patch_open_shape = self._draw_patch_open(gap = self.patch_gap, center = pya.DPoint(0, 0))
                    patch_shape = self._draw_patch(self.patch_clearance, center = pya.DPoint(0, 0))
                
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
                self._add_shapes(patch_shape, layer)  
  
if __name__ == "__main__":
    # You need to reload the library to see the changes in the PCell 
    from qfoundry.scripts import test_pcell, PDK_Lib

    pcell_decl = QfoundryManhattan
    pcell_params = {
              "junction_width_t":0.1, 
              "junction_width_b":0.2, 
              "angle": 0.,
              "draw_cap":True,
              "patch_scratch":True,}
    pcell_trans = pya.Trans(pya.Trans.R0, 0.0, 0.0)

    test_pcell(pcell_decl, pcell_params, pcell_trans)
