# Power Distribution Network (PDN) Analysis Example

## Overview

This example demonstrates **DC power distribution network analysis** using ElmerFEM to simulate voltage drop (IR drop), current density, and power dissipation in a realistic PCB power delivery system.

## Use Case

**Problem:** You're designing a PCB that needs to deliver 1 A of current at 3.3V from a voltage regulator to multiple ICs. You need to verify that the voltage drop across the power traces stays within specification (< 50 mV) to ensure proper IC operation.

**Solution:** Use ElmerFEM to simulate the DC current flow through the power distribution network and analyze:
- Voltage distribution across the PDN
- IR drop from regulator to loads
- Current density in traces
- Power dissipation (I²R losses)
- Identification of high-resistance bottlenecks

## PDN Geometry

The example models a simplified PCB power distribution network:

```
                    Load 1 (500 mA)
                         |
VDD (3.3V) ----[Wide]----+=====[Bus]====+----+---- Load 2 (300 mA)
Regulator      Trace                    |
               3mm wide           Load 3 (200 mA)
                                        |
                                        |
GND ============================================
                Ground Plane
```

**Components:**
- **Regulator trace:** 3 mm wide, 15 mm long (low resistance path from VDD)
- **Main bus:** 2 mm wide, 30 mm long (distributes power)
- **Branch traces:** 1 mm wide, 10 mm long (to each load)
- **Load pads:** 0.5 mm × 0.5 mm (connection points for ICs)
- **Ground plane:** 5 mm wide return path
- **Copper thickness:** 35 µm (1 oz copper, standard PCB)

**Electrical:**
- Supply voltage: 3.3 V
- Total current: 1.0 A (split among 3 loads)
- Load 1: 500 mA
- Load 2: 300 mA
- Load 3: 200 mA

## Running the Simulation

### Prerequisites

Ensure you're in the dev container with ElmerFEM installed (available on the ElmerFEM branch).

### Step 1: Run the Simulation

```bash
cd /workspace/kicad-examples/pdn_example
python3 pdn_analysis.py
```

**Expected output:**
```
======================================================================
PDN Analysis - Power Distribution Network Simulation
======================================================================

Geometry:
  PCB: 50.0 x 40.0 mm
  Copper thickness: 0.035 mm (35.0 um)

Electrical:
  Supply voltage: 3.3 V
  Total current: 1.0 A
  Load 1: 0.5 A at (25.0, 30.0)
  Load 2: 0.3 A at (35.0, 30.0)
  Load 3: 0.2 A at (25.0, 10.0)
  Max allowed voltage drop: 50.0 mV

Generating mesh...
  Nodes: ~2000-5000
  Elements: ~3000-8000

Converting mesh to Elmer format...
Running ElmerSolver...

✓ Simulation completed successfully!

Voltage Analysis:
  Maximum voltage: 3.3000 V
  Minimum voltage: 3.2XXX V
  Total voltage drop: XX.XX mV
  ✓ Voltage drop within spec (50.0 mV)
```

**Simulation time:** ~10-30 seconds depending on mesh resolution

### Step 2: Visualize Results in ParaView

The simulation creates `simulation/pdn.vtu` with the following fields:

1. **Open ParaView:**
   ```bash
   bash setup_gui.sh
   # In VNC desktop: paraview simulation/pdn.vtu
   ```

2. **Voltage Distribution:**
   - Click "Apply" to load the data
   - Color by: `potential`
   - This shows the voltage at every point in the PDN
   - Look for voltage drops from 3.3V (input) down to lower values (loads)

3. **Current Density:**
   - Color by: `current density`
   - Shows where current is concentrated
   - Look for high current density in narrow traces (current crowding)
   - Magnitude indicates A/m²

4. **Joule Heating:**
   - Color by: `joule heating`
   - Shows power dissipation (I²R losses)
   - Identifies hot spots where power is wasted

5. **Electric Field:**
   - Color by: `electric field`
   - Shows field strength in V/m
   - Higher field = higher voltage gradient

## Understanding the Results

### Voltage Drop Analysis

The key metric is the **voltage drop** from the regulator output (3.3V) to the load points.

**Typical results:**
- At regulator output: 3.300 V
- At main bus: 3.295 V (5 mV drop)
- At Load 1: 3.280 V (20 mV drop from source)
- At Load 2: 3.285 V (15 mV drop from source)
- At Load 3: 3.275 V (25 mV drop from source)

**Interpretation:**
- Each IC requires 3.3V ± tolerance (e.g., ±5% = 3.135-3.465V)
- Voltage drop reduces available headroom
- **Target:** Keep voltage drop < 50 mV for good design margin

### Current Density

Current density J (A/m²) shows how current distributes:

**Expected patterns:**
- **Highest density** in narrow branch traces (1 mm wide)
- **Lower density** in wide regulator trace (3 mm wide)
- **Non-uniform** distribution in corners and junctions

