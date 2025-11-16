#!/usr/bin/env python3
"""
PDN Analysis with Unified Mesh - Simple Version (Uniform Copper)
Shows voltage drop in power distribution network without explicit load resistors.
"""
import os
import sys
import numpy as np
import gmsh
import meshio
import subprocess

# ==============================================================================
# GEOMETRY PARAMETERS (mm)
# ==============================================================================

pcb_width = 50.0
pcb_height = 40.0

# Power trace dimensions (same as original)
reg_trace_width = 3.5
reg_trace_length = 15.0
bus_width = 2.5
bus_length = 30.0
bus_x_start = reg_trace_length
branch_width = 1.5
branch_length = 10.0

# Load positions (for visualization reference)
load1_pos = (bus_x_start + 10.0, pcb_height/2 + branch_length)
load2_pos = (bus_x_start + 20.0, pcb_height/2 + branch_length)
load3_pos = (bus_x_start + 10.0, pcb_height/2 - branch_length)

# Ground return
ground_y_offset = 5.0
ground_trace_width = 4.0
ground_trace_length = 45.0

# Material
copper_thickness = 0.035  # mm (1 oz copper)
copper_conductivity = 5.96e7  # S/m
sigma_eff_copper = copper_conductivity * copper_thickness / 1000.0

# Electrical
supply_voltage = 3.3
ground_voltage = 0.0

print("="*70)
print("PDN Analysis - Unified Mesh (Uniform Copper)")
print("="*70)
print(f"\nGeometry:")
print(f"  Regulator trace: {reg_trace_width} mm wide")
print(f"  Main bus: {bus_width} mm wide")
print(f"  Branch traces: {branch_width} mm wide")
print(f"  Ground return: {ground_trace_width} mm wide")
print(f"\nMaterial:")
print(f"  Copper conductivity: {sigma_eff_copper:.2e} S")
print(f"  (Effective 2D with {copper_thickness*1000:.0f} µm thickness)")
print()

# ==============================================================================
# CREATE UNIFIED MESH
# ==============================================================================

gmsh.initialize()
gmsh.model.add("pdn_unified")

# Create single unified domain
domain = gmsh.model.occ.addRectangle(0, 0, 0, pcb_width, pcb_height)
gmsh.model.occ.synchronize()

# Physical group for entire domain
gmsh.model.addPhysicalGroup(2, [domain], tag=1)
gmsh.model.setPhysicalName(2, 1, "PDN")

# ==============================================================================
# BOUNDARY CONDITIONS
# ==============================================================================

all_boundaries = gmsh.model.getBoundary([(2, domain)], oriented=False)

vdd_boundary = []
gnd_boundary = []

for dim, tag in all_boundaries:
    bbox = gmsh.model.getBoundingBox(dim, tag)
    x_min, y_min, z_min, x_max, y_max, z_max = bbox
    y_center = (y_min + y_max) / 2
    
    # VDD: left edge, central portion (avoid corners)
    if x_min < 0.1 and (pcb_height/3 < y_center < 2*pcb_height/3):
        vdd_boundary.append(tag)

    # GND: right edge, central portion (avoid corners)
    elif x_max > pcb_width - 0.1 and (pcb_height/3 < y_center < 2*pcb_height/3):
        gnd_boundary.append(tag)

if vdd_boundary:
    gmsh.model.addPhysicalGroup(1, vdd_boundary, tag=101)
    gmsh.model.setPhysicalName(1, 101, "VDD_Input")
    print(f"✓ VDD input: {len(vdd_boundary)} edge(s)")

if gnd_boundary:
    gmsh.model.addPhysicalGroup(1, gnd_boundary, tag=102)
    gmsh.model.setPhysicalName(1, 102, "Ground_Reference")
    print(f"✓ Ground reference: {len(gnd_boundary)} edge(s)")

if not vdd_boundary or not gnd_boundary:
    print("⚠ WARNING: Missing boundary conditions!")
    sys.exit(1)

gmsh.model.occ.synchronize()

# ==============================================================================
# MESHING
# ==============================================================================

print("\nGenerating mesh...")

# Default mesh size
gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 2.0)

# Refine mesh in power distribution region (where traces are)
for y in [pcb_height/2, ground_y_offset + ground_trace_width/2]:
    for x in range(0, int(pcb_width), 5):
        nearby = gmsh.model.getEntitiesInBoundingBox(
            x-1, y-5, -0.1, x+1, y+5, 0.1, dim=0
        )
        if nearby:
            gmsh.model.mesh.setSize(nearby, 0.5)

# Very fine mesh near load positions (for future load modeling)
for lx, ly in [load1_pos, load2_pos, load3_pos]:
    nearby = gmsh.model.getEntitiesInBoundingBox(
        lx-2, ly-2, -0.1, lx+2, ly+2, 0.1, dim=0
    )
    if nearby:
        gmsh.model.mesh.setSize(nearby, 0.3)

gmsh.model.mesh.generate(2)

num_nodes = len(gmsh.model.mesh.getNodes()[0])
num_elements = len(gmsh.model.mesh.getElements()[2][1])
print(f"  Nodes: {num_nodes}")
print(f"  Elements: {num_elements}")

# ==============================================================================
# EXPORT
# ==============================================================================

output_dir = "simulation"
os.makedirs(output_dir, exist_ok=True)

mesh_file = os.path.join(output_dir, "pdn_unified.msh")
gmsh.write(mesh_file)
print(f"\nMesh written to: {mesh_file}")

gmsh.finalize()

