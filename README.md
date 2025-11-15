# OpenEMS + ElmerFEM PCB Simulation Environment

Zero-install electromagnetic simulation environment combining **OpenEMS** (FDTD) and **ElmerFEM** (FEM) for teaching PCB design, signal integrity, and power distribution analysis.

## Quick Start

### Running Simulations with GUI

```bash
# 1. Start the GUI environment (runs in foreground)
bash setup_gui.sh

# 2. Open browser to http://localhost:6080/vnc.html
#    Password: openems

# 3. In another terminal, run examples

# OpenEMS examples (high-frequency FDTD)
cd Tutorials
python3 Rect_Waveguide.py

# ElmerFEM examples (DC/low-frequency FEM)
cd /workspace/elmerfem-examples
python3 tapered_working.py

# 4. Plots appear in VNC desktop window

# 5. Press Ctrl+C in setup_gui.sh terminal when done
```

### Running Simulations Headless (no GUI)

```bash
# Simulations still work without GUI
# Plots are saved as PNG files instead of displayed

cd examples
python3 microstrip_example.py

# Check the simulation output directory for results
ls microstrip_simulation/
```

## What's Included

### OpenEMS (High-Frequency FDTD)
- **OpenEMS** - Open source FDTD electromagnetic simulator
- **CSXCAD** - Geometry and material definition library
- **Use cases:** Signal integrity, transmission lines, S-parameters, antennas, RF circuits (>10 MHz)

### ElmerFEM (DC/Low-Frequency FEM)
- **ElmerFEM** - Finite element solver for multiphysics
- **Gmsh** - Mesh generation with Python API
- **Use cases:** DC current flow, IR drop, power distribution networks, current density (<1 MHz)

### KiCAD Integration (NEW!)
- **KiCAD** - PCB design software pre-installed
- **Gerber2EMS** - Convert KiCAD Gerber files → OpenEMS simulations
- **STEP Import** - Import KiCAD 3D models → Gmsh → ElmerFEM
- **Real PCB workflows** - Design in KiCAD, simulate electromagnetics

### Common Tools
- **Python bindings** - Full Python API for both simulators
- **VNC Desktop** - Browser-accessible XFCE desktop for visualization
- **ParaView support** - VTK export for 3D field visualization
- **Examples** - Working simulation examples and tutorials for both tools

## Directory Structure

```
.
├── setup_gui.sh          # One script to start GUI environment
├── examples/             # OpenEMS example simulations
│   └── README.md         # OpenEMS examples documentation
├── elmerfem-examples/    # ElmerFEM example simulations
│   └── README.md         # ElmerFEM examples documentation
├── kicad-examples/       # KiCAD → simulation workflows (NEW!)
│   ├── README.md         # Complete KiCAD workflows guide
│   └── gerber2ems_template/  # Templates for Gerber2EMS
├── Tutorials/            # Official OpenEMS tutorials
│   └── README.md         # Tutorial documentation
├── PARAVIEW_GUIDE.md     # ParaView visualization guide
├── simulations/          # Your simulation workspace
└── pcb-designs/          # KiCAD projects workspace
```

## For Students

**First time:**
1. Run `bash setup_gui.sh`
2. Open browser to http://localhost:6080/vnc.html
3. Run simulations in a separate terminal
4. View plots in browser window

**Want to simulate real PCB designs?**
- See `kicad-examples/README.md` for KiCAD → simulation workflows
- **Workflow 1:** KiCAD → Gerber2EMS → OpenEMS (S-parameters, RF)
- **Workflow 2:** KiCAD → STEP → Gmsh → ElmerFEM (current flow, IR drop)

**Need help?**
- See `Tutorials/README.md` for OpenEMS tutorial examples
- See `examples/README.md` for OpenEMS custom examples
- See `elmerfem-examples/README.md` for ElmerFEM examples
- See `kicad-examples/README.md` for KiCAD integration workflows
- See `PARAVIEW_GUIDE.md` for 3D field visualization
- Check logs: `~/.vnc/*.log` and `/tmp/novnc.log`

## For Instructors

See `DEPLOYMENT.md` for full GitHub Codespaces deployment guide.

## Environment Details

- **Platform:** Docker container (x86_64)
- **Base:** Ubuntu 22.04
- **OpenEMS:** v0.0.36+ (built from source)
- **CSXCAD:** v0.6.3+ (built from source)
- **ElmerFEM:** Latest (built from source with MUMPS/Hypre solvers)
- **Gmsh:** 4.11+ (mesh generator with Python API, OpenCASCADE support)
- **KiCAD:** Latest from Ubuntu repository (PCB design)
- **Gerber2EMS:** Latest from GitHub (via pipx)
- **gerbv:** Gerber file viewer and processor
- **Python:** 3.10+ (numpy, matplotlib, h5py, gmsh, meshio, pyvista)
- **Desktop:** XFCE4 via TigerVNC
- **Web Access:** noVNC on port 6080

## Testing Installation

```bash
# Verify complete installation (OpenEMS + ElmerFEM)
python3 test_environment.py

# Should show:
# OpenEMS Environment:
# ✓ CSXCAD
# ✓ openEMS
# ✓ numpy
# ✓ matplotlib
# ✓ h5py
#
# ElmerFEM Environment:
# ✓ ElmerSolver
# ✓ ElmerGrid
# ✓ gmsh
# ✓ meshio
# ✓ pyvista
```

## Troubleshooting

**Plots not showing?**
- Make sure `setup_gui.sh` is running
- Check environment: `echo $DISPLAY` (should be :1)
- Check environment: `echo $MPLBACKEND` (should be TkAgg)

**VNC won't connect?**
- Check VNC is running: `ps aux | grep Xvnc`
- Check noVNC logs: `cat /tmp/novnc.log`
- Try restarting: Ctrl+C in `setup_gui.sh`, then run it again

**Simulation errors?**
- Check the simulation output directory for logs
- Verify installation: `python3 test_environment.py`
- For OpenEMS issues, check mesh coordinates (use mesh units, not SI units)
- For ElmerFEM issues, check solver convergence (try Direct solver for complex geometry)

## Resources

### OpenEMS
- OpenEMS Documentation: https://docs.openems.de/
- OpenEMS GitHub: https://github.com/thliebig/openEMS
- Tutorials: https://github.com/thliebig/openEMS-Project/tree/master/python/Tutorials

### ElmerFEM
- ElmerFEM Homepage: http://www.elmerfem.org/
- ElmerFEM Documentation: https://www.nic.funet.fi/pub/sci/physics/elmer/doc/
- Gmsh Documentation: https://gmsh.info/doc/texinfo/gmsh.html

### Visualization
- ParaView: https://www.paraview.org/
- See `PARAVIEW_GUIDE.md` for detailed visualization instructions

---

**One script. Zero hassle. Two simulators. Pure electromagnetic analysis.**
