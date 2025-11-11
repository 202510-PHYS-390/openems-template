#!/usr/bin/env python3
"""Quick test to verify OpenEMS installation"""

import sys

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

    # Print results
    print("\nOpenEMS Environment Verification")
    print("=" * 50)
    all_passed = True
    for name, passed, info in tests:
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
