# Power Distribution Network (PDN) Analysis Example

## Overview

This example demonstrates **DC power distribution network analysis** using ElmerFEM with **realistic simulated IC loads**. Unlike simplified models with fixed voltage boundaries, this example models ICs as **resistive loads** that draw current based on the actual voltage delivered to them.

## Use Case

**Problem:** You're designing a PCB that needs to deliver power at 3.3V from a voltage regulator to multiple ICs drawing a total of 1.0 A. You need to verify that the voltage drop across the power traces stays within specification (< 50 mV) to ensure proper IC operation.

**Challenge:** The initial design uses narrow traces that create excessive IR drop. Your task is to widen the traces to meet the voltage drop specification.

**What's Simulated:**
- Voltage distribution across the PDN
- **Realistic load behavior**: Current draw depends on delivered voltage
- IR drop from regulator through traces to loads
- Current density and current crowding in narrow traces
- Power dissipation (I²R losses) and hotspots
- Ground return path completing the circuit

## PDN Geometry

The example models a complete PCB power distribution network with realistic loads:

```
VDD (3.3V)
    |
    +--[Reg Trace 3.5mm]--+--[Main Bus 2.5mm]--+--[Branch 1.5mm]--[Load1: R=6.5Ω]--+
                                                |                                    |
                                                +--[Branch 1.5mm]--[Load2: R=10.8Ω]-+
                                                |                                    |
                                                +--[Branch 1.5mm]--[Load3: R=16.2Ω]-+
                                                                                     |
                                                                                     v
GND (0V) <===[Ground Return 4mm wide]========================================
```

**Components:**
- **Regulator trace:** 3.5 mm wide × 15 mm long (power from VDD)
- **Main bus:** 2.5 mm wide × 30 mm long (distribution)
- **Branch traces:** 1.5 mm wide × 10 mm long (to each load) **← Primary bottleneck!**
- **Load resistors:** 1 mm wide × 20mm long (IC equivalent resistance)
- **Ground return:** 4 mm wide × 45 mm long (low-resistance return path)
- **Copper thickness:** 35 µm (1 oz copper, standard PCB)

**Electrical Properties:**
- **Supply voltage**: 3.3 V at VDD input
- **Ground reference**: 0 V at ground return
- **Load 1**: Target 0.5 A at 3.25 V → R = 6.5 Ω
- **Load 2**: Target 0.3 A at 3.25 V → R = 10.83 Ω
- **Load 3**: Target 0.2 A at 3.25 V → R = 16.25 Ω

**Key Insight**: Loads are modeled as resistors! Actual current depends on delivered voltage:
- If V_load = 3.25 V → I = V/R (design target)
- If V_load < 3.25 V (due to IR drop) → I < target (realistic IC behavior)

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

## Design Challenge

**Initial Design:** The starting trace widths (3.5mm / 2.5mm / 1.5mm) are intentionally marginal and will likely **fail the 50 mV voltage drop spec**.

**Your Goal:** Iteratively widen traces to meet the < 50 mV spec at all load points.

### Optimization Strategy

1. **Identify the bottleneck**:
   - Branch traces (1.5 mm) are the narrowest → highest resistance
   - Distant loads will show larger voltage drops
   - Run initial simulation to confirm

2. **Widen traces systematically**:
   ```python
   # Edit pdn_analysis.py, lines 35-47

   # Try increasing branch width first (biggest impact)
   branch_width = 2.0  # mm (was 1.5)

   # If still failing, widen main bus
   bus_width = 3.0  # mm (was 2.5)

   # Last resort: widen regulator trace
   reg_trace_width = 4.5  # mm (was 3.5)
   ```

3. **Re-run and verify**:
   ```bash
   python3 pdn_analysis.py
   # Check voltage at load points in ParaView
   ```

4. **Iterate** until all loads meet < 50 mV drop

### Design Tradeoffs

- **Wider traces** → Lower R → Lower voltage drop ✓
- **Wider traces** → More PCB area → Higher cost ✗
- **Thicker copper** → Lower R → Better performance ✓
- **Thicker copper** → Harder to fab → Higher cost ✗

**Find the minimum widths that meet spec!**

### Alternative Optimizations

If widening traces isn't enough:

1. **Thicker copper:**
   ```python
   copper_thickness = 0.070  # mm (2 oz copper)
   ```

2. **Shorten traces** (move ICs closer to regulator)

3. **Copper pours** instead of narrow traces

4. **Multi-layer PDN** with vias for parallel paths

### Verification workflow:

```bash
# 1. Edit pdn_analysis.py trace width parameters
# 2. Re-run simulation
python3 pdn_analysis.py

# 3. Open in ParaView and check voltages
paraview simulation/pdn_t0001.vtu

# 4. Iterate until voltage drop < 50 mV at all loads
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
