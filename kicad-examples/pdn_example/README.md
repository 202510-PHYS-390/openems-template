# Power Distribution Network (PDN) Analysis Example

## Overview

This example demonstrates **DC power distribution network analysis** using ElmerFEM with **geometric resistors**. The key insight: **resistors are just narrow copper traces!** By making trace sections very narrow (0.1-0.2 mm wide), we create controlled resistances that simulate IC loads.

## Use Case

**Problem:** You're designing a PCB that needs to deliver power at 3.3V from a voltage regulator to multiple ICs. You need to understand voltage drops, current distribution, and power dissipation in the power distribution network.

**Key Concept:** Instead of using complex load models, we model IC loads as **narrow copper traces**. The resistance comes purely from geometry:
- Narrow trace = high resistance = simulates a load
- Wide trace = low resistance = power distribution

**What's Simulated:**
- Voltage distribution across the PDN
- **Geometric resistors**: Current flow through narrow copper sections
- IR drop from regulator through traces to loads and back to ground
- Current density and current crowding in narrow resistor regions
- Power dissipation (I²R losses) showing where power is wasted
- Complete circuit path: VDD → traces → narrow resistors → ground return

## PDN Geometry

The example models a simple but realistic power distribution network:

```
VDD (3.3V)
    |
    +--[Reg Trace 3.5mm]--[Main Bus 2.5mm]--+--[Branch 1.5mm]--+
                                             |                  |
                                             |         [Narrow Resistor]
                                             |         0.2mm × 20mm
                                             |                  |
                                             +--[Branch 1.5mm]--+
                                                       |
                                              [Narrow Resistor]
                                              0.1mm × 20mm
                                                       |
                                                       v
GND (0V) <===[Ground Return 4mm wide]===================
```

**Components:**
- **Regulator trace:** 3.5 mm wide × 15 mm long (power from VDD)
- **Main bus:** 2.5 mm wide × 30 mm long (distribution)
- **Branch traces:** 1.5 mm wide (connects to loads)
- **Load 1 resistor:** **0.2 mm** wide × 20 mm long (narrow copper = resistance!)
- **Load 2 resistor:** **0.1 mm** wide × 20 mm long (even narrower = 2× resistance!)
- **Ground return:** 4 mm wide × 45 mm long (low-resistance return path)
- **Copper thickness:** 35 µm (1 oz copper, standard PCB)

**Electrical Properties:**
- **Supply voltage**: 3.3 V at VDD input
- **Ground reference**: 0 V at ground return
- **Uniform material**: All copper (σ = 5.96×10⁷ S/m × 35µm = 2086 S effective)

**Resistor Values (calculated):**
```
R = L / (σ_eff × w)

Load 1: R₁ = 20mm / (2086 S × 0.2mm) ≈ 0.048 Ω
Load 2: R₂ = 20mm / (2086 S × 0.1mm) ≈ 0.096 Ω (2× higher!)
```

**Key Insight**: Resistors are GEOMETRY, not materials!
- Narrow trace → high resistance → acts like a load
- Current flow creates voltage drop across the narrow section
- Current density is 2× higher in the 0.1mm resistor

## Running the Simulation

### Prerequisites

Ensure you're in the dev container with ElmerFEM installed (available on the ElmerFEM branch).

### Step 1: Run the Simulation

```bash
cd /workspace/kicad-examples/pdn_example
python3 pdn_geometric.py
```

**Expected output:**
```
======================================================================
PDN with Geometric Resistors
======================================================================

Geometry:
  Power traces: 3.5-1.5 mm wide
  Load 1 resistor: 0.2 mm wide × 20.0 mm long
  Load 2 resistor: 0.1 mm wide × 20.0 mm long
  Ground return: 4.0 mm tall

Material: Uniform copper (σ = 2.09e+03 S)

Resistor resistance (approx):
  R1 (0.2mm) ≈ 0.048 Ω
  R2 (0.1mm) ≈ 0.096 Ω (2× higher resistance)

Building geometry...
  Resistor 1 width before fuse: 0.2000 mm
  Resistor 2 width before fuse: 0.1000 mm
✓ VDD: 1 edge(s)
✓ GND: 1 edge(s)

Generating mesh...
  Nodes: ~3000-6000

Running ElmerSolver...
✓ Simulation completed!

✓ Results: simulation/pdn_geo0001.vtu

Visualize: paraview simulation/pdn_geo0001.vtu

You should see:
  - PDN structure (power traces + ground)
  - NARROW resistors (0.1mm wide)
  - Voltage drops in resistors
  - Current crowding in narrow regions
```

