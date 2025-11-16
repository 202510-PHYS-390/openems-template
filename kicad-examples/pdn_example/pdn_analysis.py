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

# Power trace from regulator to main bus
# Initial design - intentionally a bit narrow to create voltage drop issues!
reg_trace_width = 3.5    # mm (could be wider for lower drop)
reg_trace_length = 15.0  # mm

# Main power bus (distributes to loads)
bus_width = 2.5          # mm (moderate width - borderline for spec)
bus_length = 30.0        # mm
bus_x_start = reg_trace_length

# Branch traces to loads (narrower - likely needs widening)
branch_width = 1.5       # mm (narrow - primary bottleneck!)
branch_length = 10.0     # mm

# Load positions (x, y) - representing IC locations
load1_pos = (bus_x_start + 10.0, pcb_height/2 + branch_length)
load2_pos = (bus_x_start + 20.0, pcb_height/2 + branch_length)
load3_pos = (bus_x_start + 10.0, pcb_height/2 - branch_length)

# Load resistor dimensions (small pads representing IC equivalent resistance)
load_resistor_size = 1.0  # mm (small resistive region at each load)

# Copper thickness
copper_thickness = 0.035  # mm (1 oz copper = 35 um)

# Ground return path (wide, low-resistance return for current)
ground_trace_width = 4.0   # mm (wide ground return)
ground_trace_length = 45.0  # mm
ground_y_offset = 5.0       # mm (offset below power traces)

# ==============================================================================
# ELECTRICAL PARAMETERS
# ==============================================================================

# Material properties
copper_conductivity = 5.96e7  # S/m (copper at 20°C)

# Operating conditions
supply_voltage = 3.3  # V (at regulator output)
ground_voltage = 0.0  # V

# Load specifications (representing IC current consumption)
# Each IC has a desired voltage and current draw
# We'll model these as resistive loads: R = V_desired / I_desired
load1_voltage_target = 3.25  # V (allow 50 mV drop)
load1_current = 0.5   # A (500 mA)
load1_resistance = load1_voltage_target / load1_current  # 6.5 ohms

load2_voltage_target = 3.25  # V
load2_current = 0.3   # A (300 mA)
load2_resistance = load2_voltage_target / load2_current  # 10.83 ohms

load3_voltage_target = 3.25  # V
load3_current = 0.2   # A (200 mA)
load3_resistance = load3_voltage_target / load3_current  # 16.25 ohms

total_current = load1_current + load2_current + load3_current  # 1.0 A total

# Design requirement
max_voltage_drop = 0.05  # V (50 mV max IR drop spec)
# Note: Initial design with narrow traces will likely exceed this!
# Students should widen traces to meet spec.

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
print(f"  Regulator trace: {reg_trace_width} mm width")
print(f"  Main bus: {bus_width} mm width")
print(f"  Branch traces: {branch_width} mm width")
print(f"\nElectrical:")
print(f"  Supply voltage: {supply_voltage} V")
print(f"  Total current: {total_current} A")
print(f"  Load 1: {load1_current} A (R={load1_resistance:.2f} Ω) at {load1_pos}")
print(f"  Load 2: {load2_current} A (R={load2_resistance:.2f} Ω) at {load2_pos}")
print(f"  Load 3: {load3_current} A (R={load3_resistance:.2f} Ω) at {load3_pos}")
print(f"  Max allowed voltage drop: {max_voltage_drop*1000} mV")
print(f"\n⚠  Initial design uses narrow traces - voltage drop likely exceeds spec!")
print(f"  Challenge: Widen traces to meet {max_voltage_drop*1000} mV spec")
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

# Fuse all copper traces into single power conductor
copper_traces = gmsh.model.occ.fuse(
    [(2, reg_trace)],
    [(2, main_bus), (2, branch1), (2, branch2), (2, branch3),
     (2, load1_pad), (2, load2_pad), (2, load3_pad)]
)[0]

# ==============================================================================
# GROUND RETURN PATH
# ==============================================================================

# Create ground return trace (wide, low-resistance return path)
ground_return = gmsh.model.occ.addRectangle(
    2.0, ground_y_offset,  # x, y position
    0,
    ground_trace_length, ground_trace_width
)

# ==============================================================================
# RESISTIVE LOADS (IC equivalent resistance)
# ==============================================================================

# Vertical connection traces from load pads to ground return
# These act as resistive elements representing the IC loads
# IMPORTANT: Must overlap substantially with both power pads (top) and ground (bottom)

