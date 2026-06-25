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
  bottom_lead_comp = 0, center=pya.DPoint(0, 0), dbu = 0.001) -> pya.DPolygon:
    _angle = radians(angle)
    _inner_angle = radians(inner_angle)

    ddb = junction_width_b
    ddt = junction_width_t
    size= finger_size
    
    if mirror_offset:
        ddt += offset_compensation * cos(_angle)
    else:
        ddb += offset_compensation * cos(_angle)
    
    def finger_points(size,width, angle, lead_comp=0):
        fo_x = (finger_overshoot) * cos(angle) 
        fo_y = finger_overshoot * sin(angle) 
        pl_x = (finger_overlap + lead_comp) * cos(angle)   
        pl_y = (finger_overlap + lead_comp) * sin(angle)   
        
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

    finger_bottom = pya.DTrans(0, 0) * pya.DPolygon(finger_points(size,ddb,_angle-(_inner_angle), lead_comp=bottom_lead_comp))
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

def draw_patch(finger_size, cap_gap, conn_width, conn_height, angle, inner_angle, patch_scratch, patch_clearance=10.0, finger_overlap=1.0,
  center=pya.DPoint(0, 0), dbu=0.001) -> pya.DPolygon:
    size = finger_size
    gap = cap_gap
    
    patch_width = patch_clearance*2+conn_width
    _angle = radians(angle)
    _inner_angle = radians(inner_angle)
    
    def patch_points(heigth, size, angle, direction=1, finger_overlap=1):
        end_x = size*cos(angle)
        # Anchored at the capacitor gap edge (not the connector tip), since that
        # edge - not the finger tip - is the fixed reference the lead crosses.
        gap_edge_y = gap/2 if direction > 0 else -gap/2
        y_size = heigth+patch_clearance if direction > 0 else -(heigth+patch_clearance)
        # Matches the +1/-1 nudge that draw_connectors applies to the top/bottom
        # connector lead respectively, so the patch stays aligned to the lead.
        fudge = -finger_overlap if direction > 0 else finger_overlap

        polygon = pya.DTrans(0,False, end_x, gap_edge_y+fudge) * pya.DPolygon([
            pya.DPoint(-patch_width/2, 0),
            pya.DPoint(patch_width/2, 0),
            pya.DPoint(patch_width/2, y_size),
            pya.DPoint(-patch_width/2, y_size),
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
        bottom_angle = _angle - _inner_angle
        # Both anchor at the gap edge now, so the span is simply conn_height -
        # no more sin/cos cancellation needed to offset the connector tip's angle.
        top_height = conn_height
        bot_height = conn_height
        patches = [pya.DTrans(0,False,center.x, center.y) * (
                    patch_points(heigth=top_height, size=size, angle=_angle, direction=1, finger_overlap=finger_overlap)
                    ).to_itype(dbu),
                    pya.DTrans(0,False,center.x, center.y) * (
                    patch_points(heigth=bot_height, size=size, angle=bottom_angle, direction=-1, finger_overlap=finger_overlap)
                    ).to_itype(dbu)]

    return patches

def draw_patch_openning(finger_size, conn_width, heigth, angle, inner_angle, gap=2, direction = +1, finger_overlap=1, round_radius=0) -> pya.DPolygon:
    size = finger_size
    _angle = radians(angle)
    _inner_angle = radians(inner_angle)

    def patch_points(heigth, size, angle,rot=0, round = True):
        end_x = size*cos(angle)
        end_y = size*sin(angle)
        y_size = heigth+gap if direction>0 else -(heigth+gap)
        polygon = pya.DTrans(0,False, end_x, end_y) * pya.DPolygon([
            pya.DPoint(-conn_width/2-gap, 0),
            pya.DPoint(-conn_width/2-gap, y_size),
            pya.DPoint(conn_width/2+gap, y_size),
            pya.DPoint(conn_width/2+gap, 0),
        ])
        if True:
            polygon = polygon.round_corners(round_radius, round_radius, 32)
        return polygon

    # Fix the patch position to account for the finger overlap, so that the patch is aligned with the lead.
    fudge = -finger_overlap if direction > 0 else finger_overlap
    patch = pya.DTrans(0,False,0, fudge) * (patch_points(heigth=heigth, size=size,angle=_angle))

    return patch