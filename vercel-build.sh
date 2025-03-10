#!/bin/bash
# This script runs during Vercel's build process

# Install Python dependencies
echo "=== Installing dependencies from api/requirements.txt ==="
pip install --upgrade pip
pip install -r api/requirements.txt

# Create necessary directories
mkdir -p .vercel/output/functions

# Set execute permissions for later steps
chmod +x vercel.json