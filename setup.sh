#!/bin/bash
# Script de instalare automată a dependențelor pentru Unikernel Benchmarking Framework
set -e

echo -e "\033[1;34m========================================================\033[0m"
echo -e "\033[1;37m       INSTALARE DEPENDENȚE FRAMEWORK BENCHMARK     \033[0m"
echo -e "\033[1;34m========================================================\033[0m"

# 1. Pachete de sistem (APT)
echo -e "\n\033[1;33m>>> 1. Se instalează utilitarele de sistem (QEMU, wrk, Python)...\033[0m"
sudo apt-get update
sudo apt-get install -y qemu-kvm qemu-system-x86 wrk python3 python3-pip curl wget

# 2. Pachete Python
echo -e "\n\033[1;33m>>> 2. Se instalează pachetele de Python (tabulate, matplotlib, psutil)...\033[0m"
pip3 install --user --break-system-packages tabulate matplotlib psutil

# 3. Instalare KraftKit (pentru Unikraft)
echo -e "\n\033[1;33m>>> 3. Se verifică instalarea KraftKit...\033[0m"
if ! command -v kraft &> /dev/null; then
    echo "KraftKit nu a fost găsit. Se instalează..."
    curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh
else
    echo -e "\033[1;32m[OK]\033[0m KraftKit este deja instalat."
fi

# 4. Instalare OPS (pentru NanoVMs)
echo -e "\n\033[1;33m>>> 4. Se verifică instalarea NanoVMs (ops)...\033[0m"
if ! command -v ops &> /dev/null; then
    echo "Utilitarul 'ops' nu a fost găsit. Se instalează..."
    curl https://ops.city/get.sh -sSfL | sh
else
    echo -e "\033[1;32m[OK]\033[0m OPS (NanoVMs) este deja instalat."
fi

echo -e "\n\033[1;34m========================================================\033[0m"
echo -e "\033[1;32m Instalare finalizată cu succes!\033[0m"
echo -e "Pentru a începe, rulează:\n  \033[1;37m./uni_benchmark\033[0m"
echo -e "\033[1;34m========================================================\033[0m"

