# OpenEMS Devcontainer Deployment Guide

## What You Have

A complete GitHub Codespaces-ready repository for teaching PCB signal simulation with OpenEMS. Everything runs in a web browser with zero local installation!

## Quick Deployment (5 minutes)

### 1. Create GitHub Repository

```bash
# Create new repository on GitHub (via web interface):
# - Name: openems-pcb-simulation (or your choice)
# - Public or Private
# - Don't initialize with README
```

### 2. Push This Code

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: OpenEMS devcontainer setup"

# Connect to your GitHub repo
git remote add origin git@github.com:202510-PHYS-390/openems-template.git
git branch -M main
git push -u origin main
```

### 3. Test the Setup

1. Go to your repository on GitHub
2. Click green `<> Code` button
3. Select Codespaces tab
4. Click "Create codespace on main"
5. Wait 5-8 minutes for first build
6. Once loaded:
   - Go to PORTS tab
   - Click globe icon for port 6080
   - Enter password: `openems`
   - See desktop!
7. In terminal: `python3 verify_environment.py`

### 4. Share with Students

**Option A: Direct Access**
- Make repository public
- Students fork repository
- They create their own Codespace

**Option B: GitHub Classroom**
- Set up GitHub Classroom
- Create assignment from template
- Students auto-get their own copy

## What's Included

### Core Files Created

```
.devcontainer/
├── devcontainer.json       ✓ Codespaces configuration
├── Dockerfile              ✓ Ubuntu + OpenEMS + VNC
├── post-create.sh          ✓ Setup script
└── start-vnc.sh            ✓ Auto-start VNC/noVNC

Documentation:
├── README.md               ✓ Complete user guide
├── QUICKSTART.md           ✓ Student quick-start
├── INSTRUCTOR_GUIDE.md     ✓ Teaching guide
└── REPOSITORY_STRUCTURE.md ✓ Technical details

Examples:
└── examples/
    └── microstrip_example.py ✓ Working simulation

Verification:
├── verify_environment.py   ✓ Test all components
└── test_openems.py        ✓ Quick import test

Structure:
├── simulations/            ✓ Student workspace
├── pcb-designs/           ✓ KiCad projects
└── .gitignore             ✓ Ignore outputs
```

## Key Features

✅ **Zero Installation** - Runs entirely in browser
✅ **GUI Support** - Full desktop via noVNC
✅ **ParaView Included** - 3D field visualization
✅ **Python Interface** - Full OpenEMS Python bindings
✅ **gerber2ems Ready** - KiCad workflow supported
✅ **Example Included** - Working microstrip simulation
✅ **Documentation** - Student + instructor guides
✅ **Verification Script** - Test everything works

## For Students

**Launch and run first simulation in 5 minutes:**

1. Open repository in Codespace
2. Access desktop (port 6080)
3. Run: `cd examples && python3 microstrip_example.py`
4. View results!

**See: QUICKSTART.md for details**

## For Instructors

**Course integration:**

- Week 1: Transmission line basics
- Week 2: Mesh and convergence
- Week 3: Real PCB workflow (KiCad)
- Week 4: Signal integrity problems

**Assignment templates and rubrics included!**

**See: INSTRUCTOR_GUIDE.md for details**

## Cost & Resources

### GitHub Codespaces Free Tier

**Personal accounts:** 60 hours/month
**Education accounts:** More hours (apply at education.github.com)

**Resource usage:**
- First build: 8 minutes
- Subsequent starts: 30 seconds
- Typical simulation: 2-5 minutes
- 4 cores, 8GB RAM default

### Cost Comparison

**Traditional lab:**
- Software licenses: $5,000-50,000/year
- Lab computers: $2,000 × N students
- IT support: Ongoing

**Codespaces approach:**
- Software: $0 (open source)
- Hardware: $0 (cloud)
- IT support: Minimal
- **Total: $0 with education account** 🎉

## Customization

### Change VNC Password

Edit `.devcontainer/Dockerfile` line ~38:
```dockerfile
echo "your_password" | vncpasswd -f > ...
```

### Add Course Materials

```bash
mkdir assignments
cp examples/microstrip_example.py assignments/hw1_starter.py
git add assignments
git commit -m "Add homework 1 starter"
git push
```

### Install Additional Tools

Edit `.devcontainer/Dockerfile`:
```dockerfile
RUN apt-get install -y your-tool-here
```

### Pre-configure Environment

Edit `.devcontainer/post-create.sh`:
```bash
# Download datasets
wget https://example.com/data.zip
```

## Testing Checklist

Before releasing to students, verify:

- [ ] Codespace builds successfully (8 min first time)
- [ ] Port 6080 accessible, noVNC works
- [ ] Password "openems" connects to VNC
- [ ] Desktop shows with xterm
- [ ] `python3 verify_environment.py` passes all checks
- [ ] `cd examples && python3 microstrip_example.py` runs
- [ ] Results generated in microstrip_simulation/
- [ ] ParaView launches: `paraview &`
- [ ] Example plots visible in VS Code
- [ ] README.md displays correctly on GitHub

## Troubleshooting

### Build Fails

**Check GitHub Actions logs:**
- Go to Actions tab in repository
- View build logs

**Common issues:**
- Timeout (>60 min): Reduce package installs
- Out of disk: Clean apt cache in Dockerfile
- OpenEMS fails: Check dependencies installed

### Students Can't Connect

**Port 6080 not visible:**
- Instruct: PORTS tab → Forward Port → 6080
- Right-click → "Port Visibility" → "Public"

**VNC won't connect:**
- In terminal: `bash .devcontainer/start-vnc.sh`
- Check logs: `cat /tmp/novnc.log`

### Simulation Issues

**Import errors:**
```bash
python3 /workspace/test_openems.py
```

**Slow simulations:**
- Use default 4-core Codespace
- Reduce mesh resolution
- Shorter traces

## Going Further

### GitHub Classroom Integration

1. Create organization: github.com/orgs
2. Set up Classroom: classroom.github.com
3. Create assignment from this template
4. Students auto-fork and submit via PR

### Pre-build Container

Speed up launches by pre-building:

```yaml
# .github/workflows/prebuild.yml
name: Prebuild Container
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build container
        run: docker build -t ghcr.io/${{ github.repository }}:latest .
