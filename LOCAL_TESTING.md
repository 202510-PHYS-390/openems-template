# Local Docker Testing Guide

This guide explains how to build and test the OpenEMS devcontainer locally before deploying to GitHub Codespaces.

## Prerequisites

- Docker Desktop installed and running
- At least 8GB RAM allocated to Docker
- 10GB free disk space

## Build the Docker Image

```bash
# From the repository root
cd /path/to/openems

# Build the image (will take 10-15 minutes)
docker build -t openems-dev -f .devcontainer/Dockerfile .
```

## Run the Container

```bash
# Run with workspace mounted
docker run -it \
  --name openems-test \
  -p 5901:5901 \
  -p 6080:6080 \
  -v $(pwd):/workspace \
  openems-dev /bin/bash
```

## Inside the Container

Once inside the container:

```bash
# Run post-create setup
bash .devcontainer/post-create.sh

# Test OpenEMS installation
python3 /workspace/test_openems.py

# Start VNC server
bash .devcontainer/start-vnc.sh
```

## Access the Desktop

### Option 1: Web Browser (Recommended)
1. Open browser to: http://localhost:6080/vnc.html
2. Click "Connect"
3. Enter password: `openems`
4. You should see the XFCE desktop

### Option 2: VNC Client
1. Use any VNC client (TigerVNC, RealVNC, etc.)
2. Connect to: `localhost:5901`
3. Password: `openems`

## Test the Environment

Inside the container (via terminal or desktop):

```bash
# Verify installation
python3 test_openems.py

# Run example (once created)
cd examples
python3 microstrip_example.py

# Visualize with matplotlib (ParaView not included due to package conflicts)
# Results will be plotted using matplotlib in the example scripts
```

## Troubleshooting

### Build Fails

**Check Docker resources:**
- Ensure Docker has at least 8GB RAM
- Check available disk space

**Common issues:**
- Network timeout during apt-get or git clone
  - Solution: Retry the build
- Python package installation fails
  - Solution: Check pip version, update if needed

### VNC Won't Start

```bash
# Check if VNC process is running
ps aux | grep vnc

# Check VNC logs
cat ~/.vnc/*.log

# Manually kill and restart
vncserver -kill :1
vncserver :1 -geometry 1280x720 -depth 24
```

### Can't Connect to noVNC

```bash
# Check if websockify is running
ps aux | grep websockify

# Check noVNC logs
cat /tmp/novnc.log

# Restart websockify manually
websockify --web=/usr/share/novnc 6080 localhost:5901 &
```

### Import Errors

```bash
# Test individual imports
python3 -c "import CSXCAD; print(CSXCAD.__version__)"
python3 -c "import openEMS"

# Check library paths
ldconfig -p | grep openEMS
```

## Clean Up

```bash
# Exit container
exit

# Stop and remove container
docker stop openems-test
docker rm openems-test

# Remove image (if rebuilding)
docker rmi openems-dev
```

## Next Steps

Once local testing succeeds:

1. Push to GitHub repository
2. Create Codespace from GitHub
3. Verify same functionality in Codespaces
4. Create microstrip example
5. Test with students

## Build Time Estimates

- **First build:** 10-15 minutes (downloads, compiles OpenEMS)
- **Subsequent builds:** 2-5 minutes (uses Docker cache)
- **Container startup:** 10-20 seconds
- **VNC startup:** 5-10 seconds

## Resource Usage

- **Image size:** ~2-3 GB
- **RAM usage:** 2-4 GB (4-6 GB with ParaView)
- **CPU:** Depends on simulation complexity

## Tips for Faster Iteration

1. **Use Docker build cache:** Don't change early Dockerfile lines frequently
2. **Test incrementally:** Test each layer as you build
3. **Keep container running:** Use `docker exec` to run commands without restarting
4. **Mount workspace:** Changes to mounted files are immediate

```bash
# Execute commands in running container
docker exec -it openems-test python3 test_openems.py
```

## Validation Checklist

Before deploying to Codespaces:

- [ ] Docker image builds without errors
- [ ] Container starts successfully
- [ ] VNC server starts (port 5901)
- [ ] noVNC accessible (port 6080)
- [ ] Desktop loads with XFCE
- [ ] Python imports work (CSXCAD, openEMS)
- [ ] test_openems.py passes all checks
- [ ] Example simulation runs (once created)
- [ ] Results can be viewed/plotted with matplotlib

## Common Docker Commands

```bash
# List running containers
docker ps

# View container logs
docker logs openems-test

# Attach to running container
docker attach openems-test

# Copy files from container
docker cp openems-test:/workspace/results ./local-results

# Inspect container
docker inspect openems-test

# View resource usage
docker stats openems-test
```
