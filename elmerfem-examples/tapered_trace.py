#!/usr/bin/env python3
"""
ElmerFEM: Tapered PCB Trace - Current Density and E-Field
==========================================================

Models a copper trace that changes width, showing:
- Electric field distribution
- Current density distribution
- Voltage distribution

This demonstrates ElmerFEM for DC current flow analysis.
"""

import os
import sys
import subprocess
import numpy as np

# Check if running in container
try:
    import gmsh
    import meshio
except ImportError:
    print("ERROR: Required packages not found!")
    print("Make sure you're running in the ElmerFEM container")
    sys.exit(1)

# Simulation parameters (all in mm)
trace_length = 50.0      # Total length
trace_width_start = 5.0  # Wide end
trace_width_end = 1.0    # Narrow end
trace_thickness = 0.035  # Standard 1oz copper
substrate_thickness = 1.6

# Applied voltage
voltage_applied = 5.0    # 5V DC

# Create simulation directory
sim_path = os.path.abspath('tapered_trace_sim')
os.makedirs(sim_path, exist_ok=True)

print("=" * 60)
print("ElmerFEM: Tapered PCB Trace Analysis")
print("=" * 60)
print(f"\nTrace: {trace_width_start}mm → {trace_width_end}mm over {trace_length}mm")
print(f"Applied voltage: {voltage_applied}V")
print(f"Output directory: {sim_path}/")

# ========================================================================
# 1. Create Mesh with Gmsh
# ========================================================================

print("\n[1/4] Creating geometry with Gmsh...")

gmsh.initialize()
gmsh.model.add("tapered_trace")

# Mesh size
lc = 0.5  # Mesh characteristic length in mm

# Create tapered trace as a 3D box with varying width
# We'll create it as a lofted solid

# Bottom face (wide end)
p1 = gmsh.model.geo.addPoint(0, -trace_width_start/2, 0, lc)
p2 = gmsh.model.geo.addPoint(0, trace_width_start/2, 0, lc)
p3 = gmsh.model.geo.addPoint(0, trace_width_start/2, trace_thickness, lc)
p4 = gmsh.model.geo.addPoint(0, -trace_width_start/2, trace_thickness, lc)

l1 = gmsh.model.geo.addLine(p1, p2)
l2 = gmsh.model.geo.addLine(p2, p3)
l3 = gmsh.model.geo.addLine(p3, p4)
l4 = gmsh.model.geo.addLine(p4, p1)

face1 = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])
surf1 = gmsh.model.geo.addPlaneSurface([face1])

# Top face (narrow end)
p5 = gmsh.model.geo.addPoint(trace_length, -trace_width_end/2, 0, lc)
p6 = gmsh.model.geo.addPoint(trace_length, trace_width_end/2, 0, lc)
p7 = gmsh.model.geo.addPoint(trace_length, trace_width_end/2, trace_thickness, lc)
p8 = gmsh.model.geo.addPoint(trace_length, -trace_width_end/2, trace_thickness, lc)

l5 = gmsh.model.geo.addLine(p5, p6)
l6 = gmsh.model.geo.addLine(p6, p7)
l7 = gmsh.model.geo.addLine(p7, p8)
l8 = gmsh.model.geo.addLine(p8, p5)

face2 = gmsh.model.geo.addCurveLoop([l5, l6, l7, l8])
surf2 = gmsh.model.geo.addPlaneSurface([face2])

# Connect the two faces
l9 = gmsh.model.geo.addLine(p1, p5)
l10 = gmsh.model.geo.addLine(p2, p6)
l11 = gmsh.model.geo.addLine(p3, p7)
l12 = gmsh.model.geo.addLine(p4, p8)

# Side surfaces
side1_loop = gmsh.model.geo.addCurveLoop([l1, l10, -l5, -l9])
side1 = gmsh.model.geo.addPlaneSurface([side1_loop])

side2_loop = gmsh.model.geo.addCurveLoop([l2, l11, -l6, -l10])
side2 = gmsh.model.geo.addPlaneSurface([side2_loop])

side3_loop = gmsh.model.geo.addCurveLoop([l3, l12, -l7, -l11])
side3 = gmsh.model.geo.addPlaneSurface([side3_loop])

side4_loop = gmsh.model.geo.addCurveLoop([l4, l9, -l8, -l12])
side4 = gmsh.model.geo.addPlaneSurface([side4_loop])

# Create volume
shell = gmsh.model.geo.addSurfaceLoop([surf1, surf2, side1, side2, side3, side4])
volume = gmsh.model.geo.addVolume([shell])

# Physical groups for boundary conditions and material
gmsh.model.geo.addPhysicalGroup(3, [volume], tag=1)  # Copper volume
gmsh.model.setPhysicalName(3, 1, "Copper")

gmsh.model.geo.addPhysicalGroup(2, [surf1], tag=2)  # Input (wide end)
gmsh.model.setPhysicalName(2, 2, "Input")

gmsh.model.geo.addPhysicalGroup(2, [surf2], tag=3)  # Output (narrow end)
gmsh.model.setPhysicalName(2, 3, "Output")

gmsh.model.geo.synchronize()

# Generate mesh
gmsh.model.mesh.generate(3)

