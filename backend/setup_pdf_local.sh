#!/bin/bash
# Install dependencies for WeasyPrint on macOS
echo "Installing WeasyPrint dependencies via Homebrew..."
brew install cairo pango gdk-pixbuf libffi

echo "Dependencies installed. You may need to reinstall weasyprint if issues persist:"
echo "pip install --force-reinstall weasyprint"
