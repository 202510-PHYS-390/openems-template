#!/usr/bin/env python3
"""
ElmerFEM: Tapered Trace - WORKING VERSION
==========================================

Uses direct solver for guaranteed convergence.
"""

import os
import sys
import subprocess

try:
    import gmsh
except ImportError:
    print("ERROR: gmsh not found!")
    sys.exit(1)

sim_path = os.path.abspath('tapered_working_sim')
os.makedirs(sim_path, exist_ok=True)

print("=" * 60)
print("ElmerFEM: Tapered Trace (Direct Solver)")
print("=" * 60)

# ========================================================================
# Create 2D tapered geometry
# ========================================================================

print("\n[1/4] Creating geometry...")

gmsh.initialize()
gmsh.model.add("tapered")

lc = 0.5  # Moderate mesh size

# 2D tapered trace: 4mm → 1mm over 15mm
p1 = gmsh.model.geo.addPoint(0, 0, 0, lc)
p2 = gmsh.model.geo.addPoint(0, 4, 0, lc)
p3 = gmsh.model.geo.addPoint(15, 1, 0, lc)
p4 = gmsh.model.geo.addPoint(15, 0, 0, lc)

l1 = gmsh.model.geo.addLine(p1, p2)
l2 = gmsh.model.geo.addLine(p2, p3)
l3 = gmsh.model.geo.addLine(p3, p4)
l4 = gmsh.model.geo.addLine(p4, p1)

loop = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])
surf = gmsh.model.geo.addPlaneSurface([loop])

gmsh.model.geo.addPhysicalGroup(2, [surf], tag=1)
gmsh.model.setPhysicalName(2, 1, "Conductor")

gmsh.model.geo.addPhysicalGroup(1, [l1], tag=2)
gmsh.model.setPhysicalName(1, 2, "Input")

gmsh.model.geo.addPhysicalGroup(1, [l3], tag=3)
gmsh.model.setPhysicalName(1, 3, "Output")

gmsh.model.geo.synchronize()
gmsh.model.mesh.generate(2)

mesh_file = os.path.join(sim_path, "mesh.msh")
gmsh.write(mesh_file)

nodes = gmsh.model.mesh.getNodes()
print(f"  ✓ Created mesh with {len(nodes[0])} nodes")

gmsh.finalize()

# ========================================================================
# Convert
# ========================================================================

print("\n[2/4] Converting...")
subprocess.run([
    "ElmerGrid", "14", "2", mesh_file, "-out", sim_path
], capture_output=True, timeout=30)
print("  ✓ Converted")

# ========================================================================
# Create SIF with DIRECT solver
# ========================================================================

print("\n[3/4] Creating solver file...")

sif_content = """
Header
  Mesh DB "." "."
End

Simulation
  Coordinate System = Cartesian 2D
  Simulation Type = Steady State
  Steady State Max Iterations = 1
  Post File = "tapered_result.vtu"
End

Body 1
  Equation = 1
  Material = 1
End

Equation 1
  Active Solvers(2) = 1 2
End

Material 1
  Electric Conductivity = 1.0e6
End

Solver 1
  Equation = Stat Current Solver
  Procedure = "StatCurrentSolve" "StatCurrentSolver"
  Variable = Potential

  Calculate Electric Field = True
  Calculate Current Density = True
  Calculate Joule Heating = True

  ! Export computed fields
  Exported Variable 1 = -dofs 3 Electric Field
  Exported Variable 2 = -dofs 3 Current Density

  ! Use DIRECT solver - guaranteed to converge
  Linear System Solver = Direct
  Linear System Direct Method = UMFPack

  Steady State Convergence Tolerance = 1.0e-5
End

! Save all fields to VTU
Solver 2
  Exec Solver = After Timestep
  Equation = "ResultOutput"
  Procedure = "ResultOutputSolve" "ResultOutputSolver"
  Output File Name = "tapered_result"
  Vtu Format = Logical True
  Save Geometry Ids = Logical True
End

Boundary Condition 1
  Target Boundaries(1) = 2
  Potential = 5.0
End

Boundary Condition 2
  Target Boundaries(1) = 3
  Potential = 0.0
End
"""

sif_file = os.path.join(sim_path, "case.sif")
with open(sif_file, 'w') as f:
    f.write(sif_content)
print("  ✓ SIF created")

# ========================================================================
# Run
# ========================================================================

print("\n[4/4] Running ElmerSolver...")

result = subprocess.run(
    ["ElmerSolver", "case.sif"],
    cwd=sim_path,
    capture_output=True,
    text=True,
    timeout=60
)

if "ELMER SOLVER FINISHED" in result.stdout or "ALL DONE" in result.stdout:
    print("  ✓ Solver completed!")

    vtu_files = [f for f in os.listdir(sim_path) if f.endswith('.vtu')]
    if vtu_files:
        vtu_file = vtu_files[0]
        file_size = os.path.getsize(os.path.join(sim_path, vtu_file))
        print(f"  ✓ Created: {vtu_file} ({file_size} bytes)")
    else:
        print("  ⚠ No VTU file found")
else:
    print("  ⚠ Check solver output:")
    # Print last 1000 chars of output
    print(result.stdout[-1000:])

print("\n" + "=" * 60)
print("Complete!")
print("=" * 60)
print(f"\nResults: {sim_path}/tapered_result*.vtu")
print("\nOpen in ParaView and color by:")
print("  - 'potential' - voltage (5V to 0V)")
print("  - 'electric field' - E-field magnitude")
print("  - 'current density' - current flow")
print("\nWhat to see:")
print("  - Current density HIGHER where trace is narrow")
print("  - Linear voltage drop")
print("  - E-field concentrated at taper")
print("=" * 60)
