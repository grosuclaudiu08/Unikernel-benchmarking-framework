#!/bin/bash
set -euo pipefail
export PATH="$PATH:$HOME/.local/bin"

echo "Pornire Nginx folosind Unikraft Bincompat (app-elfloader)..."
BASE_IMAGE="${BASE_IMAGE:-unikraft.org/base:latest}"
kraft run -p 8080:8080 --rm -d --name nginx-bincompat --rootfs ./rootfs "$BASE_IMAGE" -- /nginx -c /etc/nginx/nginx.conf

echo "Instanța rulează în fundal pe portul 8080."
echo "Pentru a o opri, poți rula:"
echo "  kraft rm nginx-bincompat"
