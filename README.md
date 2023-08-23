# PDK_Starfish
QFoundry standard PDK for superconducting qbit fabrication.

## Installation

### KQcircuits
This PDk works with the KQcircuits package, develloped by IQM(TM) at Aalto University. To use 
Check the documentation in https://meetiqm.com/developers/kqcircuits/. KQcircuits is distributed using KLayout's Package Manager.
- Open KLayout, then menu item Tools | Manage Packages
- Install the 'KQcircuits' package
- Restart KLayout
You should see a new menu item, "KQcircuits", and a new quick command button named 'Edit Node'. Check back periodically in the Package Manager for updates.

### Installing the PDK
To install, first you need to clone this repository to your local machine using git. In Windows, you can install GitHub Desktop https://desktop.github.com and click on the green button in this page: 'Code' > 'Open in Github Desktop'. 
- Start KLayout
- Go to menu 'Tools' > 'Manage Technologies'
- In the window on the left (Technologies), right click and select 'Import Technology'
- Navigate to your GitHub folder and select Github / PDK_Starfish / klayout_PDK / tech / Starfish.
- Create a new layout: Select the menu 'File' > 'New Layout', use Technology = Starfish

## Design a basic layout

The fastest way to start a design is using the GUI of KLayout. First create a new layout by going to File > New Layout, in the window that appears select the correct technology (Ligentec_AN800) and make sure to set the database units as 0.005 um (the default for the Ligentec is indeed 0.005 um, but a bug in the current version of KLayout prevent this from being applied to your Layout). 

<p align="center"><img src="https://user-images.githubusercontent.com/14344419/184589605-1dcc6e92-b5cb-4e9a-855f-2b2a4cd85267.png" width="400"/> </p>


### The Ligentec AN_800 Library
If you forgot to set the database units, you can always go to File > Layout Properties and set them in the window that pops out, this will scale all the components in your layout, so make sure you do this before starting your work.

In the Library window, you will see that a set of PDK specific groups appears, these include several components of the TII Ligentec PDK that include Parametric Cells (PCells), Fixed Cells, and Black Box (BB) cells. You can drag and drop any of these components into your layout. 

- PCells are a set of parameterized common integrated devices that allow fast placement of components with variable complexity in your layout. All these components have no CML association in the current version of the PDK, except for waveguides, that use the Ligentec waveguide models.
- Fixed Cells are a set fixed devices, specifically designed for the TII Ligentec AN800 PDK (No devices in the current release).
- Black Box cells are placeholders for undisclosed IP from Ligentec, that would be replaced upon fabrication for the actual devices. A few of these include CML SPICE parameters to connect to their corresponding component model. The BB Cells in the TII Ligentec PDK have been adapted to be compatible with SiEPIC tools, but you need to take special care that they are correctly used in your design and that their dimensions and labels correspond to the latest version of the released Ligentec component library.

### Define your layout dimensions
The foundry has specific dimensions for the work submissions, so start by creating a Chip Size Layer (in the CSL layer 100/2) and a Chip Handling Size (in the CHS layer 100/0) with the correct dimensions. In the current version of the PDK. These two boxes are often of the same size, except where you need devices to protrude from the actual final chip size, in which case the CSL layer may be larger than the CHS. Aside from intended protrusions, all other devices must fit inside of the CSL box. Cells that includes the standard full and half reticles are included in the Ligentec_AN800_BB_Alpha library.

> When defining your chip dimensions, make sure that the lower left corner of your box is exactly at (0,0) or you may fail DRC checks from the foundry.

### Create your layout design
Drag and drop components in your layout, and connect them using 'paths' in the 'Waveguide' layer (you can use any layer, but for organization, you will find it useful to use this). To convert a path into a waveguide, you want to go to SiEPIC x.x.x >  Waveguides > Path to Waveguide (or hot the key '2'). In the GUI that appears select the waveguide configuration, you want to use and click ok. You may create any number of new waveguide configurations by changing the 'WAVEGUIDE.XML' file in the PDK.

<p align="center"><img src="https://user-images.githubusercontent.com/14344419/184619349-4353c747-f35c-4fae-b125-09cd88c2a40c.png" width="400" class="center"  /></p>

SiEPIC will automatically create a waveguide cell, setting Bezier curves on every corner (using the radius defined in the WAVEGUIDE specification) and snapping its ends to the connected component's ports. You may add as many pcells, fixed cells, and bb cells as you need. You may also add custom-made cells with polygons defined in the correct layers, these will probably fail TII and SiEPIC DRC but they may still be good form fabrication provided they comply with the Ligentec Design Rules.

This is an example of how your layout may look by now:

<p align="center"><img src="https://user-images.githubusercontent.com/14344419/184625289-3b613245-d90f-4ce6-af7f-d1b186a255c4.png" width="800"  /></p>

