#!/usr/bin/env python3
"""
ElmerFEM: Simple Resistor Test
================================

Simplest possible test - rectangular conductor.
If this doesn't work, ElmerFEM solver has issues.
"""

import os
import sys
import subprocess

try:
    import gmsh
except ImportError:
    print("ERROR: gmsh not found!")
    sys.exit(1)

sim_path = os.path.abspath('simple_resistor_sim')
os.makedirs(sim_path, exist_ok=True)

print("=" * 60)
print("ElmerFEM: Simple Resistor Test")
print("=" * 60)

# ========================================================================
# 1. Create simplest possible 2D mesh
# ========================================================================

print("\n[1/4] Creating simple rectangle...")

gmsh.initialize()
gmsh.model.add("resistor")

lc = 1.0  # Coarse mesh for speed

# Simple 10mm x 2mm rectangle
p1 = gmsh.model.geo.addPoint(0, 0, 0, lc)
p2 = gmsh.model.geo.addPoint(0, 2, 0, lc)
p3 = gmsh.model.geo.addPoint(10, 2, 0, lc)
p4 = gmsh.model.geo.addPoint(10, 0, 0, lc)

l1 = gmsh.model.geo.addLine(p1, p2)
l2 = gmsh.model.geo.addLine(p2, p3)
l3 = gmsh.model.geo.addLine(p3, p4)
l4 = gmsh.model.geo.addLine(p4, p1)

loop = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])
surf = gmsh.model.geo.addPlaneSurface([loop])

gmsh.model.geo.addPhysicalGroup(2, [surf], tag=1)
gmsh.model.setPhysicalName(2, 1, "Conductor")

gmsh.model.geo.addPhysicalGroup(1, [l1], tag=2)
gmsh.model.setPhysicalName(1, 2, "Left")

gmsh.model.geo.addPhysicalGroup(1, [l3], tag=3)
gmsh.model.setPhysicalName(1, 3, "Right")

gmsh.model.geo.synchronize()
gmsh.model.mesh.generate(2)

mesh_file = os.path.join(sim_path, "mesh.msh")
gmsh.write(mesh_file)
print(f"  ✓ Created mesh")

gmsh.finalize()

# ========================================================================
# 2. Convert
# ========================================================================

print("\n[2/4] Converting...")
subprocess.run([
    "ElmerGrid", "14", "2", mesh_file, "-out", sim_path
], capture_output=True, timeout=30)
print("  ✓ Converted")

# ========================================================================
# 3. Minimal SIF file
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
  Post File = "result.vtu"
End

Body 1
  Equation = 1
  Material = 1
End

Equation 1
  Active Solvers(1) = 1
End

Material 1
  Electric Conductivity = 1.0
End

Solver 1
  Equation = Stat Current Solver
  Procedure = "StatCurrentSolve" "StatCurrentSolver"
  Variable = Potential

  Calculate Electric Field = True
  Calculate Current Density = True

  Linear System Solver = Iterative
  Linear System Iterative Method = BiCGStab
  Linear System Preconditioning = ILU1
  Linear System Max Iterations = 1000
  Linear System Convergence Tolerance = 1.0e-6
  Linear System Residual Output = 10

  Steady State Convergence Tolerance = 1.0e-5
End

Boundary Condition 1
  Target Boundaries(1) = 2
  Potential = 1.0
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
# 4. Run
# ========================================================================

print("\n[4/4] Running ElmerSolver...")
print("  (Showing full output for debugging)")
print("")

result = subprocess.run(
    ["ElmerSolver", "case.sif"],
    cwd=sim_path,
    text=True,
    timeout=60
)

print("")
if result.returncode == 0:
    print("  ✓ SUCCESS!")

    vtu_files = [f for f in os.listdir(sim_path) if f.endswith('.vtu')]
    if vtu_files:
        print(f"  ✓ Created: {vtu_files[0]}")
    else:
        print("  ⚠ No VTU file found")
else:
    print(f"  ✗ FAILED with return code {result.returncode}")

print("\n" + "=" * 60)
