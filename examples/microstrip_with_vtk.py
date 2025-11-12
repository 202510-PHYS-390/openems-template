#!/usr/bin/env python3
"""
Microstrip with VTK Export for ParaView Visualization
======================================================

This example creates VTK files that can be viewed in ParaView
to visualize the electromagnetic fields.

Students can download VTK files and view them in ParaView on their laptops.
"""

import os
import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS

# Simulation parameters
unit = 1e-3  # units in mm
f_max = 10e9  # 10 GHz

# Substrate
substrate_width = 20.0   # mm
substrate_length = 40.0  # mm
substrate_height = 1.6   # mm
substrate_er = 4.3       # FR4

# Trace
trace_width = 3.0        # mm
trace_length = 30.0      # mm
trace_thickness = 0.035  # mm

# Simulation directory
sim_path = os.path.abspath('microstrip_vtk_sim')
os.makedirs(sim_path, exist_ok=True)

print("=" * 60)
print("Microstrip with VTK Export")
print("=" * 60)

# Initialize OpenEMS
FDTD = openEMS()
FDTD.SetGaussExcite(f_max/2, f_max/2)
FDTD.SetBoundaryCond(['PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8'])

# Setup CSXCAD geometry
CSX = ContinuousStructure()
FDTD.SetCSX(CSX)

print("\nCreating geometry...")

# Materials
substrate = CSX.AddMaterial('FR4', epsilon=substrate_er)
copper = CSX.AddMetal('copper')

# Substrate
# IMPORTANT: Use mesh coordinates (NOT SI units!)
substrate.AddBox(
    priority=0,
    start=[0, 0, 0],
    stop=[substrate_width, substrate_length, substrate_height]
)

# Ground plane
copper.AddBox(
    priority=10,
    start=[0, 0, 0],
    stop=[substrate_width, substrate_length, 0]
)

# Trace (centered)
trace_x_start = (substrate_width - trace_width) / 2.0
trace_y_start = (substrate_length - trace_length) / 2.0

copper.AddBox(
    priority=10,
    start=[trace_x_start, trace_y_start, substrate_height],
    stop=[trace_x_start + trace_width,
          trace_y_start + trace_length,
          substrate_height + trace_thickness]
)

print(f"  Substrate: {substrate_width} × {substrate_length} × {substrate_height} mm")
print(f"  Trace: {trace_width} × {trace_length} mm")

# Mesh
print("\nGenerating mesh...")
mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)

mesh.AddLine('x', [0, substrate_width/2, substrate_width])
mesh.AddLine('y', np.linspace(0, substrate_length, 81))
mesh.AddLine('z', [0, substrate_height, substrate_height + trace_thickness])

mesh.SmoothMeshLines('x', 0.5, 1.3)
mesh.SmoothMeshLines('y', 0.5, 1.3)
mesh.SmoothMeshLines('z', 0.1, 1.3)

# Lumped port at start of trace
# IMPORTANT: Use mesh coordinates (NOT SI units!)
print("\nSetting up port...")
port_x = substrate_width / 2.0
port_y_start = trace_y_start

port = FDTD.AddLumpedPort(
    1, 50,
    start=[port_x, port_y_start, 0],
    stop=[port_x, port_y_start, substrate_height],
    p_dir='z', excite=1, priority=5
)

# ========================================================================
# VTK Field Dumps for ParaView Visualization
# ========================================================================

print("\nConfiguring VTK dumps for ParaView...")

# Define dump region (entire substrate + some air)
# IMPORTANT: Dump coordinates must be in mesh coordinates (NOT SI units!)
# Mesh is defined in mm, so dump uses same mm coordinates
dump_start = [-2, -2, -1]
dump_stop = [substrate_width + 2,
             substrate_length + 2,
             substrate_height + 2]

# E-field dump (every 10 timesteps)
Et_dump = CSX.AddDump('Et', dump_type=0, file_type=0, dump_mode=2)
Et_dump.AddBox(start=dump_start, stop=dump_stop)

# H-field dump (every 10 timesteps)
Ht_dump = CSX.AddDump('Ht', dump_type=1, file_type=0, dump_mode=2)
Ht_dump.AddBox(start=dump_start, stop=dump_stop)

print("  E-field dump: Et_*.vtr")
print("  H-field dump: Ht_*.vtr")
print("  Location:", sim_path)

# Write geometry
CSX.Write2XML(os.path.join(sim_path, 'geometry.xml'))

# Run simulation
print("\nRunning simulation...")
print("  (This will create VTK files for ParaView)")
FDTD.Run(sim_path, cleanup=True, verbose=2)

print("\n" + "=" * 60)
print("Simulation Complete!")
print("=" * 60)
print("\nVTK Files for ParaView:")
print(f"  Location: {sim_path}/")
print("  E-field: Et_*.vtr")
print("  H-field: Ht_*.vtr")
print("\nTo view in ParaView:")
print("  1. Download files from container to your laptop")
print("  2. Open ParaView")
print("  3. File → Open → Select all .vtr files")
print("  4. Click 'Apply'")
print("  5. Use play button to animate")
print("  6. Color by: E-field magnitude, direction, etc.")
print("=" * 60)

# Count VTK files created
vtk_files = [f for f in os.listdir(sim_path) if f.endswith('.vtr')]
print(f"\n✓ Created {len(vtk_files)} VTK files")
