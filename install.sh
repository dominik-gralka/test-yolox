#!/bin/bash
# Installation script for YOLOX API
# This ensures dependencies are installed in the correct order

set -e  # Exit on error

echo "🚀 Installing YOLOX API dependencies..."
echo ""

# Step 1: Install base ML dependencies (torch, etc.)
echo "📦 Step 1/3: Installing PyTorch and base ML dependencies..."
pip install -r requirements-base.txt
echo "✓ PyTorch installed"
echo ""

# Step 2: Install main dependencies
echo "📦 Step 2/3: Installing API dependencies..."
pip install -r requirements.txt
echo "✓ API dependencies installed"
echo ""

# Step 3: Install YOLOX
echo "📦 Step 3/3: Installing YOLOX..."
pip install git+https://github.com/Megvii-BaseDetection/YOLOX.git
echo "✓ YOLOX installed"
echo ""

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Download YOLOX model weights (see YOLOX_SETUP.md)"
echo "2. Configure .env file (cp .env.example .env)"
echo "3. Start the API: python -m app.main"