# Calculate resistor dimensions to ensure proper overlap
resistor_bottom = ground_y_offset + ground_trace_width - 1.5  # 1.5mm overlap with ground
resistor_top_load1 = load1_pos[1] + 1.5  # 1.5mm overlap with power pad
resistor_top_load2 = load2_pos[1] + 1.5
resistor_top_load3 = load3_pos[1] + 1.5

# Load 1 resistor (connects load1 pad to ground with guaranteed overlap)
load1_resistor = gmsh.model.occ.addRectangle(
    load1_pos[0] - load_resistor_size/2,
    resistor_bottom,
    0,
    load_resistor_size,
    resistor_top_load1 - resistor_bottom
)

# Load 2 resistor
load2_resistor = gmsh.model.occ.addRectangle(
    load2_pos[0] - load_resistor_size/2,
    resistor_bottom,
    0,
    load_resistor_size,
    resistor_top_load2 - resistor_bottom
)

# Load 3 resistor (connects downward from load3 to ground)
load3_resistor = gmsh.model.occ.addRectangle(
    load3_pos[0] - load_resistor_size/2,
    resistor_bottom,
    0,
    load_resistor_size,
    resistor_top_load3 - resistor_bottom
)

# Use fragment operation to keep all regions separate but connected
# This will split overlapping regions at interfaces
all_regions = gmsh.model.occ.fragment(
    [copper_traces[0], (2, ground_return)],
    [(2, load1_resistor), (2, load2_resistor), (2, load3_resistor)]
)

gmsh.model.occ.synchronize()

# After fragment, we need to identify which surfaces are which
# Get all 2D surfaces
all_surfaces = gmsh.model.getEntities(2)
print(f"\nTotal surfaces after fragment: {len(all_surfaces)}")

# Identify surfaces by their position
power_net_surfaces = []
ground_surfaces = []
load1_surfaces = []
load2_surfaces = []
load3_surfaces = []
unclassified_surfaces = []

for dim, tag in all_surfaces:
    bbox = gmsh.model.getBoundingBox(dim, tag)
    x_min, y_min, z_min, x_max, y_max, z_max = bbox
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min

    classified = False

    # Ground return: bottom region (y < 9.5)
    if y_max < ground_y_offset + ground_trace_width + 0.5:
        ground_surfaces.append(tag)
        classified = True
    # Load resistors: narrow regions near load positions
    # Load 3: x near 25, y between ground and middle (8-12 mm)
    elif abs(x_center - load3_pos[0]) < 2.0 and 8.0 < y_center < 12.0:
        load3_surfaces.append(tag)
        classified = True
    # Load 1: x near 25, y > 15 (upper region)
    elif abs(x_center - load1_pos[0]) < 2.0 and y_center > 15:
        load1_surfaces.append(tag)
        classified = True
    # Load 2: x near 35, y > 15 (upper region)
    elif abs(x_center - load2_pos[0]) < 2.0 and y_center > 15:
        load2_surfaces.append(tag)
        classified = True

    # Everything else in upper region is power network
    if not classified and y_center > ground_y_offset + ground_trace_width + 1.0:
        power_net_surfaces.append(tag)
        classified = True

    if not classified:
        unclassified_surfaces.append(tag)
        print(f"  Unclassified surface {tag}: center=({x_center:.1f}, {y_center:.1f}), size=({width:.1f} x {height:.1f})")

print(f"\nSurface classification:")
print(f"  Power network: {len(power_net_surfaces)} surfaces")
print(f"  Ground return: {len(ground_surfaces)} surfaces")
print(f"  Load 1 resistor: {len(load1_surfaces)} surfaces")
print(f"  Load 2 resistor: {len(load2_surfaces)} surfaces")
print(f"  Load 3 resistor: {len(load3_surfaces)} surfaces")
print(f"  Total: {len(power_net_surfaces) + len(ground_surfaces) + len(load1_surfaces) + len(load2_surfaces) + len(load3_surfaces)}/{len(all_surfaces)}")
if unclassified_surfaces:
    print(f"  ⚠ WARNING: {len(unclassified_surfaces)} unclassified!")
else:
    print(f"  ✓ All surfaces classified")

# ==============================================================================
# PHYSICAL GROUPS (for boundary conditions and material assignment)
# ==============================================================================

# Create physical groups from identified surfaces
if power_net_surfaces:
    gmsh.model.addPhysicalGroup(2, power_net_surfaces, tag=1)
    gmsh.model.setPhysicalName(2, 1, "PowerNet")

