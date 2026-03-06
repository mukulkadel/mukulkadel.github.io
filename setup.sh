#!/bin/bash
# Setup script for Jekyll site

echo "Setting up Jekyll site..."

# Check if Ruby is installed
if ! command -v ruby &> /dev/null; then
    echo "❌ Ruby is not installed. Please install Ruby 3.0 or higher."
    exit 1
fi

echo "✓ Ruby found: $(ruby --version)"

# Check if Bundler is installed
if ! command -v bundle &> /dev/null; then
    echo "Installing Bundler..."
    gem install bundler
fi

echo "✓ Bundler found: $(bundle --version)"

# Install dependencies
echo ""
echo "Installing Ruby gems..."
bundle install

# Check if Jekyll is installed
if bundle list | grep -q "jekyll ("; then
    echo "✓ Jekyll installed successfully"
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To start the local server, run:"
    echo "  bundle exec jekyll serve"
    echo ""
    echo "Then open http://localhost:4000 in your browser"
else
    echo "❌ Jekyll installation failed"
    exit 1
fi
