#!/usr/bin/env python3
"""
PDN Analysis - Option 2: Position-Dependent Conductivity
Models power traces, ground return, and resistive loads in a unified mesh.
"""
import os
import sys
import numpy as np
import gmsh
import subprocess

# Geometry parameters (mm)
pcb_width = 50.0
pcb_height = 40.0

reg_trace_width = 3.5
reg_trace_length = 15.0
bus_width = 2.5
bus_length = 30.0
bus_x_start = reg_trace_length
branch_width = 1.5
branch_length = 10.0

load1_pos = (bus_x_start + 10.0, pcb_height/2 + branch_length)
load2_pos = (bus_x_start + 20.0, pcb_height/2 + branch_length)
load3_pos = (bus_x_start + 10.0, pcb_height/2 - branch_length)

ground_y = 5.0
ground_height = 4.0
load_resistor_width = 1.0

# Material
copper_thickness = 0.035
copper_conductivity = 5.96e7
sigma_copper = copper_conductivity * copper_thickness / 1000.0

# Load resistances
load1_R = 6.5
load2_R = 10.83
load3_R = 16.25

# Calculate load conductivities
resistor_bottom = ground_y + ground_height - 1.5
load1_height = load1_pos[1] + 1.5 - resistor_bottom
load2_height = load2_pos[1] + 1.5 - resistor_bottom  
load3_height = load3_pos[1] + 1.5 - resistor_bottom

sigma_load1 = (load1_height/1000) / (load1_R * load_resistor_width/1000)
sigma_load2 = (load2_height/1000) / (load2_R * load_resistor_width/1000)
sigma_load3 = (load3_height/1000) / (load3_R * load_resistor_width/1000)

# Very low conductivity for insulating regions
sigma_insulator = sigma_copper * 1e-6

supply_voltage = 3.3
ground_voltage = 0.0

print("="*70)
print("PDN Analysis - Option 2: Position-Dependent Conductivity")
print("="*70)
print(f"\nConductivities:")
print(f"  Copper (traces): {sigma_copper:.2e} S")
print(f"  Load 1 (R={load1_R:.1f}Ω, {load1_height:.1f}mm): {sigma_load1:.2e} S")
print(f"  Load 2 (R={load2_R:.1f}Ω, {load2_height:.1f}mm): {sigma_load2:.2e} S")
print(f"  Load 3 (R={load3_R:.1f}Ω, {load3_height:.1f}mm): {sigma_load3:.2e} S")
print(f"  Insulator (background): {sigma_insulator:.2e} S")

# Create mesh
gmsh.initialize()
gmsh.model.add("pdn")
domain = gmsh.model.occ.addRectangle(0, 0, 0, pcb_width, pcb_height)
gmsh.model.occ.synchronize()

gmsh.model.addPhysicalGroup(2, [domain], tag=1)
gmsh.model.setPhysicalName(2, 1, "PDN")

# Boundaries
all_boundaries = gmsh.model.getBoundary([(2, domain)], oriented=False)
vdd_boundary = []
gnd_boundary = []

for dim, tag in all_boundaries:
    bbox = gmsh.model.getBoundingBox(dim, tag)
    x_min, y_min, x_max, y_max = bbox[0], bbox[1], bbox[3], bbox[4]
    y_center = (y_min + y_max) / 2
    
    # VDD: left edge, central portion
    if x_min < 0.1 and abs(y_center - pcb_height/2) < reg_trace_width/2:
        vdd_boundary.append(tag)
    # GND: left edge, ground region
    elif x_min < 0.1 and ground_y < y_center < ground_y + ground_height:
        gnd_boundary.append(tag)

if vdd_boundary:
    gmsh.model.addPhysicalGroup(1, vdd_boundary, tag=101)
    gmsh.model.setPhysicalName(1, 101, "VDD")
    print(f"\n✓ VDD boundary: {len(vdd_boundary)} edge(s)")

if gnd_boundary:
    gmsh.model.addPhysicalGroup(1, gnd_boundary, tag=102)
    gmsh.model.setPhysicalName(1, 102, "GND")
    print(f"✓ GND boundary: {len(gnd_boundary)} edge(s)")

gmsh.model.occ.synchronize()

# Mesh with refinement
print("\nGenerating mesh...")
gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 1.5)

# Refine in PDN regions
for y in [pcb_height/2, ground_y + ground_height/2]:
    for x in np.linspace(0, pcb_width, 20):
        nearby = gmsh.model.getEntitiesInBoundingBox(x-1, y-3, -0.1, x+1, y+3, 0.1, dim=0)
        if nearby:
            gmsh.model.mesh.setSize(nearby, 0.4)

gmsh.model.mesh.generate(2)
print(f"  Nodes: {len(gmsh.model.mesh.getNodes()[0])}")

output_dir = "simulation"
os.makedirs(output_dir, exist_ok=True)
mesh_file = os.path.join(output_dir, "pdn_option2.msh")
gmsh.write(mesh_file)
gmsh.finalize()

# Convert to Elmer
subprocess.run(["ElmerGrid", "14", "2", mesh_file, "-out", output_dir], 
               check=True, capture_output=True)

