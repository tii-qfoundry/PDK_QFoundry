"""TransmonStar PCell: Concentric transmon qubit with configurable star-shaped couplers.

This module implements a parametric cell for creating transmon qubits with a central
circular island and multiple radial coupling connectors. Each connector can be
individually configured for angle, depth, gap, and width.

Typical applications:
    - Multi-qubit coupling in quantum processors
    - Readout resonator connections
    - Control line connections

Design based on work by A. Wallraff et al.

Author: QFoundry PDK
Date: 2026
"""

import pya
import math


class TransmonStar(pya.PCellDeclarationHelper):
    """Parametric cell for a star-shaped transmon qubit.
    
    Geometry:
        - Central circular island at outer_radius
        - N radial trapezoid cutouts for couplers (star pattern)
        - Connector waveguides extending from each coupler
        - Ground plane clearance with optional corner rounding
    
    Key Parameters:
        - outer_radius: Radius of central qubit island
        - coupler_angles: List of angles for each coupler (degrees)
        - coupler_depths: How deep each coupler cuts inward from outer_radius
        - coupler_gaps: Spacing between qubit and connector for each coupler
        - coupler_widths: Angular width of each cutout (auto-calculated if empty)
        - connector_wg: [width, gap] of output waveguides
        - corner_radius: Rounding radius for inner corners
    
    Note: All dimensional parameters in micrometers unless specified.
    """
    
    def __init__(self):
        super(TransmonStar, self).__init__()
        self.set_parameters()
        
    
    def display_text_impl(self):
        n = len(self.coupler_angles) if self.coupler_angles else 0
        return f"TransmonStar ({n} couplers)"
    
    
    def coerce_parameters_impl(self):
        """Validate and coerce parameters to ensure consistency.
        
        - Converts single values to lists
        - Pads short lists with last value
        - Enforces physical constraints
        - Auto-generates angular widths if not specified
        """
        # Count couplers from angles list
        self.n_couplers = len(self.coupler_angles) if self.coupler_angles else 0
        if self.n_couplers == 0:
            return

        # Helper function to extend lists to match n_couplers
        def extend_list(lst, n, default=None):
            if isinstance(lst, (int, float)):
                return [float(lst)] * n
            lst = list(lst) if lst else []
            if len(lst) < n:
                fill_val = lst[-1] if lst else (default or 0.0)
                lst = lst + [fill_val] * (n - len(lst))
            return lst[:n]
        
        # Extend all coupler lists to match n_couplers
        self.coupler_depths = extend_list(self.coupler_depths, self.n_couplers)
        self.coupler_gaps = extend_list(self.coupler_gaps, self.n_couplers)
        self.trap_base = extend_list(self.trap_base, self.n_couplers)

        # Auto-generate coupler_widths if empty (equal angular spacing)
        default_width = 360.0 / (2.0 * self.n_couplers)
        if not self.coupler_widths:
            self.coupler_widths = [default_width] * self.n_couplers
        else:
            self.coupler_widths = extend_list(self.coupler_widths, self.n_couplers, default_width)
        
        # Enforce physical constraints
        self.outer_radius = max(50.0, self.outer_radius)
        self.coupler_depths = [max(0, min(d, 2*self.outer_radius)) for d in self.coupler_depths]
        
        # Ensure circle resolution is multiple of 2*n_couplers for symmetry
        target_res = self.n_couplers * 2
        if self.resolution % target_res != 0:
            self.resolution = max(target_res * (self.resolution // target_res), target_res * 3)
                
        # Check connector waveguide specification is a list of two values
        if isinstance(self.connector_wg, list) and len(self.connector_wg) == 2:
            self.connector_width = float(self.connector_wg[0])
            self.connector_gap = float(self.connector_wg[1])
        else:
            self.connector_width = 15.0
            self.connector_gap = 7.5

    
    def produce_impl(self):
        """Generate the transmon geometry."""
        self._create_transmon_star()
        
   
    def set_parameters(self):
        """Define all parameters for the PCell."""
        
        # Layer parameters
        self.param("metal_layer", self.TypeLayer, "Metal layer for qubit", 
                   default=pya.LayerInfo(30, 0))
        self.param("junction_layer", self.TypeLayer, "Junction layer", 
                   default=pya.LayerInfo(2, 0))
        self.param("metal_n_layer", self.TypeLayer, "Metalization negative layer", 
                   default=pya.LayerInfo(1, 0))
        self.param("port_layer", self.TypeLayer, "Port layer for waveguide connections", 
                   default=pya.LayerInfo(997, 0), hidden=True)
        self.param("devrec_layer", self.TypeLayer, "Device recognition layer", 
                   default=pya.LayerInfo(68, 0), hidden=True)
        self.param("ground_exclude_layer", self.TypeLayer, "Ground exclusion layer", 
                   default=pya.LayerInfo(133, 1), hidden=True)
        
        # Geometric parameters for the central island
        self.param("outer_radius", self.TypeDouble, "Outer radius of qubit island [um]", 
                   default=150.0)
        self.param("ground_clearance", self.TypeDouble, "Additional clearance for ground plane [um]", 
                   default=20.0)
        self.param("margin", self.TypeDouble, "Margin for ground exclusion beyond device [um]", 
                   default=10.0)
        
        # Coupler configuration via lists
        # Each coupler defined by: angle, depth (from outer_radius), gap, angular width
        self.param("coupler_angles", self.TypeList, "Angles of couplers [degrees]",
                   default=[0.0, 72.0, 144.0, 216.0, 288.0])
        self.param("coupler_depths", self.TypeList, "Depth of each coupler from outer radius [um]",
                   default=[170.0, 45.0, 45.0, 45.0, 45.0])
        self.param("coupler_gaps", self.TypeList, "Gap between qubit and connector [um]",
                   default=[20.0, 20.0, 20.0, 20.0, 20.0])
        self.param("coupler_widths", self.TypeList, "Angular width of cutouts [degrees] (auto if empty)",
                   default=[48.0, 48.0, 48.0, 48.0, 48.0])
        self.param("trap_base", self.TypeList, "Trapezoid base width at inner edge [um]", 
                   default=[20.0, 0.0, 0.0, 0.0, 0.0])
        
        
        # Connector geometry
        self.param("connector_wg", self.TypeList, "Dimension of coupler waveguides (w,s) [um]", 
                   default=[15.0, 7.5])
        self.param("connector_extension", self.TypeDouble, "Extension length of coupler waveguides [um]", 
                   default=10.0)
        
        
        # # Junction parameters
        # self.param("junction_at_coupler", self.TypeInt, "Index of coupler with junction (0-based, -1 for none)", 
        #            default=0)
        # self.param("junction_width", self.TypeDouble, "Junction width [um]", 
        #            default=0.2)
        # self.param("junction_length", self.TypeDouble, "Junction length [um]", 
        #            default=30.0)
        
        # Rendering and geometry parameters
        self.param("resolution", self.TypeInt, "Circle resolution (number of points)", 
                   default=30)
        self.param("corner_radius", self.TypeDouble, "Corner rounding radius for inner cutouts [um]", 
                   default=0.0, hidden=False)
        
    
    def _create_transmon_star(self):
        """Create the complete transmon star structure."""
        dbu = self.layout.dbu
        
        # Parse coupler parameters
        
        if self.n_couplers == 0:
            # No couplers - just create a simple circle
            inner_star = self._make_circle(self.outer_radius, pya.DPoint(0, 0))
            self.cell.shapes(self.metal_layer).insert(inner_star.to_itype(dbu))
            return
        
        # Create the inner star (central island with cutouts for couplers)
        inner_star = self._make_inner_star()
        
        # Create the coupling connectors
        coupling_regions = self._make_coupling_connectors()
        
        # Create ground plane cutout (subtract region)
        inner_region = inner_star
        for region in coupling_regions:
            inner_region += region
        ground_cutout = self._make_ground_cutout(inner_region)
        
        # Add geometries to layers
        self.cell.shapes(self.metal_layer).insert(inner_star)
        self.cell.shapes(self.metal_n_layer).insert(ground_cutout)
        
        for i, region in enumerate(coupling_regions):
            self.cell.shapes(self.metal_layer).insert(region)
        
        # Add ports at end of each connector
        for i in range(self.n_couplers):
            ports = self._make_ports(self.coupler_angles[i])
            for port in ports:
                self.cell.shapes(self.port_layer).insert(port)
        
        # Add device recognition layer (outer boundary excluding ports)
        devrec = self._make_device_recognition(ground_cutout, inner_region)
        self.cell.shapes(self.devrec_layer).insert(devrec)
        
        # Add ground exclusion layer (devrec + margin)
        ground_exclude = self._make_ground_exclusion(devrec)
        self.cell.shapes(self.ground_exclude_layer).insert(ground_exclude)
        
        # Add junction if specified
        # if 0 <= self.junction_at_coupler < self.n_couplers:
        #     junction_path = self._make_junction()
        #     if junction_path:
        #         self.cell.shapes(self.junction_layer).insert(junction_path)
    
    
    def _make_circle(self, radius, center=pya.DPoint(0, 0), resolution=None):
        """Create a circular polygon."""
        if resolution is None:
            resolution = self.resolution
        
        points = []
        for i in range(resolution):
            angle = 2 * math.pi * i / resolution
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            points.append(pya.DPoint(x, y))
        
        return pya.DPolygon(points)
    
    
    def _make_trapezoid_cutout(self, angle_deg, gap, angular_width, depth=None, trap_base=0):
        """Create trapezoid-shaped cutout for a coupler.
        
        The trapezoid extends radially from (outer_radius - depth) to outer_radius,
        with angular width defining the cutout opening and trap_base creating
        angled sidewalls.
        
        Args:
            angle_deg: Rotation angle of cutout center (degrees)
            gap: Additional spacing added around cutout (um) 
            angular_width: Angular span of cutout opening (degrees)
            depth: Radial depth from outer_radius (um)
            trap_base: Width at inner edge for sidewall taper (um)
        
        Returns:
            pya.DPolygon: Trapezoid polygon rotated to specified angle
        """
        depth = max(10, depth if depth else 10)
        inner_radius = self.outer_radius - depth
        
        # Calculate the angular half-width in radians
        half_angle_rad = math.radians(angular_width / 2.0)
        
        # Outer edge (at outer_radius) - wider due to radius increase
        outer_half_width = abs(self.outer_radius) * math.tan(half_angle_rad)

        # Calculate sidewall angle and gap compensation
        sidewall_angle_rad = math.atan((outer_half_width - trap_base/2) / (self.outer_radius - inner_radius))
        gap_x = gap / math.cos(sidewall_angle_rad)
        xp = gap * math.tan(sidewall_angle_rad)

        # Calculate trapezoid coordinates based on angular width
        # Inner edge (at inner_radius)
        inner_half_width = trap_base/2
        
        
        # Create trapezoid in local coordinates (pointing up in +y direction)
        trap_points = [
            pya.DPoint(-inner_half_width - gap_x + xp, inner_radius - gap),
            pya.DPoint(inner_half_width + gap_x - xp, inner_radius - gap),
            pya.DPoint(outer_half_width + gap_x + xp, self.outer_radius + gap),
            pya.DPoint(-outer_half_width - gap_x - xp, self.outer_radius + gap)
        ]
        
        trap = pya.DPolygon(trap_points)
        
        # Rotate to the specified angle
        trans = pya.DCplxTrans(1.0, angle_deg, False, 0, 0)
        trap_rotated = trans * trap
        
        return trap_rotated
    
    def _make_inner_star(self):
        """Create central qubit island with star-shaped coupler cutouts.
        
        Generates outer circle, subtracts N trapezoid cutouts at specified angles,
        and applies corner rounding if enabled.
        
        Returns:
            pya.Region: Merged region representing qubit island
        """
        # Start with outer circle
        circle = self._make_circle(self.outer_radius)
        qubit_region = pya.Region(circle.to_itype(self.layout.dbu))
        
        # Create trapezoid cutouts for each coupler
        
        for i in range(self.n_couplers):
            trap = self._make_trapezoid_cutout(angle_deg = self.coupler_angles[i], 
                                               gap = self.coupler_gaps[i], 
                                               angular_width=self.coupler_widths[i], 
                                               depth=self.coupler_depths[i], 
                                               trap_base=self.trap_bases[i])
            trap_region = pya.Region(trap.to_itype(self.layout.dbu))
            qubit_region -= trap_region
        
        # # Add connectors to junction if specified
        # if 0 <= self.junction_at_coupler < self.n_couplers:
        #     junction_angle = self.coupler_angles[self.junction_at_coupler]
        #     junction_connectors = self._make_junction_connectors(junction_angle)
        #     for conn in junction_connectors:
        #         conn_region = pya.Region(conn.to_itype(self.layout.dbu))
        #         qubit_region += conn_region
        
        # Apply corner rounding to inner corners if corner_radius > 0
        if self.corner_radius > 0:
            qubit_region = self._round_inner_corners(qubit_region)
        
        # Convert back to polygon for output
        return qubit_region.merged()
    
    def _round_inner_corners(self, region):
        """Apply corner rounding to inner concave corners of star cutouts.
        
        Args:
            region: Region to round
        
        Returns:
            pya.Region: Region with rounded corners
        """
        dbu = self.layout.dbu
        radius_dbu = int(self.corner_radius / dbu)
        
        if radius_dbu <= 0:
            return region
        
        # Extract merged polygon and apply rounding
        polygon = region.merged()
        return polygon.round_corners(radius_dbu, radius_dbu, 32)
    
    def _make_junction_connectors(self, angle_deg): # NOT IMPLEMENTED
        """
        Create connection to the junction at the specified coupler angle.
        """
        return []
    
    def _make_coupling_connectors(self):
        """Create all coupling connector waveguides.
        
        Returns:
            list[pya.Region]: List of connector regions, one per coupler
        """
        return [
            self._make_single_connector(
                angle_deg=self.coupler_angles[i], 
                angular_width=self.coupler_widths[i], 
                depth=self.coupler_depths[i], 
                gap=0,  # Gap handled in trapezoid cutout
                trap_base=self.trap_bases[i]
            )
            for i in range(self.n_couplers)
        ]
    
    def _make_single_connector(self, angle_deg, angular_width, depth, gap, trap_base=0):
        """
        Create a single coupler connector.
        
        This consists of:
        1. A trapezoid cutout from the main circle
        2. A rectangular pocket extending outward (fixed extension)
        """
        angle_rad = math.radians(angle_deg)
        dbu = self.layout.dbu
        
        # Start with a base circle
        circle = self._make_circle(self.outer_radius)
        circle_region = pya.Region(circle.to_itype(dbu))
        
        # Create the trapezoid for this specific coupler with specified depth
        trap = self._make_trapezoid_cutout(angle_deg, gap, angular_width=angular_width, depth=depth, trap_base=trap_base)
        trap_region = pya.Region(trap.to_itype(dbu))
        
        # Subtract trapezoid from circle
        connector_region = circle_region & trap_region
        
        # Apply corner rounding to connector (radius reduced by gap)
        if self.corner_radius > 0:
            # The inner corners should be rounded with radius = corner_radius - gap
            connector_radius = max(0.1, self.corner_radius - gap)
            connector_region = self._round_corners(connector_region, connector_radius)

        # Add rectangular pocket extending outward (fixed extension for all connectors)
        pocket = self._make_connector_waveguide(angle_deg, self.ground_clearance + self.connector_extension, gap)
        pocket_region = pya.Region(pocket.to_itype(dbu))
        
        connector_region += pocket_region
        
        # Apply corner rounding to connector (radius reduced by gap)
        if self.corner_radius > 0:
            # Round again, only inner corners this time and can be corner radius
            connector_region = self._round_corners(connector_region, (self.corner_radius, 0))
        
        return connector_region.merged()
    
    def _round_corners(self, region, radius):
        """Apply corner rounding to a region.
        
        Args:
            region: Region to round
            radius: Rounding radius in um, or tuple (inner_r, outer_r)
        
        Returns:
            pya.Region: Rounded region
        """
        dbu = self.layout.dbu
        
        # Convert radius to DBU
        if isinstance(radius, tuple):
            radius_dbu = (int(radius[0] / dbu), int(radius[1] / dbu))
            if radius_dbu[0] <= 0 or radius_dbu[1] <= 0:
                return region
        else:
            radius_dbu = int(radius / dbu)
            if radius_dbu <= 0:
                return region
        
        # Apply rounding
        if isinstance(radius_dbu, tuple):
            return region.merged().round_corners(radius_dbu[0], radius_dbu[1], 32)
        else:
            return region.merged().round_corners(radius_dbu, radius_dbu, 32)
    
    def _make_connector_waveguide(self, angle_deg, pocket_length, gap=0):
        """Create rectangular waveguide extension for connector.
        
        Args:
            angle_deg: Rotation angle (degrees)
            pocket_length: Extension length beyond outer_radius (um)
            gap: Additional spacing (unused, for API compatibility)
        
        Returns:
            pya.DPolygon: Rectangular waveguide polygon
        """
        # Pocket dimensions
        pocket_width = self.connector_width
        
        # Create rectangle extending outward
        rect = pya.DBox(-pocket_width/2, self.outer_radius + pocket_length, 
                        pocket_width/2, self.outer_radius -10)
        rect_poly = pya.DPolygon(rect)
        
        # Rotate to angle
        trans = pya.DCplxTrans(1.0, angle_deg, False, 0, 0)
        return trans * rect_poly
    
    def _make_ground_cutout(self, inner_region):
        """Create ground plane clearance as negative layer.
        
        Generates a circular clearance region around qubit, with rectangular
        extensions at each connector for flat waveguide interfaces.
        
        Args:
            inner_region: Combined region of qubit island + connectors
        
        Returns:
            pya.Region: Ground clearance (keepout) region
        """
        dbu = self.layout.dbu
        
        # Outer circle for ground clearance
        ground_radius = self.outer_radius + self.ground_clearance
        ground_circle = self._make_circle(ground_radius)
        ground_region = pya.Region(ground_circle.to_itype(dbu))
        
        for i in range(self.n_couplers):
            # Add a rectangle pocket for each coupler (to ensure a flat facet at the waveguide connector)
            angle = self.coupler_angles[i]
            pocket = self._make_ground_pocket(angle, 10.0)
            pocket_region = pya.Region(pocket.to_itype(dbu))
            ground_region += pocket_region

        # Remove inner region (qubit island + connectors)
        ground_region -= inner_region
        
        return ground_region.merged()
    
    def _make_ground_pocket(self, angle_deg, pocket_length):
        """Create rectangular extension in ground plane at connector.
        
        Ensures flat waveguide interface at connector boundary.
        
        Args:
            angle_deg: Rotation angle (degrees)
            pocket_length: Extension length (um)
        
        Returns:
            pya.DPolygon: Rectangular pocket polygon
        """
        # Wider pocket for ground plane
        pocket_width = self.connector_width + 2*self.connector_gap
        
        # Create rectangle
        rect = pya.DBox(-pocket_width/2, self.outer_radius + self.ground_clearance + self.connector_extension, 
                        pocket_width/2, self.outer_radius + self.ground_clearance - pocket_length)
        rect_poly = pya.DPolygon(rect)
        
        # Rotate to angle
        trans = pya.DCplxTrans(1.0, angle_deg, False, 0, 0)
        return trans * rect_poly
    
    def _make_ports(self, angle_deg):
        """Create port markers at the end of a connector waveguide.
        
        Creates two path objects:
        1. Inner path with width = connector_width (signal)
        2. Outer path with width = connector_width + 2*connector_gap (signal + gap)
        
        Args:
            angle_deg: Rotation angle for the port (degrees)
        
        Returns:
            list[pya.DPath]: Two port path markers of length 1 um
        """
        # Port position at end of connector extension
        port_y = self.outer_radius + self.ground_clearance + self.connector_extension
        
        # Create two paths of length 1 um
        port_start = pya.DPoint(0, port_y-0.5)
        port_end = pya.DPoint(0, port_y + 0.5)
        
        # Port (waveguide width)
        waveguide_width = self.connector_width + 2 * self.connector_gap
        port = pya.DPath([port_start, port_end], waveguide_width )
        
        # Rotate both ports to the connector angle
        trans = pya.DCplxTrans(1.0, angle_deg, False, 0, 0)
        port_rotated = trans * port
        
        return [port_rotated]
    
    def _make_device_recognition(self, ground_cutout, inner_region):
        """Create device recognition layer showing device boundary.
        
        This is the outer edge of the complete geometry (qubit + connectors)
        excluding the port regions.
        
        Args:
            ground_cutout: Ground cutout region
            inner_region: Inner qubit + connector region
        
        Returns:
            pya.Region: Device boundary region
        """
        # Use the inner_region directly as device recognition
        # This represents the actual device geometry
        return (ground_cutout + inner_region).merged()
    
    def _make_ground_exclusion(self, devrec_region):
        """Create ground exclusion layer with margin around device.
        
        Args:
            devrec_region: Device recognition region to offset
        
        Returns:
            pya.Region: Ground exclusion region (devrec + margin)
        """
        dbu = self.layout.dbu
        margin_dbu = int(self.margin / dbu)
        
        # Offset the device recognition region by margin
        ground_exclude = devrec_region.sized(margin_dbu)
        
        return ground_exclude.merged()
    
    def _make_junction(self): # NOT IMPLEMENTED
        """
        Create the Josephson junction as a path.
        
        The junction is placed at the coupler specified by junction_at_coupler.
        This should instantaite one of the standard junction shapes.
        """
        
        return []


# Test code
if __name__ == "__main__":
    # This allows testing the PCell independently
    from qfoundry.scripts import reload_library
    from qfoundry.utils import test_pcell
    
    reload_library()
    
    # Test with 5 couplers at different angles
    pcell_decl = TransmonStar
    pcell_params = {
        "outer_radius": 150.0,
        "coupler_angles": [0.0, 72.0, 144.0, 216.0, 288.0],
        "coupler_depths": [170.0, 45.0, 45.0, 45.0, 45.0],  # Readout extends deeper inward
        "coupler_gaps": [20.0, 20.0, 20.0, 20.0, 20.0],     # Readout with smaller gap
        "coupler_widths": [48, 48, 48, 48, 48],
        "trap_bases": [20.0, 0.0, 0.0, 0.0, 0.0],
        "corner_radius": 0.0,
        "resolution": 30,
        "ground_clearance": 20.0,
        "connector_wg": [15.0, 7.5],
        "margin": 10.0,
    }
    pcell_trans = pya.Trans(pya.Trans.R0, 0, 0)
    
    test_pcell(pcell_decl, pcell_params, pcell_trans)