if ground_surfaces:
    gmsh.model.addPhysicalGroup(2, ground_surfaces, tag=2)
    gmsh.model.setPhysicalName(2, 2, "GroundReturn")

if load1_surfaces:
    gmsh.model.addPhysicalGroup(2, load1_surfaces, tag=3)
    gmsh.model.setPhysicalName(2, 3, "Load1_Resistor")

if load2_surfaces:
    gmsh.model.addPhysicalGroup(2, load2_surfaces, tag=4)
    gmsh.model.setPhysicalName(2, 4, "Load2_Resistor")

if load3_surfaces:
    gmsh.model.addPhysicalGroup(2, load3_surfaces, tag=5)
    gmsh.model.setPhysicalName(2, 5, "Load3_Resistor")

# ==============================================================================
# BOUNDARY IDENTIFICATION (Critical for ElmerFEM!)
# ==============================================================================

# Get all boundary edges from power and ground surfaces
power_boundaries = []
for surf_tag in power_net_surfaces:
    power_boundaries.extend(gmsh.model.getBoundary([(2, surf_tag)], oriented=False))

ground_boundaries = []
for surf_tag in ground_surfaces:
    ground_boundaries.extend(gmsh.model.getBoundary([(2, surf_tag)], oriented=False))

# Identify specific boundaries by position
# VDD Input: left edge of regulator trace (x ≈ 0, y around pcb_height/2)
# Ground Reference: left edge of ground return trace

vdd_boundary = []
ground_ref_boundary = []

# Find VDD input boundary (left edge of power trace, x ≈ 0)
for boundary in power_boundaries:
    dim, tag = boundary
    bbox = gmsh.model.getBoundingBox(dim, tag)
    x_min, y_min, z_min, x_max, y_max, z_max = bbox
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2

    # VDD Input: left edge (x ≈ 0) near center height
    # Avoid corners by restricting to central portion
    if x_min < 0.1 and abs(y_center - pcb_height/2) < reg_trace_width/2:
        if tag not in vdd_boundary:
            vdd_boundary.append(tag)

# Find ground reference boundary (left edge of ground return trace)
for boundary in ground_boundaries:
    dim, tag = boundary
    bbox = gmsh.model.getBoundingBox(dim, tag)
    x_min, y_min, z_min, x_max, y_max, z_max = bbox
    y_center = (bbox[1] + bbox[4]) / 2

    # Ground reference: left edge (x near 0), central portion only
    # Avoid corners to prevent current flow along top/bottom of ground plane
    if x_min < 3.0 and abs(y_center - (ground_y_offset + ground_trace_width/2)) < ground_trace_width/3:
        if tag not in ground_ref_boundary:
            ground_ref_boundary.append(tag)

# Create physical groups for boundaries
if vdd_boundary:
    gmsh.model.addPhysicalGroup(1, vdd_boundary, tag=101)
    gmsh.model.setPhysicalName(1, 101, "VDD_Input")
    print(f"✓ VDD input boundary identified: {len(vdd_boundary)} edges")

if ground_ref_boundary:
    gmsh.model.addPhysicalGroup(1, ground_ref_boundary, tag=102)
    gmsh.model.setPhysicalName(1, 102, "Ground_Reference")
    print(f"✓ Ground reference boundary: {len(ground_ref_boundary)} edges")

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
sigma_eff_copper = copper_conductivity * copper_thickness / 1000.0  # Convert mm to m

# Calculate conductivity for load resistors
# For 2D: R = L / (sigma_eff * width)
# So: sigma_eff = L / (R * width)

# Load resistor dimensions
load1_resistor_length = resistor_top_load1 - resistor_bottom  # mm
load2_resistor_length = resistor_top_load2 - resistor_bottom  # mm
load3_resistor_length = resistor_top_load3 - resistor_bottom  # mm

# Calculate required conductivity for each load resistor
# For 2D with thickness factored in: R = L[m] / (sigma_eff[S] * width[m])
# Therefore: sigma_eff = L[m] / (R[ohm] * width[m])

sigma_eff_load1 = (load1_resistor_length / 1000.0) / (load1_resistance * load_resistor_size / 1000.0)
sigma_eff_load2 = (load2_resistor_length / 1000.0) / (load2_resistance * load_resistor_size / 1000.0)
sigma_eff_load3 = (load3_resistor_length / 1000.0) / (load3_resistance * load_resistor_size / 1000.0)

