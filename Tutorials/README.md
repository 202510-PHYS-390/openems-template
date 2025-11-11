# OpenEMS Tutorials

Official OpenEMS Python tutorial examples.

## Running Tutorials with GUI Plots

These tutorials display plots using matplotlib. To see the plots in the VNC desktop:

### Quick Start

```bash
# 1. Start GUI environment (in one terminal)
bash setup_gui.sh

# 2. Open browser to VNC
# http://localhost:6080/vnc.html
# Password: openems

# 3. In another terminal, run tutorials
cd Tutorials
python3 Rect_Waveguide.py

# Plots will appear in the VNC desktop window

# 4. When done, press Ctrl+C in the setup_gui.sh terminal to stop
```

**That's it!** One script does everything.

## Available Tutorials

Check the official OpenEMS Python examples:
https://github.com/thliebig/openEMS-Project/tree/master/python/Tutorials

## Troubleshooting

### No plot window appears

Make sure:
1. VNC is running: `ps aux | grep Xvnc`
2. Environment variables are set:
   ```bash
   echo $DISPLAY      # Should be :1
   echo $MPLBACKEND   # Should be TkAgg
   ```
3. If not set, run: `source ~/.bashrc` or `bash setup_gui.sh`

### "Cannot import ImageTk" error

```bash
apt-get update && apt-get install -y python3-pil.imagetk
```

### Save plots instead of displaying

Edit the tutorial script and change:
```python
# plt.show()  # Comment out
plt.savefig('output.png')  # Add this
```

## Notes

- Tutorials may take 1-5 minutes to run
- Some require significant computational resources
- Warnings about "Max timesteps" are normal for quick tests
- Results are saved in subdirectories created by each tutorial