# Convert to Elmer format
print("Converting to Elmer format...")
subprocess.run(
    ["ElmerGrid", "14", "2", mesh_file, "-out", output_dir],
    check=True,
    capture_output=True
)

# ==============================================================================
# ELMERFEM SOLVER INPUT FILE (SIF)
# ==============================================================================

print("Creating ElmerFEM solver input file...")

sif_content = f"""! Power Distribution Network (PDN) Analysis
! Unified mesh with uniform copper conductivity

Header
  CHECK KEYWORDS Warn
  Mesh DB "." "."
  Include Path ""
  Results Directory "."
End

Simulation
  Max Output Level = 5
  Coordinate System = "Cartesian 2D"
  Coordinate Mapping(3) = 1 2 3

  Simulation Type = "Steady State"
  Steady State Max Iterations = 1
  Output Intervals = 1

  Solver Input File = "pdn_unified.sif"
  Post File = "pdn_unified.vtu"
  Output File = "pdn_unified.dat"
End

Constants
  Permittivity Of Vacuum = 8.8542e-12
End

! ============================================================================
! BODY (Single unified domain)
! ============================================================================

Body 1
  Name = "PDN"
  Target Bodies(1) = 1
  Equation = 1
  Material = 1
End

! ============================================================================
! MATERIAL (Uniform copper)
! ============================================================================

Material 1
  Name = "Copper"
  Electric Conductivity = Real {sigma_eff_copper}
End

! ============================================================================
! EQUATION
! ============================================================================

Equation 1
  Name = "StaticCurrent"
  Active Solvers(1) = 1
End

! ============================================================================
! SOLVER - Static Current Conduction
! ============================================================================

Solver 1
  Equation = "Stat Current Solver"
  Procedure = "StatCurrentSolve" "StatCurrentSolver"
  Variable = "Potential"
  Variable DOFs = 1

  Calculate Electric Field = True
  Calculate Current Density = True
  Calculate Joule Heating = True

  ! Direct solver for guaranteed convergence
  Linear System Solver = "Direct"
  Linear System Direct Method = "UMFPack"

  Steady State Convergence Tolerance = 1.0e-6

  Nonlinear System Convergence Tolerance = 1.0e-8
  Nonlinear System Max Iterations = 20
  Nonlinear System Relaxation Factor = 1.0
End

! ============================================================================
! BOUNDARY CONDITIONS
! ============================================================================

! VDD Input (3.3V power from regulator)
Boundary Condition 1
  Name = "VDD_Input"
  Target Boundaries(1) = 101
  Potential = {supply_voltage}
End

! Ground Reference (0V return path)
Boundary Condition 2
  Name = "Ground_Reference"
  Target Boundaries(1) = 102
  Potential = {ground_voltage}
End

! All other boundaries are natural BC (insulating, zero normal current)
"""

sif_file = os.path.join(output_dir, "pdn_unified.sif")
with open(sif_file, 'w') as f:
    f.write(sif_content)
print(f"Solver input file: {sif_file}")

# ==============================================================================
# RUN ELMERFEM SOLVER
# ==============================================================================

print("\n" + "="*70)
print("Running ElmerSolver...")
print("="*70 + "\n")

solver_log = os.path.join(output_dir, "solver.log")
with open(solver_log, 'w') as log_file:
    result = subprocess.run(
        ["ElmerSolver", "pdn_unified.sif"],
        cwd=output_dir,
        stdout=log_file,
        stderr=subprocess.STDOUT
    )

if result.returncode == 0:
    print("✓ Simulation completed successfully!")
else:
    print(f"✗ Simulation failed (exit code {result.returncode})")
    print(f"  Check log file: {solver_log}")
    sys.exit(1)

# ==============================================================================
# POST-PROCESSING
# ==============================================================================

print("\n" + "="*70)
print("Results")
print("="*70)

# Find VTU file
import glob
vtu_pattern1 = os.path.join(output_dir, "pdn_unified*.vtu")
vtu_pattern2 = os.path.join(output_dir, "simulation", "pdn_unified*.vtu")
vtu_files = glob.glob(vtu_pattern1) + glob.glob(vtu_pattern2)

if vtu_files:
    vtu_file = vtu_files[0]
    print(f"\n✓ Results: {vtu_file}")
    
    print("\nVisualization in ParaView:")
    print(f"  paraview {vtu_file}")
    print("\n  What to look for:")
    print("  1. Color by 'potential' - voltage distribution")
    print("  2. Red (3.3V) at VDD input, blue (0V) at ground")
    print("  3. Voltage drops along power traces (IR drop)")
    print("  4. Note: Load positions are at:")
    print(f"     - Load 1: ({load1_pos[0]:.1f}, {load1_pos[1]:.1f})")
    print(f"     - Load 2: ({load2_pos[0]:.1f}, {load2_pos[1]:.1f})")
    print(f"     - Load 3: ({load3_pos[0]:.1f}, {load3_pos[1]:.1f})")
    
    print("\n  Fields available:")
    print("  - Potential (V)")
    print("  - Electric Field (V/m)")
    print("  - Current Density (A/m²)")
    print("  - Joule Heating (W/m³)")
else:
    print(f"\n⚠ VTU file not found in {output_dir}/simulation/")

print("\n" + "="*70)
print("PDN Analysis Complete - Option 1 (Uniform Copper)")
print("="*70)
print("\nNOTE: This version uses uniform copper conductivity.")
print("Actual IC loads would draw current and create additional voltage drops.")
print("Run Option 2 for realistic load modeling with position-dependent conductivity.")
print()
