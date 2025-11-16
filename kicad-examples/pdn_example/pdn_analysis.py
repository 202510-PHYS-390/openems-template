#!/usr/bin/env python3
"""
Power Distribution Network (PDN) Analysis using ElmerFEM

This example simulates a realistic PCB power distribution network with:
- 3.3V power input from voltage regulator
- Multiple load points (ICs drawing current)
- Power traces of varying widths
- Ground return path
- Analysis of voltage drop (IR drop), current density, and power dissipation

Use case: Verify that voltage drop across the PDN stays within spec (e.g., < 50 mV)
"""

import os
import sys
import numpy as np

try:
    import gmsh
    import meshio
except ImportError:
    print("ERROR: gmsh or meshio not installed!")
    print("Install with: pip3 install gmsh meshio")
    sys.exit(1)

# ==============================================================================
# GEOMETRY PARAMETERS (all in mm)
# ==============================================================================

# PCB dimensions
pcb_width = 50.0   # mm
pcb_height = 40.0  # mm

# Power trace from regulator to main bus (wide trace)
reg_trace_width = 3.0    # mm (wide for low resistance)
reg_trace_length = 15.0  # mm

# Main power bus (distributes to loads)
bus_width = 2.0          # mm
bus_length = 30.0        # mm
bus_x_start = reg_trace_length

# Branch traces to loads (narrower)
branch_width = 1.0       # mm
branch_length = 10.0     # mm

# Load positions (x, y) - representing IC locations
load1_pos = (bus_x_start + 10.0, pcb_height/2 + branch_length)
load2_pos = (bus_x_start + 20.0, pcb_height/2 + branch_length)
load3_pos = (bus_x_start + 10.0, pcb_height/2 - branch_length)

# Copper thickness
copper_thickness = 0.035  # mm (1 oz copper = 35 um)

# Ground plane (simplified - parallel to power trace)
ground_width = 5.0       # mm
ground_length = 45.0     # mm

# ==============================================================================
# ELECTRICAL PARAMETERS
# ==============================================================================

# Material properties
copper_conductivity = 5.96e7  # S/m (copper at 20°C)

# Operating conditions
supply_voltage = 3.3  # V (at regulator output)
ground_voltage = 0.0  # V

# Load currents (representing IC current consumption)
load1_current = 0.5   # A (500 mA)
load2_current = 0.3   # A (300 mA)
load3_current = 0.2   # A (200 mA)

total_current = load1_current + load2_current + load3_current  # 1.0 A total

# Design requirement
max_voltage_drop = 0.05  # V (50 mV max IR drop spec)

# ==============================================================================
# MESH PARAMETERS
# ==============================================================================

mesh_size_trace = 0.5    # mm (fine mesh on traces)
mesh_size_load = 0.2     # mm (very fine at load points)
mesh_size_general = 2.0  # mm (coarse elsewhere)

# ==============================================================================
# GEOMETRY CREATION
# ==============================================================================

print("=" * 70)
print("PDN Analysis - Power Distribution Network Simulation")
print("=" * 70)
print(f"\nGeometry:")
print(f"  PCB: {pcb_width} x {pcb_height} mm")
print(f"  Copper thickness: {copper_thickness} mm ({copper_thickness*1000:.1f} um)")
print(f"\nElectrical:")
print(f"  Supply voltage: {supply_voltage} V")
print(f"  Total current: {total_current} A")
print(f"  Load 1: {load1_current} A at {load1_pos}")
print(f"  Load 2: {load2_current} A at {load2_pos}")
print(f"  Load 3: {load3_current} A at {load3_pos}")
print(f"  Max allowed voltage drop: {max_voltage_drop*1000} mV")
print()

gmsh.initialize()
gmsh.model.add("pdn")

# Factory for 2D geometry (extruded to 3D later if needed)
# For this example, we'll use 2D simulation (thickness included in conductivity scaling)

# Create regulator trace (from VDD input to main bus)
reg_trace = gmsh.model.occ.addRectangle(
    0, pcb_height/2 - reg_trace_width/2,  # x, y (centered vertically)
    0,                                      # z
    reg_trace_length, reg_trace_width      # dx, dy
)

# Create main power bus (horizontal distribution)
main_bus = gmsh.model.occ.addRectangle(
    bus_x_start, pcb_height/2 - bus_width/2,
    0,
    bus_length, bus_width
)

# Create branch traces to loads
branch1 = gmsh.model.occ.addRectangle(
    bus_x_start + 10.0 - branch_width/2, pcb_height/2,
    0,
    branch_width, branch_length
)

branch2 = gmsh.model.occ.addRectangle(
    bus_x_start + 20.0 - branch_width/2, pcb_height/2,
    0,
    branch_width, branch_length
)

