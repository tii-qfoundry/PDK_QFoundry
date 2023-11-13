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
    met_layer = top_cell.layout().layer(pya.LayerInfo(1, 0))
    fp_layer = top_cell.layout().layer(pya.LayerInfo(68, 0))
    
    #Draw a floor plan`f*
    top_cell.shapes(fp_layer).insert(Box(-11000/dbu,-11000/dbu, 11000/dbu, 11000/dbu))
    
    # Sweep over two parameter
    n = 11 
    sweep_width = np.linspace(0.15,0.35,n)
    sweep_angle = np.linspace(0.0,-50.0,n)
    
    # Loop through the parameter sweep
    
    dx = 300
    x0 = -(dx*(n-1))/2
    dy = dx
    y0 = x0
    for j, width in enumerate(sweep_width):
        for i, angle in enumerate(sweep_angle):
          cap_h = 90
          trans = pya.Trans(pya.Trans.R0, (x0+dx*i)/dbu, (y0+dy*j)/dbu)
          label = "a:%2.1f, w:%.2f"%(angle,width)
          cell_starfish_manhattan = ly.create_cell("Starfish%s" % "Manhattan", "DevelopmentLib", 
            { "junction_width_t":width, 
              "junction_width_b":width, 
              "angle": angle,
              "draw_cap":True,
              "patch_scratch":True,
              "path_layer":pya.LayerInfo(2,0),
              "cap_h":cap_h,
              "label":label,
              "conn_height":25.0})
          cell_instance = pya.CellInstArray(cell_starfish_manhattan.cell_index(),trans)       
          shapes = top_cell.insert(cell_instance)

array_junctions();