"""Transmon PCell: Rectangular-island transmon qubit with radial CPW stub couplers.

Islands:
    Two identical rectangles (island_width x island_height) stacked along y,
    separated by island_gap. Drawn on metal layer (30/0, positive).

Keepout / ground layer (1/0, negative):
    1/0 = round(circle(transmon_span) + cpw_gap_strips) - metal_inside_circle
    where metal_inside_circle = rounded_islands_with_slots
                               + radial coupler fingers (rounded tips)
                               + readout T-coupler shapes

Operation order (important for correct corner rounding):
    1. Build raw islands; subtract coupler slots.
    2. Round the slotted islands (outer island corners + inner slot corners).
    3. Build coupler fingers (tip-rounded) and readout T-couplers.
    4. Build keepout base = circle ∪ CPW gap strips (gaps extend _CPW_OVERLAP
       inside circle to guarantee a clean merge at the boundary).
    5. Round keepout base inner corners (at CPW-to-circle junctions).
    6. Subtract metal_inside from rounded keepout.

Main couplers (4):
    Positive-metal radial fingers (30/0) entering the keepout circle by
    coupler_inclusion.  A single base angle (30-60 deg) is auto-mirrored:
        angle, 180-angle, 180+angle, 360-angle

Readout couplers (0-2, one per island):
    T-shaped positive-metal finger (30/0) with angle fixed by target island:
        'top' → 90°  (approaches top island from above)
        'bottom' → 270°  (approaches bottom island from below)

Convention:
    Local frame for all box-based shapes: +x = radially outward.
    DCplxTrans(1, angle_deg) maps local +x → lab direction at angle_deg from +x.
    This matches math.cos/sin so all shapes use the same angle convention.

Author: QFoundry PDK
Date: 2026
"""

import pya
import math

# Extra inward overlap of CPW gap strips into the keepout circle (um).
# Prevents tiny slivers at the rectangular-strip / circle-arc junction.
_CPW_OVERLAP = 5.0

# Fixed readout angles determined solely by target island
_READOUT_ANGLE = {"top": 90.0, "bottom": 270.0}


