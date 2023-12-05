# Example of scripted Layout
# Copyright: TII QRC/QFoundry 2023
# Juan E. Villegas, 11th Nov. 2023

from pya import *
import numpy as np

def array_junctions():
    # Create an array of josephson jucntions
    
    # Create a top cell and define base application pointers
    mw = pya.Application().instance().main_window()
    ly = mw.create_layout('Starfish', 1).layout()
    top_cell = ly.create_cell('top')
    lv = mw.current_view()
    lv.select_cell(top_cell.cell_index(), 0)
    dbu = ly.dbu
  
    #Define the layers that willl be used in the layout
    met_layer = pya.LayerInfo(1, 0)
    cap_layer = pya.LayerInfo(1, 0)  #
    fp_layer  = pya.LayerInfo(68, 0) #Floor plan layer
    
    #Draw a floor plan 
    fp_layer_idx = top_cell.layout().layer(fp_layer)
    top_cell.shapes(fp_layer_idx).insert(Box(-11000/dbu,-11000/dbu, 11000/dbu, 11000/dbu))
    
    # Sweep over two parameter
    n = 11 
    sweep_width_t = np.linspace(0.15,0.35,n)
    sweep_width_b = sweep_width_t
    #sweep_angle = np.linspace(0.0,-50.0,n)
    
    #Fixed parameters
    cap_h = 100
    angle = 90.0
    
    
    # Loop through the parameter sweep
    
    dx = 300
    x0 = -(dx*(n-1))/2
    dy = dx
    y0 = x0

    for j, width_t in enumerate(sweep_width_t):
        for i, width_b in enumerate(sweep_width_b):
          
          trans = pya.Trans(pya.Trans.R0, (x0+dx*i)/dbu, (y0+dy*j)/dbu)
          label = "a:%2.1f, w:%.2f"%(width_t,width_b)
          cell_starfish_manhattan = ly.create_cell("Starfish%s" % "Manhattan", "DevelopmentLib", 

            { "angle":angle,
              "junction_width_t":width_t, 
              "junction_width_b":width_b, 
              "draw_cap":True, 
              "draw_patch":False,
              "cap_h":cap_h, 
              "label":label,
              "cap_layer":cap_layer})
          cell_instance = pya.CellInstArray(cell_starfish_manhattan.cell_index(),trans)
          
          label = "%.2f,%.2f"%(width_t,width_b)
          trans = pya.Trans(pya.Trans.R0, (x0+dx*i-100+10)/dbu, (y0+dy*j+cap_h-10)/dbu)

          if cap_layer != pya.LayerInfo(1, 0):
            trans = trans* pya.Trans(pya.Trans.R0,0,25/dbu)
          cell_label = ly.create_cell("TEXT", "Basic", {"text":label, "mag":20,"layer":cap_layer })
          cell_instance_lbl = pya.CellInstArray(cell_label.cell_index(),trans)
             
          shapes_tmn = top_cell.insert(cell_instance)
          shapes_lbl = top_cell.insert(cell_instance_lbl)

array_junctions();