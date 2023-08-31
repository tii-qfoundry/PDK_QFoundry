print('Starfish Log: Loading pchips_starfish library')

import os, pathlib, sys
import pya

# Read the files in a specific folder
dir_path = os.path.dirname(os.path.realpath(__file__))
if dir_path not in sys.path:
    sys.path.append(dir_path)
files = [f for f in os.listdir(os.path.join(os.path.dirname(
    os.path.realpath(__file__)),'')) if '.py' in pathlib.Path(f).suffixes  
    and '__init__' not in f 
    and '_library_definition' not in f]

import pchips_starfish
import importlib

importlib.invalidate_caches()
pcells_=[]
for f in files:
    module = 'pchips_starfish.%s' % f.replace('.py','')  ### folder name ###
    print('Starfish Log: - found module: %s' % module)
    m = importlib.import_module(module) 
    print("Starfish Log: %s", m)
    pcells_.append(importlib.reload(m))


# Load all the files in a library in KLayout    
# pchip: A standrad parametric chip layout library 
class Starfish_pchip_library(pya.Library):

  def __init__(self):
    
    # Configure the library identifiers
    library = 'Starfish'
    self.technology=library
    self.description = "v0.0.1, Parametric layout library"
    
    # Save the path
    import os
    self.path = os.path.dirname(os.path.realpath(__file__))

    # Import all the GDS files from the library folder if any
    import os, fnmatch
    dir_path = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./gds"))
    print('Starfish Log:  library path: %s' % dir_path)
    search_str = '*.[Oo][Aa][Ss]' # OAS
    for root, dirnames, filenames in os.walk(dir_path, followlinks=True):
        for filename in fnmatch.filter(filenames, search_str):
            file1=os.path.join(root, filename)
            print("Starfish Log: - reading %s" % file1 )
            self.layout().read(file1)
    search_str = '*.[Gg][Dd][Ss]' # GDS
    
    for root, dirnames, filenames in os.walk(dir_path, followlinks=True):
        for filename in fnmatch.filter(filenames, search_str):
            file1=os.path.join(root, filename)
            print("Starfish Log: - reading %s" % file1 )
            self.layout().read(file1)
                        
    # Create the PCell declarations
    for m in pcells_:
        class_name = m.__name__.replace('pchips_starfish.','')
        class_call = class_name+'()'
        print('Starfish Log: - register_pcell %s, %s' % (class_name,class_call))
        self.layout().register_pcell(class_name, eval(class_call))
                
    print('Starfish Log:  All paramteric chip cells have been registered')
    
    # Register us the library with the technology name
    # If a library with that name already existed, it will be replaced then.
    self.register(library)
    
    
# instantiate and register the library
Starfish_pchip_library()