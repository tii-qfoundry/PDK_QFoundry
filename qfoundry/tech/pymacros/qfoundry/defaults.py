# This code is part of KQFoundry PDK
# Copyright (C) 2025 TII
#
# It uses the KQcircuits library

import pya
from kqcircuits.defaults import default_sampleholders, default_marker_type

default_launcher_assignement = {}                          
default_launcher_enabled = {} 

LAUNCHER_FRAME_GAP = 100
LAUNCHER_WIDTH = 200
LAUNCHER_GAP = 100
FRAME_WIDTH = 200

qfoundry_connectors2 = {
        "n": 2,
        "launcher_type": "RF",
        "launcher_width": LAUNCHER_WIDTH,
        "launcher_gap": LAUNCHER_GAP,
        "launcher_indent": FRAME_WIDTH+LAUNCHER_WIDTH*2,
        "launcher_frame_gap": LAUNCHER_FRAME_GAP,
        "pad_pitch": 1250,
        "chip_box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(5000, 5000))}

qfoundry_connectors8 = {
        "n": 8,
        "launcher_type": "RF",
        "launcher_width": 300,
        "launcher_gap": 150,
        "launcher_indent": 800,
        "launcher_frame_gap": 180,
        "pad_pitch": 1250,
        "chip_box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(5000, 5000))}
        
qfoundry_connectors12 = {
        "n": 12,
        "launcher_type": "RF",
        "launcher_width": 300,
        "launcher_gap": 150,
        "launcher_indent": 800,
        "launcher_frame_gap": 180,
        "pad_pitch": 1250,
        "chip_box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(5000, 5000))}
        
qfoundry_connectors16 = {
        "n": 16,
        "launcher_type": "RF",
        "launcher_width": 200,
        "launcher_gap": 100,
        "launcher_indent": 600,
        "launcher_frame_gap": 100,
        "pad_pitch": 1250,
        "chip_box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(5000, 5000))}
        
        
default_marker_type = 'QRC12'
default_sampleholders['QRC2'] = qfoundry_connectors2
default_sampleholders['QRC6'] = qfoundry_connectors12
default_sampleholders['QRC8'] = qfoundry_connectors12
default_sampleholders['QRC12'] = qfoundry_connectors12
default_sampleholders['QRC16'] = qfoundry_connectors16

default_launcher_assignement['QRC2'] = {i: f'p{i}' for i in range(4+1)}
                          
default_launcher_assignement['QRC6'] = {1: "NW", 2: "N", 3: "NE",
                          4: "ES", 5: "E", 6: "ES", 
                          7: "SE", 8: "S", 9: "SW",
                          10: "WS", 11: "W", 12: "WN"}
                          
default_launcher_assignement['QRC8'] = {1: "NW", 2: "N", 3: "NE",
                          4: "ES", 5: "E", 6: "ES", 
                          7: "SE", 8: "S", 9: "SW",
                          10: "WS", 11: "W", 12: "WN"}
                          
default_launcher_assignement['QRC12'] = {1: "NW", 2: "N", 3: "NE",
                          4: "ES", 5: "E", 6: "ES", 
                          7: "SE", 8: "S", 9: "SW",
                          10: "WS", 11: "W", 12: "WN"}  
                                                                        
default_launcher_assignement['QRC16'] = {i: f'p{i+1}' for i in range(16+1)}
                          
default_launcher_enabled['QRC2'] = ['p2','p4']                             
default_launcher_enabled['QRC6'] = ["W","E", "N", "NE", "S", "SW" ]   
default_launcher_enabled['QRC8'] = ["N", "NE", "EN", "E","S", "SW", "WS","W"]                       
default_launcher_enabled['QRC12'] = ["NW","N", "NE", "EN", "E","ES","SE","S", "SW", "WS","W", "WN"]    
default_launcher_enabled['QRC16'] = [f'p{i+1}' for i in range(16+1)]                             