#!/usr/bin/env python3
"""
KiCAD STEP to ElmerFEM Workflow Example
========================================

This script demonstrates how to import a STEP file exported from KiCAD,
create a mesh with Gmsh, and run a DC current flow simulation in ElmerFEM.

Workflow:
  1. Import STEP geometry from KiCAD
  2. Identify copper layers and assign materials
  3. Generate FEM mesh with Gmsh
  4. Create ElmerFEM solver configuration
  5. Run simulation
  6. Export VTU for ParaView visualization

Use Case: Power distribution network analysis, IR drop, current density

Prerequisites:
  - Export your KiCAD PCB as STEP (File → Export → STEP)
  - Name it 'pcb.step' or modify the filename below
"""

import os
import sys
import subprocess
import gmsh

# ============================================================================
# Configuration
# ============================================================================

# STEP file from KiCAD (update this path to your exported file)
step_file = "pcb_example.step"  # Change to your STEP file path

# Simulation output directory
sim_path = os.path.abspath('step_elmerfem_sim')
os.makedirs(sim_path, exist_ok=True)

# Material properties
copper_conductivity = 5.96e7  # S/m (copper at 20°C)

# Boundary conditions (voltages)
input_voltage = 5.0   # Volts
output_voltage = 0.0  # Volts (ground)

# Mesh resolution (smaller = finer mesh = more accurate but slower)
mesh_size = 0.5  # mm

print("=" * 70)
print("KiCAD STEP → Gmsh → ElmerFEM Workflow")
print("=" * 70)

# ============================================================================
# Step 1: Import STEP Geometry
# ============================================================================

print("\n[1/6] Importing STEP geometry...")

# Check if STEP file exists
if not os.path.exists(step_file):
    print(f"\n❌ ERROR: STEP file not found: {step_file}")
    print("\nTo create a STEP file:")
    print("  1. Open your PCB in KiCAD PCB Editor")
    print("  2. File → Export → STEP")
    print("  3. Save as 'pcb_example.step' in this directory")
    print("\nOr create a simple example:")
    print("  See create_simple_step_example.py")
    sys.exit(1)

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)

# Import STEP file
try:
    gmsh.merge(step_file)
    print(f"  ✓ Imported: {step_file}")
except Exception as e:
    print(f"  ❌ Failed to import STEP file: {e}")
    print("\n  Gmsh requires OpenCASCADE support to read STEP files.")
    print("  Check: gmsh --version (should show 'Built with OpenCASCADE')")
    gmsh.finalize()
    sys.exit(1)

gmsh.model.geo.synchronize()

# ============================================================================
# Step 2: Identify and Tag Geometry
# ============================================================================

print("\n[2/6] Analyzing geometry...")

# Get all surfaces in the model
surfaces = gmsh.model.getEntities(dim=2)
print(f"  Found {len(surfaces)} surfaces in STEP file")

# NOTE: KiCAD STEP export creates surfaces for each copper layer
# In a real workflow, you would identify which surfaces are:
#   - Copper traces (conductors)
#   - Dielectric substrate
#   - Air regions
#
# This is typically done by:
#   1. Inspecting surface positions/heights
#   2. Using Gmsh GUI to select surfaces interactively
#   3. Pre-labeling in KiCAD using different STEP exports per layer

# For this example, we'll assume a simple 2-layer board:
# - Top layer traces are at z ≈ 1.6mm (substrate height)
# - Bottom layer traces are at z ≈ 0mm

# Get bounding boxes of all surfaces to identify layers
print("\n  Analyzing surface heights:")
top_surfaces = []
bottom_surfaces = []

for dim, tag in surfaces:
    bbox = gmsh.model.getBoundingBox(dim, tag)
    # bbox = [xmin, ymin, zmin, xmax, ymax, zmax]
    z_center = (bbox[2] + bbox[5]) / 2

    if z_center > 1.0:  # Likely top layer
        top_surfaces.append(tag)
        print(f"    Surface {tag}: z = {z_center:.3f} mm (Top Layer)")
    else:  # Likely bottom layer
        bottom_surfaces.append(tag)
        print(f"    Surface {tag}: z = {z_center:.3f} mm (Bottom Layer)")

# Create physical groups for materials
if top_surfaces:
    pg_top = gmsh.model.addPhysicalGroup(2, top_surfaces, tag=1)
    gmsh.model.setPhysicalName(2, 1, "TopCopper")
    print(f"\n  ✓ Created physical group 'TopCopper' with {len(top_surfaces)} surfaces")

if bottom_surfaces:
    pg_bottom = gmsh.model.addPhysicalGroup(2, bottom_surfaces, tag=2)
    gmsh.model.setPhysicalName(2, 2, "BottomCopper")
    print(f"  ✓ Created physical group 'BottomCopper' with {len(bottom_surfaces)} surfaces")

# For boundary conditions, we need to identify edges (lines) where voltage is applied
# This is manual in real workflow - you'd use Gmsh GUI or coordinates to select
print("\n  Note: Boundary conditions (voltage contacts) must be defined manually")
print("        based on your specific PCB geometry.")

# ============================================================================
# Step 3: Generate Mesh
# ============================================================================

print("\n[3/6] Generating mesh...")

# Set mesh size
gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size * 0.5)
gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size * 2.0)
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)

# Generate 2D mesh
gmsh.model.mesh.generate(2)

# Get mesh statistics
nodes = gmsh.model.mesh.getNodes()
print(f"  ✓ Generated mesh with {len(nodes[0])} nodes")

# Write mesh file
mesh_file = os.path.join(sim_path, "mesh.msh")
gmsh.write(mesh_file)
print(f"  ✓ Saved mesh: {mesh_file}")

gmsh.finalize()

