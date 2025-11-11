# OpenEMS Examples

This directory contains example simulations for learning PCB signal simulation with OpenEMS.

## Available Examples

1. **plane_wave_simple.py** - Simple field visualization (recommended for beginners)
2. **microstrip_with_vtk.py** - Microstrip with ParaView export
3. **microstrip_example.py** - Microstrip with S-parameter analysis

## Getting Started

### Field Visualization with ParaView (Recommended for Beginners)

The simplest way to see electromagnetic fields is with the plane wave example:

```bash
cd examples
python3 plane_wave_simple.py
```

**What it does:**
- Simulates a plane wave propagating through space
- Shows wave interaction with a dielectric slab
- **No port errors** - pure field visualization
- Creates VTK files viewable in ParaView on your laptop

**Output:** VTK files in `plane_wave_sim/` directory

**Next step:** Download the `.vtr` files and open in ParaView (see `PARAVIEW_GUIDE.md`)

### Microstrip with Field Visualization

For more advanced users, the microstrip with VTK export shows fields in a realistic transmission line:

```bash
cd examples
python3 microstrip_with_vtk.py
```

**What it does:**
- Simulates a microstrip transmission line
- Exports E-field and H-field distributions
- Creates VTK files for ParaView visualization
- **Note:** May show port configuration warnings (doesn't affect field dumps)

**Output:** VTK files in `microstrip_vtk_sim/` directory

### Running the Microstrip Example

The microstrip example simulates a simple 50-ohm transmission line on FR4 substrate.

```bash
cd examples
python3 microstrip_example.py
```

**What it does:**
- Creates a 40mm × 3mm copper trace on 1.6mm FR4 substrate
- Simulates from 500 MHz to 5 GHz
- Calculates S-parameters (S11, S21)
- Measures characteristic impedance
- Generates plots showing results

**Expected results:**
- Port impedances should be close to 50Ω
- S11 (return loss) should be < -10 dB (good matching)
- S21 (insertion loss) should be close to 0 dB (good transmission)

**Simulation time:** 2-5 minutes depending on system

### Output Files

After running, check the `microstrip_simulation/` directory:
- `microstrip.xml` - Geometry definition (viewable in AppCSXCAD)
- `results.png` - S-parameters and impedance plots
- Various `.h5` files - Raw field and port data

## Understanding the Code

The example is heavily commented. Key sections:

1. **Parameters** - Physical dimensions and material properties
2. **Materials** - Define FR4 substrate and copper
3. **Geometry** - Create substrate, ground plane, and trace
4. **Ports** - Define input/output measurement points
5. **Mesh** - Discretize the geometry for simulation
6. **Boundary** - Set up absorbing boundaries (PML)
7. **Post-processing** - Calculate and plot S-parameters

## Modifying the Example

Try experimenting with:

### Change trace width (affects impedance):
```python
trace_width = 2.0  # Narrower = higher impedance
trace_width = 4.0  # Wider = lower impedance
```

### Change substrate material:
```python
substrate_er = 2.2   # RO4003 (lower loss)
substrate_er = 4.3   # FR4 (standard)
substrate_er = 10.2  # Alumina (high εr)
```

### Change frequency range:
```python
f_start = 0.1e9  # 100 MHz
f_stop = 10e9    # 10 GHz
```

### Improve accuracy (slower):
```python
mesh_res = 0.25  # Finer mesh = more accurate
```

## Visualizing Geometry

To view the 3D geometry, you need the GUI:

```bash
# Start GUI environment
bash setup_gui.sh

# In browser: http://localhost:6080/vnc.html
# Password: openems
```

Then uncomment these lines in the example (around line 164):

```python
from CSXCAD import AppCSXCAD_BIN
os.system(AppCSXCAD_BIN + ' ' + os.path.join(sim_path, 'microstrip.xml'))
```

This will open the geometry viewer before simulation.

## Troubleshooting

### "ModuleNotFoundError: No module named 'openEMS'"
Run the environment test:
```bash
python3 /workspace/test_openems.py
```

### Simulation takes too long
Increase mesh size:
```python
mesh_res = 1.0  # Coarser mesh
```

### Out of memory
Reduce simulation size:
```python
trace_length = 20.0  # Shorter trace
f_points = 101      # Fewer frequency points
```

## Next Steps

After understanding this example:

1. Try designing a 75Ω microstrip (wider trace)
2. Add a bend or corner to see reflections
3. Simulate coupled microstrips (differential pairs)
4. Import real PCB traces from KiCad using gerber2ems

## Resources

- OpenEMS Documentation: https://docs.openems.de/
- Microstrip calculators: https://www.microwaves101.com/
- Transmission line theory: Pozar, "Microwave Engineering"
