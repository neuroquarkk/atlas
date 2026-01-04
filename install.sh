#!/usr/bin/env bash

set -e

REPO_OWNER="neuroquarkk"
REPO_NAME="atlas"
BIN_NAME="atlas"
INSTALL_DIR="/usr/local/bin"

OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}" in
Linux*)
    ASSET_OS="linux"
    ;;
Darwin*)
    ASSET_OS="macos"
    ;;
*)
    echo "Error: unsupported operating system: ${OS}"
    exit 1
    ;;
esac

if [ "$ARCH" != "x86_64" ]; then
    echo "Error: currently only x86_64 (amd64) supported"
    echo "Detected: $ARCH"
    exit 1
fi

ASSET_NAME="atlas-${ASSET_OS}-amd64.zip"
DOWNLOAD_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/latest/download/${ASSET_NAME}"

echo "Downloading latest release..."

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

if ! curl -sL "$DOWNLOAD_URL" -o "$TEMP_DIR/$ASSET_NAME"; then
    echo "Error: failed to download release"
    exit 1
fi

echo "Extracting..."
unzip -q "$TEMP_DIR/$ASSET_NAME" -d "$TEMP_DIR"

if [ ! -f "$TEMP_DIR/$BIN_NAME" ]; then
    echo "Error: binary not found in downloaded archive"
    exit 1
fi

echo "Installing to $INSTALL_DIR"
if [ -w "$INSTALL_DIR" ]; then
    mv "$TEMP_DIR/$BIN_NAME" "$INSTALL_DIR/$BIN_NAME"
    chmod +x "$INSTALL_DIR/$BIN_NAME"
else
    echo "Sudo permissions required"
    sudo mv "$TEMP_DIR/$BIN_NAME" "$INSTALL_DIR/$BIN_NAME"
    sudo chmod +x "$INSTALL_DIR/$BIN_NAME"
fi

if command -v "$BIN_NAME" >/dev/null 2>&1; then
    echo "Installed successfully"
else
    echo "Installation completed but '$BIN_NAME' not in PATH"
    echo "Please ensure $INSTALL_DIR is in your PATH"
fi