# Save mesh
mesh_file = os.path.join(sim_path, "trace.msh")
gmsh.write(mesh_file)

print(f"  ✓ Mesh created: {mesh_file}")

# Get mesh info
nodes = gmsh.model.mesh.getNodes()
elements = gmsh.model.mesh.getElements()
print(f"  Nodes: {len(nodes[0])}")
print(f"  Elements: {sum(len(e) for e in elements[1])}")

gmsh.finalize()

# ========================================================================
# 2. Convert mesh for ElmerFEM
# ========================================================================

print("\n[2/4] Converting mesh for ElmerFEM...")

# Use ElmerGrid to convert Gmsh mesh to Elmer format
elmergrid_cmd = [
    "ElmerGrid", "14", "2",
    mesh_file,
    "-out", sim_path
]

try:
    result = subprocess.run(elmergrid_cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print("  ✓ Mesh converted to Elmer format")
    else:
        print("  ⚠ ElmerGrid warning:", result.stderr)
except Exception as e:
    print(f"  ✗ ElmerGrid failed: {e}")
    sys.exit(1)

# ========================================================================
# 3. Create ElmerFEM Solver Input File (.sif)
# ========================================================================

print("\n[3/4] Creating ElmerFEM solver file...")

sif_content = f"""!
! ElmerFEM Solver Input File
! Tapered PCB Trace - Current Flow Analysis
!

Header
  Mesh DB "." "."
  Results Directory "."
End

Simulation
  Max Output Level = 5
  Coordinate System = Cartesian
  Simulation Type = Steady State
  Steady State Max Iterations = 1
  Output Intervals = 1
  Post File = "trace_results.vtu"
End

Constants
  Permittivity Of Vacuum = 8.8542e-12
End

Body 1
  Name = "Copper"
  Target Bodies(1) = 1
  Equation = 1
  Material = 1
End

Equation 1
  Name = "Current Conduction"
  Active Solvers(1) = 1
End

Material 1
  Name = "Copper"
  Electric Conductivity = 5.96e7  ! S/m (copper)
  Relative Permittivity = 1.0
End

Solver 1
  Equation = Stat Current Solver
  Procedure = "StatCurrentSolve" "StatCurrentSolver"
  Variable = Potential
  Variable DOFs = 1

  Calculate Volume Current = True
  Calculate Electric Field = True
  Calculate Electric Conductivity = True
  Calculate Joule Heating = True

  Linear System Solver = Iterative
  Linear System Iterative Method = BiCGStab
  Linear System Preconditioning = ILU0
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1.0e-8

  Nonlinear System Max Iterations = 1
  Nonlinear System Convergence Tolerance = 1.0e-6

  Steady State Convergence Tolerance = 1.0e-6
End

! Boundary Condition: Input (wide end) - Apply voltage
Boundary Condition 1
  Target Boundaries(1) = 2
  Name = "Input"
  Potential = {voltage_applied}
End

! Boundary Condition: Output (narrow end) - Ground
Boundary Condition 2
  Target Boundaries(1) = 3
  Name = "Output"
  Potential = 0.0
End
"""

sif_file = os.path.join(sim_path, "trace.sif")
with open(sif_file, 'w') as f:
    f.write(sif_content)

print(f"  ✓ Solver file created: {sif_file}")

# ========================================================================
# 4. Run ElmerSolver
# ========================================================================

print("\n[4/4] Running ElmerSolver...")
print("  (This may take 10-30 seconds...)")

solver_cmd = ["ElmerSolver", "trace.sif"]

try:
    result = subprocess.run(
        solver_cmd,
        cwd=sim_path,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode == 0:
        print("  ✓ Solver completed successfully!")

        # Check for output file
        vtu_file = os.path.join(sim_path, "trace_results.vtu")
        if os.path.exists(vtu_file):
            file_size = os.path.getsize(vtu_file)
            print(f"  ✓ Results file: trace_results.vtu ({file_size} bytes)")
        else:
            # Try alternative output name
            vtu_file = os.path.join(sim_path, "trace_results0001.vtu")
            if os.path.exists(vtu_file):
                file_size = os.path.getsize(vtu_file)
                print(f"  ✓ Results file: trace_results0001.vtu ({file_size} bytes)")
    else:
        print("  ⚠ Solver completed with warnings")
        print(result.stderr[:500])

except Exception as e:
    print(f"  ✗ Solver failed: {e}")
    sys.exit(1)

# ========================================================================
# Summary
# ========================================================================

print("\n" + "=" * 60)
print("Simulation Complete!")
print("=" * 60)
print(f"\nResults directory: {sim_path}/")
print("\nOutput files:")
print("  - trace_results*.vtu (ParaView visualization)")
print("  - trace.msh (Gmsh mesh)")
print("\nTo visualize in ParaView:")
print("  1. Open trace_results*.vtu file")
print("  2. Click Apply")
print("  3. Color by: 'Potential' (voltage)")
print("  4. Color by: 'electric field' (E-field)")
print("  5. Color by: 'current density' (J-field)")
print("\nWhat to observe:")
print("  - Voltage drop along trace")
print("  - Current crowding at narrow section")
print("  - Higher current density where trace is narrower")
print("  - Electric field concentration at width transition")
print("=" * 60)
