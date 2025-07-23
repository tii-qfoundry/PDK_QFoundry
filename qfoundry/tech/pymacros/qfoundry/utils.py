
import pya

def _round_corners_and_append(polygon: pya.DPolygon, polygon_list: list[pya.DPolygon] = None, rounding_params: dict = None, dbu = 0.001) -> list[pya.DPolygon]:
    """ Helper function to round corners of a polygon and append it to a list.
        If the polygon is empty, it returns the polygon list unchanged.
        If the polygon is not empty, it rounds the corners, converts it to integer coordinates,
        and appends it to the polygon list.
        
        Args:            
            polygon (pya.DPolygon): The polygon to round and append.
            polygon_list (list[pya.DPolygon], optional): The list to append the rounded polygon to. Defaults to None.
            rounding_params (dict, optional): Parameters for rounding corners. Defaults to None.
        Returns:
            list[pya.DPolygon]: The updated polygon list with the rounded polygon appended.
    """

    if polygon.is_empty():
        return polygon_list
    
    if polygon_list is None:
        polygon_list = []

    if rounding_params is None:
        rounding_params = {
            "rinner": 5,  # inner corner rounding radius
            "router": 10,  # outer corner rounding radius
            "n": 64,  # number of point per rounded corner
        }
    """Rounds the corners of the polygon, converts it to integer coordinates, and adds it to the polygon list."""
    polygon = polygon.round_corners(rounding_params["rinner"], rounding_params["router"], rounding_params["n"])
    polygon_list.append(polygon.to_itype(dbu))  
    return polygon_list
            
def _add_shapes(cell, shapes, layer) -> pya.Region:
    """ Helper function to merge shapes into a region and add it to a layer.
        If the shapes are a list, it merges them into a single region. 
        If the shapes are a single shape, it converts it to a region.
        Args:
            shapes (list[pya.DPolygon] or pya.DPolygon): The shapes to merge and add.
            layer (pya.Layer): The layer to add the shapes to.
        Returns:
            pya.Region: The region created from the shapes and added to the layer.

    """
    if type(shapes) == list:
        region:pya.Region = pya.Region(array=shapes).merged()
    else:
        region:pya.Region = pya.Region(shapes).merged()
    cell.shapes(layer).insert(region)
    return region    
        
def _substract_shapes(cell, shapesA, shapesB, layer) -> pya.Region:
    """ Helper function to subtract shapesB from shapesA and add the result to a layer.
        Args:
            shapesA (list[pya.DPolygon] or pya.DPolygon): The shapes to subtract from.
            shapesB (list[pya.DPolygon] or pya.DPolygon): The shapes to subtract.
            layer (pya.Layer): The layer to add the resulting region to.
        Returns:
            pya.Region: The region created from the subtraction of shapesB from shapesA and added to the layer.
    """
    region = pya.Region(shapesA).merged()-pya.Region(shapesB).merged()
    cell.shapes(layer).insert(region)
    return region

def test_pcell(pcell_decl: pya.PCellDeclarationHelper,pcell_params:dict = None, pcell_trans: pya.Trans = None,technology: str = "qfoundry"):
    """
    Test a PCellDeclarationHelper Parametric Cell by creating a new layout and instanciating the PCell in the top cell.
    """
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