#!/usr/bin/env python3
"""
Microstrip Transmission Line Example
=====================================

This example simulates a simple 50-ohm microstrip transmission line on FR4 substrate.

Physical Setup:
- Substrate: FR4 (εr = 4.3, thickness = 1.6 mm)
- Trace: Copper (width = 3 mm, length = 40 mm, thickness = 35 μm)
- Ground plane: Copper (bottom of substrate)

The simulation calculates S-parameters to verify transmission line behavior.
"""

import os
import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0, EPS0, MUE0

# ============================================================================
# Simulation Parameters
# ============================================================================

# Frequency range
f_start = 0.5e9    # 500 MHz
f_stop = 5e9       # 5 GHz
f_points = 201

# Physical dimensions (all in millimeters, converted to meters)
unit = 1e-3  # Units: mm

# Substrate parameters
substrate_width = 20.0    # mm
substrate_length = 50.0   # mm
substrate_height = 1.6    # mm (standard FR4)
substrate_er = 4.3        # FR4 relative permittivity

# Microstrip trace
trace_width = 3.0         # mm (designed for ~50 ohm)
trace_length = 40.0       # mm
trace_thickness = 0.035   # mm (35 μm = 1 oz copper)

# Port extension (for reference planes)
port_length = 5.0         # mm

# Feed position (centered)
feed_shift = 0.0          # mm from center

# Mesh resolution
mesh_res = 0.5            # mm (finer = more accurate but slower)

# ============================================================================
# Setup Simulation
# ============================================================================

print("=" * 60)
print("Microstrip Transmission Line Simulation")
print("=" * 60)

# Create simulation directory (use absolute path)
sim_path = os.path.abspath('microstrip_simulation')
os.makedirs(sim_path, exist_ok=True)

# Initialize OpenEMS
FDTD = openEMS()
FDTD.SetGaussExcite(0.5 * (f_start + f_stop), 0.5 * (f_stop - f_start))

# Setup CSXCAD geometry
CSX = ContinuousStructure()
FDTD.SetCSX(CSX)

# ============================================================================
# Define Materials
# ============================================================================

# Substrate material (FR4)
substrate = CSX.AddMaterial('FR4', epsilon=substrate_er)

# Copper (PEC - Perfect Electric Conductor)
copper = CSX.AddMetal('copper')

# ============================================================================
# Create Geometry
# ============================================================================

print("\nCreating geometry...")

# Substrate dimensions
sub_x = [0, substrate_width]
sub_y = [0, substrate_length]
sub_z = [0, substrate_height]

# Create substrate box
substrate.AddBox(
    priority=0,
    start=[sub_x[0] * unit, sub_y[0] * unit, sub_z[0] * unit],
    stop=[sub_x[1] * unit, sub_y[1] * unit, sub_z[1] * unit]
)

print(f"  Substrate: {substrate_width} × {substrate_length} × {substrate_height} mm")

# Ground plane (bottom of substrate)
copper.AddBox(
    priority=10,
    start=[sub_x[0] * unit, sub_y[0] * unit, 0],
    stop=[sub_x[1] * unit, sub_y[1] * unit, 0]
)

print(f"  Ground plane: {substrate_width} × {substrate_length} mm")

# Microstrip trace (centered on substrate)
trace_x_center = substrate_width / 2.0
trace_y_start = (substrate_length - trace_length) / 2.0
trace_y_stop = trace_y_start + trace_length

trace_start = [
    (trace_x_center - trace_width / 2.0) * unit,
    trace_y_start * unit,
    substrate_height * unit
]
trace_stop = [
    (trace_x_center + trace_width / 2.0) * unit,
    trace_y_stop * unit,
    (substrate_height + trace_thickness) * unit
]

copper.AddBox(priority=10, start=trace_start, stop=trace_stop)

print(f"  Trace: {trace_width} × {trace_length} mm")
print(f"  Trace thickness: {trace_thickness} mm")

# ============================================================================
# Setup Mesh (MUST be before ports!)
# ============================================================================

print("\nGenerating mesh...")

mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)

# Define mesh regions with appropriate resolution
# Add explicit lines at port locations for proper port snapping
mesh.AddLine('x', [0, substrate_width / 2.0 - trace_width / 2.0, substrate_width / 2.0, substrate_width / 2.0 + trace_width / 2.0, substrate_width])
# Add y-mesh with explicit lines at port locations
mesh.AddLine('y', np.linspace(0, substrate_length, int(substrate_length / mesh_res) + 1))
mesh.AddLine('y', [trace_y_start, trace_y_stop])  # Explicit port locations
# Add explicit z-lines at ground and substrate top for ports
mesh.AddLine('z', [0, substrate_height, substrate_height + trace_thickness])

# Smooth mesh
mesh.SmoothMeshLines('x', mesh_res, 1.3)
mesh.SmoothMeshLines('y', mesh_res, 1.3)
mesh.SmoothMeshLines('z', mesh_res / 4.0, 1.3)

