#!/usr/bin/env python3
"""
PDN with geometric resistors - resistors are just narrow copper traces!
Simple, robust, and demonstrates the concept clearly.
"""
import os
import sys
import numpy as np
import gmsh
import subprocess

# Geometry (mm)
pcb_width = 50.0
pcb_height = 40.0

# Power traces
reg_trace_width = 3.5
bus_width = 2.5
branch_width = 1.5

# Load positions (two parallel resistive loads)
# These mark where branches connect to the top of resistors
load1_pos = (25.0, 15.0)  # Moved up to make resistors taller
load2_pos = (35.0, 15.0)

# Ground
ground_y = 5.0
ground_height = 4.0

# Resistor dimensions - narrow enough to show effect, wide enough to mesh properly
# R_2D = L / (σ_eff * w) where σ_eff = 2086 S
resistor1_width = 0.2  # mm - 200 µm wide (lower resistance)
resistor2_width = 0.1  # mm - 100 µm wide (higher resistance, 2x current density)
resistor_length = 20.0  # mm

# Material (uniform copper everywhere!)
copper_thickness = 0.035  # mm
copper_conductivity = 5.96e7  # S/m
sigma_eff = copper_conductivity * copper_thickness / 1000.0

supply_voltage = 3.3
ground_voltage = 0.0

print("="*70)
print("PDN with Geometric Resistors")
print("="*70)
print(f"\nGeometry:")
print(f"  Power traces: {reg_trace_width}-{branch_width} mm wide")
print(f"  Load 1 resistor: {resistor1_width} mm wide × {resistor_length} mm long")
print(f"  Load 2 resistor: {resistor2_width} mm wide × {resistor_length} mm long")
print(f"  Ground return: {ground_height} mm tall")
print(f"\nMaterial: Uniform copper (σ = {sigma_eff:.2e} S)")
print(f"\nResistor resistance (approx):")
R1_approx = (resistor_length/1000) / (sigma_eff * resistor1_width/1000)
R2_approx = (resistor_length/1000) / (sigma_eff * resistor2_width/1000)
print(f"  R1 (0.2mm) ≈ {R1_approx:.3f} Ω")
print(f"  R2 (0.1mm) ≈ {R2_approx:.3f} Ω (2× higher resistance)")

gmsh.initialize()
gmsh.model.add("pdn_geo")

# Create power distribution network
print("\nBuilding geometry...")

# Regulator trace
reg = gmsh.model.occ.addRectangle(0, pcb_height/2 - reg_trace_width/2, 0,
                                   15, reg_trace_width)

# Main bus  
bus = gmsh.model.occ.addRectangle(15, pcb_height/2 - bus_width/2, 0,
                                   30, bus_width)

# Branches to loads (stop EXACTLY at load position, no overlap!)
branch1 = gmsh.model.occ.addRectangle(load1_pos[0] - branch_width/2, load1_pos[1], 0,
                                       branch_width, pcb_height/2 - load1_pos[1])

branch2 = gmsh.model.occ.addRectangle(load2_pos[0] - branch_width/2, load2_pos[1], 0,
                                       branch_width, pcb_height/2 - load2_pos[1])

# Fuse power network
power_net = gmsh.model.occ.fuse([(2, reg)],
                                 [(2, bus), (2, branch1), (2, branch2)])[0]

# Ground return - just main plane (no extra returns needed)
ground = gmsh.model.occ.addRectangle(2, ground_y, 0, 45, ground_height)

# Load resistors (NARROW vertical connectors with different widths)
# Positioned EXACTLY between ground and branch, no overlap!
resistor_bottom = ground_y + ground_height  # Exactly at top of ground
resistor_top = load1_pos[1]  # Exactly at bottom of branch
resistor_height = resistor_top - resistor_bottom

load1_res = gmsh.model.occ.addRectangle(
    load1_pos[0] - resistor1_width/2,
    resistor_bottom,
    0,
    resistor1_width,
    resistor_height
)

load2_res = gmsh.model.occ.addRectangle(
    load2_pos[0] - resistor2_width/2,
    resistor_bottom,
    0,
    resistor2_width,
    resistor_height
)

# Debug: Check resistor sizes before fuse
bbox1 = gmsh.model.occ.getBoundingBox(2, load1_res)
bbox2 = gmsh.model.occ.getBoundingBox(2, load2_res)
w1 = bbox1[3] - bbox1[0]
w2 = bbox2[3] - bbox2[0]
print(f"  Resistor 1 width before fuse: {w1:.4f} mm")
print(f"  Resistor 2 width before fuse: {w2:.4f} mm")

# Fuse everything into one connected conductor
all_parts = gmsh.model.occ.fuse(
    power_net,
    [(2, ground), (2, load1_res), (2, load2_res)]
)[0]

gmsh.model.occ.synchronize()

