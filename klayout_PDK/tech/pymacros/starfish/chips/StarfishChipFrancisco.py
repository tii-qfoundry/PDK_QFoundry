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

from starfish.defaults import default_sampleholders, default_marker_type, default_launcher_assignement, default_launcher_enabled


NAME_BRAND = "TII"
NAME_MASK = "FS_2Q"
NAME_CHIP = "231123"
RESONATOR_LENGTH = 7358

#new paramters for launchers

sampleholder_type_choices = list(default_sampleholders.keys())
            

class StarfishChipFrancisco(Chip):
    sampleholder_type = Param(pdt.TypeList, "Type of the launchers", default_marker_type, choices=sampleholder_type_choices)
    
    name_mask = Param(pdt.TypeString, "Name of the mask", NAME_MASK)
    name_chip = Param(pdt.TypeString, "Name of the chip", "")
    name_copy = Param(pdt.TypeString, "Name of the copy", NAME_CHIP)
    name_brand = Param(pdt.TypeString, "Name of the brand", NAME_BRAND)
    frames_marker_dist = Param(pdt.TypeList, "Marker distance from edge for each chip frame", [800, 400], unit="[μm]")
    frames_diagonal_squares = Param(pdt.TypeList, "Number of diagonal marker squares for each chip frame", [0, 0])
    cpw_length = Param(pdt.TypeDouble, "Length of the resonator", RESONATOR_LENGTH)
    
    a = Param(pdt.TypeDouble, "Width of the center conductor", 15)
    b = Param(pdt.TypeDouble, "Width of gap", 7.5)
    r = Param(pdt.TypeDouble, "Turn radius", 150, hidden=True)
    
    def nodes_res(self):
      """ Node list specifying the composite waveguide """
      
      splitter_params = t_cross_parameters(self.a,self.b,self.a,self.b)
      cpw_fix_length = 5272.6185408 #Length of waveguides except the extended section in node 9
      
      #cpw_length = 7358
      
      return [
          Node((0.0, 0.0)),
          Node((0.0, 300.0),FingerCapacitorSquare,
             finger_number= 3, 
             finger_width= 3,
             finger_gap= 3,
             finger_length= 30),
          Node((0.0, 900.0)),
          Node((-500.0, 900.0),WaveguideCoplanarSplitter,
              angles = [0,180,270],
              lengths=splitter_params['lengths'],
              a_list=splitter_params['a_list'],
              b_list=splitter_params['b_list']),
          Node((-1000.0, 900.0)),
          Node((-1000.0, 1200.0)),
          Node((0.0, 1200.0)),
          Node((0.0, 2250.0),length_before=self.cpw_length-cpw_fix_length),
          Node((1000.0, 2250.0)),
          Node((1000.0, 2550.0)),
          Node((500.0, 2550.0),WaveguideCoplanarSplitter,
              angles = [0,180,90],
              lengths=splitter_params['lengths'],
              a_list=splitter_params['a_list'],
              b_list=splitter_params['b_list']),
          Node((0.0, 2550.0)),
          Node((0.0, 3150.0),FingerCapacitorSquare,
             finger_number= 3, 
             finger_width= 3,
             finger_gap= 3,
             finger_length= 30),
          Node((0.0, 3450.0))
      ]

    def nodes_coupler_01(self):
      return [
        Node((0.0, 0.0)),
        Node((0.0, 280.0)),
        Node((500-self.a, 280.0))
      ]
    
    def _make_wg(self, nodes):
      layout = pya.Layout()
      wg_cell = WaveguideComposite.create(layout, nodes=nodes)
      top_cell = layout.top_cell()
      top_cell.insert(pya.DCellInstArray(wg_cell.cell_index(), pya.DTrans()))
      return wg_cell.length()
      
    
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
      
      self.insert_cell(WaveguideComposite,nodes=self.nodes_res(),trans = pya.DTrans(0,0,2525, 800))
      self.insert_cell(WaveguideComposite,r=50, term2=20, nodes=self.nodes_coupler_01(),
        trans = pya.DTrans(0,0,2525, 800)*pya.DTrans(0,0,500, 2550+self.a))
      self.insert_cell(WaveguideComposite,r=50, term2=20, nodes=self.nodes_coupler_01(),
        trans = pya.DTrans(0,0,2525, 800)*pya.DTrans(2,False,-500, 900-self.a))
        
      
        
        
      print(self)


