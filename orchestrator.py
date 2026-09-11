#!/usr/bin/env python3
import argparse
import subprocess
import time
import os
import urllib.request
import teardown
import threading
import re

def wait_for_port(port, timeout=15):
    print(f">> Așteptare bootare și inițializare (port {port})...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(f"http://127.0.0.1:{port}", timeout=1)
            if response.getcode() == 200:
                print(f"[OK] Instanța a bootat și răspunde corect pe portul {port}.")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    print(f"[EROARE] Timeout de {timeout}s la așteptarea portului {port}.")
    return False

def clean_kraft_instance(name):
    """Șterge instanța din baza de date kraft pentru a evita erori 'name already in use'."""
    subprocess.run(["kraft", "rm", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def monitor_boot_time(process, start_time, target_log, instance_name):
    last_internal_time = None
    for line in iter(process.stdout.readline, ''):
        # Căutăm un pattern de tip [0.229735] sau [  0.01234 ]
        match = re.search(r'\[\s*([\d\.]+)\s*\]', line)
        if match:
            last_internal_time = match.group(1)
            
        if target_log in line:
            boot_duration = time.time() - start_time
            print(f"[Metrică Host] {instance_name} a bootat în {boot_duration:.4f} secunde (End-to-End).")
            if last_internal_time:
                print(f"[Metrică Internă] {instance_name} timp intern din log: {last_internal_time} secunde.")
            else:
                print(f"[Metrică Internă] {instance_name} nu a afișat timestamp intern în loguri.")
            target_log = "FOUND_ALREADY"

def run_unikraft_native():
    print("\n=== Rulare Benchmark: Unikraft Native ===")
    cwd = "unikraft/nginx-native"
    clean_kraft_instance("nginx-native")
    
    # 1. Build dacă nu există deja
    if not os.path.exists(os.path.join(cwd, ".unikraft/build/nginx-native_qemu-x86_64")):
        print(">> Imaginea nativă lipsește. Se rulează 'kraft build'...")
        subprocess.run(["kraft", "build"], cwd=cwd, check=True)
    else:
        print(">> Imaginea nativă există deja, sărim peste compilare.")
    
    # 2. Lansare folosind limitele hardware din teardown.py
    flags = teardown.get_isolation_flags("unikraft")
    cmd = ["kraft", "run", "-p", "8080:80", "--rm", "--name", "nginx-native"] + flags

    start_time = time.time()
    process = subprocess.Popen(cmd, cwd = cwd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.DEVNULL, text = True)
    log_thread = threading.Thread(target = monitor_boot_time, args = (process, start_time, "Interface is up", "Unikraft Native"))
    log_thread.daemon = True
    log_thread.start()

    # print(">> Se rulează QEMU:", " ".join(cmd))
    # subprocess.run(cmd, cwd=cwd, check=True)
    
    # 3. Așteaptă Nginx
    wait_for_port(8080)

def run_unikraft_bincompat():
    print("\n=== Rulare Benchmark: Unikraft Bincompat ===")
    cwd = "unikraft/nginx-bincompat"
    clean_kraft_instance("nginx-bincompat")
    
    flags = teardown.get_isolation_flags("unikraft")
    base_image = "unikraft.org/base:latest"
    cmd = ["kraft", "run", "-p", "8080:80", "--rm", "--name", "nginx-bincompat", 
       "--rootfs", "./rootfs"] + flags + [base_image, "--", "/nginx", "-c", "/etc/nginx/nginx.conf"]
    print(">> Se rulează QEMU:", " ".join(cmd))

    start_time = time.time()
    process = subprocess.Popen(cmd, cwd = cwd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.DEVNULL, text = True)
    log_thread = threading.Thread(target = monitor_boot_time, args = (process, start_time, "Interface is up", "Unikraft Bincompat"))
    log_thread.daemon = True
    log_thread.start()

    # subprocess.run(cmd, cwd=cwd, check=True)
    
    # Așteaptă Nginx
    wait_for_port(8080)

def run_nanovms():
    print("\n=== Rulare Benchmark: NanoVMs ===")
    cwd = "nanovms/nginx"
    
    flags = teardown.get_isolation_flags("nanovms")
    # ops mapează automat porturile prin opțiunea -p
    cmd = ["ops", "pkg", "load", "eyberg/nginx:1.18.0", "-c", "config.json", "-p", "8080"] + flags
    print(">> Se rulează QEMU (prin ops):", " ".join(cmd))

    start_time = time.time()
    process = subprocess.Popen(cmd, cwd = cwd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.DEVNULL, text = True)
    log_thread = threading.Thread(target = monitor_boot_time, args = (process, start_time, "assigned", "NanoVMs"))
    log_thread.daemon = True
    log_thread.start()
    
    # NanoVMs rulează default în foreground, așa că folosim Popen
    # process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Așteaptă Nginx
    wait_for_port(8080)
    # ops spawn-uiește QEMU. La final, teardown.py se va asigura că este curățat.

def main():
    parser = argparse.ArgumentParser(description="Unikernel Benchmarking Orchestrator (Phase 2)")
    parser.add_argument("--target", choices=["unikraft-native", "unikraft-bincompat", "nanovms", "all"], 
                        required=True, help="Specificați ce țintă doriți să executați.")
    
    args = parser.parse_args()
    
    # PATH adjustment
    os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.local/bin")
    
    targets = []
    if args.target == "all":
        targets = ["unikraft-native", "unikraft-bincompat", "nanovms"]
    else:
        targets = [args.target]
        
    for target in targets:
        # Pre-cleanup
        teardown.teardown_qemu()
        
        if target == "unikraft-native":
            run_unikraft_native()
        elif target == "unikraft-bincompat":
            run_unikraft_bincompat()
        elif target == "nanovms":
            run_nanovms()
            
        print(f"\n--- Faza 2 finalizată pentru {target} ---")
        
        # Cleanup între runde dacă sunt lansate multiple
        if args.target == "all":
            print(f">> Curățare forțată instanță {target} înainte de următorul benchmark...")
            teardown.teardown_qemu()
            time.sleep(2)

    # Dacă rulăm o singură instanță, păstrăm scriptul deschis ca utilizatorul să o poată folosi
    if args.target != "all":
        print("\n========================================================")
        print("✅ Instanța rulează cu succes în fundal (Daemon).")
        print("🌐 Poți testa în alt terminal: curl http://localhost:8080")
        print("========================================================")
        print("Pentru a închide procesul, apasă CTRL+C sau tasta ENTER aici.")
        print("Dacă închizi acest terminal accidental, scrie în altul:")
        print("  kraft rm nginx-native (sau nginx-bincompat)")
        print("========================================================\n")
        try:
            input("Apasă [ENTER] pentru a opri instanța și a ieși curat...\n")
        except KeyboardInterrupt:
            pass
        print("Se execută oprirea...")

if __name__ == "__main__":
    main()

