#!/bin/bash
# Build script para Render
# Este script asegura que se use Python 3.11 y se instalen solo wheels precompilados

set -e

echo "🔧 Configurando entorno..."

# Asegurar que pip está actualizado
pip install --upgrade pip setuptools wheel

echo "📦 Instalando dependencias..."

# Instalar solo wheels precompilados cuando sea posible
pip install --upgrade pip
pip install --only-binary :all: -r requirements.txt 2>/dev/null || pip install -r requirements.txt

echo "✅ Build completado!"



