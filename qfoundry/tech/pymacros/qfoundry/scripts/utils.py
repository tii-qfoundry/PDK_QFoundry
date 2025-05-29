
import pya
from qfoundry.scripts.library import PDK_Lib

def test_pcell(pcell_decl: pya.PCellDeclarationHelper,pcell_params:dict = None, pcell_trans: pya.Trans = None,technology: str = "qfoundry"):
    '''
    Test a PCellDeclarationHelper Parametric Cell by creating a new layout and instanciating the PCell in the top cell.
    '''
    # Create a new layout instance
    mw = pya.Application().instance().main_window()
    ly = mw.create_layout('qfoundry', 1).layout()
    top_cell = ly.create_cell('top')
    ly.dbu = 0.001
    tech = pya.Technology.technology_by_name(technology)
    
    print(pcell_decl)
    # Create a new cell and instantiate the PCell
    cell = ly.create_cell(pcell_decl.__name__, "qfoundry", pcell_params)
    cell_instance = pya.CellInstArray(cell.cell_index(),pcell_trans)
    top_cell.insert(cell_instance)

    # Select the top cell in the view   
    lv = mw.current_view()
    lv.select_cell(top_cell.cell_index(), 0)