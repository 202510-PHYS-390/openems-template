#!/usr/bin/env python3
"""
Straight PCB Trace EM Simulator
Based on working FreeCAD/KiCAD example, simplified for education

Easily modifiable parameters for students to explore EM wave propagation
"""

import math
import numpy as np
import os, shutil
from pylab import *
import CSXCAD
from openEMS import openEMS
from openEMS.physical_constants import *

# =============================================================================
# STUDENT-MODIFIABLE PARAMETERS
# =============================================================================
#
# KEY PARAMETERS TO EXPERIMENT WITH:
# 1. LOAD_RESISTANCE - Change to see reflections (try 0, 50, 1000, 10000 Ω)
# 2. TRACE_WIDTH - Affects impedance and field distribution
# 3. FR4_THICKNESS - Changes wave velocity and impedance
# 4. EXCITATION_FREQ - Try different frequencies
#
# For GitHub Codespaces: Keep MAX_TIMESTEPS = 5000 (runs in ~10-15 minutes)
# On fast laptop: Can increase to 10000-20000 for more detailed visualization
#
# =============================================================================

# Geometry (all in mm)
TRACE_LENGTH = 50.0
TRACE_WIDTH = 3.0
TRACE_THICKNESS = 0.035  # 1oz copper

FR4_THICKNESS = 1.6
GROUND_THICKNESS = 0.035

# Board dimensions
BOARD_WIDTH = 20.0
BOARD_LENGTH = 60.0

# Material properties
FR4_EPSILON = 4.6
COPPER_CONDUCTIVITY = 5.8e7

# Excitation
EXCITATION_FREQ = 1.0e9  # 1 GHz center
EXCITATION_BW = 0.01e9   # 10 MHz bandwidth (narrow like working example!)

# Load resistance
LOAD_RESISTANCE = 50.0   # Try: 0 (short), 50 (roughly matched), 1000 (open)

# Simulation settings
MAX_TIMESTEPS = 20000    # Number of timesteps to run
                         # 10000 = ~2 min on fast laptop, ~10-15 min on Codespaces

MIN_DECREMENT = 0.1      # Stop when energy decays to this level (0.1 = -10dB)
                         # Lower = more strict (0.01 = -20dB), takes longer

# Advanced: 3D field dumps
ENABLE_3D_DUMPS = False  # Set to True for full 3D volume visualization
                         # WARNING: Creates VERY large files (100x bigger)!
                         # Only enable on fast computer with lots of RAM
                         # Not recommended for Codespaces

# =============================================================================
# SETUP
# =============================================================================

unit = 0.001  # All dimensions in mm

# Simulation folder
currDir = os.getcwd()
Sim_Path = os.path.join(currDir, 'output_files')
if os.path.exists(Sim_Path):
    shutil.rmtree(Sim_Path)
os.mkdir(Sim_Path)

# Setup FDTD
CSX = CSXCAD.ContinuousStructure()
FDTD = openEMS(NrTS=MAX_TIMESTEPS, EndCriteria=MIN_DECREMENT, OverSampling=100)
FDTD.SetCSX(CSX)

# Boundary conditions - PML absorbing
BC = ["PML_8","PML_8","PML_8","PML_8","PML_8","PML_8"]
FDTD.SetBoundaryCond(BC)

# Excitation - narrow Gaussian (key difference!)
f0 = EXCITATION_FREQ
fc = EXCITATION_BW
FDTD.SetGaussExcite(f0, fc)

print("="*70)
print("Straight PCB Trace Simulator")
print("="*70)
print(f"Trace: {TRACE_LENGTH} x {TRACE_WIDTH} mm")
print(f"FR4: {FR4_THICKNESS} mm, εr = {FR4_EPSILON}")
print(f"Excitation: {f0/1e9:.2f} GHz ± {fc/1e6:.0f} MHz")
print(f"Load: {LOAD_RESISTANCE} Ω")
print("="*70)

# =============================================================================
# MATERIALS
# =============================================================================

# Ground plane (PEC - perfect conductor)
gnd = CSX.AddMetal('ground')
gnd.AddBox(
    start=[-BOARD_LENGTH/2, -BOARD_WIDTH/2, -GROUND_THICKNESS],
    stop=[BOARD_LENGTH/2, BOARD_WIDTH/2, 0],
    priority=9800
)

