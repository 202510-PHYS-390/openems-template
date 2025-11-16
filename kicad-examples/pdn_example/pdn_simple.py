#!/usr/bin/env python3
"""
Simplified PDN with coordinate-based material assignment (no fragment operation)
"""
import os
import sys
import numpy as np
import gmsh
import meshio
import subprocess

# Geometry parameters
pcb_width = 50.0
pcb_height = 40.0

# Trace widths
reg_trace_width = 3.5
bus_width = 2.5
branch_width = 1.5
copper_thickness = 0.035  # mm

# Load parameters
load1_pos = (25.0, 30.0)
load2_pos = (35.0, 30.0)
load3_pos = (25.0, 10.0)

load1_resistance = 6.5
load2_resistance = 10.83
load3_resistance = 16.25

# Material
copper_conductivity = 5.96e7  # S/m
sigma_eff_copper = copper_conductivity * copper_thickness / 1000.0

# Supply
supply_voltage = 3.3
ground_voltage = 0.0

print("="*70)
print("Simplified PDN - Single Unified Mesh")
print("="*70)

# Create unified geometry - single rectangle covering everything
gmsh.initialize()
gmsh.model.add("pdn_simple")

# Create one big rectangle that includes everything
domain = gmsh.model.occ.addRectangle(0, 0, 0, pcb_width, pcb_height)

gmsh.model.occ.synchronize()

# Single physical group for the entire domain
gmsh.model.addPhysicalGroup(2, [domain], tag=1)
gmsh.model.setPhysicalName(2, 1, "PDN")

# Create boundaries for BCs
all_boundaries = gmsh.model.getBoundary([(2, domain)], oriented=False)

vdd_boundary = []
gnd_boundary = []

for dim, tag in all_boundaries:
    bbox = gmsh.model.getBoundingBox(dim, tag)
    x_min, y_min, z_min, x_max, y_max, z_max = bbox
    y_center = (y_min + y_max) / 2

    # VDD: left edge, central portion only (avoid corners!)
    # Only apply BC where y is in middle third of domain
    if x_min < 0.1 and (pcb_height/3 < y_center < 2*pcb_height/3):
        vdd_boundary.append(tag)
    # GND: right edge, central portion only (avoid corners!)
    elif x_max > pcb_width - 0.1 and (pcb_height/3 < y_center < 2*pcb_height/3):
        gnd_boundary.append(tag)

if vdd_boundary:
    gmsh.model.addPhysicalGroup(1, vdd_boundary, tag=101)
    gmsh.model.setPhysicalName(1, 101, "VDD")

if gnd_boundary:
    gmsh.model.addPhysicalGroup(1, gnd_boundary, tag=102)
    gmsh.model.setPhysicalName(1, 102, "GND")

gmsh.model.occ.synchronize()

# Mesh
gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 2.0)
gmsh.model.mesh.generate(2)

# Export
output_dir = "simulation"
os.makedirs(output_dir, exist_ok=True)
mesh_file = os.path.join(output_dir, "pdn_simple.msh")
gmsh.write(mesh_file)
print(f"\nMesh written to: {mesh_file}")
gmsh.finalize()

# Convert to Elmer
subprocess.run(["ElmerGrid", "14", "2", mesh_file, "-out", output_dir], check=True)

# Create SIF with coordinate-based conductivity
# In each point (x,y), assign conductivity based on what region it's in

sif = f"""
Header
  Mesh DB "." "."
End

Simulation
  Coordinate System = "Cartesian 2D"
  Simulation Type = "Steady State"
  Steady State Max Iterations = 1
  Post File = "pdn_simple.vtu"
End

Body 1
  Target Bodies(1) = 1
  Equation = 1
  Material = 1
End

! Simple constant conductivity for connectivity test
Material 1
  Name = "Copper"
  Electric Conductivity = Real {sigma_eff_copper}
End

Equation 1
  Active Solvers(1) = 1
End

Solver 1
  Equation = "StatCurrentSolver"
  Procedure = "StatCurrentSolve" "StatCurrentSolver"
  Variable = "Potential"
  
  Calculate Electric Field = True
  Calculate Current Density = True
  
  Linear System Solver = "Direct"
  Linear System Direct Method = "UMFPack"
  
  Steady State Convergence Tolerance = 1e-6
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

sif_file = os.path.join(output_dir, "pdn_simple.sif")
with open(sif_file, 'w') as f:
    f.write(sif)

print(f"SIF file: {sif_file}")
print("\n⚠  Note: This simplified version uses uniform conductivity")
print("   Full position-dependent conductivity requires MATC functions")
print("   For now, this tests basic connectivity")

# Run solver
print("\nRunning ElmerSolver...")
result = subprocess.run(
    ["ElmerSolver", "pdn_simple.sif"],
    cwd=output_dir,
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✓ Solver completed")
    print(f"✓ Results: {output_dir}/pdn_simple.vtu")
else:
    print(f"✗ Solver failed")
    print(result.stdout)
    print(result.stderr)

print("="*70)
