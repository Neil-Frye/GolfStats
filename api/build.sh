#!/bin/bash

# Force Python 3.9 for Vercel deployment
echo "Vercel build started"
echo "Python version: $(python --version)"

# Check if using wrong Python version and warn
if [[ $(python -c "import sys; print(sys.version_info.major, sys.version_info.minor)") != "3 9" ]]; then
  echo "WARNING: Not using Python 3.9, which may cause compatibility issues!"
  echo "Current Python version: $(python --version)"
  
  # Check for alternative Python installations
  if command -v python3.9 &> /dev/null; then
    echo "Python 3.9 is available as python3.9"
    echo "Using: $(python3.9 --version)"
    
    # Create a symlink to use Python 3.9
    ln -sf $(which python3.9) python
    export PATH=.:$PATH
    echo "Setup Python 3.9 symlink. Now using: $(python --version)"
  fi
fi

# Install just our minimal requirements
pip install -r requirements.txt

echo "Build completed"