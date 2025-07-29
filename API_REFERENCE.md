# QFoundry PDK API Reference

## Junction Components

### ManhattanFatLead

A parametric Manhattan Josephson junction with fat leads for improved connectivity and SQUID configurations.

#### Constructor
```python
ManhattanFatLead()
```

#### Key Parameters

| Parameter | Type | Default | Unit | Description |
|-----------|------|---------|------|-------------|
| `l_layer` | LayerInfo | (2, 0) | - | Junction layer specification |
| `junction_type` | List | 0 | - | 0=Single, 1=SQUID Pair, 2=SQUID Reflected |
| `angle` | Double | 0.0 | ° | Junction rotation angle (-15° to +15°) |
| `inner_angle` | Double | 90.0 | ° | Angle between junction pads |
| `junction_width_t` | Double | 0.3 | μm | Top junction width |
| `junction_width_b` | Double | 0.3 | μm | Bottom junction width |
| `finger_size` | Double | 5.0 | μm | Length of junction fingers |
| `finger_overshoot` | Double | 2.0 | μm | Finger extension beyond junction |
| `conn_width` | Double | 9.0 | μm | Connector lead width |
| `conn_height` | Double | 10.0 | μm | Connector lead height |
| `squid_spacing` | Double | 20.0 | μm | Spacing between SQUID junctions |
| `draw_cap` | Boolean | False | - | Include capacitive test pad |
| `cap_w` | Double | 200.0 | μm | Capacitor width |
| `cap_h` | Double | 200.0 | μm | Capacitor height |
| `cap_gap` | Double | 20.0 | μm | Capacitor gap |
| `draw_patch` | Boolean | False | - | Include patch layers |
| `patch_layer` | LayerInfo | (4, 0) | - | Patch layer specification |
| `patch_gap` | Double | 1.0 | μm | Patch opening gap |

#### Usage Example
```python
# Single Manhattan junction
junction = layout.create_cell("ManhattanFatLead", "Junction Library", {
    "junction_type": 0,
    "angle": 5.0,
    "junction_width_t": 0.2,
    "junction_width_b": 0.3,
    "draw_cap": True
})

# SQUID pair configuration  
squid = layout.create_cell("ManhattanFatLead", "Junction Library", {
    "junction_type": 1,
    "squid_spacing": 15.0,
    "angle": 0.0,
    "draw_patch": True
})
```

### Manhattan

Basic Manhattan Josephson junction with standard geometry.

#### Key Parameters

| Parameter | Type | Default | Unit | Description |
|-----------|------|---------|------|-------------|
| `l_layer` | LayerInfo | (2, 0) | - | Junction layer |
| `angle` | Double | 0.0 | ° | Junction angle (-60° to +60°) |
| `inner_angle` | Double | 90.0 | ° | Angle between pads |
| `junction_width_t` | Double | 0.3 | μm | Top junction width |
| `junction_width_b` | Double | 0.3 | μm | Bottom junction width |
| `finger_size` | Double | 10.0 | μm | Finger length |
| `conn_width` | Double | 5.0 | μm | Connector width |
| `draw_cap` | Boolean | True | - | Include test pad |

## Element Components

### BenasqueBridge

Catenary-shaped airbridge for low-loss waveguide crossings.

#### Key Parameters

| Parameter | Type | Default | Unit | Description |
|-----------|------|---------|------|-------------|
| `l1_layer` | LayerInfo | (146, 1) | - | Bottom layer |
| `l2_layer` | LayerInfo | (147, 1) | - | Top layer |
| `length` | Double | 60.0 | μm | Bridge span length |
| `waist_width` | Double | 10.0 | μm | Minimum bridge width |
| `land_width` | Double | 40.0 | μm | Landing pad width |
| `land_length` | Double | 16.0 | μm | Landing pad length |
| `gap` | Double | 1.0 | μm | Landing gap |
| `curve_a` | Double | 15.0 | - | Catenary curve parameter |

#### Usage Example
```python
bridge = layout.create_cell("BenasqueBridge", "Element Library", {
    "length": 80.0,
    "waist_width": 8.0,
    "land_width": 50.0
})
```

## Chip Components

### FrameQF10

10×10mm chip frame with launcher configuration.

