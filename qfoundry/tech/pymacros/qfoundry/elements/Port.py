"""Port PCell: waveguide port marker, wrapping kcq.geometry.pins.add_pin
so it's a regular kcq pin (readable by pins.get_pins/check_alignment,
routable by kcq.geometry.router). Faces local +x; instances rotate it
to the connector direction.
"""

import pya

from kcq.geometry import pins


class Port(pya.PCellDeclarationHelper):

    def __init__(self):
        super().__init__()
        self.set_parameters()

    def display_text_impl(self):
        return f"Port({self.pin_name}, w={self.wg_width:.1f}, gap={self.wg_gap:.1f})"

    def coerce_parameters_impl(self):
        self.pin_name = str(self.pin_name).strip() or "P1"
        self.wg_width = max(0.0, float(self.wg_width))
        self.wg_gap = max(0.0, float(self.wg_gap))

    def set_parameters(self):
        self.param("pin_name", self.TypeString, "Pin name", default="P1")
        self.param("wg_width", self.TypeDouble,
                   "Waveguide core width [um]", default=15.0)
        self.param("wg_gap", self.TypeDouble,
                   "Waveguide gap, core to ground [um]", default=7.5)
        self.param("layer", self.TypeLayer, "Physical layer this pin belongs to",
                   default=pya.LayerInfo(1, 1))

    def produce_impl(self):
        total_width = self.wg_width + 2.0 * self.wg_gap
        pins.add_pin(self.cell, self.layout, self.pin_name, pya.DPoint(0.0, 0.0), 0.0, total_width,
                     self.layer.layer)


# Local test block.
if __name__ == "__main__":
    from qfoundry.scripts.library import reload_library
    from qfoundry.utils import test_pcell

    reload_library()

    test_pcell(Port, {}, pya.Trans(pya.Trans.R0, 0, 0))
