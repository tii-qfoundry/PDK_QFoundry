# QFoundry PDK Quick Reference

## Installation Checklist

- [ ] KQCircuits installed via KLayout Package Manager
- [ ] Repository cloned to local machine
- [ ] Technology imported: Tools → Manage Technologies → Import → `qfoundry.lyt`
- [ ] Macros accepted during technology import
- [ ] QFoundry components visible in library browser

## Essential Components

### Junctions

| Component | Purpose | Key Parameters |
|-----------|---------|----------------|
| **Manhattan** | Basic JJ | `angle`, `junction_width_t/b`, `finger_size` |
| **ManhattanFatLead** | SQUID-capable JJ | `junction_type`, `squid_spacing`, `conn_width` |

### Elements

| Component | Purpose | Key Parameters |
|-----------|---------|----------------|
| **BenasqueBridge** | Waveguide crossing | `length`, `waist_width`, `land_width` |
| **QfoundryMarkerCross** | Alignment marker | Standard configuration |

### Chips

| Component | Die Size | I/O Ports | Purpose |
|-----------|----------|-----------|---------|
| **FrameQF5** | 5×5mm | 12 | Compact designs |
| **FrameQF10** | 10×10mm | 16 | Extended I/O |

## Layer Reference

| Layer | GDS | Type | Usage |
|-------|-----|------|-------|
| **Base Metal** | 1/0 | Negative | CPW, capacitors |
| **Junctions** | 2/0 | Positive | Josephson junctions |
| **EBeam Patch** | 3/0 | Positive | High-res contacts |
| **Laser Patch** | 4/0 | Positive | Standard contacts |
| **DevRec** | 68/0 | Positive | Component outline |

## Design Rules (Quick)

### L1/0 - Base Metal
- **Min feature**: 3 μm
- **Min spacing**: 6 μm
- **CPW core**: 6-20 μm

### L2/0 - Junctions  
- **Feature size**: 200-300 nm
- **Alignment**: ±500 nm

### Standard Waveguides
- **Width**: 15 μm center, 7.5 μm gap
- **Impedance**: 49.24 Ω
- **Turn radius**: ≥50 μm

## Common Workflows

### 1. Basic Junction Design
```
1. Place Manhattan junction
2. Set angle (±60°) and widths
3. Add connector leads
4. Include test capacitor
5. Verify minimum spacing
```

### 2. SQUID Configuration
```
1. Use ManhattanFatLead
2. Set junction_type = 1 (pair) or 2 (reflected)
3. Adjust squid_spacing
4. Enable patches if needed
5. Check lead compensation
```

### 3. Chip Assembly
```
1. Start with FrameQF5/10
2. Add launchers at chip edges
3. Route with 15μm CPW
4. Place components with DevRec
5. Include alignment markers
```

## Parameter Guidelines

### Angles
- **Junction angles**: -15° to +15° (ManhattanFatLead), -60° to +60° (Manhattan)
- **Avoid**: Sharp bends in CPW routing
- **Recommended**: Gradual curves with r≥50μm

### Junction Sizing
- **Transmon**: 0.2-0.4 μm width typical
- **Asymmetric**: Different top/bottom widths for tuning
- **Finger length**: 5-20 μm depending on design

### Capacitor Integration
- **Gap**: 15-25 μm typical
- **Size**: 100-300 μm per side
- **Patches**: Use for reliable contact

## Troubleshooting

### Component Not Visible
1. Check technology selection in new layout
2. Verify macro execution during import
3. Reload library: KQCircuits → Reload Libraries

### Parameter Errors
1. Check units (μm specified?)
2. Verify ranges (angle limits)
3. Review parameter interdependencies

### Geometry Issues
1. Enable all layers in layer panel
2. Check positive/negative layer usage
3. Verify minimum feature sizes
4. Review boolean operations

### DRC Violations
1. Check minimum spacing rules
2. Verify waveguide continuity
3. Ensure proper ground planes
4. Review component overlaps

## Junction Resistance Estimation

### Patched Junctions
```
R_n = 1.380e-05 [Ω·cm²] / Area [cm²] - 26.7 [Ω]
```

### Full EBL Junctions  
```
R_n = 5.214e-05 [Ω·cm²] / Area [cm²] - 2.958 [kΩ]
```

### Frequency Estimation (74fF shunt)
```
f_01 = 7.2012 - 0.1473 × R_n [GHz]
```

## File Management

### Layout Files
- **Database units**: 0.001 μm (1 nm)
- **Technology**: Always select "QFoundry"
- **Format**: .gds or .oas for fabrication

### Export Preparation
1. Flatten all cells except black boxes
2. Remove non-fabrication layers
3. Merge overlapping polygons
4. Run final DRC check

## Support Resources

- **API Reference**: See `API_REFERENCE.md`
- **Developer Guide**: See `DEVELOPER_GUIDE.md`  
- **Process Specs**: See main `README.md`
- **KQCircuits Docs**: [meetiqm.com/developers/kqcircuits](https://meetiqm.com/developers/kqcircuits/)

## Quick Commands

### KLayout Console
```python
# Reload PDK library
from qfoundry.scripts import reload_library
reload_library()

# Test component
from qfoundry.utils import test_pcell
test_pcell(ComponentClass, params, transform)

# Get layer index
layer_idx = layout.layer(pya.LayerInfo(2, 0))
```

### Common Transformations
```python
# Rotation
trans = pya.Trans(pya.Trans.R90, 0, 0)  # 90° rotation

# Translation  
trans = pya.Trans(pya.Trans.R0, 100000, 50000)  # 100,50 μm

# Mirror + translate
trans = pya.Trans(pya.Trans.M45, 0, 0)  # Mirror about 45°
```

## Keyboard Shortcuts (KLayout)

| Key | Function |
|-----|----------|
| **F2** | Fit all |
| **F3** | Zoom to selection |
| **Ctrl+A** | Select all |
| **Ctrl+Z** | Undo |
| **Ctrl+Y** | Redo |
| **I** | Instance mode |
| **P** | Path mode |
| **R** | Rectangle mode |
| **L** | Layer panel |
