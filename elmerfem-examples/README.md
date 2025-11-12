# ElmerFEM Examples for PCB Analysis

ElmerFEM is a finite element multiphysics solver excellent for:
- **DC current flow** in conductors
- **Power distribution** network (PDN) analysis
- **Thermal** analysis
- **Electrostatics** and magnetostatics

## Available Examples

### tapered_trace.py - Current Flow in Tapered Trace

Simulates DC current through a copper trace that changes width.

**What it shows:**
- Electric potential (voltage) distribution
- Electric field concentration at width transitions
- Current density (higher where trace is narrower)
- Joule heating distribution

**To run:**
```bash
cd /workspace/elmerfem-examples
python3 tapered_trace.py
```

**Visualization in ParaView:**
1. Open `tapered_trace_sim/trace_results*.vtu`
2. Click "Apply"
3. Change coloring to view different fields:
   - **Potential**: Voltage distribution
   - **electric field**: E-field magnitude
   - **current density**: Current density magnitude

## ElmerFEM vs OpenEMS

**Use ElmerFEM for:**
- DC or low-frequency (<1 MHz) analysis
- Resistive voltage drops
- Power distribution networks
- Thermal effects
- Static field problems

**Use OpenEMS for:**
- High-frequency (>10 MHz) analysis
- Transmission lines, S-parameters
- Signal integrity
- Antennas, RF circuits
- Wave propagation

## ElmerFEM Workflow

1. **Create mesh** - Using Gmsh or other mesh generator
2. **Convert mesh** - Use `ElmerGrid` to convert to Elmer format
3. **Write .sif file** - Solver input file defining physics
4. **Run solver** - `ElmerSolver case.sif`
5. **Visualize** - Open .vtu files in ParaView

## Key ElmerFEM Tools

- **ElmerSolver**: Main FEM solver
- **ElmerGrid**: Mesh conversion and generation
- **ElmerGUI**: Graphical interface (available via VNC)
- **Gmsh**: Mesh generation (industry standard)

## Python Integration

The examples use Python to:
- Generate geometry with Gmsh Python API
- Create mesh programmatically
- Write .sif files dynamically
- Run ElmerFEM solvers
- Post-process results

## Tips

**Mesh refinement:**
- Smaller `lc` value in Gmsh = finer mesh = more accurate, slower
- Typical: 0.5mm for PCB traces

**Convergence issues:**
- Check material properties
- Verify boundary conditions
- Refine mesh at critical areas
- Try different linear solvers

**Visualization:**
- Current density shows where current flows
- Potential shows voltage distribution
- Electric field shows field strength and direction

## Further Examples

More examples to come:
- Ground plane current distribution
- Via current capacity
- Thermal-electric coupling
- Multi-layer PCB power distribution