branch3 = gmsh.model.occ.addRectangle(
    bus_x_start + 10.0 - branch_width/2, pcb_height/2 - branch_length,
    0,
    branch_width, branch_length
)

# Create load pads (small copper areas where ICs connect)
load_pad_size = 0.5  # mm
load1_pad = gmsh.model.occ.addRectangle(
    load1_pos[0] - load_pad_size/2, load1_pos[1] - load_pad_size/2,
    0,
    load_pad_size, load_pad_size
)

load2_pad = gmsh.model.occ.addRectangle(
    load2_pos[0] - load_pad_size/2, load2_pos[1] - load_pad_size/2,
    0,
    load_pad_size, load_pad_size
)

load3_pad = gmsh.model.occ.addRectangle(
    load3_pos[0] - load_pad_size/2, load3_pos[1] - load_pad_size/2,
    0,
    load_pad_size, load_pad_size
)

# Fuse all copper traces into single conductor
copper_traces = gmsh.model.occ.fuse(
    [(2, reg_trace)],
    [(2, main_bus), (2, branch1), (2, branch2), (2, branch3),
     (2, load1_pad), (2, load2_pad), (2, load3_pad)]
)[0]

# NOTE: For this simplified PDN analysis, we model only the power distribution network
# Ground return path is implicit - we'll apply ground BC at load points
# This shows voltage drop (IR drop) in the power distribution traces

gmsh.model.occ.synchronize()

# ==============================================================================
# PHYSICAL GROUPS (for boundary conditions and material assignment)
# ==============================================================================

# Power distribution network (single conductor)
gmsh.model.addPhysicalGroup(2, [copper_traces[0][1]], tag=1)
gmsh.model.setPhysicalName(2, 1, "PowerNet")

# ==============================================================================
# BOUNDARY IDENTIFICATION (Critical for ElmerFEM!)
# ==============================================================================

# Get all boundary edges of power network
all_boundaries = gmsh.model.getBoundary([(2, copper_traces[0][1])], oriented=False)

# Identify specific boundaries by position
# VDD Input: left edge of regulator trace (x ≈ 0, y around pcb_height/2)
# Ground: at load point positions (top of load pads)

vdd_boundary = []
load1_boundary = []
load2_boundary = []
load3_boundary = []

# Find VDD input boundary (left edge of power trace, x ≈ 0)
for boundary in all_boundaries:
    dim, tag = boundary
    bbox = gmsh.model.getBoundingBox(dim, tag)
    x_min, y_min, z_min, x_max, y_max, z_max = bbox
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2

    # VDD Input: left edge (x ≈ 0) near center height
    if x_min < 0.1 and abs(y_center - pcb_height/2) < reg_trace_width:
        vdd_boundary.append(tag)

    # Load 1: near load1_pos
    elif abs(x_center - load1_pos[0]) < load_pad_size and abs(y_center - load1_pos[1]) < load_pad_size:
        # Top edge of load pad
        if y_max > load1_pos[1] + load_pad_size * 0.4:
            load1_boundary.append(tag)

    # Load 2: near load2_pos
    elif abs(x_center - load2_pos[0]) < load_pad_size and abs(y_center - load2_pos[1]) < load_pad_size:
        if y_max > load2_pos[1] + load_pad_size * 0.4:
            load2_boundary.append(tag)

    # Load 3: near load3_pos
    elif abs(x_center - load3_pos[0]) < load_pad_size and abs(y_center - load3_pos[1]) < load_pad_size:
        # Bottom edge of load pad
        if y_min < load3_pos[1] - load_pad_size * 0.4:
            load3_boundary.append(tag)

# Create physical groups for boundaries
if vdd_boundary:
    gmsh.model.addPhysicalGroup(1, vdd_boundary, tag=101)
    gmsh.model.setPhysicalName(1, 101, "VDD_Input")
    print(f"✓ VDD input boundary identified: {len(vdd_boundary)} edges")

if load1_boundary:
    gmsh.model.addPhysicalGroup(1, load1_boundary, tag=102)
    gmsh.model.setPhysicalName(1, 102, "Load1_GND")
    print(f"✓ Load 1 ground boundary: {len(load1_boundary)} edges")

if load2_boundary:
    gmsh.model.addPhysicalGroup(1, load2_boundary, tag=103)
    gmsh.model.setPhysicalName(1, 103, "Load2_GND")
    print(f"✓ Load 2 ground boundary: {len(load2_boundary)} edges")

if load3_boundary:
    gmsh.model.addPhysicalGroup(1, load3_boundary, tag=104)
    gmsh.model.setPhysicalName(1, 104, "Load3_GND")
    print(f"✓ Load 3 ground boundary: {len(load3_boundary)} edges")

gmsh.model.occ.synchronize()

# ==============================================================================
# MESHING
# ==============================================================================

print("Generating mesh...")

