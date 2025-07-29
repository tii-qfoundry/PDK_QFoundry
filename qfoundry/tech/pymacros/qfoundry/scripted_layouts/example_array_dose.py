
# Example of scripted Layout
# Copyright TII QFoundry 2023
# Juan E. Villegas

# Array with multiplejucntion widths (symmetric) and multiple dose factors

from pya import *
import numpy as np

def array_junctions():
    # Create an array of josephson jucntions
    
    # Create a top cell and define base application pointers
    mw = pya.Application().instance().main_window()
    ly = mw.create_layout('Qfoundry', 1).layout()
    top_cell = ly.create_cell('top')
    lv = mw.current_view()
    lv.select_cell(top_cell.cell_index(), 0)
    dbu = ly.dbu
  
    #Define the layers that willl be used in the layout
    met_layer = top_cell.layout().layer(pya.LayerInfo(1, 0))
    fp_layer = top_cell.layout().layer(pya.LayerInfo(68, 0))
    
    #Draw a floor plan
    top_cell.shapes(fp_layer).insert(Box(-2700/dbu,-2700/dbu, 2700/dbu, 2700/dbu))
    
    x0 = -2000
    y0 = x0
    dx = 400
    dy = dx
    
    # Sweep over two parameter
    sweep_width = np.linspace(0.15,0.35,11)
    sweep_dose = np.linspace(1,2,11)
    
    # Loop through the parameter sweep
    for j in range(len(sweep_dose)):
        for i in range(len(sweep_width)):
          trans = pya.Trans(pya.Trans.R0, (x0+(dx*i))/dbu, (y0+(dy*j))/dbu)
          width_t = sweep_width[i]
          width_b = width_t
          dose = sweep_dose[i]*1000
          layer_dose = pya.LayerInfo(2, dose)
          cell_qfoundry_manhattan = ly.create_cell("Qfoundry%s" % "Manhattan", "DevelopmentLib", 
            {"junction_width_t":width_t, "junction_width_b":width_b, "draw_cap":True, "cap_h":150,"l_layer":layer_dose})
          cell_instance = pya.CellInstArray(cell_starfish_manhattan.cell_index(),trans)
            
          shapes = top_cell.insert(cell_instance)

array_junctions();