# FR4 substrate
fr4 = CSX.AddMaterial('fr4')
fr4.SetMaterialProperty(epsilon=FR4_EPSILON, mue=1)
fr4.AddBox(
    start=[-BOARD_LENGTH/2, -BOARD_WIDTH/2, 0],
    stop=[BOARD_LENGTH/2, BOARD_WIDTH/2, FR4_THICKNESS],
    priority=9700
)

# Trace (copper)
trace = CSX.AddMetal('trace')
trace.AddBox(
    start=[-TRACE_LENGTH/2, -TRACE_WIDTH/2, FR4_THICKNESS],
    stop=[TRACE_LENGTH/2, TRACE_WIDTH/2, FR4_THICKNESS + TRACE_THICKNESS],
    priority=9900
)

# =============================================================================
# MESH (Critical - adaptive like working example!)
# =============================================================================

mesh_x = np.array([])
mesh_y = np.array([])
mesh_z = np.array([])

# Helper function
def arangeWithEndpoint(start, stop, step=1, endpoint=True):
    if start == stop:
        return [start]
    arr = np.arange(start, stop, step)
    if endpoint and arr[-1] + step == stop:
        arr = np.concatenate([arr, [stop]])
    return arr

# X-direction: Coarse outside trace, fine along trace
mesh_x = np.concatenate([mesh_x, arangeWithEndpoint(-BOARD_LENGTH/2-10, -TRACE_LENGTH/2-2, 0.5)])
mesh_x = np.concatenate([mesh_x, arangeWithEndpoint(-TRACE_LENGTH/2-2, TRACE_LENGTH/2+2, 0.1)])  # Fine!
mesh_x = np.concatenate([mesh_x, arangeWithEndpoint(TRACE_LENGTH/2+2, BOARD_LENGTH/2+10, 0.5)])

# Y-direction: Coarse outside trace, fine across trace
mesh_y = np.concatenate([mesh_y, arangeWithEndpoint(-BOARD_WIDTH/2-10, -TRACE_WIDTH/2-2, 0.5)])
mesh_y = np.concatenate([mesh_y, arangeWithEndpoint(-TRACE_WIDTH/2-2, TRACE_WIDTH/2+2, 0.1)])  # Fine!
mesh_y = np.concatenate([mesh_y, arangeWithEndpoint(TRACE_WIDTH/2+2, BOARD_WIDTH/2+10, 0.5)])

# Z-direction: Coarse in air, fine through conductors and FR4
mesh_z = np.concatenate([mesh_z, arangeWithEndpoint(-10, -GROUND_THICKNESS-0.1, 0.5)])
# Multiple lines through ground plane
mesh_z = np.concatenate([mesh_z, np.linspace(-GROUND_THICKNESS, 0, 3)])
# Medium resolution through FR4
mesh_z = np.concatenate([mesh_z, arangeWithEndpoint(0.05, FR4_THICKNESS-0.05, 0.2)])
# Multiple lines through trace
mesh_z = np.concatenate([mesh_z, np.linspace(FR4_THICKNESS, FR4_THICKNESS+TRACE_THICKNESS, 3)])
# Coarse above trace
mesh_z = np.concatenate([mesh_z, arangeWithEndpoint(FR4_THICKNESS+TRACE_THICKNESS+0.1, 10, 0.5)])

# Remove duplicates and set mesh
mesh_x = np.unique(mesh_x)
mesh_y = np.unique(mesh_y)
mesh_z = np.unique(mesh_z)

openEMS_grid = CSX.GetGrid()
openEMS_grid.SetDeltaUnit(unit)
openEMS_grid.AddLine('x', mesh_x)
openEMS_grid.AddLine('y', mesh_y)
openEMS_grid.AddLine('z', mesh_z)

print(f"\nMesh: {len(mesh_x)} x {len(mesh_y)} x {len(mesh_z)} = {len(mesh_x)*len(mesh_y)*len(mesh_z):,} cells")

# =============================================================================
# PORTS
# =============================================================================

# Port 1: Source (left end)
port_width = 1.0
port1_start = [-TRACE_LENGTH/2, -TRACE_WIDTH/2, -GROUND_THICKNESS]
port1_stop = [-TRACE_LENGTH/2 + port_width, TRACE_WIDTH/2, FR4_THICKNESS + TRACE_THICKNESS]

port1 = FDTD.AddLumpedPort(
    port_nr=1,
    R=50.0,
    start=port1_start,
    stop=port1_stop,
    p_dir='z',
    priority=10000,
    excite=1000.0  # 1000V excitation like working example!
)