#### Key Parameters

| Parameter | Type | Default | Unit | Description |
|-----------|------|---------|------|-------------|
| `a` | Double | 15.0 | μm | CPW center conductor width |
| `b` | Double | 7.5 | μm | CPW gap width |
| `r` | Double | 50.0 | μm | Turn radius |

### FrameQF5  

5×5mm chip frame for compact designs.

#### Key Parameters

| Parameter | Type | Default | Unit | Description |
|-----------|------|---------|------|-------------|
| `a` | Double | 15.0 | μm | CPW center conductor width |
| `b` | Double | 7.5 | μm | CPW gap width |
| `r` | Double | 150.0 | μm | Turn radius |

## Utility Functions

### Shape Manipulation

```python
from qfoundry.utils import _add_shapes, _substract_shapes

# Add shapes to a layer
_add_shapes(cell, shape_list, layer_index)

# Boolean subtraction
_substract_shapes(shapes_a, shapes_b, layer_index)
```

### Junction Utilities

```python
from qfoundry.junctions.utils import draw_junction, draw_pad, draw_patch_openning

# Generate junction geometry
junction_shapes = draw_junction(
    angle=0.0,                    # Junction angle in degrees
    inner_angle=90.0,             # Pad separation angle
    junction_width_b=0.3,         # Bottom width in μm
    junction_width_t=0.3,         # Top width in μm  
    finger_size=5.0,              # Finger length in μm
    mirror_offset=False,          # Mirror compensation
    offset_compensation=0.0,      # Manual offset in μm
    finger_overshoot=2.0,         # Overshoot length in μm
    finger_overlap=9.0,           # Overlap with leads in μm
    center=pya.DPoint(0, 0),      # Center position
    dbu=0.001                     # Database units
)

# Generate test pad
pad_shape = draw_pad(
    cap_w=200.0,                  # Width in μm
    cap_h=200.0,                  # Height in μm
    cap_gap=20.0,                 # Gap in μm
    dbu=0.001                     # Database units
)
```

### Testing Utilities

```python
from qfoundry.utils import test_pcell
from qfoundry.scripts import reload_library

# Reload library after changes
reload_library()

# Test a PCell
test_pcell(
    pcell_declaration_class,
    parameter_dict,
    transformation
)
```

## Layer Definitions

| Layer Name | GDS Layer | Type | Purpose |
|------------|-----------|------|---------|
| Base Metal | 1/0 | Negative | CPW, capacitors, ground planes |
| Junctions | 2/0 | Positive | Josephson junctions |
| EBeam Patch | 3/0 | Positive | High-res patches and contacts |
| Laser Patch | 4/0 | Positive | Standard-res patches |
| DevRec | 68/0 | Positive | Device recognition |
| CSL | 100/2 | Positive | Chip size layer |
| CHS | 100/0 | Positive | Chip handling size |

## Error Handling

### Common Issues

1. **Parameter Validation Errors**
   - Check parameter ranges in `coerce_parameters_impl()`
   - Ensure units are correctly specified

2. **Layer Assignment Errors**
   - Verify layer exists in technology file
   - Check positive/negative layer usage

3. **Geometry Generation Errors**
   - Validate coordinate calculations
   - Check for self-intersecting polygons

### Debugging Tips

```python
# Enable debug output
print(f"Parameter value: {self.parameter_name}")

# Check geometry validity
if polygon.area() == 0:
    print("Warning: Zero-area polygon generated")

# Verify layer assignment
layer_index = self.layout.layer(self.l_layer)
print(f"Using layer index: {layer_index}")
```

## Best Practices

1. **Parameter Naming**: Use descriptive names with units
2. **Default Values**: Choose fabrication-friendly defaults
3. **Documentation**: Include comprehensive docstrings
4. **Validation**: Implement proper parameter bounds checking
5. **Testing**: Use the provided test framework
6. **Version Control**: Commit frequently with clear messages

## Support and Contribution

- **Documentation**: See `DEVELOPER_GUIDE.md` for detailed development guidelines
- **Issues**: Report bugs and feature requests via GitHub issues
- **Contributing**: Follow the established coding patterns and submit pull requests
- **Contact**: TII QFoundry team for process-specific questions
