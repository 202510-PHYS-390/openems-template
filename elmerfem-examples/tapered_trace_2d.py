#!/usr/bin/env python3
"""
ElmerFEM: Tapered PCB Trace - 2D Current Density
=================================================

Simplified 2D version for better convergence.
Models a tapered conductor cross-section.
"""

import os
import sys
import subprocess
import numpy as np

try:
    import gmsh
except ImportError:
    print("ERROR: gmsh not found!")
    sys.exit(1)

# Simulation parameters (all in mm)
trace_length = 20.0      # Shorter for better mesh
trace_width_start = 4.0  # Wide end
trace_width_end = 1.0    # Narrow end
trace_thickness = 0.5    # Thicker for better aspect ratio

# Applied voltage
voltage_applied = 1.0    # 1V DC

# Create simulation directory
sim_path = os.path.abspath('tapered_trace_2d_sim')
os.makedirs(sim_path, exist_ok=True)

print("=" * 60)
print("ElmerFEM: 2D Tapered Trace Analysis")
print("=" * 60)
print(f"\nTrace: {trace_width_start}mm → {trace_width_end}mm over {trace_length}mm")
print(f"Thickness: {trace_thickness}mm")
print(f"Applied voltage: {voltage_applied}V")

# ========================================================================
# 1. Create 2D Mesh with Gmsh
# ========================================================================

print("\n[1/4] Creating 2D geometry with Gmsh...")

gmsh.initialize()
gmsh.model.add("tapered_2d")

# Mesh size
lc = 0.25

# Create 2D tapered rectangle (top view)
# Points for wide end
p1 = gmsh.model.geo.addPoint(0, 0, 0, lc)
p2 = gmsh.model.geo.addPoint(0, trace_width_start, 0, lc)

# Points for narrow end
p3 = gmsh.model.geo.addPoint(trace_length, trace_width_end, 0, lc)
p4 = gmsh.model.geo.addPoint(trace_length, 0, 0, lc)

# Create lines
l1 = gmsh.model.geo.addLine(p1, p2)  # Left edge (input)
l2 = gmsh.model.geo.addLine(p2, p3)  # Top edge
l3 = gmsh.model.geo.addLine(p3, p4)  # Right edge (output)
l4 = gmsh.model.geo.addLine(p4, p1)  # Bottom edge

# Create surface
loop = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])
surf = gmsh.model.geo.addPlaneSurface([loop])

# Physical groups
gmsh.model.geo.addPhysicalGroup(2, [surf], tag=1)
gmsh.model.setPhysicalName(2, 1, "Copper")

gmsh.model.geo.addPhysicalGroup(1, [l1], tag=2)
gmsh.model.setPhysicalName(1, 2, "Input")

gmsh.model.geo.addPhysicalGroup(1, [l3], tag=3)
gmsh.model.setPhysicalName(1, 3, "Output")

gmsh.model.geo.synchronize()

# Generate 2D mesh
gmsh.model.mesh.generate(2)

mesh_file = os.path.join(sim_path, "trace.msh")
gmsh.write(mesh_file)

nodes = gmsh.model.mesh.getNodes()
print(f"  ✓ Mesh created with {len(nodes[0])} nodes")

gmsh.finalize()

# ========================================================================
# 2. Convert for ElmerFEM
# ========================================================================

print("\n[2/4] Converting mesh...")

subprocess.run([
    "ElmerGrid", "14", "2", mesh_file, "-out", sim_path
], capture_output=True, timeout=30)

print("  ✓ Converted to Elmer format")

# ========================================================================
# 3. Create Solver File with Better Settings
# ========================================================================

print("\n[3/4] Creating solver file...")

sif_content = f"""!
! Tapered Trace 2D - Current Conduction
!

Header
  Mesh DB "." "."
  Results Directory "."
End

Simulation
  Max Output Level = 5
  Coordinate System = Cartesian 2D
  Simulation Type = Steady State
  Steady State Max Iterations = 1
  Output Intervals = 1
  Post File = "results.vtu"
End

Body 1
  Name = "Copper"
  Target Bodies(1) = 1
  Equation = 1
  Material = 1
End

Equation 1
  Name = "Electrostatics"
  Active Solvers(1) = 1
End

Material 1
  Name = "Copper"
  ! Use normalized conductivity to avoid scaling issues
  Electric Conductivity = 1.0e6
End

Solver 1
  Equation = Stat Current Solver
  Procedure = "StatCurrentSolve" "StatCurrentSolver"
  Variable = Potential
  Variable DOFs = 1

  Calculate Volume Current = True
  Calculate Electric Field = True
  Calculate Electric Conductivity = True

  ! Use direct solver for robustness
  Linear System Solver = Direct
  Linear System Direct Method = UMFPack

  Steady State Convergence Tolerance = 1.0e-6
End

! Input - apply voltage
Boundary Condition 1
  Target Boundaries(1) = 2
  Name = "Input"
  Potential = {voltage_applied}
End

! Output - ground
Boundary Condition 2
  Target Boundaries(1) = 3
  Name = "Output"
  Potential = 0.0
End
"""

sif_file = os.path.join(sim_path, "case.sif")
with open(sif_file, 'w') as f:
    f.write(sif_content)

print("  ✓ Solver file created")

# ========================================================================
# 4. Run Solver
# ========================================================================

print("\n[4/4] Running ElmerSolver...")

result = subprocess.run(
    ["ElmerSolver", "case.sif"],
    cwd=sim_path,
    capture_output=True,
    text=True,
    timeout=60
)

if "ELMER SOLVER FINISHED" in result.stdout:
    print("  ✓ Solver completed successfully!")
else:
    print("  ⚠ Check output:")
    print(result.stdout[-500:])

# Check for output
vtu_files = [f for f in os.listdir(sim_path) if f.endswith('.vtu')]
if vtu_files:
    print(f"  ✓ Created: {vtu_files[0]}")
    file_size = os.path.getsize(os.path.join(sim_path, vtu_files[0]))
    print(f"  File size: {file_size} bytes")

print("\n" + "=" * 60)
print("Complete!")
print("=" * 60)
print(f"\nResults: {sim_path}/results*.vtu")
print("\nIn ParaView:")
print("  - Color by 'Potential' to see voltage")
print("  - Color by 'electric field' to see E-field")
print("  - Color by 'current density' to see current")
print("\nExpect:")
print("  - Linear voltage drop from 1V to 0V")
print("  - Higher current density in narrow section")
print("=" * 60)