**Simulation time:** ~10-30 seconds depending on mesh resolution

### Step 2: Visualize Results in ParaView

The simulation creates `simulation/pdn_geo0001.vtu` with the following fields:

1. **Open ParaView:**
   ```bash
   bash setup_gui.sh
   # In VNC desktop: paraview simulation/pdn_geo0001.vtu
   ```

2. **Voltage Distribution (Potential):**
   - Click "Apply" to load the data
   - Color by: `potential`
   - This shows the voltage at every point in the PDN
   - Look for voltage drops from 3.3V (VDD input) → through narrow resistors → to 0V (ground)
   - You should see the steepest voltage gradient in the narrow 0.1mm and 0.2mm resistor sections

3. **Current Density:**
   - Color by: `current density`
   - Shows where current is concentrated
   - **Key observation:** Current density should be ~2× higher in the 0.1mm resistor than the 0.2mm resistor
   - Look for current crowding in the narrow resistor regions
   - Magnitude indicates A/m²

4. **Joule Heating:**
   - Color by: `joule heating`
   - Shows power dissipation (I²R losses)
   - **Key observation:** Heating is concentrated in the narrow resistor sections
   - Identifies hot spots where power is wasted (resistors dissipate power!)

5. **Electric Field (Gradient):**
   - Color by: `electric field` (or check available field names)
   - Shows field strength in V/m
   - Higher field = higher voltage gradient
   - Should be strongest in the narrow resistor sections

## Understanding the Results

### Voltage Drop Analysis

The key observation is how **voltage drops across the narrow resistor sections**.

**Expected voltage distribution:**
- At VDD input (left edge): 3.300 V
- Through regulator trace: ~3.295 V (minimal drop, wide trace)
- Through main bus: ~3.290 V (minimal drop, wide trace)
- At top of narrow resistors: ~3.285 V
- **Across narrow resistors:** Steep voltage drop! (this is where resistance is!)
- At bottom of resistors (ground plane): ~0.00 V

**Key Insight:**
- Most voltage drop occurs in the **narrow resistor sections** (0.1mm and 0.2mm wide)
- Wide traces (3.5mm, 2.5mm, 1.5mm) have negligible voltage drop
- This demonstrates: **Resistance = Geometry!**
  - R ∝ L / w (resistance proportional to length/width ratio)
  - Narrow section = high resistance = large voltage drop

### Current Density

Current density J (A/m²) shows how current distributes:

**Expected patterns:**
- **Highest density** in the narrow resistor sections (0.1mm and 0.2mm wide)
- **Lower density** in wide distribution traces (1.5-3.5mm wide)
- **2× higher density in 0.1mm resistor** compared to 0.2mm resistor
  - Same current flows through both (series circuit)
  - J = I / A, so narrower width → higher density

**Why it matters:**
- J = I / (w × t) where w = width, t = thickness
- Narrow section = small cross-sectional area = high current density
- High current density → more heating (Joule heating ∝ J²)
- This demonstrates **current crowding** in narrow conductors

**Physical insight:**
- Current is conserved (same current flows through entire circuit)
- Current density varies inversely with cross-section
- Narrow resistor sections concentrate current → higher density

### Power Dissipation

Joule heating P = I²R shows power wasted as heat:

**Expected patterns:**
- **Concentrated in the narrow resistor sections** (0.1mm and 0.2mm wide)
- Minimal in wide distribution traces
- Higher heating in the narrower (0.1mm) resistor due to higher resistance

**Why it matters:**
- Resistors dissipate power: P = I²R = V²/R
- Narrow sections have high resistance → more power dissipation
- This is where the "load" actually consumes power
- In a real PCB, this would be the IC power consumption

