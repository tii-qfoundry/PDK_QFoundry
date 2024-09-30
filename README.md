# QFoundry 2D - PDK
TII QFoundry standard PDK for superconductive qubit fabrication. The KLayout PDK layout tools are built on top of KQcircuits circuit package.

## Design Guide
The qfoundry microfabrication is a single layer superconductive aluminum manufacturing process with medium and high resolution lithography steps. The high resolution lithography is used **only** for josephson junction micro-fabrication, but under specific conditions can be used for the manufacturing of transmon capacitors and resonators. The superconductive layer is a low kinetic inductance Aluminum (Al) in a float-zone intrinsic Silicon substrate with no cladding. Metallization is done through ebeam evaporation of high purity aluminum. 

<p align="center"><img width="200" alt="image" src="https://github.com/tii-qfoundry/PDK_QFoundry/assets/14344419/6645d804-900d-4106-accd-3f97fbc301ad"> </p>

The current fabrication process of the TII qfoundry, uses the following process derived model parameters.

Parameter | Value | Comment
--- | --- | --- | 
$R_n^\ast$ | -210 $\Omega$ | Junction total resistance correction (to fit qubit frequencies)
$\rho_n^\ast$ | 5.9e-10 $\Omega \cdot {cm}^2$ | Junction resisitivty leakage correction (to fit qubit frequencies)
$\gamma$ | 4.513e7 $F/{cm}^2$ | Junction Capacitance per unit Area
$T_c$ | $1.14 K$ | Superconductive critical temperature, from Literature
$\Delta_{sc}$ | $2.78E-23 C$ | Superconductive bandgap, from Literature
$\varepsilon_{r,Si}$ | $11.6883$ | Cold relative permittivity of Silicon, based on resonator measurements

<p align="center"><img width="500" alt="Qubit Frequency Ambegaokar-Baratoff relations" src="https://github.com/user-attachments/assets/68768c38-5a7b-45d5-9296-9132e47d8712"> </p>



### Qubit design
In general, the josephson junction energy can be estimated using the Ambegaokar–Baratoff relation given by

$$
\frac{E_J}{\hbar} = \frac{Ic}{2e}= \frac{1}{4e^2} \frac{\pi \Delta_{SC}(T)}{R_n+R^{\ast}} tanh{\frac{\Delta_{SC}(T)}{2k_BT}}
$$

Where $R^{\ast}= \rho^{\ast}/A_{JJ}+R_0^{\ast}$ is the fabrication resistance correction factor, related to leakage currents not contributing to the superconductive critical current. Using $E_C = \frac12 \frac{e^2}{C_{\sum}+C_{J}}$, where the fabricated $C_{J}$ is the junction capacitance approximated from $C_{J} = \gamma \cdot A_{JJ}$, with $\gamma$ the capacitance per unit area of the junction (ideally $\gamma = \frac{\varepsilon_0\varepsilon_{r,ox}}{d}$, where d is the oxide thickness and $\varepsilon_{r,ox}$ is the relative permittivity of the oxide layer). 


#### Transmons
The excitation frequency of transmon qubits can be approximated by

$$
  \frac{E_{q,01}}{h}= \sqrt{8E_J E_C}-E_C
$$

The qubit frequency, for a transmon with shunt capacitance of $74 fF$ (typical transmon used by the qfoundry) can be roughly estimated from

$$
  \omega_{01}/2\pi = 7.2012 - 0.1473 \times R_n [GHz]
$$

With $R_n$ the measured junction resistance in $k\Omega$. 

#### Junction Resistance
We can estimate the resulting jucntion resistance from a known tunneling conductance of the oxide layer, here used as a room temperature resisitivity in $\Omega \times cm^2$. It has been observed that said resistivity changes when patches are added to connect the junction metallization layer (L2/0) and the transmons capacitors (L1/0). Said change does not arise from contact resistance in the path but possibly from trapped ions in the oxide layer or oxide relaxation introduced during post-processing. As such it is necessary to use two different models of room temperature junction resistance estimation. Both following the form:

$$
  R_n = \rho\cdot A_{JJ} + R_0
$$