# Set mesh sizes
gmsh.model.mesh.setSize(gmsh.model.getEntities(0), mesh_size_general)

# Refine mesh on power traces
for entity in gmsh.model.getEntitiesInBoundingBox(
    -0.1, -0.1, -0.1,
    pcb_width, pcb_height, 0.1,
    dim=2
):
    gmsh.model.mesh.setSize(
        gmsh.model.getBoundary([entity], oriented=False),
        mesh_size_trace
    )

# Very fine mesh at load points
for load_x, load_y in [load1_pos, load2_pos, load3_pos]:
    points_near_load = gmsh.model.getEntitiesInBoundingBox(
        load_x - 1.0, load_y - 1.0, -0.1,
        load_x + 1.0, load_y + 1.0, 0.1,
        dim=0
    )
    gmsh.model.mesh.setSize(points_near_load, mesh_size_load)

gmsh.model.mesh.generate(2)

# Get mesh statistics
num_nodes = len(gmsh.model.mesh.getNodes()[0])
num_elements = len(gmsh.model.mesh.getElements()[2][1])
print(f"  Nodes: {num_nodes}")
print(f"  Elements: {num_elements}")

# ==============================================================================
# EXPORT MESH
# ==============================================================================

output_dir = "simulation"
os.makedirs(output_dir, exist_ok=True)

mesh_file = os.path.join(output_dir, "pdn.msh")
gmsh.write(mesh_file)
print(f"\nMesh written to: {mesh_file}")

gmsh.finalize()

# Convert to ElmerFEM format
print("\nConverting mesh to Elmer format...")
mesh = meshio.read(mesh_file)
meshio.write(
    os.path.join(output_dir, "pdn.msh"),  # ElmerGrid will read this
    mesh,
    file_format="gmsh22",
    binary=False
)

# ==============================================================================
# ELMERFEM SOLVER INPUT FILE (SIF)
# ==============================================================================

print("Creating ElmerFEM solver input file...")

# Calculate effective conductivity (2D simulation with thickness scaling)
# sigma_eff = sigma * thickness (for 2D current flow with thickness)
sigma_eff = copper_conductivity * copper_thickness / 1000.0  # Convert mm to m

sif_content = f"""! Power Distribution Network (PDN) Analysis
! DC current flow simulation

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

  Solver Input File = "pdn.sif"
  Post File = "pdn.vtu"
  Output File = "pdn.dat"
End

Constants
  Permittivity Of Vacuum = 8.8542e-12
End

! ============================================================================
! BODIES (Materials)
! ============================================================================

Body 1
  Name = "PowerNet"
  Target Bodies(1) = 1
  Equation = 1
  Material = 1
End

! ============================================================================
! MATERIAL PROPERTIES
! ============================================================================

Material 1
  Name = "Copper"
  ! Effective conductivity for 2D simulation with thickness
  Electric Conductivity = Real {sigma_eff}
End

! ============================================================================
! EQUATION
! ============================================================================

Equation 1
  Name = "StaticCurrent"
  Active Solvers(2) = 1 2
End

! ============================================================================
! SOLVER - Static Current Conduction
! ============================================================================

Solver 1
  Equation = "Stat Current Solver"
  Procedure = "StatCurrentSolve" "StatCurrentSolver"
  Variable = "Potential"
  Variable DOFs = 1

  Calculate Volume Current = True
  Calculate Electric Conductivity = True
  Calculate Electric Field = True
  Calculate Electric Energy = True
  Calculate Joule Heating = True
  Calculate Current Density = True

  ! Direct solver for guaranteed convergence
  Linear System Solver = "Direct"
  Linear System Direct Method = "UMFPack"

  Steady State Convergence Tolerance = 1.0e-6

  Nonlinear System Convergence Tolerance = 1.0e-8
  Nonlinear System Max Iterations = 20
  Nonlinear System Relaxation Factor = 1.0
End

! ============================================================================
! SOLVER 2 - Compute Current Density (J = -sigma * grad(V))
! ============================================================================

Solver 2
  Exec Solver = After Timestep
  Equation = "Flux Compute"
  Procedure = "FluxSolver" "FluxSolver"

  ! Compute flux (current density) from potential gradient
  ! J = -sigma * grad(V)
  Flux Coefficient = String "Electric Conductivity"
  Flux Variable = String "Potential"

  ! Output fields
  Calculate Flux = Logical True
  Calculate Flux Abs = Logical True
  Calculate Grad = Logical True
  Calculate Grad Abs = Logical True

  Target Variable = String "Current Density"

  Linear System Solver = "Iterative"
  Linear System Iterative Method = "BiCGStab"
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1.0e-8
  Linear System Preconditioning = ILU0
  Linear System Residual Output = 10
End

! ============================================================================
! BOUNDARY CONDITIONS
! ============================================================================

! VDD Input (voltage source from regulator)
Boundary Condition 1
  Name = "VDD_Input"
  Target Boundaries(1) = 101
  Potential = {supply_voltage}
End

! Ground at Load 1 (IC current sink)
Boundary Condition 2
  Name = "Load1_GND"
  Target Boundaries(1) = 102
  Potential = {ground_voltage}
End

! Ground at Load 2 (IC current sink)
Boundary Condition 3
  Name = "Load2_GND"
  Target Boundaries(1) = 103
  Potential = {ground_voltage}
End

! Ground at Load 3 (IC current sink)
Boundary Condition 4
  Name = "Load3_GND"
  Target Boundaries(1) = 104
  Potential = {ground_voltage}
End

! Note: Current distribution among loads is determined by trace resistance
! Narrower traces will carry less current (higher resistance)
"""