**Physical insight:**
- Power dissipation creates heat
- In this geometric model, narrow resistors simulate IC power draw
- Real ICs would have their own internal resistance creating this same effect

## Design Challenge

**Understanding the Model:** This example uses geometric resistors (narrow traces) to demonstrate the concept. The resistors are intentionally narrow to create measurable voltage drops and current density variations.

**Your Goal:** Modify the geometry to explore different design scenarios.

### Exploration Ideas

1. **Change resistor widths**:
   ```python
   # Edit pdn_geometric.py, lines 32-33

   # Make resistors narrower → higher resistance
   resistor1_width = 0.15  # mm (was 0.2)
   resistor2_width = 0.08  # mm (was 0.1)

   # Or wider → lower resistance
   resistor1_width = 0.3  # mm
   resistor2_width = 0.2  # mm
   ```
   **Effect:** Observe how resistance and current density change

2. **Change resistor length**:
   ```python
   # Edit pdn_geometric.py, line 34

   resistor_length = 30.0  # mm (was 20.0)
   ```
   **Effect:** Longer resistor → higher resistance → more voltage drop

3. **Widen distribution traces**:
   ```python
   # Edit pdn_geometric.py, lines 17-19

   reg_trace_width = 5.0   # mm (was 3.5)
   bus_width = 4.0         # mm (was 2.5)
   branch_width = 2.5      # mm (was 1.5)
   ```
   **Effect:** Lower IR drop in distribution network (but resistors still dominate)

### Re-run workflow:

```bash
# 1. Edit pdn_geometric.py parameters
# 2. Re-run simulation
python3 pdn_geometric.py

# 3. Open in ParaView and observe changes
paraview simulation/pdn_geo0001.vtu

# 4. Compare voltage drops and current densities
```

### Understanding Geometric Resistors

**Key Concept:** In PCB design, narrow traces naturally have higher resistance:
- R = ρL / (wt) where ρ = resistivity, L = length, w = width, t = thickness
- Making w very small → high resistance
- This is how we create "loads" using only geometry

**Real-world applications:**
- Current sense resistors (use narrow trace sections)
- Heating elements (narrow traces intentionally generate heat)
- Fuses (narrow sections melt under overcurrent)

**In this example:**
- We intentionally make the "load" sections narrow (0.1-0.2mm)
- This creates controlled resistance
- Allows us to simulate IC loads without complex models

## Comparing to Analytical Calculations

You can verify the simulation with simple resistor calculations.

**For 2D analysis, use effective conductivity:**
```
σ_eff = σ × t = 5.96×10⁷ S/m × 35×10⁻⁶ m = 2086 S
```

**2D Resistance formula:**
```
R = L / (σ_eff × w)

where:
  L = length (m)
  w = width (m)
  σ_eff = effective conductivity (S)
```

**Example: Load 1 resistor (0.2 mm wide, 20 mm long)**
```
R₁ = 0.020 m / (2086 S × 0.0002 m)
R₁ = 0.020 / 0.4172
R₁ ≈ 0.048 Ω (48 mΩ)
```

**Example: Load 2 resistor (0.1 mm wide, 20 mm long)**
```
R₂ = 0.020 m / (2086 S × 0.0001 m)
R₂ = 0.020 / 0.2086
R₂ ≈ 0.096 Ω (96 mΩ)
```

**Note:** R₂ = 2 × R₁ because width is half!

The simulation should match these analytical values within ~10% (mesh discretization effects).

## Extending the Example

### Add more geometric resistors:

1. Define new load positions in `pdn_geometric.py`
2. Add new branch traces connecting to resistor tops
3. Create new narrow resistor rectangles with different widths
4. Fuse new resistors into the main conductor
5. Re-run simulation and compare current densities

**Example:** Add a third load with 0.15 mm width to see intermediate behavior

### Model different resistor ratios:

Try creating resistors with different aspect ratios:
```python
# Short, very narrow → high resistance per mm
resistor_width = 0.05   # mm
resistor_length = 10.0  # mm

# Long, moderately narrow → same total resistance
resistor_width = 0.1    # mm
resistor_length = 20.0  # mm
```

