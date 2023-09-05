
# Example of scripted Layout
# Copyright TII QFoundry 2023
# Juan E. Villegas


from pya import *

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
    
    #Draw a floor plan
    top_cell.shapes(fp_layer).insert(Box(0,-50/dbu, 605/dbu, 555/dbu))
    
    
    # Sweep over two parameter
    sweep_width_t = [0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20]
    sweep_width_b = [0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20]
    
    # Loop through the parameter sweep
    for j in range(len(sweep_width_b)):
        for i in range(len(sweep_width_t)):
          trans = pya.Trans(pya.Trans.R0, (400+(400*i))/dbu, (400*j)/dbu)
          width_t = sweep_width_t[i]
          width_b = sweep_width_b[j]
          
          cell_starfish_manhattan = ly.create_cell("Starfish%s" % "Manhattan", "DevelopmentLib", 
            {"junction_width_t":width_t, "junction_width_b":width_b, "draw_cap":True})
          cell_instance = pya.CellInstArray(cell_starfish_manhattan.cell_index(),trans)
            
          shapes = top_cell.insert(cell_instance)

array_junctions();