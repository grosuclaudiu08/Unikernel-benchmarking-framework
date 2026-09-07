#!/bin/bash
set -euo pipefail
export PATH="$PATH:$HOME/.local/bin"

echo "Pornire Nginx folosind Unikraft Native..."

kraft rm  nginx-native >/dev/null 2>&1 || true

if [ ! -f ".unikraft/build/nginx-native_qemu-x86_64" ]; then
    kraft build
fi

kraft run -M 256M -p 8080:80 --rm -d --name nginx-native

echo "Instanța rulează în fundal pe portul 8080."
echo "Pentru a o opri, poți rula:"
echo "  kraft rm nginx-native"
