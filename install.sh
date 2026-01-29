#!/bin/sh
set -e

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run as root (sudo ./install.sh)"
    exit 1
fi

echo "Checking dependencies..."

# Check python
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is not installed."
    exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl is not installed."
    exit 1
fi

echo "Installing quarkn..."

rm -rf /usr/local/bin/quarkn

curl -fsSL https://raw.githubusercontent.com/quadakr/quarkn/main/quarkn.py \
    -o /usr/local/bin/quarkn

chmod +x /usr/local/bin/quarkn

echo "quarkn installed to /usr/local/bin/quarkn"
echo "Run: quarkn --help"