### Add thermal coupling:

ElmerFEM can solve coupled thermal-electrical problems:
- Joule heating in resistors generates heat
- Temperature affects copper resistivity (ρ increases with T)
- Requires heat equation solver + temperature-dependent conductivity
- More advanced, but shows realistic thermal-electrical coupling

## Common Issues

### Resistor widths change after fusing:

**Symptom:** Narrow resistors appear wider than expected in ParaView

**Check:**
- Look at "width before fuse" debug output in the script
- Gmsh may merge nearby vertices if too close
- Solution: Use very fine mesh (0.05 mm) in resistor regions (already configured)
- Verify resistor geometry before `fuse` operation

### Mesh is too coarse in narrow regions:

**Symptom:** Results look blocky or inaccurate in resistors

**Solution:**
- The script already sets fine mesh (0.05 mm) near load positions
- For even finer resolution, reduce mesh size:
  ```python
  gmsh.model.mesh.setSize(nearby, 0.025)  # 25 µm mesh
  ```

### Simulation diverges:

**Symptom:** ElmerSolver reports "not converged" or very large residuals

**Solutions:**
- Check that all geometry fuses correctly (no gaps!)
- Ensure boundary conditions are on correct edges
- Use Direct solver (UMFPack) - already configured
- Refine mesh near narrow resistors

### Current density values seem wrong:

**Check:**
- Are units correct? (J in A/m²)
- Remember: J = I / (w × t) where t = 35 µm = 35×10⁻⁶ m
- For 0.1 mm wide resistor: cross-section = 0.1mm × 0.035mm = 3.5×10⁻⁹ m²
- Even small current (~0.1 A) creates high J (~10⁷ A/m²)

### VTU file missing fields:

**Solution:**
- Check that FluxSolver ran (Solver 2 in SIF)
- Verify "Calculate Flux = True" in solver configuration
- Current density comes from FluxSolver, not StatCurrentSolver

## Learning Objectives

After completing this example, you should understand:

1. **Geometric resistors:** How narrow traces create resistance purely through geometry
2. **2D FEM analysis:** Using ElmerFEM to solve DC current flow problems
3. **Resistance scaling:** R ∝ L/w relationship (length/width ratio)
4. **Current density:** How J varies inversely with cross-sectional area
5. **Voltage drops:** Where IR drop occurs in a conductor network
6. **Current conservation:** Same current flows through series elements, but density varies
7. **Joule heating:** Power dissipation concentrated in high-resistance regions
8. **Mesh refinement:** Importance of fine mesh in narrow geometric features
9. **Field visualization:** Using ParaView to understand current flow and voltage distribution
10. **Analytical verification:** Comparing FEM results to simple calculations

## References

- **ElmerFEM Documentation:** http://www.elmerfem.org/
- **ElmerFEM Tutorials:** Electrical conduction examples
- **Gmsh Documentation:** https://gmsh.info/doc/texinfo/gmsh.html
- **2D Sheet Resistance:** https://en.wikipedia.org/wiki/Sheet_resistance
- **Copper Properties:** https://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity
- **PCB Trace Resistance:** IPC-2221 standards

## Next Steps

1. **Run `pdn_geometric.py`** and visualize results in ParaView
2. **Modify resistor widths** (0.05-0.5 mm) and observe how resistance changes
3. **Change resistor lengths** and verify R ∝ L relationship
4. **Add a third resistor** with intermediate width (0.15 mm)
5. **Compare analytical calculations** to FEM results
6. **Explore current density** variations with geometry
7. **Try thermal coupling** (advanced: temperature-dependent conductivity)

## Summary

This example demonstrates the **fundamental relationship between geometry and resistance**:
- Narrow traces = high resistance
- Wide traces = low resistance
- Same material throughout (copper)
- Resistance comes purely from geometry!

**Key Takeaway:** You don't need special materials to create resistors on a PCB. Just make a trace narrow enough, and it becomes a resistor. This is how current-sense resistors, fuses, and heating elements work!

---

**Happy exploring!**
