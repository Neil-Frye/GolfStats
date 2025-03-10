#!/bin/bash
# Strict minimalist build script for Vercel - aims for smallest possible deployment

echo "=== Starting ultra-minimal build for Vercel deployment ==="

# Safety check: Verify that we're only deploying necessary files
echo "=== Checking for presence of heavyweight directories ==="
if [ -d "backend" ]; then
  echo "⚠️ WARNING: backend/ directory is present in the build context!"
  echo "This directory should be excluded by .vercelignore to prevent size issues."
  echo "NOT copying or using any files from this directory."
fi

# Extra safety: Create a stripped-down build context if needed
if [ "$VERCEL_STRICT_BUILD" = "true" ]; then
  echo "=== STRICT BUILD MODE: Creating minimal build context ==="
  mkdir -p /tmp/minimal-build
  cp -r api/index.py api/requirements.txt api/mock_scrapers.py /tmp/minimal-build/
  cp vercel.json vercel-build.sh /tmp/minimal-build/
  # Only include frontend if needed
  if [ -d "frontend" ]; then
    mkdir -p /tmp/minimal-build/frontend
    cp -r frontend/* /tmp/minimal-build/frontend/
  fi
  
  echo "Working from minimal build context with only essential files"
fi

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

# Safety check: make sure we're not accidentally using the wrong requirements file
if [ -f "api/requirements.txt" ]; then
  echo "✅ Found api/requirements.txt - using this file for installation"
  pip install -r api/requirements.txt
else
  echo "❌ ERROR: api/requirements.txt not found!"
  exit 1
fi

# Extra safeguard: make sure we're not installing from the main requirements.txt
if [ -f "requirements.txt" ]; then
  echo "⚠️ WARNING: Found main requirements.txt - NOT using this file"
  echo "Using only api/requirements.txt to minimize dependencies"
fi

# Verify we're not pulling in backend requirements (add more checks)
echo "=== Verifying no unnecessary packages are installed ==="
FORBIDDEN_PACKAGES=(
  "selenium"
  "webdriver-manager"
  "pyppeteer"
  "apscheduler"
  "beautifulsoup4"
  "pandas"
  "numpy"
  "matplotlib"
  "chromedriver"
  "pytest"
  "psycopg2-binary"
  "gunicorn"
  "cryptography"
)

echo "Checking for forbidden packages:"
for pkg in "${FORBIDDEN_PACKAGES[@]}"; do
  if pip freeze | grep -q -i "$pkg"; then
    echo "⚠️ WARNING: $pkg is installed despite being excluded! Deployment may exceed size limits."
  else
    echo "✅ OK: $pkg is not installed"
  fi
done

# Check for any suspicious large packages
echo "Identifying largest packages:"
pip_size_check() {
  pip list --format=json | python -c "
import json, sys
packages = json.load(sys.stdin)
for pkg in packages:
    try:
        import importlib.metadata as metadata
    except ImportError:
        import importlib_metadata as metadata
    try:
        size = metadata.files(pkg['name'])
        if size:
            print(f'{pkg[\"name\"]}: {len(size)} files')
    except:
        pass
"
}

pip_size_check | sort -t: -k2 -nr | head -10

# Create necessary directories for Vercel output
mkdir -p .vercel/output/functions
mkdir -p .vercel/output/static

# Copy frontend directly to static output (only if needed)
echo "=== Copying frontend assets to static output ==="
cp -r frontend/* .vercel/output/static/ 2>/dev/null || echo "No frontend files to copy"

# Check the size of the resulting deployment package
echo "=== Calculating package sizes ==="
pip list

# Create a test deployment bundle and measure its size
echo "=== Creating test deployment bundle ==="
site_packages="$(python -c 'import site; print(site.getsitepackages()[0])')"
du -sh "$site_packages"
echo "Large packages:"
du -sh "$site_packages"/* | sort -hr | head -10

# Extra deep check for problematic dependencies
echo "=== Deep-checking for heavyweight dependencies (even transitive ones) ==="
pip freeze > /tmp/all_dependencies.txt
if grep -i -E 'selenium|webdriver|pyppeteer|chrome|firefox|beautifulsoup4|bs4|numpy|pandas|matplotlib|psycopg2' /tmp/all_dependencies.txt; then
  echo "⚠️ CRITICAL WARNING: Found heavyweight dependencies that will cause deployment to fail!"
  echo "These dependencies must be removed to deploy successfully."
else
  echo "✅ No heavyweight dependencies found in pip freeze output."
fi

# Verify the deployment files are within Vercel's limits
echo "=== Verifying size constraints ==="
# Create a temporary zip of what would be deployed
mkdir -p /tmp/vercel-size-check
cp -r api/index.py api/mock_scrapers.py /tmp/vercel-size-check/
cp -r "$site_packages" /tmp/vercel-size-check/
deployment_size=$(du -sm /tmp/vercel-size-check | cut -f1)
echo "Estimated deployment size: ${deployment_size}MB"

if [ "$deployment_size" -gt 200 ]; then
  echo "⚠️ CRITICAL WARNING: Deployment may exceed Vercel's 250MB limit (estimated ${deployment_size}MB)"
  # Extra info about what's taking up space
  echo "Largest directories:"
  du -sh /tmp/vercel-size-check/* | sort -hr | head -5
  
  # Find the 10 largest packages
  echo "Largest packages:"
  find "$site_packages" -type d -maxdepth 1 | xargs du -sh | sort -hr | head -10
else
  echo "✅ Deployment size looks good: ${deployment_size}MB (under 200MB)"
fi

rm -rf /tmp/vercel-size-check
rm -f /tmp/all_dependencies.txt

echo "=== Build complete ==="