# ============================================================================
# Setup Ports (requires mesh to be defined first!)
# ============================================================================

print("\nSetting up ports...")

# Port 1 (input) - at beginning of trace
# Use lumped ports for simplicity (vertical from ground to trace)
port1_start = [
    trace_x_center * unit,
    trace_y_start * unit,
    0
]
port1_stop = [
    trace_x_center * unit,
    trace_y_start * unit,
    substrate_height * unit
]

port1 = FDTD.AddLumpedPort(1, 50, port1_start, port1_stop, 'z', excite=1, priority=5)

# Port 2 (output) - at end of trace
port2_start = [
    trace_x_center * unit,
    trace_y_stop * unit,
    0
]
port2_stop = [
    trace_x_center * unit,
    trace_y_stop * unit,
    substrate_height * unit
]

port2 = FDTD.AddLumpedPort(2, 50, port2_start, port2_stop, 'z', priority=5)

print("  Port 1 (input): Active")
print("  Port 2 (output): Passive")

# ============================================================================
# Add Boundary Conditions (PML absorbing boundaries)
# ============================================================================

print("\nApplying boundary conditions (PML)...")

# Add 8 cells PML in all directions
FDTD.SetBoundaryCond(['PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8'])

# ============================================================================
# Run Simulation
# ============================================================================

print("\nPreparing simulation...")
print(f"  Frequency range: {f_start/1e9:.1f} - {f_stop/1e9:.1f} GHz")
print(f"  Simulation path: {sim_path}")

# Write geometry files
CSX.Write2XML(os.path.join(sim_path, 'microstrip.xml'))

# Show geometry in AppCSXCAD (requires GUI - comment out if running headless)
# from CSXCAD import AppCSXCAD_BIN
# os.system(AppCSXCAD_BIN + ' ' + os.path.join(sim_path, 'microstrip.xml'))

print("\nRunning simulation...")
print("  (This may take a few minutes)")
FDTD.Run(sim_path, cleanup=True, verbose=2)

print("\nSimulation complete!")

# ============================================================================
# Post-Processing
# ============================================================================

print("\nProcessing results...")

# Load port data
freq = np.linspace(f_start, f_stop, f_points)
port1.CalcPort(sim_path, freq)
port2.CalcPort(sim_path, freq)

# Get S-parameters (for lumped ports, use u_ref/u_inc)
s11 = port1.uf_ref / port1.uf_inc
s21 = port2.uf_ref / port1.uf_inc

# Convert to dB
s11_dB = 20 * np.log10(np.abs(s11))
s21_dB = 20 * np.log10(np.abs(s21))

# Get port impedances
Zc_port1 = port1.uf_tot / port1.if_tot
Zc_port2 = port2.uf_tot / port2.if_tot

print("\nResults:")
print(f"  Port 1 impedance (avg): {np.mean(np.abs(Zc_port1)):.1f} Ω")
print(f"  Port 2 impedance (avg): {np.mean(np.abs(Zc_port2)):.1f} Ω")
print(f"  S11 @ 2.5 GHz: {s11_dB[f_points//2]:.2f} dB")
print(f"  S21 @ 2.5 GHz: {s21_dB[f_points//2]:.2f} dB")
print(f"\nNote: Using lumped ports (50Ω reference)")

# ============================================================================
# Plot Results
# ============================================================================

print("\nGenerating plots...")

import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# S-parameters magnitude
ax1.plot(freq / 1e9, s11_dB, 'b-', linewidth=2, label='S11 (Return Loss)')
ax1.plot(freq / 1e9, s21_dB, 'r-', linewidth=2, label='S21 (Insertion Loss)')
ax1.set_xlabel('Frequency (GHz)', fontsize=12)
ax1.set_ylabel('Magnitude (dB)', fontsize=12)
ax1.set_title('S-Parameters', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10)
ax1.set_ylim([-40, 5])

# Impedance
ax2.plot(freq / 1e9, np.abs(Zc_port1), 'b-', linewidth=2, label='Port 1')
ax2.plot(freq / 1e9, np.abs(Zc_port2), 'r-', linewidth=2, label='Port 2')
ax2.axhline(y=50, color='k', linestyle='--', alpha=0.5, label='50 Ω')
ax2.set_xlabel('Frequency (GHz)', fontsize=12)
ax2.set_ylabel('Impedance (Ω)', fontsize=12)
ax2.set_title('Port Impedances', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)
ax2.set_ylim([0, 100])

plt.tight_layout()
plot_file = os.path.join(sim_path, 'results.png')
plt.savefig(plot_file, dpi=150, bbox_inches='tight')
print(f"\nPlot saved: {plot_file}")

plt.show()

print("\n" + "=" * 60)
print("Simulation complete! Check the results:")
print(f"  - Geometry: {sim_path}/microstrip.xml")
print(f"  - Plot: {sim_path}/results.png")
print("=" * 60)
