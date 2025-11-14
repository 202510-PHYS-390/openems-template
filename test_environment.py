#!/usr/bin/env python3
"""Quick test to verify OpenEMS + ElmerFEM installation"""

import sys
import subprocess

def test_imports():
    """Test that all required packages can be imported"""
    tests = []

    # Test CSXCAD
    try:
        import CSXCAD
        tests.append(("CSXCAD", True, f"version {CSXCAD.__version__}"))
    except Exception as e:
        tests.append(("CSXCAD", False, str(e)))

    # Test openEMS
    try:
        import openEMS
        tests.append(("openEMS", True, "imported successfully"))
    except Exception as e:
        tests.append(("openEMS", False, str(e)))

    # Test numpy
    try:
        import numpy as np
        tests.append(("numpy", True, f"version {np.__version__}"))
    except Exception as e:
        tests.append(("numpy", False, str(e)))

    # Test matplotlib
    try:
        import matplotlib
        tests.append(("matplotlib", True, f"version {matplotlib.__version__}"))
    except Exception as e:
        tests.append(("matplotlib", False, str(e)))

    # Test h5py
    try:
        import h5py
        tests.append(("h5py", True, f"version {h5py.__version__}"))
    except Exception as e:
        tests.append(("h5py", False, str(e)))

    # Test meshio (for ElmerFEM)
    try:
        import meshio
        tests.append(("meshio", True, f"version {meshio.__version__}"))
    except Exception as e:
        tests.append(("meshio", False, str(e)))

    # Test pyvista (for ElmerFEM)
    try:
        import pyvista
        tests.append(("pyvista", True, f"version {pyvista.__version__}"))
    except Exception as e:
        tests.append(("pyvista", False, str(e)))

    # Print results
    print("\nPython Environment Verification")
    print("=" * 50)
    all_passed = True
    for name, passed, info in tests:
        status = "✓" if passed else "✗"
        print(f"{status} {name:15s} {info}")
        if not passed:
            all_passed = False

    # Test ElmerFEM executables
    print("\nElmerFEM Executables")
    print("=" * 50)
    elmer_tests = []

    for cmd in ["ElmerSolver", "ElmerGrid", "ElmerGUI"]:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 or "Elmer" in result.stdout or "Elmer" in result.stderr:
                elmer_tests.append((cmd, True, "found"))
            else:
                elmer_tests.append((cmd, False, "not working"))
        except:
            elmer_tests.append((cmd, False, "not found"))

    for name, passed, info in elmer_tests:
        status = "✓" if passed else "✗"
        print(f"{status} {name:15s} {info}")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("All tests passed! Environment is ready.")
        return 0
    else:
        print("Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())
