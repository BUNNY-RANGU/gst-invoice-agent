#!/usr/bin/env bash
set -euo pipefail

# Install rustup (non-interactive) so python-bidi can build
curl https://sh.rustup.rs -sSf | sh -s -- -y

# Make cargo/rust available in PATH for remainder of build
export PATH="$HOME/.cargo/bin:$PATH"

# Upgrade pip tooling and install Python dependencies
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# Continue with normal build step(s) in your project setup
# If you have a static site build command, add it here.
# (Example for streamlit deploy via a custom adapter may not need extra steps.)

echo "Netlify build dependency install completed."