```

### Add Auto-Grading

```yaml
# .github/workflows/test.yml
name: Test Assignment
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run student code
        run: python3 assignment.py
      - name: Check output
        run: test -f results.png && echo "✓ Pass"
```

## Student Feedback

Monitor these for improvements:
- Time to complete first simulation
- Common errors (check verify script output)
- Codespace hour usage
- Assignment submission quality
- Student questions/issues

## Support Resources

**Documentation:**
- OpenEMS: https://docs.openems.de/
- Codespaces: https://docs.github.com/codespaces
- Docker: https://docs.docker.com/

**Community:**
- OpenEMS Forum: https://www.elmerfem.org/forum
- GitHub Discussions: Enable in your repo
- Course Q&A: Piazza, Discord, etc.

**Help:**
- Students: Direct to QUICKSTART.md
- Instructors: See INSTRUCTOR_GUIDE.md
- Issues: Open on GitHub

## Success Metrics

**Track these indicators:**
- ✓ % students complete first simulation in <10 min
- ✓ % environment verification passes
- ✓ Average Codespace build time
- ✓ Assignment completion rate
- ✓ Student satisfaction scores

**Goals:**
- 95%+ successful first launch
- <5 min to first simulation result
- <10% support tickets
- Students focus on learning, not setup!

## Next Steps

1. **Deploy:** Push to GitHub
2. **Test:** Launch own Codespace, verify
3. **Document:** Customize README with your course info
4. **Share:** Give students repository link
5. **Iterate:** Gather feedback, improve

## Contact

**Repository maintainer:** [Your Name]
**Email:** [your.email@university.edu]
**Office hours:** [Your schedule]

---

## One-Line Summary

**"Zero-install PCB simulation environment for students - just click and code!"**

---

## Quick Start Command Summary

```bash
# For students:
python3 verify_environment.py        # Test setup
cd examples                          # Go to examples
python3 microstrip_example.py        # Run simulation
paraview &                           # Visualize fields

# For instructors:
git clone https://github.com/YOUR_USERNAME/REPO_NAME
cd REPO_NAME
# Edit examples, add assignments
git add .
git commit -m "Add course materials"
git push
```

🎉 **You're ready to teach PCB simulation with zero setup hassles!** 🎉
