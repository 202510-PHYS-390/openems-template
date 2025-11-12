#!/usr/bin/env python3
"""
Simple Plane Wave Propagation - VTK Export for ParaView
========================================================

This example shows a plane wave propagating through space and a dielectric.
NO PORTS - just pure field visualization to avoid port configuration errors.

Perfect for learning ParaView visualization of electromagnetic fields.

ADJUSTABLE PARAMETERS:
- max_timesteps: Controls simulation duration (10k = ~1-2 min, creates ~2000 VTK files)
- box_length/width/height: Simulation volume (smaller = faster)
- mesh_res: Mesh resolution (larger = faster, less accurate)

NOTE: VTK dumps occur every ~10 timesteps (hardcoded in OpenEMS).
To reduce file count, decrease max_timesteps or delete every Nth file after simulation.
"""

import os
import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS

# Simulation parameters
unit = 1e-3  # units in mm
f0 = 5e9     # 5 GHz center frequency
f_max = 10e9 # 10 GHz max frequency

# Simulation box size (smaller = faster simulation)
box_length = 40.0  # mm (along propagation direction)
box_width = 20.0   # mm
box_height = 20.0  # mm

# Dielectric slab (to show field interaction)
slab_start = 15.0  # mm from start
slab_thickness = 10.0  # mm
slab_er = 4.3      # FR4 dielectric

# Simulation directory
sim_path = os.path.abspath('plane_wave_sim')
os.makedirs(sim_path, exist_ok=True)

print("=" * 60)
print("Simple Plane Wave Field Visualization")
print("=" * 60)

# Initialize OpenEMS
FDTD = openEMS()
FDTD.SetGaussExcite(f0, f_max/2)
FDTD.SetBoundaryCond(['PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8'])

# Limit simulation time to reasonable duration
# VTK dumps happen every ~10 timesteps by default
# 10,000 timesteps = ~1,000 VTK files per field = 2,000 total
max_timesteps = 10000  # Approximately 1-2 minutes on most systems
FDTD.SetNumberOfTimeSteps(max_timesteps)

# Setup CSXCAD geometry
CSX = ContinuousStructure()
FDTD.SetCSX(CSX)

print("\nCreating geometry...")

# Define air material (default background)
air = CSX.AddMaterial('air', epsilon=1.0)

# Add dielectric slab
# IMPORTANT: Use mesh coordinates (NOT SI units!)
dielectric = CSX.AddMaterial('FR4', epsilon=slab_er)
dielectric.AddBox(
    priority=0,
    start=[0, 0, slab_start],
    stop=[box_width, box_height, slab_start + slab_thickness]
)

print(f"  Air region: {box_width} × {box_height} × {box_length} mm")
print(f"  Dielectric slab (ε_r={slab_er}): {slab_thickness} mm thick at z={slab_start} mm")

# Mesh
print("\nGenerating mesh...")
mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)

# Create mesh lines
mesh_res = 2.0  # mesh resolution in mm
mesh.AddLine('x', np.arange(0, box_width + mesh_res/2, mesh_res))
mesh.AddLine('y', np.arange(0, box_height + mesh_res/2, mesh_res))
mesh.AddLine('z', np.arange(0, box_length + mesh_res/2, mesh_res))

# Refine mesh at dielectric interfaces
mesh.AddLine('z', [slab_start, slab_start + slab_thickness])

mesh.SmoothMeshLines('x', mesh_res/2, 1.3)
mesh.SmoothMeshLines('y', mesh_res/2, 1.3)
mesh.SmoothMeshLines('z', mesh_res/2, 1.3)

# ========================================================================
# Plane Wave Excitation (Simple - No Port!)
# ========================================================================

print("\nSetting up plane wave excitation...")

# Create a plane wave excitation at z=5mm
# This is just an electric field applied across the plane
excite_z = 5.0  # mm from start

# Add excitation - E-field in x-direction
# IMPORTANT: Use mesh coordinates (NOT SI units!)
excitation = CSX.AddExcitation('plane_wave', exc_type=0, exc_val=[1, 0, 0])
excitation.AddBox(
    priority=10,
    start=[0, 0, excite_z],
    stop=[box_width, box_height, excite_z]
)

print(f"  Plane wave at z={excite_z} mm")
print(f"  E-field direction: x-axis")
print(f"  Propagation direction: +z")

# ========================================================================
# VTK Field Dumps for ParaView Visualization
# ========================================================================

print("\nConfiguring VTK dumps for ParaView...")

# Define dump region (entire simulation box)
# IMPORTANT: Dump coordinates must match mesh coordinates (NOT SI units!)
# Mesh is defined in mm (0 to box_width), so dump uses same coordinates
dump_start = [0, 0, 0]
dump_stop = [box_width, box_height, box_length]  # In mesh coordinates, NOT multiplied by unit!

# VTK dumps happen every ~10 timesteps by default (hardcoded in OpenEMS)
# With 10,000 max timesteps, we get ~1,000 files per field
dump_interval = 10  # Default, cannot be easily changed

# E-field dump
Et_dump = CSX.AddDump('Et', dump_type=0, file_type=0, dump_mode=2)
Et_dump.AddBox(start=dump_start, stop=dump_stop)

# H-field dump
Ht_dump = CSX.AddDump('Ht', dump_type=1, file_type=0, dump_mode=2)
Ht_dump.AddBox(start=dump_start, stop=dump_stop)

print(f"  E-field dump: Et_*.vtr (every ~{dump_interval} timesteps)")
print(f"  H-field dump: Ht_*.vtr (every ~{dump_interval} timesteps)")
print(f"  Max timesteps: {max_timesteps}")
print(f"  Expected VTK files: ~{2 * max_timesteps // dump_interval}")
print("  Location:", sim_path)

# Write geometry
CSX.Write2XML(os.path.join(sim_path, 'geometry.xml'))

# Run simulation
print("\nRunning simulation...")
print(f"  Max timesteps: {max_timesteps}")
print(f"  Expected duration: 1-2 minutes")
print(f"  Expected VTK files: ~{2 * max_timesteps // dump_interval}")
print("  (Creating VTK files for ParaView)")
print("  You will see the plane wave propagate and interact with dielectric")
print("")
FDTD.Run(sim_path, cleanup=True, verbose=2)

print("\n" + "=" * 60)
print("Simulation Complete!")
print("=" * 60)

# Count VTK files created
vtk_files = [f for f in os.listdir(sim_path) if f.endswith('.vtr')]
print(f"\n✓ Created {len(vtk_files)} VTK files")
print("✓ No port errors - pure field visualization!")

print("\nVTK Files for ParaView:")
print(f"  Location: {sim_path}/")
print("  E-field: Et_*.vtr")
print("  H-field: Ht_*.vtr")
print("\nTo view in ParaView:")
print("  1. Download files to your laptop")
print("  2. Open ParaView")
print("  3. File → Open → Select all Et_*.vtr files")
print("  4. Click 'Apply'")
print("  5. Select 'E' from dropdown to color by E-field")
print("  6. Click play button to animate")
print("\nWhat to observe:")
print("  - Plane wave propagating in +z direction")
print("  - Partial reflection at dielectric interface")
print("  - Slower propagation inside dielectric (v = c/√ε_r)")
print("  - Transmission through dielectric")
print("\nAdjusting simulation parameters:")
print(f"  - To run longer: increase max_timesteps (currently {max_timesteps})")
print(f"  - Note: VTK dumps every ~10 timesteps (hardcoded)")
print(f"  - To reduce files: decrease max_timesteps or thin files afterward")
print("  - For faster sim: increase mesh_res or reduce box size")
print("=" * 60)
