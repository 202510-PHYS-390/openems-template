# Gerber2EMS Template Directory

This directory provides template configuration files for running Gerber2EMS simulations.

## Directory Structure

```
gerber2ems_template/
├── README.md           # This file
├── stackup.json        # PCB material properties (layer thicknesses, ε_r, tan δ)
├── simulation.json     # Simulation parameters (frequency, mesh, ports)
└── fab/                # Place your Gerber files here
    ├── *.gbr           # Gerber files from KiCAD (copper layers, silkscreen, etc.)
    └── *.drl           # Drill files from KiCAD
```

## Quick Start

### 1. Export Gerber Files from KiCAD

In KiCAD PCB Editor:

1. **Set Drill Origin** (Important!)
   - Edit → Origin → Drill and Place Offset
   - Click at the bottom-left corner of your board

2. **Mark Port Locations**
   - Add small rectangles or pads on the F.Fab layer where signals enter/exit
   - Note their coordinates relative to drill origin

3. **Export Gerber Files**
   - File → Plot
   - Plot format: Gerber
   - Include layers:
     - F.Cu (top copper)
     - B.Cu (bottom copper)
     - Inner layers if multi-layer
     - F.Mask, B.Mask (solder mask)
     - F.Silkscreen, B.Silkscreen
     - Edge.Cuts (board outline)
     - F.Fab (contains port markers)
   - Click "Plot"
   - Output directory: Select `fab/` folder

4. **Generate Drill Files**
   - Still in Plot dialog, click "Generate Drill Files"
   - Format: Excellon
   - Click "Generate Drill File"
   - Close dialog

### 2. Configure Stackup

Edit `stackup.json`:

```json
{
  "layers": [
    {
      "name": "F.Cu",
      "type": "copper",
      "thickness": 35e-6      // 1 oz copper = 35 µm
    },
    {
      "name": "dielectric1",
      "type": "dielectric",
      "thickness": 1.6e-3,    // FR4 substrate, 1.6 mm
      "epsilon_r": 4.3,       // FR4 dielectric constant
      "loss_tangent": 0.02    // FR4 loss tangent
    },
    {
      "name": "B.Cu",
      "type": "copper",
      "thickness": 35e-6
    }
  ]
}
```

**Common Material Properties:**

| Material | ε_r | tan δ | Use Case |
|----------|-----|-------|----------|
| FR4 | 4.3 | 0.02 | General purpose, low cost |
| Rogers RO4003C | 3.38 | 0.0027 | High frequency, low loss |
| Rogers RO4350B | 3.48 | 0.0037 | Controlled impedance |
| PTFE (Teflon) | 2.1 | 0.0002 | Very high frequency |

**Copper Thickness:**
- 1 oz (standard): 35 µm = 35e-6 m
- 2 oz (heavy copper): 70 µm = 70e-6 m

### 3. Configure Simulation

Edit `simulation.json`:

```json
{
  "frequency": {
    "start": 1e9,    // 1 GHz
    "stop": 10e9,    // 10 GHz
    "points": 100
  },
  "ports": [
    {
      "name": "port1",
      "position": {
        "x": 0,      // mm, from drill origin
        "y": 0       // mm, from drill origin
      },
      "impedance": 50
    }
  ]
}
```

**To find port positions:**
1. In KiCAD, hover over port marker on F.Fab layer
2. Note coordinates shown at bottom of screen
3. Subtract drill origin coordinates: `port_pos = marker_pos - drill_origin`

### 4. Run Gerber2EMS

```bash
cd /workspace/kicad-examples/gerber2ems_template
gerber2ems -a --export-field
```

Options:
- `-a` : Auto-run simulation after setup
- `--export-field` : Export electromagnetic field dumps (VTK) for ParaView
- `--help` : Show all available options

### 5. View Results

Results are saved in `ems/simulation/`:

**S-Parameters:**
- `s_parameters.png` - Smith chart and S11/S21 plots
- `s_parameters.s2p` - Touchstone file (import to QUCS, ADS, etc.)

