# This code is part of KQFoundry PDK
# Copyright (C) 2025 TII
#
# It uses the KQcircuits library

from kqcircuits.chips.chip import Chip

from kqcircuits.defaults import (
  default_layers, 
  default_junction_type, 
  default_mask_parameters,
  default_bump_parameters
)
                                
from kqcircuits.elements.chip_frame import ChipFrame
from kqcircuits.chips.launchers import Launchers
from kqcircuits.elements.waveguide_coplanar_splitter import WaveguideCoplanarSplitter, t_cross_parameters
from kqcircuits.pya_resolver import pya
from kqcircuits.elements.waveguide_composite import Node, WaveguideComposite
from kqcircuits.elements.airbridges.airbridge import Airbridge
from kqcircuits.elements.airbridge_connection import AirbridgeConnection
from kqcircuits.elements.airbridges.airbridge_rectangular import AirbridgeRectangular
from kqcircuits.elements.waveguide_coplanar_taper import WaveguideCoplanarTaper
from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar
from kqcircuits.elements.finger_capacitor_square import FingerCapacitorSquare
from kqcircuits.elements.flip_chip_connectors.flip_chip_connector_rf import FlipChipConnectorRf
from kqcircuits.util.parameters import Param, pdt

from qfoundry.defaults import default_sampleholders, default_marker_type, default_launcher_assignement, default_launcher_enabled
from importlib import reload

from qfoundry import defaults
reload(defaults)

NAME_BRAND = "TII"
NAME_MASK = "01H###"
NAME_CHIP = ""

sampleholder_type_choices = list(default_sampleholders.keys())
            

class FrameQF5(Chip):
    sampleholder_type = Param(pdt.TypeList, "Type of the launchers", 'QRC12', choices=sampleholder_type_choices)
    
    name_mask = Param(pdt.TypeString, "Name of the mask", NAME_MASK)
    name_chip = Param(pdt.TypeString, "Name of the chip", "")
    name_copy = Param(pdt.TypeString, "Name of the copy", NAME_CHIP)
    name_brand = Param(pdt.TypeString, "Name of the brand", NAME_BRAND)
    
    frames_marker_dist = Param(pdt.TypeList, "Marker distance from edge for each chip frame", [800, 400], unit="[μm]")
    frames_diagonal_squares = Param(pdt.TypeList, "Number of diagonal marker squares for each chip frame", [0, 0])
    
    # Overrides inner element parameters
    a = Param(pdt.TypeDouble, "Width of center conductor", 15.5, unit="μm")
    b = Param(pdt.TypeDouble, "Width of gap", 7.0, unit="μm")
    n = Param(pdt.TypeInt, "Number of points on turns", 32)
    r = Param(pdt.TypeDouble, "Turn radius", 100, unit="μm")
    margin = Param(pdt.TypeDouble, "Margin of the protection layer", 30., unit="μm")
    face_ids = Param(pdt.TypeList, "Chip face IDs list", ["1t1"], hidden=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #Hide parameters not set in this PCell (check inherited ones from Chip)
        
        print(super().get_parameters())

    def produce_structures(self):
        """
        Produces chip frame and possibly other structures before the ground grid.

        """
        self.name_brand = NAME_BRAND
        
        for i, face in enumerate(self.frames_enabled):
            face = int(face)
            frame_box = self.get_box(face)
            print(default_mask_parameters[self.face_ids[face]])
            frame_parameters = self.pcell_params_by_name(
                ChipFrame,
                name_brand = self.name_brand,
                name_mask = self.name_mask,
                name_chip = self.name_chip,
                box = frame_box,
                face_ids =[self.face_ids[face]],
                use_face_prefix =len(self.frames_enabled) > 1,
                dice_width =float(self.frames_dice_width[i]),
                text_margin = default_mask_parameters[self.face_ids[face]]["text_margin"],
                marker_dist = float(self.frames_marker_dist[i]),
                diagonal_squares = int(self.frames_diagonal_squares[i]),
                marker_types = self.marker_types[i*4:(i+1)*4]
            )

            if str(self.frames_mirrored[i]).lower() == 'true':  # Accept both boolean and string representation
                frame_trans = pya.DTrans(frame_box.center()) * pya.DTrans.M90 * pya.DTrans(-frame_box.center())
            else:
                frame_trans = pya.DTrans(0, 0)
            self.produce_frame(frame_parameters, frame_trans)

        if self.with_gnd_tsvs:
            pass
            #self._produce_ground_tsvs(face_id=0)
        
        if self.with_gnd_bumps:
            pass
            #self._produce_ground_bumps()
    

    def build(self):
      self.produce_n_launchers(**default_sampleholders[self.sampleholder_type], 
        launcher_assignments=default_launcher_assignement[self.sampleholder_type], 
        enabled = default_launcher_enabled[self.sampleholder_type])
       


if __name__ == "__main__":
    # You need to reload the library to see the changes in the PCell 
    from qfoundry.scripts import reload_library
    from qfoundry.utils import test_pcell
    reload_library()

    pcell_decl = FrameQF5
    pcell_params = {
        "sampleholder_type": "QRC12",
        "name_mask": NAME_MASK,
        "name_chip": NAME_CHIP,
        "name_brand": NAME_BRAND,
        "frames_marker_dist": [800, 400],
        "frames_diagonal_squares": [0, 0],
        "a": 15,
        "b": 7.5,
        "r": 150
    }
    pcell_trans = pya.Trans(pya.Trans.R0, 0.0, 0.0)
    test_pcell(pcell_decl, pcell_params, pcell_trans)

