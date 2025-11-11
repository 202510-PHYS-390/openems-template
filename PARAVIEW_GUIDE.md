# ParaView Visualization Guide

This guide explains how to visualize OpenEMS electromagnetic field simulations using ParaView on your local computer.

## Why ParaView?

ParaView is a powerful, free 3D visualization tool that lets you:
- View electromagnetic field distributions
- Animate field propagation over time
- Create publication-quality images
- Export videos of simulations

## Setup

### 1. Install ParaView (One-Time)

Download and install ParaView on your laptop:
- **Website:** https://www.paraview.org/download/
- **Recommended Version:** 5.11+ (latest stable)
- **Available for:** Windows, Mac, Linux

### 2. Run OpenEMS Simulation with VTK Export

In the container, run a simulation that exports VTK files:

**Recommended for beginners - Simple plane wave (no port errors):**
```bash
cd /workspace/examples
python3 plane_wave_simple.py
```

This creates `.vtr` files in `plane_wave_sim/`

**Alternative - Microstrip with port (more complex):**
```bash
cd /workspace/examples
python3 microstrip_with_vtk.py
```

This creates `.vtr` files in `microstrip_vtk_sim/`

### 3. Download VTK Files to Your Laptop

**If using mounted volume (recommended):**
```bash
# Files are already on your host machine
ls microstrip_vtk_sim/*.vtr
```

**If files are only in container:**
```bash
# From your laptop terminal
docker cp openems-container:/workspace/examples/microstrip_vtk_sim ./
```

## Using ParaView

### Opening Files

1. **Launch ParaView**
2. **File → Open**
3. **Select all `.vtr` files** (Shift+Click or Ctrl+A)
   - Example: `Et_0000000.vtr` through `Et_0001000.vtr`
4. **Click OK**
5. **In Properties panel, click "Apply"**

### Basic Visualization

**View E-field magnitude:**
1. In toolbar, select "E" from dropdown
2. Click "Apply"
3. Adjust color scale using legend

**Animate over time:**
1. Click ▶ button in toolbar
2. Fields animate showing propagation
3. Adjust speed with time controls

**View H-field:**
1. Open `Ht_*.vtr` files same way
2. Select "H" from dropdown

### Advanced Visualization

**Slice through structure:**
```
Filters → Common → Slice
- Origin: [x, y, z] at desired position
- Normal: [0, 0, 1] for horizontal slice
Click Apply
```

**Vector field (shows direction):**
```
Filters → Common → Glyph
- Glyph Type: Arrow
- Scale Array: E or H
- Scale Factor: Adjust for visibility
Click Apply
```

**Streamlines (field flow):**
```
Filters → Common → Stream Tracer
- Seed Type: Point Source or Line Source
- Place seeds where you want streamlines
Click Apply
```

**Clip to see inside:**
```
Filters → Common → Clip
- Plane to clip
- Show interior fields
Click Apply
```

## Tips & Tricks

### Performance

- **Too many files?** Load every Nth file instead of all
- **Slow animation?** Reduce opacity or use coarser mesh
- **Memory issues?** Close other applications

### Creating Figures

**High-quality screenshot:**
1. Set resolution: View → Preview → 1920×1080 (or higher)
2. Adjust camera angle
3. File → Save Screenshot
4. Choose format (PNG recommended)

**Export animation:**
1. Set up view
2. File → Save Animation
3. Choose format (AVI, MP4, image sequence)
4. Set frame rate (typically 10-30 fps)

### Common Visualizations

**Field magnitude heatmap:**
- Use "E" or "H" magnitude
- Adjust color map (cool to warm, rainbow, etc.)
- Show color legend

**Field vectors:**
- Use Glyph filter with arrows
- Scale arrows appropriately
- Color by magnitude

**Cross-sections:**
- Slice at multiple planes
- Show both E and H fields
- Overlay geometry

## Example Workflows

**Visualizing plane wave propagation (simple):**

1. Run: `python3 plane_wave_simple.py`
2. Open `Et_*.vtr` files from `plane_wave_sim/`
3. Color by: E-field magnitude
4. Animate to see wave propagation
5. Observe reflection/transmission at dielectric interface
6. Export as MP4 video

**Visualizing microstrip propagation (advanced):**

1. Run: `python3 microstrip_with_vtk.py`
2. Open `Et_*.vtr` files from `microstrip_vtk_sim/`
3. Color by: E-field magnitude
4. Add horizontal slice at trace height
5. Add vertical slice along trace
6. Animate to see wave propagation
7. Export as MP4 video

## OpenEMS VTK Export Options

### In Your Python Script

```python
# E-field dump
Et_dump = CSX.AddDump('Et', dump_type=0, file_type=0, dump_mode=2)
Et_dump.AddBox(start=[x0,y0,z0], stop=[x1,y1,z1])

# H-field dump
Ht_dump = CSX.AddDump('Ht', dump_type=1, file_type=0, dump_mode=2)
Ht_dump.AddBox(start=[x0,y0,z0], stop=[x1,y1,z1])

# Current density
Jt_dump = CSX.AddDump('Jt', dump_type=2, file_type=0, dump_mode=2)
Jt_dump.AddBox(start=[x0,y0,z0], stop=[x1,y1,z1])
```

**Parameters:**
- `dump_type`: 0=E, 1=H, 2=J, 3=total
- `file_type`: 0=VTK (ParaView), 1=HDF5
- `dump_mode`: 0=off, 1=single, 2=multi (timesteps)

**Dump frequency:**
```python
# Every 10 timesteps (default)
dump = CSX.AddDump(..., dump_mode=2)

# Specific timesteps
dump = CSX.AddDump(..., dump_mode=2, dump_interval=20)  # every 20 steps
```

## Assignment Ideas

**For Students:**

1. **Field visualization assignment:**
   - Run simulation
   - Create 3 different visualizations
   - Export high-quality images
   - Write captions explaining physics

2. **Animation assignment:**
   - Show wave propagation
   - Include both E and H fields
   - Add annotations
   - Export as video

3. **Comparison study:**
   - Simulate two different designs
   - Create side-by-side visualizations
   - Quantify differences

## Troubleshooting

**Files won't open:**
- Check file extension is `.vtr` not `.vtk`
- Ensure all timesteps present (no gaps)
- Try opening single file first

**Can't see fields:**
- Click "Apply" in Properties panel
- Check color scale range (auto-scale)
- Adjust opacity if clipping

**Animation jerky:**
- Reduce timestep output frequency
- Close other applications
- Use simpler visualization

**Colors look wrong:**
- Adjust color map in properties
- Check data range (may need rescale)
- Try different color schemes

## Resources

- **ParaView Tutorial:** https://www.paraview.org/tutorials/
- **ParaView Guide:** https://docs.paraview.org/
- **OpenEMS Wiki:** https://openems.de/index.php/Field_Dumps

## Quick Reference Card

```
Common ParaView Operations:

View Controls:
  Left-click+drag:     Rotate
  Middle-click+drag:   Pan
  Scroll:              Zoom
  Ctrl+Left-drag:      Roll

Useful Filters:
  Slice:               2D cut through 3D
  Clip:                Remove portion
  Glyph:               Show vectors
  Stream Tracer:       Field lines
  Calculator:          Compute derived quantities

Export:
  Screenshot:          File → Save Screenshot
  Animation:           File → Save Animation
  Data:                File → Save Data (CSV, etc.)
```
