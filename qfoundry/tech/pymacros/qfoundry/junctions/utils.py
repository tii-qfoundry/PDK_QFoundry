import pya
from numpy import cos, sin, radians, linspace, sign
from math import pi

from kqcircuits.util.symmetric_polygons import polygon_with_vsym
from qfoundry.utils import _add_shapes, _round_corners_and_append

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

def draw_junction(angle, inner_angle, junction_width_b, junction_width_t, finger_size, mirror_offset, offset_compensation, finger_overshoot, finger_overlap, 
  center=pya.DPoint(0, 0), dbu = 0.001) -> pya.DPolygon:
    _angle = radians(angle)
    _inner_angle = radians(inner_angle)

    ddb = junction_width_b
    ddt = junction_width_t
    size= finger_size
    
    if mirror_offset:
        ddt += offset_compensation * cos(_angle)
    else:
        ddb += offset_compensation * cos(_angle)
    
    def finger_points(size,width, angle):
        fo_x = (finger_overshoot) * cos(angle) 
        fo_y = finger_overshoot * sin(angle) 
        pl_x = (finger_overlap) * cos(angle)   
        pl_y = (finger_overlap) * sin(angle)   
        
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
    
    junction_shapes = [ (pya.DTrans(0, False, center.x,center.y) * finger_top).to_itype(dbu),
                        (pya.DTrans(0, False, center.x,center.y) * finger_bottom).to_itype(dbu)]
    
    return junction_shapes

def draw_pad(cap_w, cap_h, cap_gap, dbu):
    cap_shape = []
    rounding_params = {
        "rinner": 5,  # inner corner rounding radius
        "router": 10,  # outer corner rounding radius
        "n": 64,  # number of point per rounded corner
    }
    
    metal_cap_pts_left = [
        pya.DPoint(-cap_w / 2, cap_gap/2.0),
        pya.DPoint(-cap_w / 2, cap_gap/2.0+cap_h)
    ]
    
    metal_cap_shape = polygon_with_vsym(metal_cap_pts_left)
    _round_corners_and_append(metal_cap_shape, cap_shape, rounding_params, dbu = dbu)
    _round_corners_and_append(metal_cap_shape*pya.DTrans(2,False,0,0), cap_shape, rounding_params, dbu = dbu) 
    return cap_shape





def _patch_scratches(gap, patch_width, conn_height, patch_clearance, size, angle, rot=0, round = False):
    scratch_w = 0.5
    end_x = size*cos(angle)
    end_y = size*sin(angle)

    span_y = conn_height+patch_clearance+(end_y)*sign(end_y)
    
    scratch_ang = abs(pi/4-abs(angle))
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

def draw_patch(finger_size, cap_gap, conn_width, conn_height, angle, inner_angle, patch_scratch, patch_clearance=10.0, 
  center=pya.DPoint(0, 0), dbu=0.001) -> pya.DPolygon:
    size = finger_size
    gap = cap_gap
    
    patch_width = patch_clearance*2+conn_width
    _angle = radians(angle)
    _inner_angle = radians(inner_angle)
    
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
    
    patches = []
    if patch_scratch:
        dy_arr = linspace(0.0,10.0,5)
        for dy in dy_arr:
            patches.append((pya.DTrans(0,False,center.x,dy) * (_patch_scratches(gap, patch_width, conn_height, patch_clearance, size=size,  angle=_angle))).to_itype(dbu))
        for dy in dy_arr:
            patches.append((pya.DTrans(0,False,center.x, -dy) * (_patch_scratches(gap, patch_width, conn_height, patch_clearance, size=size,  angle=_angle-(_inner_angle),rot=2))).to_itype(dbu))  
    else:    
        patches = [pya.DTrans(0,False,center.x, 0) * (
                    patch_points( heigth=conn_height-cap_gap/2.0*sin(_angle)+patch_clearance,
                                    size=size,  
                                    angle=_angle)
                    ).to_itype(dbu),
                    pya.DTrans(0,False,center.x, 0) * (
                    patch_points( heigth=conn_height-cap_gap/2.0*cos(_angle)+patch_clearance,
                                    size=size,  
                                    angle=_angle-(_inner_angle),rot=2)
                    ).to_itype(dbu)]

    return patches