# ============================================================================
# Step 4: Convert Mesh to ElmerFEM Format
# ============================================================================

print("\n[4/6] Converting mesh to ElmerFEM format...")

result = subprocess.run(
    ["ElmerGrid", "14", "2", mesh_file, "-out", sim_path],
    capture_output=True,
    text=True,
    timeout=60
)

if result.returncode == 0:
    print("  ✓ Mesh converted successfully")
else:
    print("  ❌ Mesh conversion failed")
    print(result.stderr)
    sys.exit(1)

# ============================================================================
# Step 5: Create ElmerFEM Solver Configuration
# ============================================================================

print("\n[5/6] Creating ElmerFEM solver configuration...")

# NOTE: This SIF assumes you have defined boundary conditions
# In a real workflow, you need to identify which boundaries correspond to
# voltage input/output based on your PCB design

sif_content = """
Header
  Mesh DB "." "."
End

Simulation
  Coordinate System = Cartesian 3D
  Simulation Type = Steady State
  Steady State Max Iterations = 1
  Post File = "step_result.vtu"
End

! Conductor body (copper traces)
Body 1
  Equation = 1
  Material = 1
End

Equation 1
  Active Solvers(2) = 1 2
End

! Copper material
Material 1
  Electric Conductivity = {copper_conductivity}
End

! Electrostatic current solver
Solver 1
  Equation = Stat Current Solver
  Procedure = "StatCurrentSolve" "StatCurrentSolver"
  Variable = Potential

  Calculate Electric Field = True
  Calculate Current Density = True
  Calculate Joule Heating = True

  ! Export computed fields to VTU
  Exported Variable 1 = -dofs 3 Electric Field
  Exported Variable 2 = -dofs 3 Current Density

  ! Use direct solver for guaranteed convergence
  Linear System Solver = Direct
  Linear System Direct Method = UMFPack

  Steady State Convergence Tolerance = 1.0e-5
End

! Result output
Solver 2
  Exec Solver = After Timestep
  Equation = "ResultOutput"
  Procedure = "ResultOutputSolve" "ResultOutputSolver"
  Output File Name = "step_result"
  Vtu Format = Logical True
  Save Geometry Ids = Logical True
End

! NOTE: Boundary conditions must be customized for your specific geometry
! The boundary numbers depend on how Gmsh numbered the edges in your STEP file
!
! To find boundary numbers:
!   1. Open mesh in ElmerGUI
!   2. View → Mesh → Boundary Mesh
!   3. Identify which boundaries correspond to voltage contacts
!
! Example boundary conditions (commented out - customize for your PCB):

! Boundary Condition 1
!   Target Boundaries(1) = 10  ! Update boundary number
!   Potential = {input_voltage}
! End

! Boundary Condition 2
!   Target Boundaries(1) = 20  ! Update boundary number
!   Potential = {output_voltage}
! End

! For this demonstration, the solver will run but produce trivial results
! without proper boundary conditions
""".format(
    copper_conductivity=copper_conductivity,
    input_voltage=input_voltage,
    output_voltage=output_voltage
)

sif_file = os.path.join(sim_path, "case.sif")
with open(sif_file, 'w') as f:
    f.write(sif_content)

print("  ✓ Created solver configuration: case.sif")
print("\n  ⚠ WARNING: Boundary conditions are NOT set in this template!")
print("             You must edit case.sif and add proper boundary conditions")
print("             based on your PCB geometry.")

# ============================================================================
# Step 6: Run ElmerFEM (will succeed but give trivial results without BCs)
# ============================================================================

print("\n[6/6] Running ElmerSolver...")
print("  (Note: Results will be trivial without boundary conditions)")

result = subprocess.run(
    ["ElmerSolver", "case.sif"],
    cwd=sim_path,
    capture_output=True,
    text=True,
    timeout=120
)

if "ELMER SOLVER FINISHED" in result.stdout or "ALL DONE" in result.stdout:
    print("  ✓ Solver completed")

    vtu_files = [f for f in os.listdir(sim_path) if f.endswith('.vtu')]
    if vtu_files:
        vtu_file = vtu_files[0]
        file_size = os.path.getsize(os.path.join(sim_path, vtu_file))
        print(f"  ✓ Created: {vtu_file} ({file_size} bytes)")
else:
    print("  ⚠ Check solver output for warnings:")
    print(result.stdout[-1000:])

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 70)
print("Workflow Complete!")
print("=" * 70)

print(f"\nOutput directory: {sim_path}/")
print("\nFiles created:")
print("  - mesh.msh (Gmsh mesh)")
print("  - case.sif (ElmerFEM solver config)")
print("  - step_result*.vtu (Simulation results)")

print("\n" + "=" * 70)
print("IMPORTANT: Next Steps to Get Useful Results")
print("=" * 70)

print("""
This script successfully imported STEP geometry and ran ElmerFEM,
but to get meaningful current flow results, you need to:

1. **Identify Boundary Conditions:**
   - Open the mesh in ElmerGUI or Gmsh
   - Find which boundaries correspond to your voltage contacts
   - Note the boundary numbers

2. **Edit case.sif:**
   - Uncomment and update the Boundary Condition sections
   - Set correct boundary numbers for voltage input/output

3. **Re-run ElmerSolver:**
   cd {sim_path}
   ElmerSolver case.sif

4. **Visualize in ParaView:**
   - Open step_result*.vtu
   - Color by: potential, current density, electric field
   - Analyze voltage drop and current distribution

Alternative Approach:
---------------------
For simpler workflow, consider manually creating geometry in Gmsh
instead of importing complex STEP files. See the ElmerFEM examples
in /workspace/elmerfem-examples/ for working examples.
""".format(sim_path=sim_path))

print("=" * 70)
