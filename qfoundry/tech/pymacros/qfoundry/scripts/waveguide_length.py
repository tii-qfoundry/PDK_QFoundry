
import pya

def measure_waveguide_length(layout, selection):
    """
    Measure the total length of WaveguideCoplanar and WaveguideComposite cells
    in the selected cell and its nested hierarchy.
    
    The length is calculated by measuring the area of geometry on layer 130/1
    and dividing by the center conductor width (parameter 'a').
    
    Args:
        layout: KLayout Layout object
        selection: List of selected cells or cell instances
        
    Returns:
        dict: Dictionary with cell names as keys and their measured lengths in micrometers
    """
    
    # Define the measurement layer (130/1 - base metal gap)
    layer_info = pya.LayerInfo(130, 1)
    layer_idx = layout.layer(layer_info)
    
    if layer_idx is None:
        print("Warning: Layer 130/1 not found in layout")
        return {}
    
    # Dictionary to store results: {cell_name: length_in_um}
    waveguide_lengths = {}
    total_length = 0.0
    
    # Get database unit
    dbu = layout.dbu
    
    def is_waveguide_cell(cell):
        """Check if a cell is a WaveguideCoplanar or WaveguideComposite"""
        cell_name = cell.name
        return "Waveguide$Coplanar" in cell_name or "Waveguide$Composite" in cell_name
    
    def get_parameter_a(cell):
        """
        Try to extract the 'a' parameter (center conductor width) from a PCell.
        Returns the parameter value in micrometers, or None if not found.
        """
        try:
            # Check if this is a PCell variant
            if cell.is_pcell_variant():
                pcell_decl = cell.pcell_declaration()
                if pcell_decl:
                    # Get the PCell parameters
                    params = cell.pcell_parameters_by_name()
                    
                    # Try to get the 'a' parameter
                    if 'a' in params:
                        return params['a']
                    
                    # Some waveguides might store it differently
                    for key in params.keys():
                        if 'width' in key.lower() and 'center' in key.lower():
                            return params[key]
                        if key.lower() == 'a':
                            return params[key]
        except Exception as e:
            print(f"Warning: Could not extract parameter 'a' from cell {cell.name}: {e}")
        
        # Default value if parameter not found (typical default from KQCircuits)
        return 10.0  # Default center conductor width in micrometers
    
    def measure_cell_waveguide(cell, transformation=pya.Trans()):
        """
        Recursively measure waveguide length in a cell and its children.
        
        Args:
            cell: The cell to measure
            transformation: Cumulative transformation from parent cells
        """
        nonlocal total_length
        
        # Check if this cell itself is a waveguide
        if is_waveguide_cell(cell):
            # Get the center conductor width parameter
            width_a = get_parameter_a(cell)
            
            if width_a is None or width_a == 0:
                print(f"Warning: Could not determine width 'a' for {cell.name}, skipping")
                return
            
            # Calculate the area of shapes on layer 130/1 in this cell
            area_dbu_sq = 0.0
            shapes_iter = cell.shapes(layer_idx)
            
            for shape in shapes_iter.each():
                if shape.is_polygon() or shape.is_box() or shape.is_path():
                    # Get the polygon and calculate its area
                    if shape.is_polygon():
                        poly = shape.polygon
                    elif shape.is_box():
                        poly = shape.box.to_dtype(dbu)
                    elif shape.is_path():
                        poly = shape.path.polygon()
                    
                    # Area in database units squared
                    area_dbu_sq += abs(poly.area())
            
            # Convert area from dbu^2 to um^2
            area_um_sq = area_dbu_sq * (dbu ** 2)
            
            # Calculate length: area / width
            if area_um_sq > 0:
                length_um = area_um_sq / width_a
                
                # Store result
                cell_key = f"{cell.name} (a={width_a:.2f}µm)"
                if cell_key in waveguide_lengths:
                    waveguide_lengths[cell_key] += length_um
                else:
                    waveguide_lengths[cell_key] = length_um
                
                total_length += length_um
                
                print(f"  Found waveguide: {cell.name}")
                print(f"    Area: {area_um_sq:.2f} µm², Width (a): {width_a:.2f} µm, Length: {length_um:.2f} µm")
        
        # Recursively process all instances in this cell
        for inst in cell.each_inst():
            child_cell = inst.cell
            # Combine transformations
            combined_trans = transformation * inst.trans
            measure_cell_waveguide(child_cell, combined_trans)
    
    # Process the selection
    print("\n=== Measuring Waveguide Lengths ===\n")
    
    if not selection or len(selection) == 0:
        print("No cells selected. Please select a cell to measure.")
        return {}
    
    # Process each selected cell
    for sel in selection:
        # Get the cell from the selection
        if hasattr(sel, 'cell'):
            cell = sel.cell
        elif hasattr(sel, 'inst'):
            cell = sel.inst().cell
        else:
            # Assume it's already a cell
            cell = sel
        
        print(f"Analyzing cell: {cell.name}")
        print("-" * 50)
        measure_cell_waveguide(cell)
    
    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if waveguide_lengths:
        for cell_name, length in sorted(waveguide_lengths.items()):
            print(f"{cell_name}: {length:.2f} µm")
        print("-" * 50)
        print(f"TOTAL LENGTH: {total_length:.2f} µm ({total_length/1000:.3f} mm)")
    else:
        print("No waveguides found in the selected cells.")
    
    print("=" * 50 + "\n")
    
    return waveguide_lengths


if __name__ == "__main__":
    # Get the current view and selection
    app = pya.Application.instance()
    mw = app.main_window()
    view = mw.current_view()
    
    if not view:
        print("No layout view open. Please open a layout first.")
    else:
        layout = view.active_cellview().layout()
        
        # Get the current selection
        selection = []
        for sel in view.each_object_selected():
            if sel.is_cell_inst():
                selection.append(sel.inst().cell)
            elif hasattr(sel, 'shape'):
                # If a shape is selected, use its parent cell
                selection.append(view.active_cellview().cell)
                break
        
        # If nothing is selected, use the current top cell
        if not selection:
            current_cell = view.active_cellview().cell
            if current_cell:
                selection = [current_cell]
                print(f"No selection found. Using current cell: {current_cell.name}")
            else:
                print("No cell available. Please open a layout and select a cell.")
        
        if selection:
            results = measure_waveguide_length(layout, selection)

            
            
    