## Checking your design
A series of rules now need to be checked before your layout is ready for submission. Rules may be application-defined, like connectivity between components or making sure that two devices are not overlapping, or process defined, checking that two different elements are not too close to each other or making sure that an etching step has something to etch under it. 

### Functional verification
SiEPIC includes a basic functional verification, mostly checking that components are connected to each other. Any polygons that were not created using the PDK may fail these checks. At the moment the TII Ligentec PDK does not include any netlist extraction or testing. A typical verification test error looks like:

<p align="center"> <img src="https://user-images.githubusercontent.com/14344419/184627914-712f0b6c-c6c8-42aa-944e-9ac60bc2195a.png" width="600"  /></p>

### DRC verification
DRC rules from TII (basic component overlapping checks) and Ligentec can be tested using KLayout's native DRC Check engine. To run this just press the key 'D', or select SiEPIC > Verification > Ligentec (TII) DRC. The current DRC's are updated to Ligentec's May2022 DRC version, and need to be kept up top date to ensure design specifications match the fabrication limits. When you run the DRC a database visualizer will open with the list of DRC check made and the number of errors found in eacah category. By selecting any one category or element from this list you can visualize the area where the error occurs and get a description of the error:
<p align="center"> <img src="https://user-images.githubusercontent.com/14344419/186352926-bfb39350-08f3-41ec-b7ab-997ce7dd4636.png" width="600"  /></p>


### Layout submission verification
This runs a set of scripts from Ligentec that test basic layout considerations, like checking that the BB cells are correctly included and that the size and layers used are consistent with their definitions. A layout generated with the TII PDK will always show the SiEPIC layers are non-consistent with the standard specification, however, these get stripped upon exporting the layout form fabrication an you may waive this error (I can modify the script, but for now it's left exactly as is provided by Ligentec). To run this check go to SiEPIC x.x.x > Run Ligentec Pre-submission check.

## Exporting your design
Go to SiEPIC > Export for Ligentec fabrication
This will generate an OASIS file where all cells except black boxes have been flattened and elements in layers not part of the Ligentec PDK are removed. The new file should be stored in the same location as your layout file.

## Creating your own components
To allow the simulation of optical circuits from KLayout, SiEPIC tools needs *all* elements in a circuit to be proper SiEPIC components. Because SiEPIC is a layout centric design tool, creating new components from the layout is very easy and can all be done using basic elements avaiable in the KLayout base library.  You basically need to:
- Define the polygon that describes your device geometry.
- Define optical and metal pins connected to your system
- Create labels to specify your Compact Model (Library, Component, SPICE Parameters)

You can find complete documentation on  how to ccreate components in https://github.com/SiEPIC/SiEPIC-Tools/wiki/Component-and-PCell-Layout. If you create a compact model in Lumerical for your component, make sure that the cell that contains your device has the same name as the component in Interconnect, otherwise the netlist generation and export will miss it.

# Running a circuit simulation
### Define your inputs and outputs
If all your components have Compact Models associated in libraries in Lumerical-Interconnect, you can automatically generate a netlist and export your circuit to the simulator. To setup your simulation, first tell SiEPIC where in your layout the lasers and detectors are configured. For this, from the SiEPIC General library, drag and drop a Lumerical_INTERCONNECT_Laser Cell over the Grating_Coupler / Edge_Coupler that the circuit uses as an inputs and a Lumerical_INTERCONNECT_Detector Cell over the Grating_Coupler(s) / Edge_Coupler(s) that are used as outputs. **Note**: You can only simulate one laser at a time, this is equivalent in Interconnect to setting an Optical Networks Analyzer.

To change the setting of your simulation, modify the laser specification by doubli clicking in the cell, or selecting it a pressing 'Q'. In the PCell parameters, you can determine the start and end wavelengths, the number of steps, and the poalrization state (most models use orthogonal identifiers 0 and 1 for 'TE' and 'TM' respectively, if your model uses somehting different, you need to specify the mode accordingly).
<p align="center"> <img src="https://user-images.githubusercontent.com/14344419/186392286-198bab8f-8919-43e0-8372-01f7eb9bf469.png" width="900"  /></p>

### Run the simulation
Click on SiEPIC > Simulation, Circuits > Circuit Simulation: Lumerical Interconnect, or hit in the button  that says simulation (and has blue eye diagram on it). This will generate the SPICE netlist,  open interconnect, load the netlist in the simualtor and run the simulation. Once completed a window will autom atically pop-up shopwing the transmission results of the ONA. You may configure any new analysis directly in Lumerical, but any changes you make will be overwritten if you run the simulation again from KLayout. 

![image](https://user-images.githubusercontent.com/14344419/186395524-a46091a0-14b4-4cf0-b686-db4da12611c6.png)

*After running the simulation do not close Interconnect, the current release of the Lumerical API cannot detect that you closed it and this will cause KLayout to freeze if you try to run a new simulation.*
