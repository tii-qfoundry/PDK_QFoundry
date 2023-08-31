import pya

from kqcircuits.defaults import default_sampleholders, default_marker_type
default_launcher_assignement = {}                          


qfoundry_connectors8 = {
        "n": 8,
        "launcher_type": "RF",
        "launcher_width": 300,
        "launcher_gap": 150,
        "launcher_indent": 800,
        "launcher_frame_gap": 180,
        "pad_pitch": 1250,
        "chip_box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(6200, 6200))}
qfoundry_connectors12 = {
        "n": 12,
        "launcher_type": "RF",
        "launcher_width": 300,
        "launcher_gap": 150,
        "launcher_indent": 800,
        "launcher_frame_gap": 180,
        "pad_pitch": 1250,
        "chip_box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(6200, 6200))}
        
        
default_marker_type = 'QRC8'
default_sampleholders['QRC8'] = qfoundry_connectors8
default_sampleholders['QRC12'] = qfoundry_connectors12

default_launcher_assignement['QRC8'] = {1: "NW", 2: "NE", 3: "EN", 4: "ES", 5: "SE", 6: "SW", 7: "WS", 8: "WN"}
default_launcher_assignement['QRC12'] = {1: "NW", 2: "N", 3: "NE",
                          4: "ES", 5: "E", 6: "ES", 
                          7: "SE", 8: "S", 9: "SW",
                          10: "WS", 11: "W", 12: "WN"}