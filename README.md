# QFoundry 2D - PDK

TII QFoundry standard PDK for superconducting qubit fabrication. The KLayout PDK layout tools are built on top of the KQCircuits circuit package, providing a comprehensive design environment for quantum device development.

**Latest Version**: v2.0 | **Technology Node**: QFoundry Process v1.2 | **KQCircuits Compatibility**: v4.7+

## Quick Start

1. **Install KQCircuits** via KLayout Package Manager
2. **Clone this repository** to your local machine
3. **Import technology** in KLayout: Tools → Manage Technologies → Import → Select `qfoundry.lyt`
4. **Start designing** with parametric quantum components

## Contents

- [Quick Start](#quick-start)
- [Design Guide](#design-guide): process, parameters, [qubit model](#qubit-design), [junction resistance](#junction-resistance), [airbridges](#airbridges)
- [Layout Specification](#layout-specification): layers, [components](#standard-components), [waveguides](#waveguide-standards), [PCB launchers](#standard-pcb-design)
- [KLayout PDK Installation](#klayout-pdk-installation)
- [Design a basic layout](#design-a-basic-layout)
- [Checking your design](#checking-your-design) and [Exporting](#exporting-your-design)
- [Creating your own components](#creating-your-own-components)

## Design Guide

The QFoundry microfabrication process is a single-layer superconducting aluminum manufacturing process with medium and high-resolution lithography steps. The high-resolution lithography is used **exclusively** for Josephson junction micro-fabrication, while standard resolution is suitable for resonators, transmission lines, and capacitive elements.

### Process Overview

The superconducting layer consists of low kinetic inductance Aluminum (Al) deposited on float-zone intrinsic Silicon substrate. Metallization is achieved through electron-beam evaporation of high-purity aluminum, providing excellent superconducting properties and low loss characteristics.

<p align="center"><img width="200" alt="QFoundry Process Flow" src="https://github.com/tii-qfoundry/PDK_QFoundry/assets/14344419/6645d804-900d-4106-accd-3f97fbc301ad"> </p>

### Process Parameters

Current fabrication process parameters derived from device characterization and modeling:

These feed the [qubit frequency model](#transmons) $f_{01}(R_N, T)$.

Parameter | Value | Comment
--- | --- | --- | 
$R_n^\ast$ | -210 $\Omega$ | Junction total resistance correction (to fit qubit frequencies)
$\rho_n^\ast$ | 5.9e-10 $\Omega \cdot {cm}^2$ | Junction resisitivty leakage correction (to fit qubit frequencies)
$\gamma$ | 4.513e7 $F/{cm}^2$ | Junction Capacitance per unit Area
$T_c$ | $1.14 K$ | Superconductive critical temperature, from Literature
$\Delta_{sc}$ | $2.78E-23 C$ | Superconductive bandgap, from Literature
$\varepsilon_{r,Si}$ | $11.6883$ | Cold relative permittivity of Silicon, based on resonator measurements

<p align="center"><img width="500" alt="Qubit Frequency Ambegaokar-Baratoff relations" src="https://github.com/user-attachments/assets/68768c38-5a7b-45d5-9296-9132e47d8712"> </p>

Standard coplanar waveguides used by the foundry are 15 $\mu m$ wide with 7.5 $\mu m$ spacing to the ground plane. This creates a waveguide with characteristic impedance of $Z_0 = 49.24 \Omega$ and effective permittivity of $\epsilon_{eff}=6.345$.

### Qubit design

#### Josephson junction model
The junction critical current follows the Ambegaokar–Baratoff (AB) relation. The QFoundry model extends it with two fitted corrections: a series/leakage resistance offset $R^\ast$ and a dimensionless gap-scaling factor $k_\Delta$ that absorbs the deviation of the measured $I_c R_N$ product from the ideal BCS value.

For reference, the ideal AB relation is

$$
I_c R = \frac{\pi \Delta(T)}{2 e_0}\tanh\left(\frac{\Delta(T)}{2 k_B T}\right), \qquad \frac{E_J}{\hbar} = \frac{I_c}{2e_0}
$$

The QFoundry model parametrizes the measured room-temperature junction resistance $R_N$ as follows:

- $R^\ast = \rho^\ast / A_{JJ} + R_0^\ast$ is the fabrication resistance correction, accounting for leakage currents that do not contribute to the superconducting critical current ($A_{JJ}$ is the junction area).
- $\Delta(T)$ is the superconducting gap at temperature $T$, and $\Delta_{\text{eff}}$ the effective gap fitted to the measured devices.
- $k_\Delta = \dfrac{2 e_0 \, I_c (R_N + R^\ast)}{\pi \Delta_{\text{eff}}}$ is the ratio between the measured $I_c (R_N+R^\ast)$ product and the ideal zero-temperature AB value ($k_\Delta = 1$ recovers the ideal AB relation).
- $E_C = \dfrac{e_0^2}{2\left(C_\Sigma + C_J\right)}$ is the charging energy, where $C_\Sigma$ is the shunt capacitance and $C_J = \gamma \cdot A_{JJ}$ is the junction capacitance. $\gamma$ is the capacitance per unit area of the junction (ideally $\gamma = \varepsilon_0\varepsilon_{r,ox}/d$, with $d$ the oxide thickness and $\varepsilon_{r,ox}$ the relative permittivity of the oxide).

#### Transmons
Combining the AB relation with the transmon approximation $E_{01} \approx \sqrt{8 E_J E_C} - E_C$, the qubit frequency as a function of the room-temperature junction resistance and the operating temperature is

$$
f_{01}(R_N, T) = \sqrt{\frac{A(T)\, E_C}{R_N + R^\ast}} - E_C
$$

with

$$
\begin{cases}
A(T) = k_\Delta \cdot \dfrac{\Delta(T)}{e_0^2} \tanh\left(\dfrac{\Delta(T)}{2 k_B T}\right) \\[10pt]
k_\Delta = \dfrac{2 e_0 \, I_c (R_N + R^\ast)}{\pi \Delta_{\text{eff}}}
\end{cases}
$$

##### $I_c R$ product
Inverting the definition of $k_\Delta$ gives the critical current–resistance product, which is the figure usually reported for a junction:

$$
I_c \left(R_N + R^\ast\right) = k_\Delta \cdot \frac{\pi \Delta_{\text{eff}}}{2 e_0}
$$

With $\Delta_{\text{eff}}$ in joules and $e_0$ in coulombs, the result is in volts. The ideal AB value ($k_\Delta = 1$) with $\Delta_{sc} = 2.78\times10^{-23}\,J$ from the [process parameters](#process-parameters) is $\pi\Delta_{sc}/2e_0 \approx 273\,\mu V$, so a fitted $k_\Delta$ scales this directly: e.g. $k_\Delta = 0.8$ corresponds to $I_c R \approx 218\,\mu V$. Conversely, a measured $I_c R$ gives $k_\Delta = 2 e_0\, I_c R / (\pi \Delta_{\text{eff}})$. The critical current of a given junction follows from $I_c = I_c R / (R_N + R^\ast)$.

Here $E_C$ is expressed in frequency units, so $f_{01}$ is obtained directly in Hz (the Planck constant is absorbed in $A(T)$). $R_N$ is the measured junction resistance, $R^\ast$ is the fitted correction from the [process parameters](#process-parameters) table, and $\Delta(T)$ follows the BCS temperature dependence with $T_c$ from the same table. $k_\Delta$ and $R^\ast$ are fitted jointly against measured qubit frequencies; refit them when the process changes.

To use the model for design:

1. Choose the shunt capacitance $C_\Sigma$ (and thus $E_C$) from the qubit layout.
2. Pick the target $f_{01}$ and invert the equation above for $R_N + R^\ast$.
3. Convert the required $R_N$ into a junction area with the [Junction Resistance](#junction-resistance) models, using the patched or full-EBL parameters as appropriate.

> ``📝``
> The earlier linear approximation $\omega_{01}/2\pi = 7.2012 - 0.1473\, R_n$ [GHz] ($R_n$ in $k\Omega$, $C_\Sigma = 74\,fF$) is **superseded** by the model above. It is only valid close to that specific shunt capacitance and resistance range, and should not be used for new designs.

#### Junction Resistance
We can estimate the resulting jucntion resistance from a known tunneling conductance of the oxide layer, here used as a room temperature resisitivity in $\Omega \times cm^2$. It has been observed that said resistivity changes when patches are added to connect the junction metallization layer (L2/0) and the transmons capacitors (L1/0). Said change does not arise from contact resistance in the path but possibly from trapped ions in the oxide layer or oxide relaxation introduced during post-processing. As such it is necessary to use two different models of room temperature junction resistance estimation. Both following the form:

$$
  R_n = \rho/ A_{JJ} + R_0
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

#### Airbridges
Aluminum airbridges can be manufactured using a two step litography process, in which the base resist layer is heated to reflow it and generate a profile that serves as support structure during the metal deposition. Airbridges are a common way to remove parastic modes in waveguides and help make sure the ground plane remains equi-potential, and they can be used to build waveguide crossings. However, airbridges are know to cause losses related to impedance missmatch, additional scattering and will add a parasitic capacitance to the waveguide, that may have a strong effect on the system.

The following parameters can be used to model the effect of the QFoundry's standard airbridges to your circuit
Parameter | Value | Comment
--- | --- | --- | 
$C_{b}$ |  0.434 $fF$ | Bridge capacitance, from measured SC resonators
$\delta_{b}$ |  0.0  | Additional loss tangent of the waveguide

<p align="center"><img width="400" alt="airbridge" src="https://github.com/user-attachments/assets/c6e05ecf-8391-4bb0-8d88-428b8849526f"> </p>

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

The QFoundry PDK provides a comprehensive library of parametric components:

#### Junctions
- **Manhattan**: Basic Manhattan Josephson junction with configurable geometry
- **ManhattanFatLead**: Enhanced junction with wider leads for SQUID configurations
  - Single junction, SQUID pair, and SQUID reflected configurations
  - Automatic lead compensation for complex geometries
  - Integrated capacitive test structures

#### Elements  
- **BenasqueBridge**: Catenary-shaped airbridge for waveguide crossings
- **QfoundryMarkerCross**: Precision alignment markers for lithography

#### Chips
- **FrameQF5**: 5×5mm chip frame with standard launcher configuration
- **FrameQF10**: 10×10mm chip frame with expanded I/O capabilities

All components are fully parametric and include design rule checking for fabrication compatibility.

### Waveguide Standards

Waveguide geometry (trace, gap, ground clearance) is generated by
[kcq](https://github.com/tii-qfoundry/kcQED), installed as a second KLayout Salt package (no pip
dependency needed). Every dimension lives in `qfoundry/tech/waveguides.xml`, not in Python:

CPW | Trace width | Gap | Ground clearance | Bend radius (min/default) | Routing
--- | --- | --- | --- | --- | ---
`feedline` | 15.5 μm | 7.0 μm | 20 μm | 50 / 100 μm | octilinear
`resonator` | 10.0 μm | 6.0 μm | 20 μm | 50 / 80 μm | octilinear
`flux_line` | 15.5 μm | 7.0 μm | 10 μm | 15 / 25 μm | manhattan

Routing between two ports:

```python
import pya
from kcq.geometry import router
from kcq.pcells.Waveguide import Waveguide

# port_a, port_b: kcq.geometry.pins.PinInfo (see "Ports" below)
waypoints = router.route_octilinear(port_a.position, port_a.angle_deg,
                                     port_b.position, port_b.angle_deg,
                                     bend_radius=100.0)
wg_cell = layout.create_cell("Waveguide", "qfoundry", {
    "path": pya.DPath(waypoints, 1.0),
    "cpw_name": "feedline",       # or "resonator" / "flux_line"
    "tech_name": "qfoundry",      # size from this PDK's waveguides.xml
})
top_cell.insert(pya.CellInstArray(wg_cell.cell_index(), pya.Trans()))
```

`Pin` (kcq's `kcq.pcells.Pin`) is also in the QFoundry library, for a standalone draggable port
marker placed by hand.

#### Ports

`Port.py` and every port `Transmon`/`TransmonStar` place are kcq pins
(`kcq.geometry.pins.add_pin`), each on its own physical layer's reserved `.pin` datatype (`4`,
per [kcq's layer/datatype convention](https://github.com/tii-qfoundry/kcQED/blob/main/doc/readme.html) —
`layer=1/1` gets its pin at `1/4`, `layer=2/0` at `2/4`, and so on). Read them with
`pins.get_pins(cell, layout)`; check two can connect directly with
`pins.check_alignment(port_a, port_b)`.

### Standard PCB design
The qfoundry can provide wirebonding of supercondcutive QPUs to PCBs in any of the following standard launcher configurations. 

PCB Type | Die Size | Max Number of Ports | Launcher Type | Comments
--- | --- | --- | --- | --- 
P001 | 5 x 5 mm | 12 (3 in each side) | 300 x 200 um |  Available
P002 | 10 x 10 mm | 12 (3 in each side) | 300 x 200 um |  Available
P003* | 10 x 10 mm | 16 (4 in each side) | 300 x 200 um |  Available

## KLayout PDK Installation

### KQcircuits
This PDK works with the KQcircuits package, develloped by IQM at Aalto University. To use 
Check the documentation in https://meetiqm.com/developers/kqcircuits/. KQcircuits is distributed using KLayout's Package Manager.
- Open KLayout, then menu item Tools | Manage Packages
- Install the 'KQcircuits' package
- Restart KLayout
You should see a new menu item, "KQcircuits", and a new quick command button named 'Edit Node'. Check back periodically in the Package Manager for updates.

### kcq
Waveguide synthesis (see [Waveguide Standards](#waveguide-standards)) is provided by
[kcq](https://github.com/tii-qfoundry/kcQED), installed like any other Salt package: clone it,
then Tools | Manage Packages | Install New Package (or add it as a User Package), and restart
KLayout. No pip install needed -- `import kcq` resolves once both packages are installed.

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

Now you are ready to design!

## Documentation

- **[Quick Reference](QUICK_REFERENCE.md)** - Essential commands and component guide
- **[API Reference](API_REFERENCE.md)** - Complete component parameter documentation  
- **[Developer Guide](developper.md)** - Creating custom components and contributing
- **[Process Specifications](#design-guide)** - Fabrication parameters and design rules

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
DRC rules from TII QFoundry (basic component overlapping checks) can be tested using KLayout's native DRC Check engine. To run this just press the 'Shift'+'D', or select Tools > Verification > DRC. The current DRC's are updated to the QFoundry's most up to date process. When you run the DRC a database visualizer will open with the list of DRC check made and the number of errors found in eacah category. By selecting any one category or element from this list you can visualize the area where the error occurs and get a description of the error.

## Exporting your design
Go to KQCircuits > Export for fabrication
This will generate an new GDS file where all cells except black boxes have been flattened and elements in layers not part of the Fabrication PDK are removed. The layer mapping for the fabrication conversion can be only modified in the script code at the moment. The generate layout has a cell depth of 1, preserving all first depth cells in the top cell of the original layout.

## Creating your own components
To allow the consistency of the Layout to System specification from KLayout, we need that  **all** elements in a circuit to be proper KQcirucits components. Because KQcirucits is a layout centric design tool, creating new components from the layout is very easy and can all be done using basic elements avaiable in the KLayout base library. In addition, every component need to be inside a polygon in the DevRec layer (68/0) that is used to test component overlaps in pre-production. Make sure that all overlapping polygons in the same layer are merged to avoid double exposure during fabrication, resulting in low quality lithography.