**Why it matters:**
- High current density → higher resistance → more voltage drop
- High current density → more heating
- Excessive current density can cause:
  - Electromigration (long-term reliability issue)
  - Thermal issues
  - Voltage drop exceeding spec

**Rule of thumb:** Keep J < 20 A/mm² for reliability (< 2×10⁷ A/m²)

### Power Dissipation

Joule heating P = I²R shows power wasted as heat:

**Expected patterns:**
- Concentrated in narrow, high-resistance paths
- Minimal in wide, low-resistance traces

**Why it matters:**
- Wasted power reduces efficiency
- Heating can affect nearby components
- Excessive heating may require thermal management

## Design Optimization

Based on simulation results, you can optimize the PDN:

### If voltage drop is too high:

1. **Widen traces:**
   - Resistance R ∝ 1/width
   - Doubling width cuts resistance in half
   - Edit `reg_trace_width`, `bus_width`, `branch_width` in script

2. **Use thicker copper:**
   - Standard: 1 oz (35 µm)
   - Heavy copper: 2 oz (70 µm) or 4 oz (140 µm)
   - Resistance R ∝ 1/thickness
   - Edit `copper_thickness` in script

3. **Shorten traces:**
   - Move components closer to regulator
   - Reduce `reg_trace_length`, `branch_length`

4. **Use copper pours:**
   - Instead of narrow traces, use filled copper areas
   - Much lower resistance

5. **Add parallel paths:**
   - Use both top and bottom layer with vias
   - Effective resistance: R_total = R1 || R2

### Verification workflow:

```bash
# 1. Edit pdn_analysis.py parameters
# 2. Re-run simulation
python3 pdn_analysis.py

# 3. Check voltage drop in output
# 4. Visualize in ParaView
# 5. Iterate until voltage drop < spec
```

## Comparing to Analytical Calculations

You can verify the simulation with simple resistor calculations:

**Resistance of rectangular trace:**
```
R = ρ × L / (W × T)

where:
  ρ = resistivity of copper = 1.68×10⁻⁸ Ω·m
  L = length (m)
  W = width (m)
  T = thickness (m)
```

**Example: Regulator trace (3 mm wide, 15 mm long, 35 µm thick)**
```
R = 1.68×10⁻⁸ × 0.015 / (0.003 × 35×10⁻⁶)
R = 2.4 mΩ
```

**Voltage drop at 1 A:**
```
V_drop = I × R = 1.0 A × 2.4 mΩ = 2.4 mV
```

The simulation should match this within ~10% (mesh discretization effects).

## Extending the Example

### Add more loads:

1. Define new load positions in the script
2. Add new branch traces and pads
3. Update load currents
4. Re-run simulation

### Model a real PCB:

1. Design PCB in KiCAD
2. Export STEP file (File → Export → STEP)
3. Import STEP geometry into Gmsh
4. Adapt this script to use imported geometry
5. Assign materials and boundary conditions

### Add thermal coupling:

ElmerFEM can solve coupled thermal-electrical problems:
- Joule heating generates heat
- Temperature affects copper resistivity
- Requires heat equation solver (more advanced)

## Common Issues

### Simulation diverges:

**Symptom:** ElmerSolver reports "not converged" or very large residuals

**Solutions:**
- Check that geometry doesn't have gaps or overlaps
- Ensure boundary conditions are physically valid
- Use Direct solver (already configured in this example)
- Refine mesh near boundaries

### Voltage drop seems wrong:

**Check:**
- Are load currents realistic? (1-2 A is typical for ICs)
- Is copper conductivity correct? (5.96×10⁷ S/m for pure copper)
- Is thickness scaled correctly? (35 µm = 0.035 mm)
- Compare to analytical calculation (R = ρL/A)

### VTU file has no fields:

**Solution:**
- Check `Exported Variable` declarations in SIF file
- Ensure `Calculate ... = True` is set in Solver section
- Verify ElmerSolver ran without errors (check solver.log)

## Learning Objectives

After completing this example, you should understand:

1. How to model power distribution networks in ElmerFEM
2. How to calculate and interpret voltage drop (IR drop)
3. How current density varies with trace geometry
4. The relationship between resistance, current, and voltage drop
5. How to optimize PDN design for low voltage drop
6. The trade-offs between trace width, cost, and performance

## References

- **ElmerFEM Tutorials:** http://www.elmerfem.org/
- **PCB Design Guidelines:** IPC-2221 (trace current capacity)
- **Voltage Drop Calculators:** https://www.4pcb.com/trace-width-calculator.html
- **Copper Resistivity:** https://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity

## Next Steps

1. **Run the example** and visualize results
2. **Modify parameters** (trace widths, currents) and observe effects
3. **Design your own PDN** in KiCAD and import via STEP
4. **Combine with thermal analysis** for complete power integrity study
5. **Compare results** with OpenEMS for AC impedance analysis

---

**Happy PDN analyzing!**
