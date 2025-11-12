#!/usr/bin/env python3
"""
Inspect VTU file structure
"""

import sys
import os

try:
    import pyvista as pv
except ImportError:
    print("ERROR: pyvista not found!")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python3 inspect_vtu.py <vtu_file>")
    print("\nLooking for VTU files in current directory...")
    vtu_files = [f for f in os.listdir('.') if f.endswith('.vtu')]
    if vtu_files:
        print(f"\nFound {len(vtu_files)} VTU files:")
        for f in vtu_files:
            print(f"  - {f}")
        print(f"\nTry: python3 inspect_vtu.py {vtu_files[0]}")
    sys.exit(1)

vtu_file = sys.argv[1]

if not os.path.exists(vtu_file):
    print(f"ERROR: File not found: {vtu_file}")
    sys.exit(1)

print("=" * 60)
print(f"Inspecting: {vtu_file}")
print("=" * 60)

# Read the VTU file
mesh = pv.read(vtu_file)

print(f"\nFile size: {os.path.getsize(vtu_file)} bytes")
print(f"Number of points: {mesh.n_points}")
print(f"Number of cells: {mesh.n_cells}")
print(f"Bounds: {mesh.bounds}")

print("\n" + "=" * 60)
print("POINT DATA (node-based fields):")
print("=" * 60)

if mesh.point_data:
    for name in mesh.point_data.keys():
        data = mesh.point_data[name]
        if hasattr(data, 'shape'):
            shape = data.shape
            if len(shape) == 1:
                print(f"\n  {name} (scalar)")
                print(f"    Shape: {shape}")
                print(f"    Range: [{data.min():.3e}, {data.max():.3e}]")
                print(f"    Mean: {data.mean():.3e}")
            elif len(shape) == 2:
                print(f"\n  {name} (vector, {shape[1]} components)")
                print(f"    Shape: {shape}")
                magnitude = (data**2).sum(axis=1)**0.5
                print(f"    Magnitude range: [{magnitude.min():.3e}, {magnitude.max():.3e}]")
                print(f"    Component ranges:")
                for i in range(shape[1]):
                    print(f"      [{i}]: [{data[:,i].min():.3e}, {data[:,i].max():.3e}]")
else:
    print("  (none)")

print("\n" + "=" * 60)
print("CELL DATA (element-based fields):")
print("=" * 60)

if mesh.cell_data:
    for name in mesh.cell_data.keys():
        data = mesh.cell_data[name]
        if hasattr(data, 'shape'):
            shape = data.shape
            if len(shape) == 1:
                print(f"\n  {name} (scalar)")
                print(f"    Shape: {shape}")
                print(f"    Range: [{data.min():.3e}, {data.max():.3e}]")
            elif len(shape) == 2:
                print(f"\n  {name} (vector, {shape[1]} components)")
                print(f"    Shape: {shape}")
else:
    print("  (none)")

print("\n" + "=" * 60)
print("FIELD DATA (global metadata):")
print("=" * 60)

if mesh.field_data:
    for name, value in mesh.field_data.items():
        print(f"  {name}: {value}")
else:
    print("  (none)")

print("\n" + "=" * 60)
print("Array names available:")
print("=" * 60)
print("  ", mesh.array_names)

print("\n" + "=" * 60)
