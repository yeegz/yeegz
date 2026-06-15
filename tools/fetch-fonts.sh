#!/usr/bin/env bash
# Downloads the variable fonts the build subsets + embeds (Open Font License).
set -e
cd "$(dirname "$0")"
mkdir -p fonts
base="https://raw.githubusercontent.com/google/fonts/main/ofl"
curl -fsSL -o fonts/Archivo.ttf      "$base/archivo/Archivo%5Bwdth%2Cwght%5D.ttf"
curl -fsSL -o fonts/JBMono.ttf       "$base/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
curl -fsSL -o fonts/SpaceGrotesk.ttf "$base/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf"
curl -fsSL -o fonts/Amiri.ttf        "$base/amiri/Amiri-Regular.ttf"
echo "fonts fetched into ./fonts"
