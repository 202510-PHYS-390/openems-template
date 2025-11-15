# KiCAD to OpenEMS/ElmerFEM Workflows

This directory contains examples and tutorials for importing PCB designs from KiCAD into electromagnetic simulation tools.

## Available Workflows

### 1. **KiCAD → Gerber2EMS → OpenEMS** (High-Frequency Analysis)
Best for: Signal integrity, S-parameters, transmission lines, RF circuits

### 2. **KiCAD → STEP → Gmsh → ElmerFEM** (DC/Low-Frequency Analysis)
Best for: Power distribution networks, IR drop, current density, DC resistance

### 3. **KiCAD → FreeCAD → OpenEMS** (Alternative GUI Workflow)
Best for: Users who prefer GUI-based setup

---

## Prerequisites

All tools are pre-installed in this dev container:
- KiCAD (PCB design)
- Gerber2EMS (Gerber → OpenEMS converter)
- gerbv (Gerber file viewer)
- Gmsh (Mesh generator with STEP import)
- OpenEMS (FDTD simulator)
- ElmerFEM (FEM solver)

---

## Workflow 1: KiCAD → Gerber2EMS → OpenEMS

### Overview
This workflow converts KiCAD PCB designs to OpenEMS simulations using Gerber files (the manufacturing files).

### Step-by-Step Process

#### 1. Design Your PCB in KiCAD

Open KiCAD in the VNC desktop:
```bash
bash setup_gui.sh
# In VNC desktop: Applications → Development → KiCAD
```

Design your circuit with proper considerations:
- **Add port markers** on the F.Fab layer (small rectangles or pads at signal start/end points)
- **Set drill origin** at bottom-left corner (Edit → Origin → Drill and Place Offset)
- **Use proper layer stackup** (Board Setup → Board Stackup)
- **Add Edge.Cuts** outline for board boundary

#### 2. Export Gerber Files

In KiCAD PCB Editor:
1. File → Plot
2. Select **Gerber** format
3. Include these layers:
   - F.Cu, B.Cu (and inner layers if used)
   - F.Mask, B.Mask
   - F.Paste, B.Paste
   - F.Silkscreen, B.Silkscreen
   - Edge.Cuts
   - F.Fab (contains port markers)
4. Click "Plot"
5. Click "Generate Drill Files"
6. Close and save to `fab/` directory

#### 3. Create Configuration Files

Create `stackup.json` (material properties):
```json
{
  "layers": [
    {
      "name": "F.Cu",
      "type": "copper",
      "thickness": 35e-6,
      "conductivity": 5.96e7
    },
    {
      "name": "dielectric1",
      "type": "dielectric",
      "thickness": 1.6e-3,
      "epsilon_r": 4.3,
      "loss_tangent": 0.02
    },
    {
      "name": "B.Cu",
      "type": "copper",
      "thickness": 35e-6,
      "conductivity": 5.96e7
    }
  ]
}
```

Create `simulation.json` (simulation parameters):
```json
{
  "frequency": {
    "start": 1e9,
    "stop": 10e9,
    "points": 100
  },
  "mesh": {
    "resolution": {
      "x": 0.1e-3,
      "y": 0.1e-3,
      "z": 0.1e-3
    }
  },
  "ports": [
    {
      "name": "port1",
      "type": "microstrip",
      "position": [0, 0],
      "impedance": 50
    },
    {
      "name": "port2",
      "type": "microstrip",
      "position": [20, 0],
      "impedance": 50
    }
  ]
}
```

#### 4. Run Gerber2EMS

```bash
cd /workspace/kicad-examples/my_pcb
gerber2ems -a --export-field
```

Options:
- `-a` : Auto-run simulation
- `--export-field` : Export VTK field files for ParaView

#### 5. View Results

Results are in `ems/simulation/`:
- S-parameter plots (PNG images)
- VTK field dumps (for ParaView)
- Port definitions and mesh files

Open in ParaView to visualize electromagnetic fields.

---

## Workflow 2: KiCAD → STEP → Gmsh → ElmerFEM

### Overview
This workflow exports 3D geometry from KiCAD as STEP files, imports into Gmsh for meshing, then simulates DC/low-frequency current flow in ElmerFEM.

### Step-by-Step Process

#### 1. Design Your PCB in KiCAD

Same as Workflow 1, but focus on:
- Power distribution traces
- Ground planes
- Via placement
- Current-carrying paths

#### 2. Export STEP File

In KiCAD PCB Editor:
1. File → Export → STEP
2. Options:
   - ✓ Include board outline
   - ✓ Include copper layers
   - ✓ Include components (optional - can simplify by unchecking)
   - Output units: mm
3. Save as `pcb.step`

#### 3. Import STEP → Gmsh → ElmerFEM

See the example script: `step_to_elmerfem.py`

```bash
cd /workspace/kicad-examples
python3 step_to_elmerfem.py
```

This script:
1. Imports STEP geometry using Gmsh
2. Assigns material properties to copper layers
3. Generates FEM mesh
4. Creates ElmerFEM solver configuration
5. Runs current flow simulation
6. Exports VTU results for ParaView

#### 4. View Results

Open `simulation/result.vtu` in ParaView and visualize:
- Electric potential (voltage distribution)
- Current density (where current concentrates)
- Joule heating (I²R losses)
- Electric field

---

## Workflow 3: KiCAD → FreeCAD → OpenEMS

