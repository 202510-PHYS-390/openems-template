#!/bin/bash
# Complete GUI setup and launcher for OpenEMS
# This script starts VNC, noVNC, and sets up the environment
# Press Ctrl+C to stop everything

set -e

# Trap Ctrl+C and cleanup
cleanup() {
    echo ""
    echo "Shutting down GUI environment..."
    vncserver -kill :1 2>/dev/null || true
    pkill -f websockify 2>/dev/null || true
    echo "✓ VNC server stopped"
    echo "✓ noVNC stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "========================================="
echo "OpenEMS GUI Environment Setup"
echo "========================================="
echo ""

# Set environment variables for current session
export DISPLAY=:1
export MPLBACKEND=TkAgg

# Add to bashrc if not already there (for future sessions)
if ! grep -q "DISPLAY=:1" ~/.bashrc 2>/dev/null; then
    echo "Adding environment variables to ~/.bashrc..."
    echo "" >> ~/.bashrc
    echo "# GUI support for OpenEMS/matplotlib" >> ~/.bashrc
    echo "export DISPLAY=:1" >> ~/.bashrc
    echo "export MPLBACKEND=TkAgg" >> ~/.bashrc
fi

# Always create/recreate xstartup to ensure it's correct
echo "Creating VNC startup script..."
mkdir -p ~/.vnc
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS

# Start dbus
dbus-launch --exit-with-session xfce4-session &

# Keep script alive
wait
EOF
chmod +x ~/.vnc/xstartup

# Set VNC password if not already set
if [ ! -f ~/.vnc/passwd ]; then
    echo "Setting VNC password..."
    echo "openems" | vncpasswd -f > ~/.vnc/passwd
    chmod 600 ~/.vnc/passwd
fi

# Kill any existing VNC/noVNC
echo "Cleaning up any existing VNC sessions..."
vncserver -kill :1 2>/dev/null || true
pkill -f websockify 2>/dev/null || true
sleep 1

# Start VNC server
echo "Starting VNC server..."
vncserver :1 -geometry 1920x1080 -depth 24 -localhost no
echo "Waiting for desktop to initialize..."
sleep 8

# VNC server logs will show if there were issues
# (XFCE warnings are normal in containers)

# Start noVNC
echo "Starting noVNC web interface..."
websockify --web=/usr/share/novnc 6080 localhost:5901 > /tmp/novnc.log 2>&1 &
WEBSOCKIFY_PID=$!
sleep 2

echo ""
echo "========================================="
echo "✓ GUI Environment Ready!"
echo "========================================="
echo ""
echo "VNC Desktop Access:"
echo "  Browser: http://localhost:6080/vnc.html"
echo "  Password: openems"
echo ""
echo "Environment Variables Set:"
echo "  DISPLAY=:1"
echo "  MPLBACKEND=TkAgg"
echo ""
echo "You can now run Python scripts with GUI plots!"
echo "Example:"
echo "  cd Tutorials"
echo "  python3 Rect_Waveguide.py"
echo ""
echo "========================================="
echo "Press Ctrl+C to stop VNC and exit"
echo "========================================="
echo ""

# Keep script running and tail the noVNC log
# This allows Ctrl+C to trigger cleanup
tail -f /tmp/novnc.log