Patched junctions
<p align="center"><img width="400" alt="image" src="https://github.com/user-attachments/assets/6ac16944-4e01-4553-be56-d598301ad649"> </p>

Full EBL junctions
<p align="center"><img width="400" alt="image" src="https://github.com/user-attachments/assets/b6d2be6c-73de-46ed-98b0-fdd69b9ea4c3"> </p>

Values for $R_0$ and $\rho$ are derived from measurements over >70 functional test junctions carried on the 26/07/2024 for Patched jucntions and 12/08/2024 for full EBL junctions.

Parameter | Value | Comment
--- | --- | --- | 
$\rho_{patch}$ |  1.380e-05 $\Omega\cdot cm^2$ | Junction resisitivity of Manhattan junctions for Room Temperature measurements, see section below
$\rho_{ebl}$ |  5.214e-05 $\Omega\cdot cm^2$ | Junction resisitivity of Manhattan junctions for Room Temperature measurements, see section below
$R_{0,patch}$ | -26.7 $\Omega$ | Total resistance correction
$R_{0,ebl}$ | -2.958 $k\Omega$ | Total resistance correction

Furthermore, the junctions R.T. resistance can tuned by annealing the fabricated device. Such process is normally carried to tune the R.T. resistance to match the design specification. 

## Layout Specification

### Fabrication Specifications

General Process Specifications:
Parameter | Value | Comment
--- | --- | --- | 
Substrate Thickness | 650 $\mu m$ | 
Substrate Relative Permittivity | 11.65 | 
Substrate Relative Resistivity | 10 $M\Omega \cdot cm$ |


#### Layer 1/0 - Coplanar Waveguides (CPW) and Capacitors (Negative)
All superconductivce circuitry. 
> ``📝``
> Layout components are specified as negative cells i.e. you draw the cells where no metalization is expected in the final design.

Parameter | Value | Comment
--- | --- | --- | 
Minimum Feature Size | $3 \mu m$ |
Minimum Feature Spacing | $6 \mu m$ |
Minimum Feature Size (CPW core) | $6 \mu m$ |
Maximum Feature Size (CPW core) | $20 \mu m$ |
Metal Thickness | $200 nm$ | Measured
Superconductive Layer Tc | $1.2 K$ | From Literature
Superconductive Loss Tangent ($tan(\delta )$ ) | $3.3\times10^{-5}$ | Measured

#### Layer 2/0 - Junctions 
Junctions are manufactured using a 2 step evaporation process at 40 degrees inclination with a single step of oxidation between them. Generating a 3 nm thick oxide layer that forms the tunneling junction. The metal layers are finally capped with an oxide grown in a controlled environment to stabilize the junction parameters.
> ``📝``
> Layout Components are specified as positive cells i.e. you draw the cells where metalization is desired. 

Parameter | Value | Comment
--- | --- | --- | 
Minimum Feature Size (Junctions) | 200 $nm$ |
Maximum Feature Size (Junctions) | 300 $nm$ |
Metal Thickness | 200 $nm$ |

#### Layer 3/0 - Positive Lithography - EBeam   
Second metalization layer using high resolution lithography for the fabrication of metal patches or other metal features.
> ``📝``
> Layout Components are specified as positive cells i.e. you draw the cells where metalization is desired. You can definbe layout strctures in Layer 3/0 or 4/0 but not both.

Parameter | Value | Comment
--- | --- | --- | 
Minimum Feature Size | $3 um$ |
Minimum Feature Spacing | $6 um$ |
Alignement Accuracy | $3 \mu m$ | Standard alignement marks need to be placed in Layer 1/0
Metal Thickness | $200 nm$ | Measured


#### Layer 4/0 - Positive Lithography - Laser   
Second metalization layer using low resolution lithography for the fabrication of metal patches or other metal featrues.
> ``📝``
> Layout Components are specified as positive cells i.e. you draw the cells where metalization is desired. You can definbe layout strctures in Layer 3/0 or 4/0 but not both.

Parameter | Value | Comment
--- | --- | --- | 
Minimum Feature Size | $200 nm$ |
Minimum Feature Spacing | $500 nm$ |
Alignement Accuracy | $500 nm$ | Standard alignement marks need to be placed in Layer 1/0
Metal Thickness | $200 nm$ | Measured

