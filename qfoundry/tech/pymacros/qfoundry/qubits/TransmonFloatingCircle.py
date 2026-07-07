"""Transmon PCell with rectangular islands and radial CPW couplers.

Layers:
    30/0 -> metal
    1/0 -> keepout (circle + CPW gaps - metal)

Extras:
    - Readout selector: none, top, bottom, both
    - Flux cutout selector: none, left, right, both
"""

import pya
import math

# Finger/center overlap (um).
_CPW_OVERLAP = 5.0

# Readout angle per island.
_READOUT_ANGLE = {"top": 90.0, "bottom": 270.0}


class TransmonFloatingCircle(pya.PCellDeclarationHelper):

    def __init__(self):
        super().__init__()
        self.set_parameters()

    def display_text_impl(self):
        return f"Transmon(span={self.transmon_span:.0f}μm, α={self.coupler_angle:.0f}°)"

    def coerce_parameters_impl(self):
        self.coupler_angle = max(30.0, min(60.0, float(self.coupler_angle)))
        self.island_gap = max(1.0, float(self.island_gap))
        self.transmon_span = max(50.0, float(self.transmon_span))
        self.coupler_inclusion = max(1.0, min(float(self.coupler_inclusion),
                                              self.transmon_span - 1.0))
        self.depth_flux_cutout = max(0.0, min(float(self.depth_flux_cutout),
                              self.transmon_span - 1.0))
        self.flux_cutout_base = max(1.0, float(self.flux_cutout_base))
        self.flux_cutout_angle = max(-30.0, min(float(self.flux_cutout_angle), 30.0))
        self.flux_cutout_radius = max(0.0, float(self.flux_cutout_radius))

        # Normalize readout selector.
        ro = self.readout_islands
        if isinstance(ro, (list, tuple)):
            vals = {str(s).strip().lower() for s in ro}
            if {"top", "bottom"}.issubset(vals):
                ro = "both"
            elif "bottom" in vals:
                ro = "bottom"
            elif "none" in vals:
                ro = "none"
            else:
                ro = "top"
        else:
            ro = str(ro).strip().lower()
            if ro not in ("none", "top", "bottom", "both"):
                ro = "top"
        self.readout_islands = ro

        fs = str(self.flux_input_side).strip().lower()
        if fs not in ("none", "left", "right", "both"):
            fs = "both"
        self.flux_input_side = fs

    def set_parameters(self):
        # Layers
        self.param("metal_layer", self.TypeLayer, "Metal layer (positive)",
                   default=pya.LayerInfo(30, 0))
        self.param("metal_n_layer", self.TypeLayer, "Ground plane negative layer",
                   default=pya.LayerInfo(1, 0))
        self.param("port_layer", self.TypeLayer, "Port layer",
                   default=pya.LayerInfo(997, 0), hidden=True)
        self.param("devrec_layer", self.TypeLayer, "Device recognition layer",
                   default=pya.LayerInfo(68, 0), hidden=True)
        self.param("ground_exclude_layer", self.TypeLayer, "Ground exclusion layer",
                   default=pya.LayerInfo(133, 1), hidden=True)

        # Islands
        self.param("island_width", self.TypeDouble, "Island width [um]", default=400.0)
        self.param("island_height", self.TypeDouble, "Island height [um]", default=180.0)
        self.param("island_gap", self.TypeDouble,
                   "Vertical gap between islands [um]", default=40.0)
        self.param("corner_radius", self.TypeDouble,
                   "Island corner rounding radius (outer + inner slot corners) [um]",
                   default=25.0)

        # Keepout
        self.param("transmon_span", self.TypeDouble,
                   "Radius of keepout circle around transmon [um]", default=300.0)
        self.param("keepout_corner_radius", self.TypeDouble,
                   "Rounding of keepout inner corners at CPW-circle junctions [um]",
                   default=13.0)
        
        # Flux cutout
        p_flux_side = self.param("flux_input_side", self.TypeString,
                     "Flux cutout side: left, right, or both",
                     default="both")
        p_flux_side.add_choice("None", "none")
        p_flux_side.add_choice("Left", "left")
        p_flux_side.add_choice("Right", "right")
        p_flux_side.add_choice("Both", "both")
        self.param("depth_flux_cutout", self.TypeDouble,
               "Flux cutout depth into keepout [um]", default=88.0)
        self.param("flux_cutout_base", self.TypeDouble,
                   "Flux cutout base width at inner (deep) edge [um]", default=94.0)
        self.param("flux_cutout_angle", self.TypeDouble,
                   "Flux cutout wall angle [deg, -30..30] (signed)", default=12.0)
        self.param("flux_cutout_radius", self.TypeDouble,
               "Flux cutout C-termination radius [um] (0 = flat)", default=0.0)

        # Main couplers
        self.param("coupler_angle", self.TypeDouble,
                   "Base coupler angle [deg, 30-60]; mirrored to 4 quadrant positions",
                   default=45.0)
        self.param("coupler_wg_width", self.TypeDouble,
                   "Coupler CPW center conductor width [um]", default=15.0)
        self.param("coupler_wg_gap", self.TypeDouble,
                   "Coupler CPW gap (outside circle) [um]", default=7.5)
        self.param("coupler_inclusion", self.TypeDouble,
                   "Coupler finger depth inside circle from boundary [um]", default=120.0)
        self.param("coupler_gap", self.TypeDouble,
                   "Capacitive gap between finger tip and island edge [um]", default=10.0)
        self.param("coupler_extensions", self.TypeList,
                   "Waveguide extension beyond circle [um] (1 value or 4 per coupler)",
                   default=[50.0])

        # Readout couplers
        p_readout = self.param("readout_islands", self.TypeString,
                       "Readout target: top, bottom, or both",
                       default="bottom")
        p_readout.add_choice("None", "none")
        p_readout.add_choice("Top", "top")
        p_readout.add_choice("Bottom", "bottom")
        p_readout.add_choice("Both", "both")
        self.param("readout_wg_width", self.TypeDouble,
                   "Readout CPW center conductor width [um]", default=15.0)
        self.param("readout_wg_gap", self.TypeDouble,
                   "Readout CPW gap [um]", default=7.5)
        self.param("readout_gap", self.TypeDouble,
                   "Capacitive gap from T-bar inner edge to island face [um]", default=30.0)
        self.param("readout_width", self.TypeDouble,
                   "T-bar thickness along radial direction [um]", default=30.0)
        self.param("readout_span", self.TypeDouble,
                   "T-bar total transverse length [um]", default=180.0)
        self.param("readout_extension", self.TypeDouble,
                   "Readout waveguide extension beyond circle [um]", default=100.0)

        # Auxiliary
        self.param("margin", self.TypeDouble,
                   "Ground exclusion margin beyond device [um]", default=10.0)
        self.param("resolution", self.TypeInt,
                   "Circle polygon resolution (vertices)", default=48)

    def produce_impl(self):
        dbu = self.layout.dbu

        # Four mirrored coupler angles.
        a = float(self.coupler_angle)
        coupler_angles = [a, 180.0 - a, 180.0 + a, 360.0 - a]

        # Broadcast extension list to 4 values.
        raw_ext = [float(x) for x in (list(self.coupler_extensions)
                                       if self.coupler_extensions else [100.0])]
        if len(raw_ext) < 4:
            raw_ext += [raw_ext[-1]] * (4 - len(raw_ext))
        ext_list = raw_ext[:4]

        # Readout target(s).
        ro_sel = str(self.readout_islands).strip().lower()
        if ro_sel == "none":
            ro_isl = []
        elif ro_sel == "both":
            ro_isl = ["top", "bottom"]
        elif ro_sel == "bottom":
            ro_isl = ["bottom"]
        else:
            ro_isl = ["top"]
        ro_angles = [_READOUT_ANGLE.get(s, 90.0) for s in ro_isl]
        n_ro = len(ro_isl)

        # Coupler fingers
        coupler_gap_dbu = int(self.coupler_gap / dbu)
        fingers = pya.Region()
        finger_list = []
        for angle in coupler_angles:
            f = self._radial_finger(angle, self.coupler_wg_width, dbu)
            fingers += f
            finger_list.append(f)

        # Raw islands with coupler slots.
        raw_islands = (self._raw_island("top", dbu) +
                       self._raw_island("bottom", dbu)).merged()
        for f in finger_list:
            raw_islands -= f.sized(coupler_gap_dbu)

        # Round island and slot corners.
        if self.corner_radius > 0.0:
            cr = int(self.corner_radius / dbu)
            island_region = raw_islands.round_corners(cr, cr, 64)
        else:
            island_region = raw_islands

        # Readout metal and CPW centers.

        readout_inner = pya.Region()
        for i in range(n_ro):
            readout_inner += self._readout_t_coupler(ro_angles[i], ro_isl[i], dbu)

        cpw_centers = pya.Region()
        for i, angle in enumerate(coupler_angles):
            cpw_centers += self._cpw_center(angle, ext_list[i],
                                            self.coupler_wg_width, dbu)
        for i in range(n_ro):
            cpw_centers += self._cpw_center(ro_angles[i],
                                            float(self.readout_extension),
                                            self.readout_wg_width, dbu)

        # Final metal region.
        metal = (island_region + fingers + readout_inner + cpw_centers).merged()

        # Build keepout core and optional flux opening.
        circle = pya.Region(self._circle_poly(self.transmon_span).to_itype(dbu))

        keepout_core = circle

        # Apply flux cutout before rounding.
        if self.depth_flux_cutout > 0.0:
            fs = str(self.flux_input_side).strip().lower()
            if fs == "none":
                pass
            elif fs == "both":
                keepout_core -= self._flux_cutout("left", dbu)
                keepout_core -= self._flux_cutout("right", dbu)
            else:
                keepout_core -= self._flux_cutout(fs, dbu)

        # Round opening corners before adding extensions.
        if self.keepout_corner_radius > 0.0:
            kr = int(self.keepout_corner_radius / dbu)
            keepout_core = keepout_core.round_corners(kr, kr, 64)

        # Add CPW gap strips.
        cpw_gaps = pya.Region()
        for i, angle in enumerate(coupler_angles):
            cpw_gaps += self._cpw_gaps(angle, ext_list[i],
                                       self.coupler_wg_width, self.coupler_wg_gap, dbu)
        for i in range(n_ro):
            cpw_gaps += self._cpw_gaps(ro_angles[i],
                                       float(self.readout_extension),
                                       self.readout_wg_width, self.readout_wg_gap, dbu)

        keepout_base = (keepout_core + cpw_gaps).merged()

        # Round keepout concave corners.
        if self.keepout_corner_radius > 0.0:
            kr = int(self.keepout_corner_radius / dbu)
            keepout_base = keepout_base.round_corners(kr, 0, 64)

        # Subtract metal from keepout.
        ground_neg = (keepout_base - metal).merged()

        # Write layers.
        self.cell.shapes(self.metal_layer).insert(metal)
        self.cell.shapes(self.metal_n_layer).insert(ground_neg)

        for i, angle in enumerate(coupler_angles):
            self.cell.shapes(self.port_layer).insert(
                self._port(angle, self.transmon_span + ext_list[i],
                           self.coupler_wg_width + 2.0 * self.coupler_wg_gap))
        for i in range(n_ro):
            self.cell.shapes(self.port_layer).insert(
                self._port(ro_angles[i],
                           self.transmon_span + float(self.readout_extension),
                           self.readout_wg_width + 2.0 * self.readout_wg_gap))

        full = (metal + ground_neg).merged()
        self.cell.shapes(self.devrec_layer).insert(full)
        margin_dbu = int(self.margin / dbu)
        self.cell.shapes(self.ground_exclude_layer).insert(full.sized(margin_dbu))

    def _rot(self, dpoly, angle_deg):
        """Rotate a DPolygon around origin."""
        return pya.DCplxTrans(1.0, angle_deg, False, 0, 0) * dpoly

    def _circle_poly(self, radius):
        pts = []
        n = self.resolution
        for i in range(n):
            ang = 2.0 * math.pi * i / n
            pts.append(pya.DPoint(radius * math.cos(ang), radius * math.sin(ang)))
        return pya.DPolygon(pts)

    def _raw_island(self, which, dbu):
        """Return unrounded top or bottom island."""
        w = self.island_width
        h = self.island_height
        g = self.island_gap / 2.0
        if which == "top":
            box = pya.DBox(-w / 2, g, w / 2, g + h)
        else:
            box = pya.DBox(-w / 2, -g - h, w / 2, -g)
        return pya.Region(pya.DPolygon(box).to_itype(dbu))

    def _radial_finger(self, angle_deg, width, dbu):
        """Return one rounded-tip radial finger on metal layer."""
        r_in = self.transmon_span - self.coupler_inclusion
        r_out = self.transmon_span + _CPW_OVERLAP
        box = pya.DBox(r_in, -width / 2.0, r_out, width / 2.0)
        ipoly = self._rot(pya.DPolygon(box), angle_deg).to_itype(dbu)
        if width > 0:
            rr = int((width / 2.0) / dbu)
            ipoly = ipoly.round_corners(0, rr, 32)
        return pya.Region(ipoly)

    def _cpw_center(self, angle_deg, extension, width, dbu):
        """Return CPW center strip on metal layer."""
        x0 = self._cpw_inward_start()
        x1 = self.transmon_span + extension
        box = pya.DBox(x0, -width / 2.0, x1, width / 2.0)
        return pya.Region(self._rot(pya.DPolygon(box), angle_deg).to_itype(dbu))

    def _cpw_gaps(self, angle_deg, extension, center_width, gap_width, dbu):
        """Return the two CPW gap strips on keepout layer."""
        hw = center_width / 2.0
        x0 = self._cpw_inward_start()
        x1 = self.transmon_span + extension
        top_gap = pya.DBox(x0, hw, x1, hw + gap_width)
        bot_gap = pya.DBox(x0, -hw - gap_width, x1, -hw)
        r_top = pya.Region(self._rot(pya.DPolygon(top_gap), angle_deg).to_itype(dbu))
        r_bot = pya.Region(self._rot(pya.DPolygon(bot_gap), angle_deg).to_itype(dbu))
        return (r_top + r_bot).merged()

    def _cpw_inward_start(self):
        """Midpoint between island outer edge and keepout radius."""
        island_outer_r = self.island_gap / 2.0 + self.island_height
        x0 = 0.5 * (float(self.transmon_span) + float(island_outer_r))
        return max(0.0, min(x0, float(self.transmon_span) - 1e-3))

    def _flux_cutout(self, side, dbu):
        """Return one trapezoidal flux cutout for left or right side."""
        depth = float(self.depth_flux_cutout)
        base = float(self.flux_cutout_base)
        ang = math.radians(float(self.flux_cutout_angle))
        r_cap = float(self.flux_cutout_radius)

        # Inner width uses flux_cutout_base.
        w_inner = max(1.0, base)
        w_outer = max(1.0, w_inner + 2.0 * depth * math.tan(ang))
        w_outer_2 = w_outer / 2.0
        w_inner_2 = w_inner / 2.0

        if side == "left":
            x_out = -float(self.transmon_span)
            x_in = x_out + depth
            poly = pya.DPolygon([
                pya.DPoint(x_out, -w_outer_2),
                pya.DPoint(x_out, w_outer_2),
                pya.DPoint(x_in, w_inner_2),
                pya.DPoint(x_in, -w_inner_2),
            ])
        else:
            x_out = float(self.transmon_span)
            x_in = x_out - depth
            poly = pya.DPolygon([
                pya.DPoint(x_out, -w_outer_2),
                pya.DPoint(x_out, w_outer_2),
                pya.DPoint(x_in, w_inner_2),
                pya.DPoint(x_in, -w_inner_2),
            ])
        cutout = pya.Region(poly.to_itype(dbu))

        # Optional C-shaped termination at the deep edge.
        if r_cap > 0.0:
            inward_sign = 1.0 if side == "left" else -1.0
            # Set center so the chord at x = x_in has length flux_cutout_base.
            # Chord formula: L = 2*sqrt(r^2 - d^2) -> d = sqrt(r^2 - (L/2)^2)
            d_join = math.sqrt(max(0.0, r_cap * r_cap - w_inner_2 * w_inner_2))
            cx = x_in + inward_sign * d_join

            outer = pya.Region(
                (pya.DCplxTrans(1.0, 0.0, False, cx, 0.0) * self._circle_poly(r_cap)).to_itype(dbu)
            )

            ring = outer
            cutout = (cutout - ring).merged()

        return cutout

    def _readout_t_coupler(self, angle_deg, target_island, dbu):
        """Return a rounded T-shaped readout coupler."""
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        g = self.island_gap / 2.0
        x_half = self.island_width / 2.0
        if target_island == "top":
            y_lo, y_hi = g, g + self.island_height
        else:
            y_lo, y_hi = -(g + self.island_height), -g

        # Radius where the ray first hits the island boundary.
        entry_r = self._ray_island_entry(cos_a, sin_a, x_half, y_lo, y_hi)
        if entry_r is None:
            entry_r = y_hi / max(abs(sin_a), 1e-9)

        rg = float(self.readout_gap)
        rw = float(self.readout_width)
        rs = float(self.readout_span)
        rww = float(self.readout_wg_width)

        tbar_x_inner = entry_r + rg
        tbar_x_outer = min(tbar_x_inner + rw, self.transmon_span - 1.0)
        tbar_x_inner = tbar_x_outer - rw

        # Stem overlaps T-bar to avoid seams.
        tbar_box = pya.DBox(tbar_x_inner, -rs / 2.0, tbar_x_outer, rs / 2.0)
        stem_box = pya.DBox(tbar_x_inner, -rww / 2.0, self.transmon_span, rww / 2.0)

        r_tbar = pya.Region(self._rot(pya.DPolygon(tbar_box), angle_deg).to_itype(dbu))
        r_stem = pya.Region(self._rot(pya.DPolygon(stem_box), angle_deg).to_itype(dbu))
        tcoupler = (r_stem + r_tbar).merged()
        if self.corner_radius > 0.0:
            cr = int(self.corner_radius / dbu)
            tcoupler = tcoupler.round_corners(cr, cr, 32)
        return tcoupler

    def _ray_island_entry(self, cos_a, sin_a, x_half, y_lo, y_hi):
        """Largest positive ray parameter crossing the island boundary."""
        eps = 1e-9
        hits = []
        if abs(sin_a) > eps:
            for y_face in (y_lo, y_hi):
                t = y_face / sin_a
                if t > eps and -x_half - eps <= t * cos_a <= x_half + eps:
                    hits.append(t)
        if abs(cos_a) > eps:
            for x_face in (x_half, -x_half):
                t = x_face / cos_a
                if t > eps and y_lo - eps <= t * sin_a <= y_hi + eps:
                    hits.append(t)
        return max(hits) if hits else None

    def _port(self, angle_deg, port_r, total_width):
        """1 µm DPath port marker at the waveguide end."""
        angle_rad = math.radians(angle_deg)
        ca, sa = math.cos(angle_rad), math.sin(angle_rad)
        p0 = pya.DPoint((port_r - 0.5) * ca, (port_r - 0.5) * sa)
        p1 = pya.DPoint((port_r + 0.5) * ca, (port_r + 0.5) * sa)
        return pya.DPath([p0, p1], total_width)


# Local test block.
if __name__ == "__main__":
    from qfoundry.scripts.library import reload_library
    from qfoundry.utils import test_pcell

    reload_library()

    params = {
        "flux_input_side": "right",
        "flux_cutout_radius": 40.0
    }
    test_pcell(TransmonFloatingCircle, params, pya.Trans(pya.Trans.R0, 0, 0))