# Create Fortran user function for position-dependent conductivity
fortran_code = f"""
FUNCTION Conductivity(Model, n, x) RESULT(sigma)
  USE DefUtils
  IMPLICIT NONE
  TYPE(Model_t) :: Model
  INTEGER :: n
  REAL(KIND=dp) :: x, sigma
  REAL(KIND=dp) :: cx, cy
  
  cx = Model % Nodes % x(n)
  cy = Model % Nodes % y(n)
  
  sigma = {sigma_insulator}d0  ! Default: insulator
  
  ! Regulator trace: x<{reg_trace_length}, y near {pcb_height/2}
  IF (cx < {reg_trace_length:.1f}d0 .AND. &
      ABS(cy - {pcb_height/2:.1f}d0) < {reg_trace_width/2:.2f}d0) THEN
    sigma = {sigma_copper}d0
  END IF
  
  ! Main bus: x>{bus_x_start}, y near {pcb_height/2}
  IF (cx > {bus_x_start:.1f}d0 .AND. cx < {bus_x_start + bus_length:.1f}d0 .AND. &
      ABS(cy - {pcb_height/2:.1f}d0) < {bus_width/2:.2f}d0) THEN
    sigma = {sigma_copper}d0
  END IF
  
  ! Branch 1: x near {load1_pos[0]}, y>{pcb_height/2}
  IF (ABS(cx - {load1_pos[0]:.1f}d0) < {branch_width/2:.2f}d0 .AND. &
      cy > {pcb_height/2:.1f}d0 .AND. cy < {load1_pos[1]:.1f}d0) THEN
    sigma = {sigma_copper}d0
  END IF
  
  ! Branch 2
  IF (ABS(cx - {load2_pos[0]:.1f}d0) < {branch_width/2:.2f}d0 .AND. &
      cy > {pcb_height/2:.1f}d0 .AND. cy < {load2_pos[1]:.1f}d0) THEN
    sigma = {sigma_copper}d0
  END IF
  
  ! Branch 3
  IF (ABS(cx - {load3_pos[0]:.1f}d0) < {branch_width/2:.2f}d0 .AND. &
      cy < {pcb_height/2:.1f}d0 .AND. cy > {load3_pos[1]:.1f}d0) THEN
    sigma = {sigma_copper}d0
  END IF
  
  ! Ground return
  IF (cx > 2.0d0 .AND. cy > {ground_y:.1f}d0 .AND. cy < {ground_y + ground_height:.1f}d0) THEN
    sigma = {sigma_copper}d0
  END IF
  
  ! Load 1 resistor
  IF (ABS(cx - {load1_pos[0]:.1f}d0) < {load_resistor_width/2:.2f}d0 .AND. &
      cy > {resistor_bottom:.1f}d0 .AND. cy < {load1_pos[1] + 1.5:.1f}d0) THEN
    sigma = {sigma_load1}d0
  END IF
  
  ! Load 2 resistor
  IF (ABS(cx - {load2_pos[0]:.1f}d0) < {load_resistor_width/2:.2f}d0 .AND. &
      cy > {resistor_bottom:.1f}d0 .AND. cy < {load2_pos[1] + 1.5:.1f}d0) THEN
    sigma = {sigma_load2}d0
  END IF
  
  ! Load 3 resistor
  IF (ABS(cx - {load3_pos[0]:.1f}d0) < {load_resistor_width/2:.2f}d0 .AND. &
      cy > {resistor_bottom:.1f}d0 .AND. cy < {load3_pos[1] + 1.5:.1f}d0) THEN
    sigma = {sigma_load3}d0
  END IF
  
END FUNCTION Conductivity
"""

func_file = os.path.join(output_dir, "Conductivity.F90")
with open(func_file, 'w') as f:
    f.write(fortran_code)

print("\nCompiling user function...")
compile_result = subprocess.run(
    ["elmerf90", "-o", "Conductivity.so", "Conductivity.F90"],
    cwd=output_dir,
    capture_output=True,
    text=True
)

if compile_result.returncode != 0:
    print("✗ Compilation failed:")
    print(compile_result.stderr)
    sys.exit(1)
else:
    print("✓ User function compiled")

# Create SIF
sif = f"""
Header
  Mesh DB "." "."
End

Simulation
  Coordinate System = "Cartesian 2D"
  Simulation Type = "Steady State"
  Steady State Max Iterations = 1
  Post File = "pdn_option2.vtu"
End

Body 1
  Target Bodies(1) = 1
  Equation = 1
  Material = 1
End

Material 1
  Name = "PositionDependent"
  Electric Conductivity = Variable Coordinate
    Real Procedure "Conductivity" "Conductivity"
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
  Calculate Joule Heating = True
  
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

sif_file = os.path.join(output_dir, "pdn_option2.sif")
with open(sif_file, 'w') as f:
    f.write(sif)

# Run solver
print("\nRunning ElmerSolver...")
result = subprocess.run(
    ["ElmerSolver", "pdn_option2.sif"],
    cwd=output_dir,
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✓ Simulation completed!")
    import glob
    vtu_files = glob.glob(os.path.join(output_dir, "pdn_option2*.vtu"))
    if vtu_files:
        print(f"\n✓ Results: {vtu_files[0]}")
        print("\nVisualize with: paraview", vtu_files[0])
        print("\nYou should now see:")
        print("  - Power distribution network structure")
        print("  - Voltage drops in narrow traces")
        print("  - Current flow through load resistors")
        print("  - Realistic PDN behavior!")
else:
    print("✗ Solver failed:")
    print(result.stdout[-500:])

print("\n" + "="*70)
