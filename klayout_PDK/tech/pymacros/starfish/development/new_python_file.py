
from kqcircuits.pya_resolver import pya
import kqcircuits.util.macro_prepare as macroprep
from kqcircuits.klayout_view import KLayoutView

from kqcircuits.elements.waveguide_composite import WaveguideComposite
from kqcircuits.elements.waveguide_composite import Node

#view = KLayoutView(current=True, initialize=False)
#layout = KLayoutView.get_active_layout()



#(layout, top_c, layout_view, cell_view) = macroprep.prep_empty_layout()

#top_cell = layout.create_cell('top')

#layout_view = view.layout_view
#cell_view = view.get_active_cell_view()
#cell_view.cell_name = 'top'  # Shows the new cell
        
#wg_cell = WaveguideComposite.create(layout, nodes=[Node((-1.0, 750.0)), Node((-901.0, -750.0)), Node((-901.0, -1000.0)), Node((-1.0, -1000.0)), Node((-1.0, -1900.0), length_before=2000.0)])
#top_cell.insert(pya.DCellInstArray(wg_cell.cell_index(), pya.DTrans()))