# OpenEMS + ElmerFEM Development Container with VNC Desktop
# Force amd64/x86_64 architecture for better compatibility
# (OpenEMS build tools are more mature on x86_64)
# build command:
#   docker buildx build --push --platform linux/amd64 --tag ghcr.io/202510-phys-390/openems:1 .devcontainer
#
# Includes:
#   - OpenEMS: FDTD electromagnetic simulator (high-frequency)
#   - ElmerFEM: Finite element multiphysics (DC/low-frequency, thermal, structural)
FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Fix potential GPG key issues
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/lib/apt/lists/partial

# Set up VNC environment variables
ENV DISPLAY=:1
ENV VNC_PORT=5901
ENV NOVNC_PORT=6080
ENV VNC_RESOLUTION=1920x1080

# Install base dependencies
RUN apt-get update && apt-get install -y \
    # Build essentials
    build-essential \
    cmake \
    git \
    wget \
    curl \
    pkg-config \
    autoconf \
    automake \
    libtool \
    # Python and pip
    python3 \
    python3-pip \
    python3-dev \
    python3-tk \
    python3-pil.imagetk \
    # OpenEMS dependencies
    libtinyxml-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libvtk9-dev \
    libboost-all-dev \
    libcgal-dev \
    libcgal-qt5-dev \
    libfftw3-dev \
    libfparser-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    qttools5-dev \
    libvtk9-qt-dev \
    # VNC and desktop environment
    tigervnc-standalone-server \
    tigervnc-common \
    xfce4 \
    xfce4-terminal \
    xterm \
    dbus-x11 \
    # noVNC for browser access
    novnc \
    websockify \
    net-tools \
    # Additional utilities
    vim \
    nano \
    htop \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up VNC password (default: openems)
RUN mkdir -p ~/.vnc && \
    echo "openems" | vncpasswd -f > ~/.vnc/passwd && \
    chmod 600 ~/.vnc/passwd

# Clone and build CSXCAD (OpenEMS geometry library)
WORKDIR /tmp
RUN git clone https://github.com/thliebig/CSXCAD.git
WORKDIR /tmp/CSXCAD
RUN mkdir build
WORKDIR /tmp/CSXCAD/build
RUN cmake .. \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING=OFF
RUN make -j$(nproc) VERBOSE=1
RUN make install
RUN ldconfig

# Clone and build OpenEMS
WORKDIR /tmp
RUN git clone https://github.com/thliebig/openEMS.git
WORKDIR /tmp/openEMS
RUN mkdir build
WORKDIR /tmp/openEMS/build
RUN cmake .. \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING=OFF
RUN make -j$(nproc) VERBOSE=1
RUN make install
RUN ldconfig

# Install Python bindings for CSXCAD (use already cloned repo)
WORKDIR /tmp/CSXCAD/python
ENV CSXCAD_INSTALL_PATH=/usr/local
RUN pip3 install .

# Install Cython and scientific Python packages
RUN pip3 install --no-cache-dir \
    numpy \
    matplotlib \
    Cython

# Install Python bindings for OpenEMS (use already cloned repo)
WORKDIR /tmp/openEMS/python
ENV OPENEMS_INSTALL_PATH=/usr/local
RUN pip3 install .

# Clean up source directories
WORKDIR /tmp
RUN rm -rf /tmp/CSXCAD /tmp/openEMS

# Install additional Python packages
RUN pip3 install --no-cache-dir \
    h5py \
    scipy \
    pandas \
    scikit-rf

# Note: ParaView is skipped due to package conflicts with python3-vtk9
# For visualization, use matplotlib (included) or install ParaView separately:
# apt-get install --no-install-recommends paraview
# Or use Python-based visualization with vtk

# ========================================================================
# KiCAD and PCB Import Tools
# ========================================================================

# Install KiCAD 9.0+ from official PPA
# Install dependencies for PPA management and GPG key handling
RUN apt-get update && apt-get install -y \
    software-properties-common \
    dirmngr \
    ca-certificates \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add KiCad 9.0 PPA and install
# Using --yes to avoid prompts, --no-update to handle apt update separately
RUN add-apt-repository --yes --no-update ppa:kicad/kicad-9.0-releases \
    && apt-get update \
    && apt-get install -y --install-recommends \
    kicad \
    kicad-libraries \
    gerbv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install gerber2ems only on AMD64 (triangle package has ARM64 compilation issues)
# ARM64 users can still use Docker emulation (--platform linux/amd64) if needed
RUN if [ "$(uname -m)" = "x86_64" ]; then \
        echo "Installing gerber2ems on AMD64..." && \
        apt-get update && \
        apt-get install -y pipx && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* && \
        pipx ensurepath && \
        git clone https://github.com/antmicro/gerber2ems.git /tmp/gerber2ems && \
        cd /tmp/gerber2ems && \
        pipx install --system-site-packages . && \
        rm -rf /tmp/gerber2ems && \
        export PATH="/root/.local/bin:${PATH}"; \
    else \
        echo "Skipping gerber2ems on ARM64 (use --platform linux/amd64 for emulation if needed)"; \
    fi

# Add pipx binaries to PATH for all users (if pipx was installed)
ENV PATH="/root/.local/bin:${PATH}"

# ========================================================================
# ElmerFEM Installation
# ========================================================================

# Install ElmerFEM build dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    gfortran \
    # ElmerFEM dependencies
    liblapack-dev \
    libblas-dev \
    libmumps-seq-dev \
    libhypre-dev \
    libparmetis-dev \
    libmetis-dev \
    # Mesh tools
    gmsh \
    python3-gmsh \
    # Qt for ElmerGUI (qtbase5-dev includes Qt5::Xml)
    qtbase5-dev \
    libqt5opengl5-dev \
    libqt5svg5-dev \
    qttools5-dev \
    libqwt-qt5-dev \
    # VTK for visualization (already installed for OpenEMS)
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone and build ElmerFEM from source
WORKDIR /tmp
RUN git clone https://github.com/ElmerCSC/elmerfem.git
WORKDIR /tmp/elmerfem
RUN mkdir build
WORKDIR /tmp/elmerfem/build

# Configure ElmerFEM with GUI support
RUN cmake .. \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DCMAKE_BUILD_TYPE=Release \
    -DWITH_MPI=FALSE \
    -DWITH_OpenMP=TRUE \
    -DWITH_MUMPS=TRUE \
    -DWITH_Hypre=TRUE \
    -DWITH_ElmerGUI=TRUE \
    -DWITH_ELMERGRID=TRUE \
    -DWITH_MATC=TRUE

# Build and install (this takes a while)
RUN make -j$(nproc)
RUN make install
RUN ldconfig

# Clean up ElmerFEM source
WORKDIR /tmp
RUN rm -rf /tmp/elmerfem

# Install Python packages for ElmerFEM pre/post-processing
# Note: gmsh is installed via apt (python3-gmsh) for ARM64 compatibility
RUN pip3 install --no-cache-dir \
    meshio \
    pygmsh \
    pyvista

# ========================================================================
# Node.js and npm Installation (for Claude Code support)
# ========================================================================

# Install Node.js 20.x LTS from NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Verify installation
RUN node --version && npm --version

# Set up workspace
WORKDIR /workspace

# Create directories for student work
RUN mkdir -p /workspace/simulations \
    /workspace/pcb-designs \
    /workspace/kicad-examples \
    /workspace/examples \
    /workspace/elmerfem-examples

# Expose VNC and noVNC ports
EXPOSE 5901 6080

# Default command (will be overridden by devcontainer.json)
CMD ["/bin/bash"]
