# $autorun

import os
import pya
import qfoundry as pdk
from kqcircuits.util.library_helper import load_libraries 

def reload_library():
  return __PDK_Lib__()

# The PCell library declaration
class __PDK_Lib__(pya.Library):

  def __init__(self, technology = 'qfoundry'):
    self.description = "QFoundry Library"
    self.technology = "qfoundry"
    tech = pya.Technology.technology_by_name(technology)

    library_folders = [
      "chips",
      "elements",
      "junctions",
      "qubits",
    ]
    
    pdk_module_path = os.path.dirname(pdk.__file__)

    for library_name in library_folders:
      print("Importing module: " + library_name)
      library_path = os.path.join(pdk_module_path, library_name)  
      root, _, files = next(os.walk(library_path))
      
      for file_name in files:
        if file_name.endswith(".py") and file_name != "__init__.py":
          print("Importing file: " + file_name)
          #exec(open(os.path.join(root, file)).read())
          cell_name = file_name[:-3]
          cell_module= import_module_from_path(cell_name, os.path.join(root, file_name))
          
          
          try:
            obj = getattr(cell_module, cell_name)
            if issubclass(obj,pya.PCellDeclarationHelper) or issubclass(obj, pya._PCellDeclarationHelperMixin): #Check if the type of the cell is a Klayout PCellDeclaration
              self.layout().register_pcell(cell_module.__name__, obj())
          except AttributeError as e:
            print(f"Module {cell_module} may not be a PCell (no {cell_name} attribute) : {e}")
          except Exception as e:
            print(f"Error importing {cell_name} from {file_name}: {e}")

    # TODO: The different cells need to be registered in accordance to their respective library fodlers to match KQCircuits Specification
    load_libraries(flush = True)
    self.register("qfoundry")

def import_module_from_path(module_name, file_path):
        '''
        import a Python module given a path 
        '''
        from importlib import util, invalidate_caches
        import sys
        from pathlib import Path
        invalidate_caches()
        
        path = Path(file_path).resolve()
        spec = util.spec_from_file_location(module_name, path)
        
        if not spec:
            raise Exception('Cannot import module: %s, from path: %s ' % (module_name,path))
        
        module = util.module_from_spec(spec)
        sys.modules[module_name] = module  # Add it to sys.modules
        spec.loader.exec_module(module)  # Execute the module code   
             
        return module    


if __name__ == "__main__":
  lib = reload_library()
