# QFoundry PDK Developer Guide

## Overview

The QFoundry PDK (Process Design Kit) is a comprehensive library for designing superconducting quantum devices using KLayout. Built on top of KQCircuits, it provides parametric cells (PCells) and layout tools specifically tailored for the TII QFoundry fabrication process.

The PDK follows a hierarchical component structure based on KQCircuits design patterns. All components are implemented as parametric cells that generate layout geometry programmatically.

## Architecture

### Directory Structure

```
qfoundry/
├── tech/                           # Technology files and layer definitions
│   ├── pymacros/qfoundry/         # Python implementation
│   │   ├── chips/                 # Chip-level components
│   │   ├── elements/              # Basic elements (bridges, markers)
│   │   ├── junctions/             # Junction libraries
│   │   ├── qubits/                # Qubit implementations
│   │   ├── scripts/               # Utility scripts
│   │   └── __development__/       # Development and testing
│   ├── drc/                       # Design Rule Check files
│   ├── gds/                       # Reference GDS files
│   └── lvs/                       # Layout vs Schematic
└── docs/                          # Documentation
```

### Component Hierarchy

```
└── pya.PCellDeclarationHelper
    ├── Element (Base component class)
    │   ├── Junction (Josephson junction base)
    │   │   ├── Manhattan (Basic Manhattan junction)
    │   │   └── ManhattanFatLead (Enhanced with SQUID support)
    │   ├── BenasqueBridge (Airbridge element)
    │   └── QfoundryMarkerCross (Alignment markers)
    ├── Chip (Chip-level components)
    │   ├── FrameQF5 (5×5mm chip frame)
    │   └── FrameQF10 (10×10mm chip frame)
    └── Qubit (Complete qubit implementations)
        └── [Future implementations]
```

### Development Components

Development components in `__development__/` provide:
- Standalone geometry libraries using QFoundry layer specifications
- Compatibility testing with KQCircuits
- Prototype implementations for new features

## Component Categories

### 1. Junctions (`qfoundry/junctions/`)

Josephson junction implementations with various geometries:

- **Manhattan**: Basic Manhattan junction with configurable angles
- **ManhattanFatLead**: Enhanced version with wider connector leads for SQUID configurations

#### Key Features:
- Single junction and SQUID (pair/reflected) configurations
- Parametric finger geometries and junction widths
- Automatic lead compensation for complex SQUID layouts
- Optional capacitive test pads and patch layers

### 2. Elements (`qfoundry/elements/`)

Basic layout elements and structures:

- **BenasqueBridge**: Catenary-shaped airbridge with landing pads
- **Markers**: Alignment markers for lithography

### 3. Chips (`qfoundry/chips/`)

Chip-level frame and packaging components:

- **FrameQF5**: 5×5mm chip frame with launcher patterns
- **FrameQF10**: 10×10mm chip frame with expanded I/O

### 4. Qubits (`qfoundry/qubits/`)

Complete qubit implementations (currently in development)

## Development Guidelines

### Creating New PCells

1. **File Naming**: Use CamelCase matching the class name
2. **Class Structure**: Follow the standard PCell pattern
3. **Documentation**: Include comprehensive docstrings
4. **Parameters**: Use descriptive names and appropriate units
5. **Layer Management**: Use the predefined layer stack

### PCell Structure

Each PCell must implement the standard KLayout PCell interface:

```python
class ComponentName(pya.PCellDeclarationHelper):
    """
    Brief description of the component.
    
    Detailed description including:
    - Purpose and applications
    - Key features and capabilities
    - Parameter relationships
    """
    
    def __init__(self):
        """Initialize with parameter definitions"""
        super().__init__()
        self.set_parameters()
    
    def display_text_impl(self):
        """Return display name for layout browser"""
        return "ComponentName: Description"
    
    def coerce_parameters_impl(self):
        """Validate and constrain parameters"""
        # Parameter validation logic
        pass
    
    def produce_impl(self):
        """Generate component geometry"""
        # Geometry generation logic
        pass
    
    def set_parameters(self):
        """Define all component parameters"""
        # Parameter definitions
        pass
```

#### Example Template:

```python
import pya
from qfoundry.utils import _add_shapes

class NewComponent(pya.PCellDeclarationHelper):
    """
    Brief description of the component.
    
    Detailed description including:
    - Purpose and applications
    - Key features and capabilities
    - Parameter relationships
    """
    
    def __init__(self):
        """Initialize the PCell with default parameters."""
        super().__init__()
        self.set_parameters()
    
    def display_text_impl(self):
        """Return descriptive text for the layout browser."""
        return "NewComponent: Brief description"
    
    def coerce_parameters_impl(self):
        """Validate and constrain parameter values."""
        # Add parameter validation logic
        pass
    
    def produce_impl(self):
        """Generate the component geometry."""
        # Implementation here
        pass
    
    def set_parameters(self):
        """Define all PCell parameters."""
        self.param("param_name", self.TypeDouble, "Description", 
                  default=1.0, unit="μm")
        # Add more parameters
```

