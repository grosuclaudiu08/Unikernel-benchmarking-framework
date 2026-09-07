#!/bin/bash
export PATH=$PATH:$HOME/.local/bin

echo "Pornire Nginx folosind Unikraft Bincompat (app-elfloader)..."
kraft run -p 8080:8080 --rm -d --name nginx-bincompat --rootfs ./rootfs unikraft.org/base:latest -- /nginx -c /etc/nginx/nginx.conf

echo "Instanța rulează în fundal pe portul 8080."
echo "Pentru a o opri, poți rula:"
echo "  kraft rm nginx-bincompat"
