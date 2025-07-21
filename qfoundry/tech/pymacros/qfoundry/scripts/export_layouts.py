# Klayout python script
# Export all top cells in the current layout to inidivudal GDS files.
# An generates a report of the exported layouts, the josephson jucntion 
# locations and current (extracted from the Josephson Jucntion cell names)

# Teh jospehson junctions are expected to be named as follows:
#   QW_<type>_<current>_nA
#   where <type> = 'single_junction'
#   <current> is the current in nA (separated by '_' e.g QW_single_junction_10_5_nA)

import pya 
import os
import sys

def export_layouts(layout, output_dir):
    # Create output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize report data
    report_data = []

    # Iterate over all top cells in the layout
    for cell_index in layout.each_top_cell():
        cell = layout.cell(cell_index)
        cell_name = cell.name
        file_path = os.path.join(output_dir, f"{cell_name}.gds")
        
        # Remove anything in layers 133/1
        # Remove all shapes from layer 133/1
        layer_info = pya.LayerInfo(133, 1)
        if layout.layer(layer_info) is not None:
            layer_index = layout.layer(layer_info)
            cell.shapes(layer_index).clear()

        # Export the cell to GDS file
        save_options = pya.SaveLayoutOptions()
        save_options.format = "GDS2"
        save_options.select_all_layers()
        save_options.add_cell(cell_index)
        layout.write(file_path, save_options)
        
        # Extract Josephson junction information for all the josephson junctions
        # junction in this cell
        
        for instance in cell.each_inst():
            inst_cell = instance.cell
            if "QW_single_junction" in inst_cell.name:
                # Extract the current from the cell name
                parts = inst_cell.name.split('_')
                cell_location = instance.trans.disp
                if len(parts) >= 4 and parts[-1] == "nA":
                    current: float = int(parts[-3]) + float('0.' + parts[-2])  # Convert to nA
                    # Append to report data
                    report_data.append((cell_name, inst_cell.name, cell_location, current))


    return report_data

if __name__ == "__main__":
    # Get the current layout
    layout = pya.Application.instance().main_window().current_view().active_cellview().layout()
    
    # Define output directory
    output_dir = "exported_layouts"
    
    cellview = pya.Application.instance().main_window().current_view().active_cellview()
    if cellview.filename():
        working_dir = os.path.dirname(cellview.filename())
        output_dir = os.path.join(working_dir, output_dir)
        print(f"Exporting layouts to: {output_dir}")
    else:
        print(f"No file path found, using current directory: {output_dir}")
    # Export layouts and get report data
    report_data = export_layouts(layout, output_dir)
    
    # Print report
    print("Exported Layouts Report:")
    for _, cell_name, cell_location, current in report_data:
        print(f"Cell: {cell_name}\t Location: {cell_location}\t Ic: {current} nA")

    # Save report to a text file
    report_file = os.path.join(output_dir, "export_report.txt")
    with open(report_file, "w") as f:
        f.write("Exported Layouts Report:\n")
        f.write("========================================\n")
        last_parent_layout = "Unknown"
        for parent_layout, cell_name, cell_location, current in report_data:
            if parent_layout != last_parent_layout:
                last_parent_layout = parent_layout
                f.write(f"\nLayout: {parent_layout}\n")
                f.write("Cell Name\t Location\t Ic (nA)\n")
                f.write("-" * 50 + "\n")
            f.write(f"{cell_name}\t {cell_location}\t {current}\n")
