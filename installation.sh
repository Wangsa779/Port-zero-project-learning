#!/bin/bash

# PORT-ZERO Installation Script
# Author: wangsa

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="port-zero"

echo -e "${BLUE}PORT-ZERO Installation Script${NC}"
echo "=================================="

# Check if running as root for system-wide installation
if [[ $EUID -eq 0 ]]; then
    echo -e "${GREEN}Running as root - installing system-wide${NC}"
    INSTALL_MODE="system"
else
    echo -e "${YELLOW}Running as user - installing to ~/.local/bin${NC}"
    INSTALL_DIR="$HOME/.local/bin"
    INSTALL_MODE="user"
    
    # Create user bin directory if it doesn't exist
    mkdir -p "$INSTALL_DIR"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python 3
echo -n "Checking for Python 3... "
if command_exists python3; then
    echo -e "${GREEN}✓${NC}"
    PYTHON_CMD="python3"
elif command_exists python; then
    # Check if python is python3
    if python --version 2>&1 | grep -q "Python 3"; then
        echo -e "${GREEN}✓${NC}"
        PYTHON_CMD="python"
    else
        echo -e "${RED}✗${NC}"
        echo "Python 3 is required but not found"
        exit 1
    fi
else
    echo -e "${RED}✗${NC}"
    echo "Python 3 is required but not found"
    echo "Install it with: sudo apt update && sudo apt install python3"
    exit 1
fi

# Check for pip3
echo -n "Checking for pip3... "
if command_exists pip3; then
    echo -e "${GREEN}✓${NC}"
    PIP_CMD="pip3"
elif command_exists pip; then
    echo -e "${GREEN}✓${NC}"
    PIP_CMD="pip"
else
    echo -e "${RED}✗${NC}"
    echo "pip3 is required but not found"
    echo "Install it with: sudo apt update && sudo apt install python3-pip"
    exit 1
fi

# Install required Python packages
echo "Installing Python dependencies..."
PACKAGES=(
    "pyfiglet"
)

for package in "${PACKAGES[@]}"; do
    echo -n "  Installing $package... "
    if $PIP_CMD show "$package" >/dev/null 2>&1; then
        echo -e "${YELLOW}already installed${NC}"
    else
        if [[ $INSTALL_MODE == "system" ]]; then
            $PIP_CMD install "$package" >/dev/null 2>&1
        else
            $PIP_CMD install --user "$package" >/dev/null 2>&1
        fi
        echo -e "${GREEN}✓${NC}"
    fi
done

# Copy the script
echo -n "Installing PORT-ZERO script... "
if [[ -f "PORT-ZERO.py" ]]; then
    cp "PORT-ZERO.py" "$INSTALL_DIR/$SCRIPT_NAME"
    chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "PORT-ZERO.py not found in current directory"
    exit 1
fi

# Add shebang if not present
if ! head -1 "$INSTALL_DIR/$SCRIPT_NAME" | grep -q "python3"; then
    sed -i "1i#!/usr/bin/env $PYTHON_CMD" "$INSTALL_DIR/$SCRIPT_NAME"
fi

# Update PATH for user installation
if [[ $INSTALL_MODE == "user" ]]; then
    echo -n "Updating PATH... "
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        # Add to .bashrc
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        # Add to .zshrc if it exists
        if [[ -f ~/.zshrc ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        fi
        echo -e "${YELLOW}added to shell config${NC}"
        echo -e "${YELLOW}Please run: source ~/.bashrc${NC}"
    else
        echo -e "${GREEN}✓${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Installation completed successfully!${NC}"
echo ""
echo "Usage:"
echo "  $SCRIPT_NAME <target> [options]"
echo "  $SCRIPT_NAME --help"
echo ""
echo "Examples:"
echo "  $SCRIPT_NAME 192.168.1.1"
echo "  $SCRIPT_NAME scanme.nmap.org -p 1-1000 -sV"
echo "  $SCRIPT_NAME example.com -sn"
echo ""

if [[ $INSTALL_MODE == "user" ]]; then
    echo -e "${YELLOW}Note: If 'port-zero' command is not found, restart your terminal or run:${NC}"
    echo -e "${YELLOW}source ~/.bashrc${NC}"
fi