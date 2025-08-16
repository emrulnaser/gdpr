#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting build.sh for esecurity project..."

# 1. Update pip
pip install --upgrade pip

# 2. Install requirements
pip install -r requirements.txt

# 3. Install Chromium (if using Playwright)
# Only needed if you still plan to use Playwright
# playwright install chromium

# 4. Any other setup commands
echo "Build setup completed successfully."
