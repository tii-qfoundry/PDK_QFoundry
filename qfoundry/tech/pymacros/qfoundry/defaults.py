import pya

from kqcircuits.defaults import default_sampleholders, default_marker_type

default_launcher_assignement = {}                          
default_launcher_enabled = {} 

qfoundry_connectors8 = {
        "n": 8,
        "launcher_type": "RF",
        "launcher_width": 300,
        "launcher_gap": 150,
        "launcher_indent": 800,
        "launcher_frame_gap": 180,
        "pad_pitch": 1250,
        "chip_box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(5050, 5050))}
        
qfoundry_connectors12 = {
        "n": 12,
        "launcher_type": "RF",
        "launcher_width": 300,
        "launcher_gap": 150,
        "launcher_indent": 800,
        "launcher_frame_gap": 180,
        "pad_pitch": 1250,
        "chip_box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(5050, 5050))}
        
qfoundry_connectors16 = {
        "n": 16,
        "launcher_type": "RF",
        "launcher_width": 200,
        "launcher_gap": 100,
        "launcher_indent": 600,
        "launcher_frame_gap": 100,
        "pad_pitch": 1250,
        "chip_box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(5050, 5050))}
        
        
default_marker_type = 'QRC12'
default_sampleholders['QRC6'] = qfoundry_connectors12
default_sampleholders['QRC8'] = qfoundry_connectors12
default_sampleholders['QRC12'] = qfoundry_connectors12
default_sampleholders['QRC16'] = qfoundry_connectors16

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
                                                                        
default_launcher_assignement['QRC16'] = {1: "p9", 2: "p13", 3: "p1",4: "p5",
                           5: "p2", 6: "p6", 7: "p7", 8: "p3",
                           9: "p8", 10: "p4", 11: "p16", 12: "p12",
                           13:"p15" , 14: "p11", 15: "p10", 16: "p14"}
                          
     
default_launcher_enabled['QRC6'] = ["W","E", "N", "NE", "S", "SW" ]   
default_launcher_enabled['QRC8'] = ["N", "NE", "EN", "E","S", "SW", "WS","W"]                       
default_launcher_enabled['QRC12'] = ["NW","N", "NE", "EN", "E","ES","SE","S", "SW", "WS","W", "WN"]    
default_launcher_enabled['QRC16'] = [f'p{i+1}' for i in range(16)]                             