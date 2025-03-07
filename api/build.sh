#!/bin/bash
# Install system dependencies required for cryptography package
apt-get update -y
apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# Install Python dependencies
pip install -r ../backend/requirements.txt