class Transmon(pya.PCellDeclarationHelper):

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

        # Clamp readout_islands to 2 entries of valid values
        if self.readout_islands:
            isl = [str(s) for s in list(self.readout_islands)
                   if str(s) in ("top", "bottom")][:2]
            self.readout_islands = isl if isl else ["top"]

    def set_parameters(self):
        # ---- Layers ----
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

        # ---- Island geometry ----
        self.param("island_width", self.TypeDouble, "Island width [um]", default=200.0)
        self.param("island_height", self.TypeDouble, "Island height [um]", default=100.0)
        self.param("island_gap", self.TypeDouble,
                   "Vertical gap between islands [um]", default=20.0)
        self.param("corner_radius", self.TypeDouble,
                   "Island corner rounding radius (outer + inner slot corners) [um]",
                   default=0.0)

        # ---- Transmon span ----
        self.param("transmon_span", self.TypeDouble,
                   "Radius of keepout circle around transmon [um]", default=300.0)
        self.param("keepout_corner_radius", self.TypeDouble,
                   "Rounding of keepout inner corners at CPW-circle junctions [um]",
                   default=5.0)

        # ---- Main coupler parameters ----
        self.param("coupler_angle", self.TypeDouble,
                   "Base coupler angle [deg, 30-60]; mirrored to 4 quadrant positions",
                   default=45.0)
        self.param("coupler_wg_width", self.TypeDouble,
                   "Coupler CPW center conductor width [um]", default=10.0)
        self.param("coupler_wg_gap", self.TypeDouble,
                   "Coupler CPW gap (outside circle) [um]", default=6.0)
        self.param("coupler_inclusion", self.TypeDouble,
                   "Coupler finger depth inside circle from boundary [um]", default=50.0)
        self.param("coupler_gap", self.TypeDouble,
                   "Capacitive gap between finger tip and island edge [um]", default=5.0)
        self.param("coupler_extensions", self.TypeList,
                   "Waveguide extension beyond circle [um] (1 value or 4 per coupler)",
                   default=[100.0])

        # ---- Readout coupler parameters ----
        # Angle is fixed: 'top' island → 90°, 'bottom' island → 270°
        self.param("readout_islands", self.TypeList,
                   "Readout island(s): 'top' and/or 'bottom' (up to 2 entries)",
                   default=["top"])
        self.param("readout_wg_width", self.TypeDouble,
                   "Readout CPW center conductor width [um]", default=10.0)
        self.param("readout_wg_gap", self.TypeDouble,
                   "Readout CPW gap [um]", default=6.0)
        self.param("readout_gap", self.TypeDouble,
                   "Capacitive gap from T-bar inner edge to island face [um]", default=5.0)
        self.param("readout_width", self.TypeDouble,
                   "T-bar thickness along radial direction [um]", default=5.0)
        self.param("readout_span", self.TypeDouble,
                   "T-bar total transverse length [um]", default=50.0)
        self.param("readout_extension", self.TypeDouble,
                   "Readout waveguide extension beyond circle [um]", default=100.0)

        # ---- Auxiliary ----
        self.param("margin", self.TypeDouble,
                   "Ground exclusion margin beyond device [um]", default=10.0)
        self.param("resolution", self.TypeInt,
                   "Circle polygon resolution (vertices)", default=64)

    # =========================================================================
    # produce_impl
    # =========================================================================

    def produce_impl(self):
        dbu = self.layout.dbu

        # Derived coupler angles (4 mirrored quadrant positions)
        a = float(self.coupler_angle)
        coupler_angles = [a, 180.0 - a, 180.0 + a, 360.0 - a]

        # Broadcast single extension value to 4 per-coupler values
        raw_ext = [float(x) for x in (list(self.coupler_extensions)
                                       if self.coupler_extensions else [100.0])]
        if len(raw_ext) < 4:
            raw_ext += [raw_ext[-1]] * (4 - len(raw_ext))
        ext_list = raw_ext[:4]

        # Readout config: angle fixed by target island
        ro_isl = [str(s) for s in (list(self.readout_islands)
                                    if self.readout_islands else [])][:2]
        ro_angles = [_READOUT_ANGLE.get(s, 90.0) for s in ro_isl]
        n_ro = len(ro_isl)

        # ------------------------------------------------------------------
        # Step 1: Coupler fingers (built first so their shape defines the slot).
        #         Each finger's rounded tip is used as the slot template.
        # ------------------------------------------------------------------
        coupler_gap_dbu = int(self.coupler_gap / dbu)
        fingers = pya.Region()
        finger_list = []          # keep individual regions for slot derivation
        for angle in coupler_angles:
            f = self._radial_finger(angle, self.coupler_wg_width, dbu)
            fingers += f
            finger_list.append(f)

        # Step 2: Raw islands; subtract slot = Minkowski offset of each finger
        #         by coupler_gap.  Because the finger tip is a semicircle of
        #         radius coupler_wg_width/2, the offset tip is a semicircle of
        #         radius coupler_wg_width/2 + coupler_gap → gap is exactly
        #         coupler_gap on all sides (lateral, axial, and at the corners).
        raw_islands = (self._raw_island("top", dbu) +
                       self._raw_island("bottom", dbu)).merged()
        for f in finger_list:
            raw_islands -= f.sized(coupler_gap_dbu)

        # Step 3: Round the slotted islands (outer corners AND inner slot corners)
        if self.corner_radius > 0.0:
            cr = int(self.corner_radius / dbu)
            island_region = raw_islands.round_corners(cr, cr, 32)
        else:
            island_region = raw_islands

        # ------------------------------------------------------------------
        # Step 4: Remaining 30/0 metal (readout T-couplers, CPW centers).
        #         CPW centers start _CPW_OVERLAP inside the circle so they overlap
        #         the fingers and form one continuous strip after merged().
        # ------------------------------------------------------------------

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

        # Full joined metal: each coupler is now one continuous strip from
        # finger tip (inside circle) to port (outside circle).
        metal = (island_region + fingers + readout_inner + cpw_centers).merged()

        # ------------------------------------------------------------------
        # Step 5: Keepout base = circle ∪ CPW gap strips
        #         (gap strips overlap _CPW_OVERLAP inside circle)
        # ------------------------------------------------------------------
        circle = pya.Region(self._circle_poly(self.transmon_span).to_itype(dbu))

        cpw_gaps = pya.Region()
        for i, angle in enumerate(coupler_angles):
            cpw_gaps += self._cpw_gaps(angle, ext_list[i],
                                       self.coupler_wg_width, self.coupler_wg_gap, dbu)
        for i in range(n_ro):
            cpw_gaps += self._cpw_gaps(ro_angles[i],
                                       float(self.readout_extension),
                                       self.readout_wg_width, self.readout_wg_gap, dbu)

        keepout_base = (circle + cpw_gaps).merged()

        # Step 6: Round keepout inner corners BEFORE subtracting metal.
        #         Rounds the concave junctions between CPW gap rectangles and
        #         the circle arc; leaves the outer arc convex corners untouched.
        if self.keepout_corner_radius > 0.0:
            kr = int(self.keepout_corner_radius / dbu)
            keepout_base = keepout_base.round_corners(kr, 0, 32)

        # Step 7: Subtract the FULL joined metal from the rounded keepout.
        #         Using metal (not a subset) ensures the keepout correctly
        #         accounts for the entire coupler strip from tip to port.
        ground_neg = (keepout_base - metal).merged()

        # ------------------------------------------------------------------
        # Write shapes to layers
        # ------------------------------------------------------------------
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

    # =========================================================================
    # Geometry helpers
    #
    # All box-based helpers use local +x = radially outward, so rotating by
    # angle_deg maps +x to the lab direction at angle_deg from the +x axis.
    # This is consistent with math.cos/sin (angle=0 → +x lab, angle=90 → +y lab).
    # =========================================================================

    def _rot(self, dpoly, angle_deg):
        """Rotate DPolygon about origin (CCW, standard math convention)."""
        return pya.DCplxTrans(1.0, angle_deg, False, 0, 0) * dpoly

    def _circle_poly(self, radius):
        pts = []
        n = self.resolution
        for i in range(n):
            ang = 2.0 * math.pi * i / n
            pts.append(pya.DPoint(radius * math.cos(ang), radius * math.sin(ang)))
        return pya.DPolygon(pts)

    def _raw_island(self, which, dbu):
        """Raw island rectangle with NO corner rounding (rounding applied later,
        after coupler slots are cut so all corners are rounded in one pass)."""
        w = self.island_width
        h = self.island_height
        g = self.island_gap / 2.0
        if which == "top":
            box = pya.DBox(-w / 2, g, w / 2, g + h)
        else:
            box = pya.DBox(-w / 2, -g - h, w / 2, -g)
        return pya.Region(pya.DPolygon(box).to_itype(dbu))

    def _radial_finger(self, angle_deg, width, dbu):
        """Radial CPW finger (30/0) entering the circle by coupler_inclusion.
        Tip (inner end) is rounded with a semicircle of radius = width/2.
        Outer end overlaps _CPW_OVERLAP into the CPW center strip so they
        merge into one continuous metal trace after Region.merged().
        Local +x frame: finger spans x ∈ [span-inclusion, span+_CPW_OVERLAP]."""
        r_in = self.transmon_span - self.coupler_inclusion
        r_out = self.transmon_span + _CPW_OVERLAP   # overlap with cpw_center
        box = pya.DBox(r_in, -width / 2.0, r_out, width / 2.0)
        ipoly = self._rot(pya.DPolygon(box), angle_deg).to_itype(dbu)
        if width > 0:
            rr = int((width / 2.0) / dbu)
            # router (2nd arg) rounds convex corners → creates semicircle at inner tip;
            # the outer-end rounded corners are merged away by the cpw_center overlap.
            ipoly = ipoly.round_corners(0, rr, 16)
        return pya.Region(ipoly)

    def _cpw_center(self, angle_deg, extension, width, dbu):
        """CPW center conductor (30/0) running from circle boundary outward.
        Starts _CPW_OVERLAP inside the circle so it overlaps the finger and the
        two shapes merge into one continuous strip after Region.merged().
        Local +x frame: x ∈ [span-_CPW_OVERLAP, span+extension], y ∈ ±width/2."""
        x0 = self.transmon_span - _CPW_OVERLAP   # extends into circle to meet finger
        x1 = self.transmon_span + extension
        box = pya.DBox(x0, -width / 2.0, x1, width / 2.0)
        return pya.Region(self._rot(pya.DPolygon(box), angle_deg).to_itype(dbu))

    def _cpw_gaps(self, angle_deg, extension, center_width, gap_width, dbu):
        """CPW gap strips (both sides, 1/0).
        Inner boundary at span-_CPW_OVERLAP ensures merge with circular keepout."""
        hw = center_width / 2.0
        x0 = self.transmon_span - _CPW_OVERLAP   # extends into circle
        x1 = self.transmon_span + extension
        top_gap = pya.DBox(x0, hw, x1, hw + gap_width)
        bot_gap = pya.DBox(x0, -hw - gap_width, x1, -hw)
        r_top = pya.Region(self._rot(pya.DPolygon(top_gap), angle_deg).to_itype(dbu))
        r_bot = pya.Region(self._rot(pya.DPolygon(bot_gap), angle_deg).to_itype(dbu))
        return (r_top + r_bot).merged()

    def _readout_t_coupler(self, angle_deg, target_island, dbu):
        """T-shaped coupler finger (30/0) coupling to the outer face of target_island.

        In local +x frame (radially outward):
          - Stem: width=readout_wg_width, x ∈ [tbar_x_inner, transmon_span].
            Overlaps the T-bar region so the two shapes merge into one polygon.
          - T-bar: width=readout_span, x ∈ [tbar_x_inner, tbar_x_outer].
            Inner edge is readout_gap outside the island outer face.

        Returns merged pya.Region."""
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        g = self.island_gap / 2.0
        x_half = self.island_width / 2.0
        if target_island == "top":
            y_lo, y_hi = g, g + self.island_height
        else:
            y_lo, y_hi = -(g + self.island_height), -g

        # entry_r: radius at which the ray first hits the island (outer face)
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

        # Both shapes in local +x frame; stem overlaps T-bar for seamless join
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
        """Largest positive r where the ray (r·cos_a, r·sin_a) crosses the island boundary.
        y_lo ≤ y_hi.  Returns None if the ray misses the rectangle."""
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


# =============================================================================
# Test block — run from a KLayout macro to preview the cell
# =============================================================================
if __name__ == "__main__":
    from qfoundry.scripts.library import reload_library
    from qfoundry.utils import test_pcell

    reload_library()

    params = {
        "island_width": 400.0,
        "island_height": 180.0,
        "island_gap": 40.0,
        "corner_radius": 50.0,
        "transmon_span": 300.0,
        "keepout_corner_radius": 20.0,
        "coupler_angle": 45.0,
        "coupler_wg_width": 15.0,
        "coupler_wg_gap": 7.5,
        "coupler_inclusion": 60.0,
        "coupler_gap": 5.0,
        "coupler_extensions": [20.0],
        "readout_islands": ["bottom"],
        "readout_wg_width": 15.0,
        "readout_wg_gap": 7.5,
        "readout_gap": 20.0,
        "readout_width": 20.0,
        "readout_span": 80.0,
        "readout_extension": 20.0,
        "margin": 10.0,
        "resolution": 128,
    }
    test_pcell(Transmon, params, pya.Trans(pya.Trans.R0, 0, 0))