### Parameter Management

Parameters should follow these conventions:

1. **Dimensional Parameters**: Always include units
   ```python
   self.param("width", self.TypeDouble, "Component width", 
             default=10.0, unit="μm")
   ```

2. **Layer Parameters**: Use LayerInfo objects
   ```python
   self.param("layer", self.TypeLayer, "Target layer", 
             default=pya.LayerInfo(2, 0))
   ```

3. **Choice Parameters**: Provide clear options
   ```python
   choices = [("Option A", 0), ("Option B", 1)]
   self.param("selection", self.TypeList, "Choose option", 
             choices=choices, default=0)
   ```

#### Parameter Best Practices

1. **Units**: Always specify units for dimensional parameters
2. **Defaults**: Choose sensible defaults for typical use cases
3. **Hidden Parameters**: Use `hidden=True` for advanced/internal parameters
4. **Parameter Groups**: Organize related parameters together
5. **Validation**: Implement bounds checking in `coerce_parameters_impl()`

### Geometry Generation

#### Coordinate System
- Work in micrometers for calculations
- Convert to database units before adding to layout
- Use `self.layout.dbu` for conversion

```python
def produce_impl(self):
    dbu = self.layout.dbu
    layer = self.layout.layer(self.target_layer)
    
    # Work in micrometers
    width_um = self.width
    height_um = self.height
    
    # Create polygon
    polygon = pya.DPolygon([
        pya.DPoint(0, 0),
        pya.DPoint(width_um, 0),
        pya.DPoint(width_um, height_um),
        pya.DPoint(0, height_um)
    ])
    
    # Convert and add to layout
    self.cell.shapes(layer).insert(polygon.to_itype(dbu))
```

#### Layer Management

QFoundry uses specific layer conventions:
- **L1/0 (Negative)**: CPW and capacitor structures
- **L2/0 (Positive)**: Josephson junctions
- **L3/0 (Positive)**: EBeam patches
- **L4/0 (Positive)**: Laser patches

## Layer Specifications

The QFoundry process uses the following standard layers:

| Layer | GDS Layer | Purpose | Type |
|-------|-----------|---------|------|
| L1/0 | 1/0 | Base metal (CPW, capacitors) | Negative |
| L2/0 | 2/0 | Junctions | Positive |
| L3/0 | 3/0 | EBeam lithography patches | Positive |
| L4/0 | 4/0 | Laser lithography patches | Positive |
| DevRec | 68/0 | Device recognition | Positive |

### Layer Usage Guidelines

- **Negative layers**: Draw areas where metal should be removed
- **Positive layers**: Draw areas where metal should be added
- **DevRec**: Always include for component recognition
- **Patches**: Use L3/0 for high-resolution features, L4/0 for low-resolution

## Fabrication Considerations

### Design Rules

- **Minimum feature size (L1/0)**: 3 μm
- **Minimum spacing (L1/0)**: 6 μm  
- **Junction dimensions**: 200-300 nm
- **Alignment accuracy**: 3 μm (EBeam), 500 nm (Laser)

### Junction Design

1. **Resistance Calculation**: Use provided models for room-temperature resistance
2. **SQUID Geometries**: Consider flux bias requirements
3. **Lead Compensation**: Account for asymmetric SQUID layouts
4. **Patch Integration**: Design for reliable electrical contact

### Capacitor Integration

- **Gap Control**: Maintain consistent capacitor gaps
- **Patch Openings**: Design appropriate openings for patches
- **Negative Layer Handling**: Proper boolean operations for negative layers

## Utilities and Helper Functions

### Shape Manipulation

Use provided utilities for common operations:

```python
from qfoundry.utils import _add_shapes, _substract_shapes

# Add multiple shapes to a layer
_add_shapes(self.cell, shape_list, layer_index)

# Boolean operations
_substract_shapes(shapes_a, shapes_b, layer_index)
```

### Junction Utilities

```python
from qfoundry.junctions.utils import draw_junction, draw_pad, draw_patch_openning

# Generate junction fingers
fingers = draw_junction(angle, inner_angle, width_b, width_t, 
                       finger_size, mirror_offset, offset_comp, 
                       overshoot, overlap, center, dbu)
```

## Testing Framework

### Component Testing

Each component should include a test section:

```python
if __name__ == "__main__":
    from qfoundry.scripts import reload_library
    from qfoundry.utils import test_pcell
    reload_library()
    
    pcell_decl = ComponentName
    pcell_params = {
        "width": 20.0,
        "height": 15.0,
        "angle": 45.0
    }
    pcell_trans = pya.Trans(pya.Trans.R0, 0.0, 0.0)
    
    test_pcell(pcell_decl, pcell_params, pcell_trans)
```