print(f"\nCalculated conductivities:")
print(f"  Copper (power/ground): {sigma_eff_copper:.6e} S")
print(f"  Load 1 resistor ({load1_resistance:.2f} Ω): {sigma_eff_load1:.6e} S")
print(f"  Load 2 resistor ({load2_resistance:.2f} Ω): {sigma_eff_load2:.6e} S")
print(f"  Load 3 resistor ({load3_resistance:.2f} Ω): {sigma_eff_load3:.6e} S")

sif_content = f"""! Power Distribution Network (PDN) Analysis
! DC current flow simulation with realistic resistive loads

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

Body 2
  Name = "GroundReturn"
  Target Bodies(1) = 2
  Equation = 1
  Material = 1
End

Body 3
  Name = "Load1_Resistor"
  Target Bodies(1) = 3
  Equation = 1
  Material = 2
End

Body 4
  Name = "Load2_Resistor"
  Target Bodies(1) = 4
  Equation = 1
  Material = 3
End

Body 5
  Name = "Load3_Resistor"
  Target Bodies(1) = 5
  Equation = 1
  Material = 4
End

! ============================================================================
! MATERIAL PROPERTIES
! ============================================================================

Material 1
  Name = "Copper"
  ! Effective conductivity for 2D simulation with thickness
  Electric Conductivity = Real {sigma_eff_copper}
End

Material 2
  Name = "Load1_Resistance"
  ! Tuned conductivity to achieve {load1_resistance:.2f} ohm resistance
  Electric Conductivity = Real {sigma_eff_load1}
End

Material 3
  Name = "Load2_Resistance"
  ! Tuned conductivity to achieve {load2_resistance:.2f} ohm resistance
  Electric Conductivity = Real {sigma_eff_load2}
End

Material 4
  Name = "Load3_Resistance"
  ! Tuned conductivity to achieve {load3_resistance:.2f} ohm resistance
  Electric Conductivity = Real {sigma_eff_load3}
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

! VDD Input (voltage source from regulator at power net)
Boundary Condition 1
  Name = "VDD_Input"
  Target Boundaries(1) = 101
  Potential = {supply_voltage}
End

! Ground Reference (0V at ground return path)
Boundary Condition 2
  Name = "Ground_Reference"
  Target Boundaries(1) = 102
  Potential = {ground_voltage}
End

! Notes on circuit operation:
! - Current flows from VDD input (+3.3V) through power distribution network
! - Power reaches load pads via branch traces
! - Current flows through resistive load elements (representing ICs)
! - Current returns through ground return path to ground reference (0V)
! - Voltage drop in power traces determines voltage at each load
! - Load currents determined by: I = V_load / R_load
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
    print(f"\nVoltage Analysis:")
    print(f"  Note: Automatic analysis skipped due to VTU format")
    print(f"  Open {vtu_file} in ParaView to analyze:")
    print(f"    - Check voltage at VDD input (should be ~{supply_voltage} V)")
    print(f"    - Check voltage at each load point")
    print(f"    - Calculate IR drop = V_VDD - V_load")
    print(f"    - Goal: All loads should see < {max_voltage_drop*1000} mV drop")
    print(f"\n  Expected behavior with current design:")
    print(f"    - Narrow branches ({branch_width} mm) will show high resistance")
    print(f"    - Distant loads will have larger drops")
    print(f"    - Increase trace widths to reduce resistance and voltage drop")
else:
    print(f"\n✗ VTU file not found: {vtu_file}")

print("\n" + "=" * 70)
print("PDN Analysis Complete")
print("=" * 70)
print("\nNext steps:")
print("  1. Open simulation/pdn.vtu in ParaView")
print("  2. Color by 'potential' to see voltage distribution")
print("  3. Identify voltage drops in narrow traces")
print("  4. Analyze current density to find current crowding")
print(f"  5. If voltage drop > {max_voltage_drop*1000} mV, try these fixes:")
print("     - Increase reg_trace_width (currently {:.1f} mm)".format(reg_trace_width))
print("     - Increase bus_width (currently {:.1f} mm)".format(bus_width))
print("     - Increase branch_width (currently {:.1f} mm)".format(branch_width))
print("     - Increase copper_thickness (currently {:.0f} µm)".format(copper_thickness*1000))
print("  6. Re-run simulation after changes to verify improvement")
print("\nDesign Challenge:")
print(f"  Goal: Reduce voltage drop from current value to < {max_voltage_drop*1000} mV")
print("  Method: Systematically widen traces (start with narrowest branches)")
print("  Target: All loads receive > {load1_voltage_target} V (current draw unaffected)")
print()
