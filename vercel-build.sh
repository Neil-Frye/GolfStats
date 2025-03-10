#!/bin/bash
# Optimized build script for Vercel deployment

echo "=== Starting optimized build for Vercel deployment ==="

# Print Python version for debugging
python --version
echo "=== Using Python from: $(which python) ==="

# Install minimal dependencies
echo "=== Installing optimized dependencies from api/requirements.txt ==="
pip install --upgrade pip
pip install -r api/requirements.txt

# Create necessary directories
mkdir -p .vercel/output/functions
mkdir -p .vercel/output/static

# Copy frontend directly to static output
echo "=== Copying frontend assets to static output ==="
cp -r frontend/* .vercel/output/static/ 2>/dev/null || echo "No frontend files to copy"

# Check bundle size before deployment (pip list for debugging)
echo "=== Checking installed dependencies sizes ==="
pip list

# Print current directory size
echo "=== Current directory size ==="
du -sh .

# Display ignored files (debugging)
echo "=== Files excluded by .vercelignore ==="
find . -type f -not -path "*/.git/*" | grep -v -f <(grep -v '^#' .vercelignore | sed 's/\*/\.*/g' | sed 's/^/\.\//') | wc -l

# Set execute permissions
chmod +x vercel.json

echo "=== Build complete ==="