**Field Visualization:**
- `Et_*.vtr` - Electric field time series (VTK)
- `Ht_*.vtr` - Magnetic field time series (VTK)

**Open in ParaView:**
```bash
# Download VTK files to your local machine
# Open ParaView → File → Open → Select Et_*.vtr
# Color by: E-field magnitude
# Play animation to see wave propagation
```

## Troubleshooting

### "gerbv not found"
```bash
which gerbv  # Should show /usr/bin/gerbv
# If not installed:
sudo apt-get install gerbv
```

### "No Gerber files found"
- Check that Gerber files are in `fab/` directory
- Files should have extensions: `.gbr`, `.gbl`, `.gtl`, `.gto`, etc.
- Verify export succeeded in KiCAD

### "Port position error"
- Verify port positions in `simulation.json` match F.Fab markers
- Check that drill origin was set correctly (bottom-left)
- Ensure coordinates are in mm, not mils or inches

### "Mesh generation failed"
- Increase mesh size (make values larger): `"x": 0.2e-3` instead of `0.1e-3`
- Simplify PCB geometry (remove very small features)
- Check for overlapping traces or invalid geometry in KiCAD

### "Simulation takes too long"
- Reduce frequency range: fewer points or narrower bandwidth
- Increase mesh size (coarser mesh)
- Reduce simulation volume (smaller board or tighter bounds)
- Lower maximum timesteps if specified

## Tips for Good Results

### Port Placement
- Place ports perpendicular to trace direction
- Avoid placing ports on curves or bends
- Ensure port width matches trace width
- Mark ports clearly on F.Fab layer in KiCAD

### Mesh Resolution
Rule of thumb: **mesh_size < wavelength / 10**

At 10 GHz in FR4 (ε_r = 4.3):
- Wavelength = c / (f × √ε_r) ≈ 14 mm
- Mesh should be < 1.4 mm (we use 0.1 mm for good margin)

Faster simulation (less accurate): 0.2-0.5 mm
Balanced (recommended): 0.1 mm
High accuracy (slow): 0.05 mm

### Frequency Range
- Start with narrow range around your operating frequency
- Expand once you verify simulation works
- More points = better resolution but longer runtime

### Stackup Accuracy
- Get actual PCB stackup from manufacturer if possible
- FR4 ε_r varies: 4.2-4.5 (temperature and frequency dependent)
- Copper thickness affects impedance significantly

## Example Workflows

### Microstrip Transmission Line
1. Design 50Ω microstrip in KiCAD (use impedance calculator)
2. Add ports at both ends (F.Fab layer)
3. Export Gerbers to `fab/`
4. Set frequency range: 1-10 GHz
5. Run simulation
6. Check S11 < -10 dB (good matching)
7. Check S21 ≈ 0 dB (low loss)

### Differential Pair
1. Design differential traces (equal length, controlled spacing)
2. Add port pairs at both ends
3. Configure in simulation.json:
   - port1: positive signal
   - port2: negative signal (differential)
4. Analyze differential impedance (should be 90-100Ω for USB, etc.)

### Antenna Feed
1. Design antenna trace with feed point
2. Port at feed point (50Ω typical)
3. Wide frequency range for bandwidth analysis
4. Check S11 for resonance and impedance matching

## Next Steps

1. **Start simple:** Single trace, two ports, verify S-parameters
2. **Iterate design:** Adjust trace width/spacing based on results
3. **Validate:** Compare with analytical calculations or commercial tools
4. **Optimize:** Use simulation feedback to improve PCB layout

## Additional Resources

- Gerber2EMS GitHub: https://github.com/antmicro/gerber2ems
- Tutorial: https://nuclearrambo.com/wordpress/gerber2ems-a-short-tutorial-to-simulate-your-pcbs-in-openems/
- OpenEMS Docs: https://docs.openems.de/
- KiCAD Docs: https://docs.kicad.org/