sif_file = os.path.join(output_dir, "pdn.sif")
with open(sif_file, 'w') as f:
    f.write(sif_content)
print(f"Solver input file written to: {sif_file}")

# ==============================================================================
# CREATE MESH DIRECTORY STRUCTURE FOR ELMER
# ==============================================================================

print("\nRunning ElmerGrid to convert mesh...")
import subprocess

elmer_mesh_dir = os.path.join(output_dir, "pdn")
os.makedirs(elmer_mesh_dir, exist_ok=True)

# Run ElmerGrid to convert Gmsh mesh to Elmer format
subprocess.run([
    "ElmerGrid", "14", "2",  # 14 = Gmsh format, 2 = Elmer format
    mesh_file,
    "-out", output_dir
], check=True)

print(f"Elmer mesh created in: {output_dir}")

# ==============================================================================
# RUN ELMERFEM SOLVER
# ==============================================================================

print("\n" + "=" * 70)
print("Running ElmerSolver...")
print("=" * 70 + "\n")

solver_log = os.path.join(output_dir, "solver.log")
with open(solver_log, 'w') as log_file:
    result = subprocess.run(
        ["ElmerSolver", "pdn.sif"],
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

print("\n" + "=" * 70)
print("Post-Processing Results")
print("=" * 70)

# ElmerFEM adds timestep suffix to VTU files
import glob
vtu_files = glob.glob(os.path.join(output_dir, "pdn*.vtu"))
if vtu_files:
    vtu_file = vtu_files[0]  # Use the first (should be only) VTU file
elif os.path.exists(os.path.join(output_dir, "pdn.vtu")):
    vtu_file = os.path.join(output_dir, "pdn.vtu")
else:
    vtu_file = None

if vtu_file and os.path.exists(vtu_file):
    print(f"\n✓ Results exported to: {vtu_file}")
    print("\nVisualization in ParaView:")
    print("  1. Open pdn.vtu in ParaView")
    print("  2. Color by 'Potential' to see voltage distribution")
    print("  3. Color by 'current density' to see current flow")
    print("  4. Color by 'joule heating' to see power dissipation")
    print("\nFields available:")
    print("  - Potential (V) - voltage at each point")
    print("  - Electric Field (V/m)")
    print("  - Current Density (A/m²)")
    print("  - Joule Heating (W/m³)")

    # Try to extract voltage drop estimate
    try:
        mesh_result = meshio.read(vtu_file)
        if 'potential' in mesh_result.point_data:
            potential = mesh_result.point_data['potential']
            v_max = np.max(potential)
            v_min = np.min(potential)
            v_drop = v_max - v_min

            print(f"\nVoltage Analysis:")
            print(f"  Maximum voltage: {v_max:.4f} V")
            print(f"  Minimum voltage: {v_min:.4f} V")
            print(f"  Total voltage drop: {v_drop*1000:.2f} mV")

            if v_drop > max_voltage_drop:
                print(f"  ⚠ WARNING: Voltage drop ({v_drop*1000:.1f} mV) exceeds spec ({max_voltage_drop*1000:.1f} mV)!")
                print(f"    Consider: wider traces, thicker copper, or lower resistance")
            else:
                print(f"  ✓ Voltage drop within spec ({max_voltage_drop*1000:.1f} mV)")
    except Exception as e:
        print(f"\nNote: Could not automatically extract voltage data: {e}")
        print("Use ParaView for detailed analysis.")
else:
    print(f"\n✗ VTU file not found: {vtu_file}")

print("\n" + "=" * 70)
print("PDN Analysis Complete")
print("=" * 70)
print("\nNext steps:")
print("  1. Open simulation/pdn.vtu in ParaView")
print("  2. Analyze voltage drop across the power distribution network")
print("  3. Identify current crowding in narrow traces")
print("  4. Optimize trace widths based on results")
print(f"  5. Iterate design to meet {max_voltage_drop*1000} mV voltage drop spec")
print()
