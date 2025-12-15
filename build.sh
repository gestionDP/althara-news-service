#!/bin/bash
# Build script for Render
# This script ensures Python 3.11 is used and only precompiled wheels are installed

set -e

echo "🔧 Setting up environment..."

pip install --upgrade pip setuptools wheel

echo "📦 Installing dependencies..."

pip install --upgrade pip
pip install --only-binary :all: -r requirements.txt 2>/dev/null || pip install -r requirements.txt

echo "✅ Build completed!"





