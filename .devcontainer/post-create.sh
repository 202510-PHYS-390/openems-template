#!/bin/bash
# Post-create script for OpenEMS + ElmerFEM development container
# Runs once after container is created

set -e

echo "========================================="
echo "OpenEMS + ElmerFEM Container Setup"
echo "========================================="

# Ensure workspace directories exist
echo "Creating workspace directories..."
mkdir -p /workspace/simulations
mkdir -p /workspace/pcb-designs
mkdir -p /workspace/examples
mkdir -p /workspace/elmerfem-examples

# Set up Python environment
echo "Setting up Python environment..."
pip3 install --upgrade pip

# Verify OpenEMS installation
echo "Verifying OpenEMS installation..."
python3 -c "import CSXCAD; print('CSXCAD version:', CSXCAD.__version__)" || echo "Warning: CSXCAD import failed"
python3 -c "import openEMS; print('OpenEMS imported successfully')" || echo "Warning: openEMS import failed"

# Verify ElmerFEM installation
echo "Verifying ElmerFEM installation..."
which ElmerSolver || echo "Warning: ElmerSolver not found"
which ElmerGrid || echo "Warning: ElmerGrid not found"
which ElmerGUI || echo "Warning: ElmerGUI not found"

# Create a simple verification script
cat > /workspace/test_environment.py << 'EOF'
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
EOF

chmod +x /workspace/test_environment.py

# Set up VNC directory
echo "Setting up VNC configuration..."
mkdir -p ~/.vnc

# Create xstartup for VNC (matches setup_gui.sh)
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS

# Start dbus with xfce4-session
dbus-launch --exit-with-session xfce4-session &

# Keep script alive
wait
EOF

chmod +x ~/.vnc/xstartup

# Setup environment variables for matplotlib GUI
echo "" >> ~/.bashrc
echo "# Matplotlib GUI support" >> ~/.bashrc
echo "export DISPLAY=:1" >> ~/.bashrc
echo "export MPLBACKEND=TkAgg" >> ~/.bashrc

# Setup custom shell prompt
echo "" >> ~/.bashrc
echo "# Custom shell prompt" >> ~/.bashrc
echo 'export PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> ~/.bashrc

echo "========================================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Test installation: python3 test_environment.py"
echo "2. Start GUI: bash setup_gui.sh"
echo "3. Access desktop: http://localhost:6080/vnc.html"
echo "4. Password: openems"
echo ""
echo "Available Tools:"
echo "  - OpenEMS: High-frequency EM simulation (FDTD)"
echo "  - ElmerFEM: Low-frequency/DC FEM simulation"
echo "  - Gmsh: Mesh generation"
echo ""
echo "Documentation:"
echo "  README.md - Quick start guide"
echo "  Tutorials/README.md - OpenEMS tutorial examples"
echo "  examples/README.md - OpenEMS custom examples"
echo "  elmerfem-examples/ - ElmerFEM examples (TBD)"
echo "========================================="
