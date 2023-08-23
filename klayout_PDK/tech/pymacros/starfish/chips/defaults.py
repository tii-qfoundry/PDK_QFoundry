
from kqcircuits.defaults import default_sampleholders, default_marker_type
                                


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