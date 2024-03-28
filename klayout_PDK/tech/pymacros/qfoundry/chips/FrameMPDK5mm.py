
# Enter your Python code here

# This code is part of KQFoundry
# Copyright (C) 2023 TII
#
# It uses the KQcircuits library

from kqcircuits.chips.chip import Chip
from kqcircuits.defaults import default_layers, default_junction_type, default_mask_parameters, \
                                default_bump_parameters
                                
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


NAME_BRAND = "TII"
NAME_MASK = "5Q"
NAME_CHIP = "D__"

#new paramters for launchers

sampleholder_type_choices = list(default_sampleholders.keys())
            

class FrameMPDK5mm(Chip):
    sampleholder_type = Param(pdt.TypeList, "Type of the launchers", 'mQRC12', choices=sampleholder_type_choices)
    
    name_mask = Param(pdt.TypeString, "Name of the mask", NAME_MASK)
    name_chip = Param(pdt.TypeString, "Name of the chip", "")
    name_copy = Param(pdt.TypeString, "Name of the copy", NAME_CHIP)
    name_brand = Param(pdt.TypeString, "Name of the brand", NAME_BRAND)
    frames_marker_dist = Param(pdt.TypeList, "Marker distance from edge for each chip frame", [800, 400], unit="[μm]")
    frames_diagonal_squares = Param(pdt.TypeList, "Number of diagonal marker squares for each chip frame", [0, 0])
    
    a = Param(pdt.TypeDouble, "Width of the center conductor", 15)
    b = Param(pdt.TypeDouble, "Width of gap", 7.5)
    r = Param(pdt.TypeDouble, "Turn radius", 150, hidden=True)
    
    def produce_structures(self):
        """Produces chip frame and possibly other structures before the ground grid.
        This method overrides that from the KQcircuit / Chip library.
        """
        self.name_brand = NAME_BRAND
        
        
        for i, face in enumerate(self.frames_enabled):
            face = int(face)
            frame_box = self.get_box(face)
            print(default_mask_parameters[self.face_ids[face]])
            frame_parameters = self.pcell_params_by_name(
                ChipFrame,
                name_brand=self.name_brand,
                name_mask=self.name_mask,
                name_chip=self.name_chip,
                box=frame_box,
                face_ids=[self.face_ids[face]],
                use_face_prefix=len(self.frames_enabled) > 1,
                dice_width=float(self.frames_dice_width[i]),
                text_margin=default_mask_parameters[self.face_ids[face]]["text_margin"],
                marker_dist=float(self.frames_marker_dist[i]),
                diagonal_squares=int(self.frames_diagonal_squares[i]),
                marker_types=self.marker_types[i*4:(i+1)*4]
            )

            if str(self.frames_mirrored[i]).lower() == 'true':  # Accept both boolean and string representation
                frame_trans = pya.DTrans(frame_box.center()) * pya.DTrans.M90 * pya.DTrans(-frame_box.center())
            else:
                frame_trans = pya.DTrans(0, 0)
            self.produce_frame(frame_parameters, frame_trans)

        if self.with_gnd_tsvs:
            self._produce_ground_tsvs(face_id=0)
        if self.with_face1_gnd_tsvs:
            tsv_box = self.get_box(1).enlarged(pya.DVector(-self.edge_from_tsv, -self.edge_from_tsv))
            self._produce_ground_tsvs(face_id=1, tsv_box=tsv_box)

        if self.with_gnd_bumps:
            self._produce_ground_bumps()
    

    def build(self):
      self.produce_n_launchers(**default_sampleholders[self.sampleholder_type], 
        launcher_assignments=default_launcher_assignement[self.sampleholder_type], 
        enabled = default_launcher_enabled[self.sampleholder_type])
       
      print(self)


