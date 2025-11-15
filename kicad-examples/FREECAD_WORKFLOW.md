# KiCAD → FreeCAD → OpenEMS Workflow (Optional)

## Overview

This workflow uses FreeCAD as a GUI intermediary to import KiCAD PCBs and export to OpenEMS.

**Status:** ⚠️ **Optional workflow with known compatibility issues**

**Recommendation:** Use Gerber2EMS (Workflow 1) or STEP import (Workflow 2) instead.

## Known Issues

- "Import KiCad PCB" button grayed out in FreeCAD 1.0+
- Ground plane import issues with KiCAD 8
- Requires specific FreeCAD version (0.19 works better than 1.0+)
- Macro may need to be run twice due to FreeCAD bug

## When to Use This Workflow

Consider FreeCAD workflow if:
- You prefer GUI-based simulation setup over scripting
- You need visual feedback during geometry import
- You're already familiar with FreeCAD

**For most users:** Gerber2EMS provides a better automated workflow.

## Installation

FreeCAD is **not pre-installed** in this dev container due to:
- Large installation size (~1 GB)
- Compatibility issues with recent versions
- Better alternatives available (Gerber2EMS, STEP import)

### To Install FreeCAD (Optional)

```bash
# Install FreeCAD 0.19 (more compatible than 1.0+)
sudo apt-get update
sudo apt-get install freecad
```

### Install FreeCAD-OpenEMS-Export Macro

```bash
# Clone the macro repository
cd /workspace
git clone https://github.com/LubomirJagos/FreeCAD-OpenEMS-Export.git

# Copy macros to FreeCAD directory
mkdir -p ~/.FreeCAD/Macro
cp FreeCAD-OpenEMS-Export/macros/*.FCMacro ~/.FreeCAD/Macro/
```

## Usage

### 1. Start FreeCAD in VNC Desktop

```bash
# Start VNC desktop
bash setup_gui.sh

# In browser: http://localhost:6080/vnc.html
# In VNC desktop: Applications → Graphics → FreeCAD
```

### 2. Run the Macro

In FreeCAD:
1. Macro → Macros
2. Select "FreeCAD_to_OpenEMS"
3. Click "Execute"

### 3. Import KiCAD PCB

1. In the macro GUI, click **"Import KiCad PCB"**
2. If button is grayed out:
   - Try running the macro a second time (known bug)
   - Or use alternative STEP import method (below)
3. Select your `.kicad_pcb` file
4. Wait for import (report view shows "all done" when finished)

### 4. Configure Simulation

1. Define ports using the GUI
2. Set frequency range
3. Configure materials (substrate, copper)
4. Set mesh resolution
5. Define boundary conditions

### 5. Export to OpenEMS

1. Click "Export to OpenEMS"
2. Save as Python script
3. Run the generated script:
   ```bash
   python3 my_simulation.py
   ```

## Alternative: STEP Import Method

If "Import KiCad PCB" button doesn't work:

### In KiCAD:
1. File → Export → STEP
2. Save as `pcb.step`

### In FreeCAD:
1. File → Open → Select `pcb.step`
2. Geometry imports as 3D model
3. Use FreeCAD-OpenEMS macro to define simulation parameters
4. Export to OpenEMS Python script

## Workarounds for Common Issues

### Button Grayed Out
- Run macro twice (close and re-run)
- Use FreeCAD 0.19 instead of 1.0+
- Use STEP import method instead

### Ground Plane Import Failure (KiCAD 8)
- Export STEP from KiCAD instead of direct import
- Manually draw ground plane in FreeCAD
- Use Gerber2EMS workflow instead

### Macro Crashes
- Check FreeCAD console for error messages
- Simplify PCB (remove components, use simple traces)
- Verify KiCAD PCB file is valid (open in KiCAD to confirm)

## Comparison with Other Workflows

| Feature | FreeCAD Workflow | Gerber2EMS | STEP Import |
|---------|------------------|------------|-------------|
| Ease of use | GUI (easier for beginners) | Command-line | Scripting |
| Reliability | ⚠️ Compatibility issues | ✅ Stable | ✅ Stable |
| Flexibility | Medium (GUI limits) | High (JSON config) | Very High (Python) |
| Geometry support | KiCAD PCB, STEP | Gerber files | STEP files |
| Simulation tool | OpenEMS only | OpenEMS | ElmerFEM, OpenEMS |
| Speed | Slow (manual setup) | Fast (automated) | Fast (scriptable) |
| Learning curve | Low | Medium | High |

## Recommendation

**For OpenEMS simulations:**
→ Use **Gerber2EMS** (Workflow 1)
- More reliable
- Better automation
- Active development

**For ElmerFEM simulations:**
→ Use **STEP Import** (Workflow 2)
- Direct Gmsh import
- Better control over materials
- Script-based workflow

**Only use FreeCAD workflow if:**
- You specifically need GUI interaction
- You have experience with FreeCAD
- You're using older KiCAD/FreeCAD versions

## Resources

- GitHub: https://github.com/LubomirJagos/FreeCAD-OpenEMS-Export
- Instructables Tutorial: https://www.instructables.com/Free-KiCad-Filter-Capacitor-Layout-Simulation/
- FreeCAD Forum: Discussion of known issues and workarounds

## Getting Help

If you encounter issues with FreeCAD workflow:

1. **Try alternative workflows first** (Gerber2EMS or STEP import)
2. Check GitHub issues for known problems
3. Verify FreeCAD version compatibility
4. Consider using STEP export from KiCAD instead of direct import

---

**Bottom Line:** FreeCAD workflow is available but not recommended for most users. Gerber2EMS and STEP import provide more reliable alternatives.
