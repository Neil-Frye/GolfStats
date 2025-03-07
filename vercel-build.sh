#!/bin/bash
# This script runs during Vercel's build process

# Install Python dependencies including cryptography
pip install -r backend/requirements.txt

# Create necessary directories
mkdir -p .vercel/output/functions

# Set execute permissions for later steps
chmod +x vercel.json