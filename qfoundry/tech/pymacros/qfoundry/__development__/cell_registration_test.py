import pya
from pya import *
import os
import pathlib
import importlib

import qfoundry
"""
Cell registration etsts for Paramteric Cells in the PDK

Origynal code by Jasmina Brar, 2023/08
"""

# Enter your Python code here

def cell_registration_test():
  print('QFoundry PDK Python module: PCell registration tests')
  
  current_directory = os.path.dirname(os.path.abspath(__file__))
  custom_exceptions_path = os.path.join(current_directory, "exceptions.py")
  exec(open(custom_exceptions_path).read()) #Import custom exceptions
  
  library_folders = [
      "qfoundry/chips",
      "qfoundry/elements",
      "qfoundry/junctions",
      "qfoundry/qubits",
  ]
  
  tech_name = ["qfoundry"]*6
  library_name =  [ "Chip Library",
                    "Element Library",
                    "Junction Library",
                    "Qubit Library",]
  error_list = []
  for i in range(len(library_folders)):
      # get all .py files in library folder
      files = [
          f
          for f in os.listdir(
              os.path.join(
                  os.path.dirname(os.path.realpath(__file__)), library_folders[i]
              )
          )
          if ".py" in pathlib.Path(f).suffixes and "__init__" not in f
      ]
  
      importlib.invalidate_caches()
      library = pya.Library().library_by_name(library_name[i], tech_name[i])
  
      print("*** Testing library: %s" % library_name[i])
  
      # If library does not exist in klayout
      if library == None:
          raise LibraryNotRegisteredError(library_name[i])
  
      layout = library.layout()
  
      # check that the library is registered in klayout
      try:
          if layout == None:
              raise LibraryNotRegisteredError(library_name[i])
  
      except LibraryNotRegisteredError as e:
          print("Caught {}: {}".format(type(e).__name__, str(e)))
          pya.Application.instance().exit(1)
  
      # loop through all pcells from this library's folder
      for f in files:
          try:
              mm = f.replace(".py", "")
  
              print("  * Testing cell: %s" % mm)
  
              # check that the pcell has been registered in the library's layout
              if mm not in layout.pcell_names():
                  raise PCellRegistrationError(mm, library_name[i])
  
              # instantiate pcell in a new layer and check that it contains polygons
              new_layout = pya.Layout()
              pcell_decl = layout.pcell_declaration(mm)
              new_layout.register_pcell(mm, pcell_decl)
  
              parameter_decl = pcell_decl.get_parameters()
  
              all_params = {}
              for p in parameter_decl:
                  all_params[p.name] = p.default
  
              pcell = new_layout.create_cell(mm, all_params)
  
              # check that there were no errors generated from the pcell
  
              error_shapes = pcell.shapes(new_layout.error_layer())
  
              for error in error_shapes.each():
                  raise PCellImplementationError(mm, library_name, error.text)
  
              if pcell.is_empty() or pcell.bbox().area() == 0:
                  raise PCellInstantiationError(mm, library_name)
  
              # topcell = new_layout.create_cell("top")
              # t = Trans(Trans.R0, 0,0)
              # inst = topcell.insert(CellInstArray(pcell.cell_index(), t))
  
          except (PCellRegistrationError,Exception) as e:
              print("Caught {}: {}".format(type(e).__name__, str(e)))
              error_list += str(e) #return
              # pya.Application.instance().exit(1)
      
      if len(error_list) == 0:
        print(
            "Complete. All pcells from {} folder were successfully registered in {} library".format(
                library_folders[i], library_name[i]
            )
        )
  
  print("Tests complete.")

cell_registration_test()