# OpenEMS PCB Simulation Environment

Zero-install OpenEMS electromagnetic simulation environment for teaching PCB design and signal integrity.

## Quick Start

### Running Simulations with GUI

```bash
# 1. Start the GUI environment (runs in foreground)
bash setup_gui.sh

# 2. Open browser to http://localhost:6080/vnc.html
#    Password: openems

# 3. In another terminal, run examples
cd Tutorials
python3 Rect_Waveguide.py

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

- **OpenEMS** - Open source FDTD electromagnetic simulator
- **CSXCAD** - Geometry and material definition library
- **Python bindings** - Full Python API for simulation scripting
- **VNC Desktop** - Browser-accessible XFCE desktop for visualization
- **Examples** - Working simulation examples and tutorials

## Directory Structure

```
.
├── setup_gui.sh          # One script to start GUI environment
├── examples/             # Example simulations
│   └── README.md         # Examples documentation
├── Tutorials/            # Official OpenEMS tutorials
│   └── README.md         # Tutorial documentation
├── simulations/          # Your simulation workspace
└── pcb-designs/          # KiCad projects (if using)
```

## For Students

**First time:**
1. Run `bash setup_gui.sh`
2. Open browser to http://localhost:6080/vnc.html
3. Run simulations in a separate terminal
4. View plots in browser window

**Need help?**
- See `Tutorials/README.md` for tutorial examples
- See `examples/README.md` for custom examples
- Check logs: `~/.vnc/*.log` and `/tmp/novnc.log`

## For Instructors

See `DEPLOYMENT.md` for full GitHub Codespaces deployment guide.

## Environment Details

- **Platform:** Docker container (x86_64)
- **Base:** Ubuntu 22.04
- **OpenEMS:** v0.0.36+ (built from source)
- **CSXCAD:** v0.6.3+ (built from source)
- **Python:** 3.10+
- **Desktop:** XFCE4 via TigerVNC
- **Web Access:** noVNC on port 6080

## Testing Installation

```bash
# Verify OpenEMS installation
python3 test_openems.py

# Should show:
# ✓ CSXCAD
# ✓ openEMS
# ✓ numpy
# ✓ matplotlib
# ✓ h5py
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
- Verify test passes: `python3 test_openems.py`

## Resources

- OpenEMS Documentation: https://docs.openems.de/
- OpenEMS GitHub: https://github.com/thliebig/openEMS
- Tutorials: https://github.com/thliebig/openEMS-Project/tree/master/python/Tutorials

---

**One script. Zero hassle. Pure simulation.**
