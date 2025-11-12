#!/usr/bin/env python3
"""
Simplest Possible Field Dump Example
=====================================

Minimal example to create valid VTK files for ParaView.
Based on working OpenEMS examples.
"""

import os
import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS

# Units and frequency
unit = 1e-3  # mm
f0 = 2e9     # 2 GHz

# Simple box (all dimensions in mm, converted by unit)
size_x = 40
size_y = 40
size_z = 60

# Simulation directory
sim_path = os.path.abspath('simple_field_dump')
os.makedirs(sim_path, exist_ok=True)

print("=" * 60)
print("Simple Field Dump Example")
print("=" * 60)

# Initialize
FDTD = openEMS()
FDTD.SetGaussExcite(f0, f0/2)
FDTD.SetBoundaryCond(['PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8'])
FDTD.SetNumberOfTimeSteps(5000)

CSX = ContinuousStructure()
FDTD.SetCSX(CSX)

# Create a simple mesh - explicit lines in base units (mm here)
mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)

# Define mesh with good resolution (1mm)
mesh.AddLine('x', np.linspace(0, size_x, 41))  # 41 points = 1mm spacing
mesh.AddLine('y', np.linspace(0, size_y, 41))
mesh.AddLine('z', np.linspace(0, size_z, 61))

print(f"Mesh: {41} x {41} x {61} cells")
print(f"Box size: {size_x} x {size_y} x {size_z} mm")

# Simple excitation - Gaussian pulse in center
# IMPORTANT: Use mesh coordinates (NOT SI units!)
exc = CSX.AddExcitation('excite', exc_type=0, exc_val=[1, 0, 0])
exc.AddBox(
    start=[size_x/2, 0, size_z/3],
    stop=[size_x/2, size_y, size_z/3]
)

print(f"Excitation at z={size_z/3} mm")

# VTK dump - smaller region to reduce file size
# Dump in the center third of the box
# IMPORTANT: Use mesh coordinates (same as mesh.AddLine), NOT SI units!
dump_margin = 5  # mm margin from edges

Et_dump = CSX.AddDump('Et', dump_type=0, file_type=0, dump_mode=2)
Et_dump.AddBox(
    start=[dump_margin, dump_margin, dump_margin],
    stop=[size_x - dump_margin, size_y - dump_margin, size_z - dump_margin]
)

print(f"VTK dump region: {dump_margin} to {size_x-dump_margin} mm in each direction")
print(f"This creates a {size_x-2*dump_margin} x {size_y-2*dump_margin} x {size_z-2*dump_margin} mm volume")

# Write and run
CSX.Write2XML(os.path.join(sim_path, 'geometry.xml'))

print("\nRunning simulation...")
print("Expected: ~2-3 minutes, ~500 VTK files")
FDTD.Run(sim_path, cleanup=True, verbose=2)

print("\n" + "=" * 60)
print("Complete!")
print("=" * 60)

# Count files
vtk_files = [f for f in os.listdir(sim_path) if f.endswith('.vtr')]
print(f"\n✓ Created {len(vtk_files)} VTK files in {sim_path}/")
print("\nTo view:")
print("  1. Open ParaView")
print("  2. File → Open → Select all Et_*.vtr")
print("  3. Click Apply")
print("  4. Color by: E-field")
print("  5. Play animation")
print("=" * 60)
