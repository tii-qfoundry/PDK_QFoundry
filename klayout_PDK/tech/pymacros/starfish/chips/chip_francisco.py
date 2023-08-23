# This code is part of KQFoundry
# Copyright (C) 2023 TII
#
# It uses the KQcircuits library

from starfish.chips import defaults

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

from ..defaults import default_sampleholders, default_marker_type

NAME_BRAND = "TII"
NAME_MASK = "M001"
NAME_CHIP = "FS_1Q"

#new paramters for launchers


sampleholder_type_choices = list(default_sampleholders.keys())
launcher_assignments8 = {1: "NW", 2: "NE", 3: "EN", 4: "ES", 5: "SE", 6: "SW", 7: "WS", 8: "WN"}
launcher_assignments12 = {1: "NW", 2: "N", 3: "NE",
                          4: "ES", 5: "E", 6: "ES", 
                          7: "SE", 8: "S", 9: "SW",
                          10: "WS", 11: "W", 12: "WN"}
            
class ChipFrancisco(Chip):
    sampleholder_type = Param(pdt.TypeList, "Type of the launchers", Sampleholder_name, choices=sampleholder_type_choices)
    
    name_mask = Param(pdt.TypeString, "Name of the mask", NAME_MASK)
    name_chip = Param(pdt.TypeString, "Name of the chip", NAME_CHIP)
    name_copy = Param(pdt.TypeString, "Name of the copy", NAME_CHIP)
    name_brand = Param(pdt.TypeString, "Name of the brand", NAME_BRAND)
    def nodes1():
      """ Node list specifying *the composite waveguide """
      return [
          Node((0, 1900)),
          Node((0, 1400), AirbridgeRectangular, a=5, b=4),
          Node((0, 1000)),
          Node((500, 1000), WaveguideCoplanarSplitter),
          Node((900, 1000)),
          Node((900, 750)),
          
          Node((0.0, 750.0)),
          Node((0.0, -750.0), {'length_before': 3000.0}),
          Node((-900.0, -750.0)),
          Node((-900.0, -1000.0)),
          Node((-500.0, -1000.0), 'WaveguideCoplanarSplitter', {'angle': 0.0}),
          Node((0.0, -1000.0)),
          Node((0.0, -1400.0), 'FingerCapacitorSquare'),
          Node((0.0, -1900.0)),
          
          
          
          Node((1060, 100), ab_across=True),
          Node((1100, 100), a=10, b=5),
          Node((1300, 100)),
          Node((1400, 0), n_bridges=3),
          Node((1700, 0), face_id="1t1", connector_type="Single"),
          Node((1900, 0), AirbridgeConnection),
          Node((2100, 0)),
          Node(pya.DPoint(2150, 0), WaveguideCoplanarSplitter, **t_cross_parameters(a=10, b=5), align=("port_left", "port_right")),
          Node(pya.DPoint(2350, 50)),
          Node(pya.DPoint(2400, 50), WaveguideCoplanarSplitter, **t_cross_parameters(a=10, b=5), align=("port_right", "port_left"), inst_name="second_tee"),
          Node(pya.DPoint(2500, 50)),
          Node(pya.DPoint(2600, 50), WaveguideCoplanarSplitter, **t_cross_parameters(a=10, b=5), align=("port_bottom", "port_right")),
          Node(pya.DPoint(2700, -200)),
          Node(pya.DPoint(2700, -500), face_id="2b1", output_rotation=90),
          Node(pya.DPoint(2500, -400))
      ]

    def _make_wg(capfd, nodes):
      layout = pya.Layout()
      wg = WaveguideComposite.create(layout, nodes=nodes1)
      _, err = capfd.readouterr()
      assert err == "", err
      return wg.length()
      
    
    def produce_structures(self):
        """Produces chip frame and possibly other structures before the ground grid.
        This method override that from the KQcircuit / Chip library.
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
      self.produce_n_launchers(**default_sampleholders[self.sampleholder_type], launcher_assignments=launcher_assignments12, enabled=None)
      print(self)


class PCellLib(pya.Library):

  def __init__(self):
    self.description = "QFoundry library"
    self.layout().register_pcell("Fransisco", ChipFrancisco())
    self.register("QFoundry library")
    
# instantiate and register the library
PCellLib()