# One physical group for entire conductor
gmsh.model.addPhysicalGroup(2, [all_parts[0][1]], tag=1)
gmsh.model.setPhysicalName(2, 1, "Conductor")

# Boundaries
all_bounds = gmsh.model.getBoundary(all_parts, oriented=False)
vdd_boundary = []
gnd_boundary = []

for dim, tag in all_bounds:
    bbox = gmsh.model.getBoundingBox(dim, tag)
    x_min, y_min, x_max, y_max = bbox[0], bbox[1], bbox[3], bbox[4]
    y_center = (y_min + y_max) / 2
    
    # VDD: left edge at power net height
    if x_min < 0.1 and abs(y_center - pcb_height/2) < reg_trace_width/3:
        vdd_boundary.append(tag)
    # GND: left edge at ground height
    elif x_min < 3.0 and ground_y < y_center < ground_y + ground_height:
        gnd_boundary.append(tag)

if vdd_boundary:
    gmsh.model.addPhysicalGroup(1, vdd_boundary, tag=101)
    print(f"✓ VDD: {len(vdd_boundary)} edge(s)")

if gnd_boundary:
    gmsh.model.addPhysicalGroup(1, gnd_boundary, tag=102)
    print(f"✓ GND: {len(gnd_boundary)} edge(s)")

gmsh.model.occ.synchronize()

# Mesh - FINE in narrow resistors!
print("\nGenerating mesh...")
gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 1.0)  # Default

# Very fine mesh in narrow resistor regions
for load_pos in [load1_pos, load2_pos]:
    nearby = gmsh.model.getEntitiesInBoundingBox(
        load_pos[0] - 0.5, ground_y, -0.1, load_pos[0] + 0.5, 30, 0.1, dim=0)
    if nearby:
        gmsh.model.mesh.setSize(nearby, 0.05)  # 50 µm mesh!

gmsh.model.mesh.generate(2)
num_nodes = len(gmsh.model.mesh.getNodes()[0])
print(f"  Nodes: {num_nodes}")

output_dir = "simulation"
os.makedirs(output_dir, exist_ok=True)
mesh_file = os.path.join(output_dir, "pdn_geo.msh")
gmsh.write(mesh_file)
gmsh.finalize()

subprocess.run(["ElmerGrid", "14", "2", mesh_file, "-out", output_dir],
               check=True, capture_output=True)

# SIF with uniform material
sif = f"""
Header
  Mesh DB "." "."
End

Simulation
  Coordinate System = "Cartesian 2D"
  Simulation Type = "Steady State"
  Steady State Max Iterations = 1
  Post File = "pdn_geo.vtu"
End

Body 1
  Target Bodies(1) = 1
  Equation = 1
  Material = 1
End

Material 1
  Name = "Copper"
  Electric Conductivity = {sigma_eff}
End

Equation 1
  Active Solvers(2) = 1 2
End

Solver 1
  Equation = "StatCurrentSolver"
  Procedure = "StatCurrentSolve" "StatCurrentSolver"
  Variable = "Potential"

  Calculate Joule Heating = True

  Linear System Solver = "Direct"
  Linear System Direct Method = "UMFPack"
End

Solver 2
  Exec Solver = After Timestep
  Equation = "Flux Compute"
  Procedure = "FluxSolver" "FluxSolver"

  ! Compute current density: J = -sigma * grad(V)
  Flux Coefficient = String "Electric Conductivity"
  Flux Variable = String "Potential"

  Calculate Flux = Logical True
  Calculate Flux Abs = Logical True
  Calculate Grad = Logical True
  Calculate Grad Abs = Logical True

  Target Variable = String "Current Density"

  Linear System Solver = "Iterative"
  Linear System Iterative Method = "BiCGStab"
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1.0e-6
  Linear System Preconditioning = ILU0
  Linear System Residual Output = 10
End

Boundary Condition 1
  Target Boundaries(1) = 101
  Potential = {supply_voltage}
End

Boundary Condition 2
  Target Boundaries(1) = 102
  Potential = {ground_voltage}
End
"""

sif_file = os.path.join(output_dir, "pdn_geo.sif")
with open(sif_file, 'w') as f:
    f.write(sif)

print("\nRunning ElmerSolver...")
result = subprocess.run(["ElmerSolver", "pdn_geo.sif"],
                       cwd=output_dir, capture_output=True, text=True)

if result.returncode == 0:
    print("✓ Simulation completed!")
    import glob
    vtu = glob.glob(os.path.join(output_dir, "pdn_geo*.vtu"))
    if vtu:
        print(f"\n✓ Results: {vtu[0]}")
        print("\nVisualize: paraview", vtu[0])
        print("\nYou should see:")
        print("  - PDN structure (power traces + ground)")
        print("  - NARROW resistors (0.1mm wide)")
        print("  - Voltage drops in resistors")
        print("  - Current crowding in narrow regions")
else:
    print("✗ Failed:", result.stdout[-300:])

print("="*70)