### Registration Testing

Use the registration test framework to verify component integration:

```python
from qfoundry.__development__.cell_registration_test import cell_registration_test
cell_registration_test()
```

## Advanced Features

### SQUID Geometries

For complex SQUID implementations, consider:
- Lead compensation for asymmetric layouts
- Flux bias line integration
- Loop area optimization

### Patch Integration

When designing components with patches:
1. Create patch openings in base metal layer
2. Generate patch geometries on appropriate layer
3. Handle layer polarity (positive/negative) correctly

### Negative Layer Handling

For negative layers (like L1/0):
```python
# Create positive region (where metal exists)
metal_region = pya.Region(positive_shapes)

# Create negative region (where metal is removed)
negative_region = pya.Region(substrate_box) - metal_region

# Add to negative layer
self.cell.shapes(negative_layer).insert(negative_region)
```

## File Organization

### Directory Structure
```
component_category/
├── __init__.py              # Component exports
├── ComponentName.py         # Main implementation
└── __pycache__/            # Compiled Python (auto-generated)
```

### Import Conventions
```python
# In __init__.py
from .ComponentName import ComponentName

# Usage in other files  
from qfoundry.category import ComponentName
```

## Documentation Standards

### Docstring Format

Use comprehensive docstrings following this pattern:

```python
def method_name(self, param1, param2):
    """
    Brief description of the method purpose.
    
    Detailed description including:
    - Method behavior and algorithms
    - Parameter relationships
    - Return value description
    - Usage examples or notes
    
    Args:
        param1 (type): Description of parameter 1
        param2 (type): Description of parameter 2
        
    Returns:
        type: Description of return value
        
    Raises:
        ExceptionType: Description of when this exception is raised
    """
```

### Code Comments

- Explain complex geometric calculations
- Document parameter validation logic  
- Clarify layer handling and boolean operations
- Note fabrication-specific considerations

## Contribution Workflow

1. **Development Setup**
   - Fork the repository
   - Create feature branch
   - Set up development environment

2. **Implementation**
   - Follow coding standards
   - Add comprehensive tests
   - Update documentation

3. **Testing**
   - Run registration tests
   - Verify geometry generation
   - Check parameter validation

4. **Submission**
   - Create pull request
   - Include test results
   - Document changes and new features

## Common Patterns

### Junction Components
- Always include DevRec layer for recognition
- Support both positive and negative layer workflows
- Implement proper parameter validation
- Consider fabrication tolerances

### Element Components
- Design for reusability across different chips
- Include configurable layer assignments
- Support standard waveguide interfaces
- Optimize for low parasitic effects

### Chip Components
- Include standard launcher configurations
- Support multiple die sizes
- Implement proper ground plane management
- Include alignment marker placement

## Common Issues and Solutions

### 1. Indentation Errors
- Ensure consistent indentation (4 spaces)
- Check for mixed tabs and spaces
- Validate Python syntax before testing

### 2. Layer Management
- Always use `self.layout.layer()` to get layer indices
- Check for correct positive/negative layer usage
- Verify layer assignments match process specification

### 3. Coordinate Systems
- Work in micrometers for clarity
- Convert to database units using `dbu` before adding to layout
- Be consistent with coordinate system throughout the design

### 4. Parameter Validation
- Implement proper bounds checking
- Provide meaningful error messages
- Consider parameter interdependencies

### Debugging Tips

#### Geometry Issues
1. Check coordinate calculations step by step
2. Verify polygon orientation and closure
3. Use intermediate visualization for complex shapes
4. Validate boolean operations with test cases

#### Parameter Issues
1. Implement bounds checking in `coerce_parameters_impl()`
2. Test edge cases and limit values
3. Provide meaningful error messages
4. Document parameter interdependencies

#### Layer Issues
1. Verify layer exists in technology file
2. Check positive/negative layer usage
3. Test layer assignments with simple geometries
4. Validate layer stack in final layouts

## Contributing

1. **Fork and Branch**: Create feature branches for new components
2. **Documentation**: Update this guide for new patterns or utilities
3. **Testing**: Ensure all new components pass registration tests
4. **Code Review**: Follow established patterns and conventions
5. **Version Control**: Commit frequently with descriptive messages

## References

- [KQCircuits Documentation](https://meetiqm.com/developers/kqcircuits/)
- [KLayout PCell Programming Guide](https://www.klayout.de/doc/programming/index.html)
- QFoundry Process Specification (internal)
- TII QFoundry Fabrication Guidelines (internal)

For additional technical details, see the API reference and quick reference guides.
