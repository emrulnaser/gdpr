#!/usr/bin/env bash

# Exit on error
set -o errexit

# Define the installation directory within Render's writable space
STORAGE_DIR=/opt/render/project/.render

# Create directory for Chrome and ChromeDriver if it doesn't exist
mkdir -p $STORAGE_DIR/chrome

# Versions to download
CHROME_VERSION="139.0.7258.68"
CHROMEDRIVER_VERSION="139.0.7258.68" # Must match Chrome version

# Install Google Chrome if not already present
if [[ ! -d $STORAGE_DIR/chrome/chrome-linux64 ]]; then
    echo "--- Downloading Google Chrome ---"
    wget -P $STORAGE_DIR/chrome/ "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip"
    unzip $STORAGE_DIR/chrome/chrome-linux64.zip -d $STORAGE_DIR/chrome/
    rm $STORAGE_DIR/chrome/chrome-linux64.zip
    echo "--- Google Chrome installed ---"
else
    echo "--- Google Chrome already present in cache ---"
fi

# Install ChromeDriver if not already present
if [[ ! -f $STORAGE_DIR/chrome/chromedriver-linux64/chromedriver ]]; then
    echo "--- Downloading ChromeDriver ---"
    wget -P $STORAGE_DIR/chrome/ "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
    unzip $STORAGE_DIR/chrome/chromedriver-linux64.zip -d $STORAGE_DIR/chrome/
    rm $STORAGE_DIR/chrome/chromedriver-linux64.zip
    echo "--- ChromeDriver installed ---"
else
    echo "--- ChromeDriver already present in cache ---"
fi

# Add Chrome and ChromeDriver paths to PATH environment variable
export PATH="${PATH}:$STORAGE_DIR/chrome/chrome-linux64:$STORAGE_DIR/chrome/chromedriver-linux64"

echo "--- Build script finished ---"
