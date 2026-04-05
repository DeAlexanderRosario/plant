#!/bin/bash
echo "[EdenScope] Installing stable Python 3.11 via Micromamba..."

# 1. Download Micromamba for ARM (aarch64 or armv7l)
ARCH=$(uname -m)
if [[ "$ARCH" == "aarch64" ]]; then
    MAMBA_ARCH="linux-aarch64"
elif [[ "$ARCH" == "armv7l" ]]; then
    MAMBA_ARCH="linux-armv7l"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

echo "[EdenScope] Detected architecture: $ARCH"
curl -Ls https://micro.mamba.pm/api/micromamba/$MAMBA_ARCH/latest | tar -xvj bin/micromamba

# 2. Initialize and create environment
./bin/micromamba shell init -s bash -p ~/micromamba
source ~/.bashrc

# 3. Create Python 3.11 environment
./bin/micromamba create -n edenscope python=3.11 -c conda-forge -y

echo "--------------------------------------------------------"
echo "Python 3.11 has been installed in environment 'edenscope'."
echo "To use it, run:"
echo "  ./bin/micromamba activate edenscope"
echo "  python --version"
echo "--------------------------------------------------------"
