import pya

# This code is part of Starfish PDK
# A PDK based om the KQCircuits packge.
# Copyright (C) 2023 TII
# Based on code form the KQCircuits Salt Pacackage
#

from math import sqrt
from autologging import logged
from kqcircuits.pya_resolver import pya
from kqcircuits.util.parameters import Param, pdt
from kqcircuits.junctions.junction import Junction
from kqcircuits.util.symmetric_polygons import polygon_with_vsym
from numpy import cos, sin, radians

@logged
class QfoundryManhattan(Junction):
    """The PCell declaration for a Manhattan style single junction.
    """

    finger_overshoot = Param(pdt.TypeDouble, "Length of fingers after the junction.", 1.0, unit="μm", hidden = False)
    include_base_metal_gap = Param(pdt.TypeBoolean, "Include base metal gap layer.", True)
    shadow_margin = Param(pdt.TypeDouble, "Shadow layer margin near the the pads.", 0.5, unit="μm")
    separate_junctions = Param(pdt.TypeBoolean, "Junctions to separate layer.", False)
    offset_compensation = Param(pdt.TypeDouble, "Junction lead offset from junction width", 0, unit="μm")
    mirror_offset = Param(pdt.TypeBoolean, "Move the junction lead offset to the other lead", False)
    finger_overlap = Param(pdt.TypeDouble, "Length of fingers inside the pads.", 1.0, unit="μm")
    height = Param(pdt.TypeDouble, "Height of the junction element.", 22.0, unit="μm")
    width = Param(pdt.TypeDouble, "Width of the junction element.", 22.0, unit="μm")
    
    junction_width_t = Param(pdt.TypeDouble, "Top jucntion width", 0.2, unit="μm")
    junction_width_b = Param(pdt.TypeDouble, "Bottom jucntion width", 0.2, unit="μm")
    angle = Param(pdt.TypeDouble, "Junction angle [0 45]", 45.0, unit="[deg]")
    
    
    def build(self):
        self.produce_manhattan_junction()

    def produce_manhattan_junction(self):

        # geometry constants
        p_height = 6  # pad height
        p_width = self.a + 2  # pad width

        # corner rounding parameters
        rounding_params = {
            "rinner": 0.5,  # inner corner rounding radius
            "router": 0.5,  # outer corner rounding radius
            "n": 64,  # number of point per rounded corner
        }

        junction_shapes_top = []
        junction_shapes_bottom = []
        shadow_shapes = []

        # create rounded bottom part
        y0 = self.height / 2 - 9
        bp_pts_left = [
            pya.DPoint(-p_width / 2, y0),
            pya.DPoint(-p_width / 2, y0 + p_height)
        ]
        bp_shape = polygon_with_vsym(bp_pts_left)
        self._round_corners_and_append(bp_shape, junction_shapes_bottom, rounding_params)

        bp_shadow_pts_left = [
            bp_pts_left[0] + pya.DPoint(-self.shadow_margin, -self.shadow_margin),
            bp_pts_left[1] + pya.DPoint(-self.shadow_margin, self.shadow_margin)
        ]
        bp_shadow_shape = polygon_with_vsym(bp_shadow_pts_left)
        self._round_corners_and_append(bp_shadow_shape, shadow_shapes, rounding_params)

        # create rounded top part
        tp_shape = pya.DTrans(0, False, 0, 12) * polygon_with_vsym(bp_pts_left)
        self._round_corners_and_append(tp_shape, junction_shapes_top, rounding_params)

        tp_shadow_shape = pya.DTrans(0, False, 0, 12) * polygon_with_vsym(bp_shadow_pts_left)
        self._round_corners_and_append(tp_shadow_shape, shadow_shapes, rounding_params)

        # create rectangular junction-support structures and junctions
        self._make_junction(pya.DPoint(0, self.height / 2 + 2.8), self.height / 2 - 5, 0)
        self._add_shapes(junction_shapes_bottom, "SIS_junction")
        self._add_shapes(junction_shapes_top, "SIS_junction")
        self._add_shapes(shadow_shapes, "SIS_shadow")
        self._produce_ground_metal_shapes()
        self._produce_ground_grid_avoidance()
        self._add_refpoints()

    def _make_junction(self, top_corner, b_corner_y, finger_margin=0):
        """Create junction fingers and add them to some SIS layer.
        Choose 'SIS_junction' layer by default but 'SIS_junction_2' if ``separate_junctions`` is True.
        """
        _angle = radians(self.angle)
        jx = top_corner.x - (top_corner.y - b_corner_y) / 2
        jy = (top_corner.y + b_corner_y) / 2
        ddb = self.junction_width_b * cos(_angle)
        ddt = self.junction_width_t * cos(_angle)
        if self.mirror_offset:
            ddt += self.offset_compensation * cos(_angle)
        else:
            ddb += self.offset_compensation * cos(_angle)
        
        def finger_points(size, angle):
            fo_x = self.finger_overshoot * cos(_angle) - 1.1
            fo_y = self.finger_overshoot * sin(_angle) - 1.1
            pl_x = self.finger_overlap * cos(_angle) + 0.2  # plus length to connect despite of rounding
            pl_y = self.finger_overlap * sin(_angle) + 0.2  # plus length to connect despite of rounding
            
            return [
                pya.DPoint(top_corner.x + pl_x, top_corner.y + size + pl_y),
                pya.DPoint(top_corner.x + size + pl_x, top_corner.y + pl_y),
                pya.DPoint(jx - fo_x, jy - fo_y - size*sin(_angle)),
                pya.DPoint(jx - fo_x - size*cos(_angle), jy - fo_y),
            ]

        finger_bottom = pya.DTrans(-jx, -jy) * pya.DPolygon(finger_points(ddb,_angle ))
        finger_top = pya.DTrans(-jx, -jy) * pya.DPolygon(finger_points(ddt, _angle-90))

        junction_shapes = [(pya.DTrans(jx - finger_margin, jy) * finger_top).to_itype(self.layout.dbu),
                           (pya.DTrans(0, False, jx-2*top_corner.x, jy) * finger_top).to_itype(self.layout.dbu),
                           (pya.DTrans(3, False, jx - finger_margin, jy+2.2) * finger_bottom).to_itype(self.layout.dbu),
                           (pya.DTrans(3, False, jx-2*top_corner.x, jy+2.2) * finger_bottom).to_itype(self.layout.dbu)]

        junction_region = pya.Region(junction_shapes).merged()
        layer_name = "SIS_junction_2" if self.separate_junctions else "SIS_junction"
        self.cell.shapes(self.get_layer(layer_name)).insert(junction_region)

        # place refpoint at the middle of the junctions
        self.refpoints["c"] = pya.DPoint(jx + 1.1 - finger_margin, jy + 1.1)

    def _add_shapes(self, shapes, layer):
        """Merge shapes into a region and add it to layer."""
        region = pya.Region(shapes).merged()
        self.cell.shapes(self.get_layer(layer)).insert(region)

    def _add_refpoints(self):
        """Adds the "origin_squid" refpoint and port "common"."""
        self.refpoints["origin_squid"] = pya.DPoint(0, 0)
        self.add_port("common", pya.DPoint(0, self.height))

    def _produce_ground_metal_shapes(self):
        """Produces hardcoded shapes in metal gap and metal addition layers."""
        # metal additions bottom
        x0 = - self.a / 2
        y0 = self.height / 2
        bottom_pts = [
            pya.DPoint(x0 + 2, y0 - 7),
            pya.DPoint(x0 + 2, y0 - 5),
            pya.DPoint(x0 + 3, y0 - 5),
            pya.DPoint(x0 + 3, y0 - 4),
            pya.DPoint(x0, y0 - 4),
            pya.DPoint(x0, 0)
        ]
        shape = polygon_with_vsym(bottom_pts)
        self.cell.shapes(self.get_layer("base_metal_addition")).insert(shape)
        # metal additions top
        top_pts = [
            pya.DPoint(x0 + 2, y0 + 7),
            pya.DPoint(x0 + 2, y0 + 5),
            pya.DPoint(x0 + 3, y0 + 5),
            pya.DPoint(x0 + 3, y0 + 4),
            pya.DPoint(x0, y0 + 4),
            pya.DPoint(x0, self.height),
        ]
        shape = polygon_with_vsym(top_pts)
        self.cell.shapes(self.get_layer("base_metal_addition")).insert(shape)
        # metal gap
        if self.include_base_metal_gap:
            pts = bottom_pts + [pya.DPoint(-self.width/2, 0), pya.DPoint(-self.width/2, self.height)] + top_pts[::-1]
            shape = polygon_with_vsym(pts)
            self.cell.shapes(self.get_layer("base_metal_gap_wo_grid")).insert(shape)

    def _produce_ground_grid_avoidance(self):
        """Add ground grid avoidance."""
        w = self.cell.dbbox().width()
        h = self.cell.dbbox().height()
        protection = pya.DBox(-w / 2 - self.margin, - self.margin, w / 2 + self.margin, h + self.margin)
        self.cell.shapes(self.get_layer("ground_grid_avoidance")).insert(protection)

    def _round_corners_and_append(self, polygon, polygon_list, rounding_params):
        """Rounds the corners of the polygon, converts it to integer coordinates, and adds it to the polygon list."""
        polygon = polygon.round_corners(rounding_params["rinner"], rounding_params["router"], rounding_params["n"])
        polygon_list.append(polygon.to_itype(self.layout.dbu))

  
  