### Standard Components

### Standard PCB design
The qfoundry can provide wirebonding of supercondcutive QPUs to PCBs in any of the following standard launcher configurations. 

PCB Type | Die Size | Max Number of Ports | Launcher Type | Comments
--- | --- | --- | --- | --- 
P001 | 5 x 5 mm | 12 (3 in each side) | 300 x 200 um |  
P002 | 10 x 10 mm | 12 (3 in each side) | 300 x 200 um |  Available in August 2024
P003* | 10 x 10 mm | 12 (3 in each side) | 300 x 200 um |  PCB not yet available for production

## KLayout PDK Installation

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

<p align="center"><img width="326" alt="image" src="https://github.com/tii-qfoundry/PDK_QFoundry/assets/14344419/32b387f9-40fb-43f5-80e9-e71746cca50d"> </p>
  
- Navigate in your GitHub repository to '%USERPROFILE%\Documents\Github\PDK_QFoundry\klayout_PDK\tech', here select the 'QFoundry.lyt' technology specification. You should immediatly see a new technology with multiple panels with its different specifications. Click OK to accept the new changes.
<p align="center"><img width="449" alt="image" src="https://github.com/tii-qfoundry/PDK_QFoundry/assets/14344419/5f98f33f-0918-4ebd-a565-8edf2b78646f"> </p>

- When prompted to run the macros in the new technology, make sure to accept. This will configure KQCircuits to include the custom cells of the PDK.
<p align="center"><img width="350" alt="image" src="https://github.com/tii-qfoundry/PDK_QFoundry/assets/14344419/bb6e27a2-c7fb-4a12-9f2b-d21c72d37239"> </p>

If you cannot see the custom cells of the QFoundry PDK (if you didnt accept running the macros for example), you may need to configure KQCircuits to recognize all the cells from the PDK. Go to the menu KQCircuits > Add User Package, and in the source directory, point to the folder '%USERPROFILE%\Github\PDK_QFoundry\klayout_PDK\tech\pymacros\qfoundry'.

<p align="center"> <img width="449" alt="image" src="https://github.com/tii-qfoundry/PDK_QFoundry/assets/14344419/41c81ad7-5c1d-4aa4-8cac-cbe46b4be78c">  </p>

Now you are redy to design!

## Design a basic layout

The fastest way to start a design is using the GUI of KLayout. First create a new layout by going to File > New Layout, in the window that appears select the correct technology (QFoundry) and make sure to set the database units as 0.001 um (the default for the TII Quantum Foundry is indeed 0.001 um, but a you can use any other specification according to you foundry's process).

<p align="center"><img width="305" alt="image" src="https://github.com/tii-qfoundry/PDK_QFoundry/assets/14344419/6958674b-6697-4122-a1b1-6ea58ce2388a"> </p>

If you forget to set the database units, you can always go to File > Layout Properties and set them in the window that pops out, this will scale all the components in your layout, so make sure you do this before starting your work. Some parametric elements will re-generate with the correct size after you reload KLayout but any flat polygons will need to be manually scaled after the change in units.

### The QFoundry Library

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
[Design Verification is not yet supported in the PDK]
> ~ DRC rules from TII QFoundry (basic component overlapping checks) can be tested using KLayout's native DRC Check engine. To run this just press the key 'D', or select Tools > Verification > DRC. The current DRC's are updated to the QFoundry's most up to date process. When you run the DRC a database visualizer will open with the list of DRC check made and the number of errors found in eacah category. By selecting any one category or element from this list you can visualize the area where the error occurs and get a description of the error:~

## Exporting your design
[Export for Fabrication is not yet supported in the PDK]
> Go to KQCircuits > QFoundry > Export for fabrication
> This will generate an OASIS file where all cells except black boxes have been flattened and elements in layers not part of the Fabrication PDK are removed. The new file should be stored in the same location as your layout file.

## Creating your own components
To allow the cnsistnecy of the Layout to System specification from KLayout, we need that  **all** elements in a circuit to be proper KQcirucits components. Because KQcirucits is a layout centric design tool, creating new components from the layout is very easy and can all be done using basic elements avaiable in the KLayout base library.