### Overview
Uses FreeCAD as GUI intermediary for easier setup. **Note:** This workflow has some compatibility issues with recent FreeCAD/KiCAD versions.

### Installation (if not already installed)

FreeCAD is not pre-installed due to size and compatibility concerns. To install:
```bash
sudo apt-get update
sudo apt-get install freecad
```

Install the FreeCAD-OpenEMS-Export macro:
1. Clone: `git clone https://github.com/LubomirJagos/FreeCAD-OpenEMS-Export.git`
2. Copy macro files to `~/.FreeCAD/Macro/`
3. Restart FreeCAD

### Usage

1. Open FreeCAD in VNC desktop
2. Macro → Macros → Execute "FreeCAD_to_OpenEMS"
3. Click "Import KiCad PCB"
4. Select your `.kicad_pcb` file
5. Configure simulation parameters in GUI
6. Export to OpenEMS Python script
7. Run the generated script

**Known Issues:**
- "Import KiCad PCB" button may be grayed out in FreeCAD 1.0+
- Ground plane import issues with KiCAD 8
- Workaround: Export STEP from KiCAD → Import STEP in FreeCAD

---

## Example Projects

### Simple Microstrip Transmission Line
- File: `microstrip_example/`
- Use Case: Learn S-parameter extraction
- Workflow: Gerber2EMS

### Power Distribution Network
- File: `pdn_example/`
- Use Case: Analyze voltage drop and current density
- Workflow: STEP → ElmerFEM

### Tapered Trace
- File: `tapered_trace/`
- Use Case: Study impedance matching and current crowding
- Both workflows available for comparison

---

## Tips and Best Practices

### For Gerber2EMS:
1. **Port placement is critical** - mark ports clearly on F.Fab layer
2. **Drill origin matters** - always set to bottom-left corner
3. **Port positions** must be calculated relative to drill origin
4. **Mesh resolution** affects accuracy and runtime (start coarse, refine if needed)
5. **Check Gerber files** with gerbv before running simulation

### For STEP Import:
1. **Simplify geometry** - remove unnecessary components for faster meshing
2. **Check units** - ensure mm consistency between KiCAD and Gmsh
3. **Material assignment** - manually assign physical groups to copper/dielectric regions
4. **Mesh quality** - use smaller mesh size near traces, larger in air regions
5. **2D vs 3D** - for simple traces, 2D cross-sections are much faster

### General KiCAD Tips:
1. **Start simple** - single trace between two ports for first tests
2. **Document stackup** - record layer thicknesses and materials
3. **Ground plane** - use solid pours, not just outlines
4. **Via stitching** - important for return current paths
5. **Trace width** - calculate using impedance calculators first

---

## Troubleshooting

### Gerber2EMS Issues

**Error: "gerbv not found"**
```bash
which gerbv  # Should show /usr/bin/gerbv
sudo apt-get install gerbv
```

**Error: "No ports found"**
- Check F.Fab layer has port markers
- Verify port positions in CSV file match PCB coordinates

**Error: "Mesh generation failed"**
- Reduce mesh resolution (increase values in simulation.json)
- Simplify PCB geometry
- Check for overlapping traces or invalid geometry

### STEP Import Issues

**Error: "STEP file not found"**
- Verify export path from KiCAD
- Check file permissions

**Error: "Gmsh cannot open STEP file"**
```bash
gmsh --version  # Check OpenCASCADE support
# Should show "Built with OpenCASCADE"
```

**Error: "ElmerSolver diverges"**
- Switch to Direct solver (UMFPack) instead of iterative
- Refine mesh near sharp corners
- Check material properties are physical
- Verify boundary conditions are correct

### FreeCAD Macro Issues

**Button grayed out:**
- Try running macro twice (known FreeCAD bug)
- Use older FreeCAD 0.19 instead of 1.0+
- Alternative: Export STEP from KiCAD, import STEP in FreeCAD

---

## Learning Path

### Beginner:
1. Start with workflow 2 (STEP → ElmerFEM)
2. Use provided example scripts
3. Modify geometry parameters
4. Visualize in ParaView

### Intermediate:
1. Design simple PCB in KiCAD (single trace)
2. Export Gerbers and run Gerber2EMS
3. Compare results with analytical calculations
4. Experiment with mesh resolution

### Advanced:
1. Multi-layer PCB with vias
2. Coupled transmission lines (crosstalk)
3. Power distribution network analysis
4. Optimize trace geometry based on simulation

---

## Additional Resources

- **Gerber2EMS GitHub:** https://github.com/antmicro/gerber2ems
- **OpenEMS Docs:** https://docs.openems.de/
- **ElmerFEM Tutorials:** http://www.elmerfem.org/
- **KiCAD Docs:** https://docs.kicad.org/
- **Gmsh Manual:** https://gmsh.info/doc/texinfo/gmsh.html

---

## Files in This Directory

- `README.md` - This file
- `step_to_elmerfem.py` - Example script for STEP → Gmsh → ElmerFEM
- `gerber2ems_template/` - Template directory structure for Gerber2EMS
- `simple_trace_example/` - Minimal working example (both workflows)

---

## Next Steps

1. **Try the examples** in `simple_trace_example/`
2. **Design your own PCB** in KiCAD
3. **Run simulations** and visualize in ParaView
4. **Compare workflows** - which is better for your application?
5. **Iterate and optimize** - use simulation feedback to improve design

Happy simulating!
