# PDK_Starfish
TII QFoundry standard PDK for superconductive qubit fabrication. It uses the KQcircuitrs.

## Installation

### KQcircuits
This PDK works with the KQcircuits package, develloped by IQM at Aalto University. To use 
Check the documentation in https://meetiqm.com/developers/kqcircuits/. KQcircuits is distributed using KLayout's Package Manager.
- Open KLayout, then menu item Tools | Manage Packages
- Install the 'KQcircuits' package
- Restart KLayout
You should see a new menu item, "KQcircuits", and a new quick command button named 'Edit Node'. Check back periodically in the Package Manager for updates.

### Installing the PDK
To install, first you need to clone this repository to your local machine using git. In Windows, you can install GitHub Desktop https://desktop.github.com and then come back to this website and click on the green button in this page: 'Code' > 'Open in Github Desktop'. You should now have a copy of the repository in your machine. Now:
- Start KLayout
- Go to menu 'Tools' > 'Manage Technologies'
- In the panel on the left (Technologies), right click and select 'Import Technology'

<p align="center"><img width="326" alt="image" src="https://github.com/tii-qfoundry/PDK_Starfish/assets/14344419/32b387f9-40fb-43f5-80e9-e71746cca50d"> </p>
  
- Navigate in your GitHub repository to '%USERPROFILE%\Documents\Github\PDK_Starfish\klayout_PDK\tech', here select the 'Starfish.lyt' technology specification. You should immediatly see a new technology with multiple panels with its different specifications. Click OK to accept the new changes.
<p align="center"><img width="449" alt="image" src="https://github.com/tii-qfoundry/PDK_Starfish/assets/14344419/5f98f33f-0918-4ebd-a565-8edf2b78646f"> </p>

- When prompted to run the macros in the new technology, make sure to accept. This will configure KQCircuits to include the custom cells of the PDK.
<p align="center"><img width="350" alt="image" src="https://github.com/tii-qfoundry/PDK_Starfish/assets/14344419/bb6e27a2-c7fb-4a12-9f2b-d21c72d37239"> </p>

If you cannot see the custom cells of the Starfish PDK (if you didnt accept running the macros for example), you may need to configure KQCircuits to recognize all the cells from the PDK. Go to the menu KQCircuits > Add User Package, and in the source directory, point to the folder '%USERPROFILE%\Github\PDK_Starfish\klayout_PDK\tech\pymacros\starfish'.

<p align="center"> <img width="449" alt="image" src="https://github.com/tii-qfoundry/PDK_Starfish/assets/14344419/41c81ad7-5c1d-4aa4-8cac-cbe46b4be78c">  </p>

Now you are redy to design!

## Design a basic layout

The fastest way to start a design is using the GUI of KLayout. First create a new layout by going to File > New Layout, in the window that appears select the correct technology (Starfish) and make sure to set the database units as 0.001 um (the default for the TII Quantum Foundry is indeed 0.001 um, but a you can use any other specification according to you foundry's process).

<p align="center"><img width="305" alt="image" src="https://github.com/tii-qfoundry/PDK_Starfish/assets/14344419/6958674b-6697-4122-a1b1-6ea58ce2388a"> </p>

If you forget to set the database units, you can always go to File > Layout Properties and set them in the window that pops out, this will scale all the components in your layout, so make sure you do this before starting your work. Some parametric elements will re-generate with the correct size after you reload KLayout but any flat polygons will need to be manually scaled after the change in units.

### The Starfish Library

In the Library window, you will see that a set of PDK specific groups appears, these include several components of the TII QFoundry that include Parametric Cells (PCells), Fixed Cells, and Black Box (BB) cells. You can drag and drop any of these components into your layout. All of thee are extensions of the KQcircuits Package but will work even when the PDK is not selected as your technology. Note that updates in KQCircuits may make some of the cells of the PDK incompatible at any time, but we make sure to update these cells as soon as stable releases are available.

- PCells are a set of parameterized common integrated devices that allow fast placement of components with variable complexity in your layout. All these components have no CML association in the current version of the PDK, except for waveguides, that use the Ligentec waveguide models.
- Fixed Cells are a set fixed devices, specifically designed for the TII Ligentec AN800 PDK (No devices in the current release).
- Black Box cells are placeholders for undisclosed IP from the QFoundry.

All files are organized following the KQcircuit file structure {Elements, junctions, qubits, test_strctureschips}.

### Define your layout dimensions
The Quantum foundry has specific dimensions for the work submissions, so start by creating a Chip Size Layer (in the CSL layer 100/2) and a Chip Handling Size (in the CHS layer 100/0) with the correct dimensions. In the current version of the PDK, the CHS is 30 x 30 mm and the CSL is 15 x 15 mm.

### Create your layout design
Drag and drop components in your layout, and connect them using 'paths' in the 'Waveguide' layer (you can use any layer, but for organization, you will find it useful to use this).

## Checking your design
A series of rules now need to be checked before your layout is ready for submission. Rules may be application-defined, like connectivity between components or making sure that two devices are not overlapping, or process defined, checking that two different elements are not too close to each other or making sure that an etching step has something to etch under it. 

### DRC verification
DRC rules from TII QFoundry (basic component overlapping checks) can be tested using KLayout's native DRC Check engine. To run this just press the key 'D', or select Tools > Verification > DRC. The current DRC's are updated to the QFoundry's most up to date process. When you run the DRC a database visualizer will open with the list of DRC check made and the number of errors found in eacah category. By selecting any one category or element from this list you can visualize the area where the error occurs and get a description of the error:
<p align="center"> <img src="https://user-images.githubusercontent.com/14344419/186352926-bfb39350-08f3-41ec-b7ab-997ce7dd4636.png" width="600"  /></p>

### Layout submission verification
This runs a set of scripts from the QFoundry that test basic layout considerations, like checking that the Chip Size cells are correctly included and that the size and layers used are consistent with their definitions. To run this check go to KQCircuits > Starfish x.x.x > Run Ligentec Pre-submission check.

## Exporting your design
Go to KQCircuits > Starfish > Export for fabrication
(to do...)
This will generate an OASIS file where all cells except black boxes have been flattened and elements in layers not part of the Fabrication PDK are removed. The new file should be stored in the same location as your layout file.

## Creating your own components
To allow the cnsistnecy of the Layout to System specification from KLayout, we need that  **all** elements in a circuit to be proper KQcirucits components. Because KQcirucits is a layout centric design tool, creating new components from the layout is very easy and can all be done using basic elements avaiable in the KLayout base library.

