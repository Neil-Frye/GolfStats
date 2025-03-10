#!/bin/bash
# Minimalist build script for Vercel - aims for smallest possible deployment

echo "=== Starting ultra-minimal build for Vercel deployment ==="

# Clean any cached pip packages or old builds
echo "=== Cleaning any previous Python packages ==="
rm -rf __pycache__ .pytest_cache .mypy_cache
find . -name "*.pyc" -delete

# Print Python version for debugging
python --version
echo "=== Using Python from: $(which python) ==="

# Install ONLY the minimal API requirements
echo "=== Installing ultra-minimal dependencies from api/requirements.txt only ==="
pip install --upgrade pip
pip install -r api/requirements.txt

# Verify we're not pulling in backend requirements
echo "=== Verifying no unexpected packages are installed ==="
if pip freeze | grep -q selenium; then
  echo "WARNING: selenium is still installed despite being excluded"
fi
if pip freeze | grep -q webdriver-manager; then
  echo "WARNING: webdriver-manager is still installed despite being excluded"
fi
if pip freeze | grep -q pyppeteer; then
  echo "WARNING: pyppeteer is still installed despite being excluded"
fi

# Create necessary directories for Vercel output
mkdir -p .vercel/output/functions
mkdir -p .vercel/output/static

# Copy frontend directly to static output
echo "=== Copying frontend assets to static output ==="
cp -r frontend/* .vercel/output/static/ 2>/dev/null || echo "No frontend files to copy"

# List installed packages and their sizes (for debugging)
echo "=== Checking installed dependencies sizes ==="
pip list

# Calculate total size of the installation
echo "=== Calculating bundle size ==="
du -sh "$(python -c 'import site; print(site.getsitepackages()[0])')"

# Set execute permissions
chmod +x vercel.json

echo "=== Build complete ==="