# Port 2: Load (right end)
port2_start = [TRACE_LENGTH/2 - port_width, -TRACE_WIDTH/2, -GROUND_THICKNESS]
port2_stop = [TRACE_LENGTH/2, TRACE_WIDTH/2, FR4_THICKNESS + TRACE_THICKNESS]

port2 = FDTD.AddLumpedPort(
    port_nr=2,
    R=LOAD_RESISTANCE,
    start=port2_start,
    stop=port2_stop,
    p_dir='z',
    priority=10000,
    excite=0  # Load, not excited
)

# =============================================================================
# FIELD DUMPS (Like working example - horizontal planes!)
# =============================================================================

# E-field at Z=1.0mm (middle of FR4) - this is what works!
efield_dump = CSX.AddDump('efield', dump_type=0, dump_mode=2)
efield_dump.AddBox(
    start=[-BOARD_LENGTH/2, -BOARD_WIDTH/2, 1.0],
    stop=[BOARD_LENGTH/2, BOARD_WIDTH/2, 1.0]
)

# H-field at Z=0.9mm (near bottom of FR4)
hfield_dump = CSX.AddDump('hfield', dump_type=1, dump_mode=2)
hfield_dump.AddBox(
    start=[-BOARD_LENGTH/2, -BOARD_WIDTH/2, 0.9],
    stop=[BOARD_LENGTH/2, BOARD_WIDTH/2, 0.9]
)

# E-field cross-section (YZ plane at X=0)
cross_efield_dump = CSX.AddDump('cross_section_E', dump_type=0, dump_mode=2)
cross_efield_dump.AddBox(
    start=[0, -BOARD_WIDTH/2, -GROUND_THICKNESS-1],
    stop=[0, BOARD_WIDTH/2, FR4_THICKNESS + TRACE_THICKNESS + 2]
)

# H-field cross-section (YZ plane at X=0) - shows magnetic field loops!
cross_hfield_dump = CSX.AddDump('cross_section_H', dump_type=1, dump_mode=2)
cross_hfield_dump.AddBox(
    start=[0, -BOARD_WIDTH/2, -GROUND_THICKNESS-1],
    stop=[0, BOARD_WIDTH/2, FR4_THICKNESS + TRACE_THICKNESS + 2]
)

# Optional 3D volume dumps (disabled by default - very large files!)
if ENABLE_3D_DUMPS:
    # 3D E-field volume around trace region only
    efield_3d_dump = CSX.AddDump('efield_3D', dump_type=0, dump_mode=2,
                                  sub_sampling=[4, 4, 4])  # Reduce resolution to save space
    efield_3d_dump.AddBox(
        start=[-TRACE_LENGTH/2-5, -TRACE_WIDTH/2-5, -GROUND_THICKNESS],
        stop=[TRACE_LENGTH/2+5, TRACE_WIDTH/2+5, FR4_THICKNESS + TRACE_THICKNESS + 2]
    )

    # 3D H-field volume
    hfield_3d_dump = CSX.AddDump('hfield_3D', dump_type=1, dump_mode=2,
                                  sub_sampling=[4, 4, 4])
    hfield_3d_dump.AddBox(
        start=[-TRACE_LENGTH/2-5, -TRACE_WIDTH/2-5, -GROUND_THICKNESS],
        stop=[TRACE_LENGTH/2+5, TRACE_WIDTH/2+5, FR4_THICKNESS + TRACE_THICKNESS + 2]
    )

    print("\n  WARNING: 3D dumps enabled - will create large files!")

print("\nField dumps:")
print("  - E-field horizontal (Z=1.0mm) for wave propagation")
print("  - H-field horizontal (Z=0.9mm)")
print("  - E-field cross-section (YZ at X=0)")
print("  - H-field cross-section (YZ at X=0) - shows magnetic loops")
if ENABLE_3D_DUMPS:
    print("  - E-field 3D volume (around trace region)")
    print("  - H-field 3D volume (around trace region)")

# =============================================================================
# RUN SIMULATION
# =============================================================================

print("\n" + "="*70)
print("Running simulation...")
print("="*70)

FDTD.Run(Sim_Path, cleanup=True, verbose=3)

print("\n" + "="*70)
print("Simulation Complete!")
print("="*70)
print(f"\nResults in: {Sim_Path}/")
print("\nVisualize in ParaView:")
print("  - efield_*.vtr - Wave propagation in XY plane")
print("  - hfield_*.vtr - Magnetic field")
print("  - cross_section_*.vtr - Side view")
print("\n" + "="*70)
