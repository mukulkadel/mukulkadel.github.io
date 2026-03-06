#!/bin/bash
# Quick migration runner script

if [ -z "$1" ]; then
    echo "Usage: ./run-migration.sh <wordpress_url>"
    echo "Example: ./run-migration.sh https://mukulkadel.com"
    exit 1
fi

WORDPRESS_URL=$1

echo "=========================================="
echo "WordPress to Jekyll Migration"
echo "=========================================="
echo ""
echo "Source WordPress URL: $WORDPRESS_URL"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.6 or higher"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if requests library is installed
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "📦 Installing required Python packages..."
    pip3 install requests
fi

echo ""
echo "Starting migration..."
echo ""

# Run migration
python3 migrate.py "$WORDPRESS_URL" ./

echo ""
echo "=========================================="
echo "Migration Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review the converted posts in _posts/"
echo "2. Download media files manually"
echo "3. Run 'bundle exec jekyll serve' to test locally"
echo "4. Commit changes with 'git add . && git commit -m \"Migrate from WordPress\"'"
echo "5. Push to GitHub with 'git push origin main'"
echo ""
