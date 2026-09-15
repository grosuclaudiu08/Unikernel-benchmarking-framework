#!/usr/bin/env python3
import argparse
import subprocess
import time
import os
import urllib.request
import teardown
import threading
import re
import psutil
import json

DEBUG_MODE = False
def dprint(*args, **kwargs):
    if DEBUG_MODE:
        print(*args, **kwargs)

def wait_for_port(port, timeout=15):
    dprint(f">> Așteptare bootare și inițializare (port {port})...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(f"http://127.0.0.1:{port}", timeout=1)
            if response.getcode() == 200:
                dprint(f"[OK] Instanța a bootat și răspunde corect pe portul {port}.")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    dprint(f"[EROARE] Timeout de {timeout}s la așteptarea portului {port}.")
    return False

def clean_kraft_instance(name):
    """Șterge instanța din baza de date kraft pentru a evita erori 'name already in use'."""
    subprocess.run(["kraft", "rm", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def monitor_boot_time(process, start_time, target_log, instance_name, boot_data):
    last_internal_time = None
    for line in iter(process.stdout.readline, ''):
        # Căutăm un pattern de tip [0.229735] sau [  0.01234 ]
        match = re.search(r'\[\s*([\d\.]+)\s*\]', line)
        if match:
            last_internal_time = match.group(1)
            
        if target_log in line:
            boot_duration = time.time() - start_time
            boot_data["host_boot_time"] = round(boot_duration, 4)

            dprint(f"[Metrică Host] {instance_name} a bootat în {boot_duration:.4f} secunde (End-to-End).")
            if last_internal_time:
                boot_data["internal_boot_time"] = float(last_internal_time)
                dprint(f"[Metrică Internă] {instance_name} timp intern din log: {last_internal_time} secunde.")
            else:
                boot_data["internal_boot_time"] = None
                dprint(f"[Metrică Internă] {instance_name} nu a afișat timestamp intern în loguri.")
            target_log = "FOUND_ALREADY"

def measure_ram_usage(process):
    try:
        parent = psutil.Process(process.pid)
        children = parent.children(recursive = True)
        total_rss = parent.memory_info().rss
        for child in children:
            total_rss += child.memory_info().rss
        return total_rss / (1024 * 1024) #return MB
    except psutil.NoSuchProcess:
        return 0.0

def monitor_peak_ram(process, stop_event, ram_data):
    peak_rss = 0.0
    while not stop_event.is_set():
        current_rss = measure_ram_usage(process)
        if current_rss > peak_rss:
            peak_rss = current_rss
        time.sleep(0.1)
    ram_data["peak_ram_mb"] = peak_rss

def get_image_size_mb(filepath):
    if os.path.exists(filepath):
        return os.path.getsize(filepath) / (1024 * 1024)
    return 0.0

def get_kraft_base_image_size(image_name="unikraft.org/base:latest"):
    try:
        result = subprocess.run(["kraft", "pkg", "ls", "-o", "json"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        packages = json.loads(result.stdout)
        for pkg in packages:
            # Pachetul conține tag-ul în nume sau e "unikraft.org/base" cu version "latest"
            full_name = f"{pkg.get('name', '')}:{pkg.get('version', '')}"
            if full_name == image_name or pkg.get('name') == image_name:
                size_str = pkg.get("size", "")
                match = re.search(r'([\d\.]+)\s*MB', size_str)
                if match:
                    return float(match.group(1))
    except Exception:
        pass
    return 12.0 # Valoare default dacă nu găsim exact în JSON

def run_wrk_benchmark(url="http://127.0.0.1:8080", duration="10s", connections=100, threads=2):
    try:
        cmd = ["wrk", f"-t{threads}", f"-c{connections}", f"-d{duration}", url]
        dprint(f">> Se rulează wrk: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        output = result.stdout
        
        latency_match = re.search(r'Latency\s+([\d\.]+[a-zA-Z]+)', output)
        rps_match = re.search(r'Requests/sec:\s+([\d\.]+)', output)
        
        latency = latency_match.group(1) if latency_match else "N/A"
        rps = float(rps_match.group(1)) if rps_match else 0.0
        
        dprint(f"[Metrică Rețea] RPS: {rps}, Latență: {latency}")
        return {"rps": rps, "latency": latency}
        
    except FileNotFoundError:
        dprint("[EROARE] Utilitarul 'wrk' nu este instalat.")
        return {"rps": 0.0, "latency": "N/A"}
    except subprocess.CalledProcessError as e:
        dprint(f"[EROARE] wrk a eșuat: {e.stderr}")
        return {"rps": 0.0, "latency": "N/A"}

def run_unikraft_native():
    dprint("\n=== Rulare Benchmark: Unikraft Native ===")
    cwd = "unikraft/nginx-native"
    clean_kraft_instance("nginx-native")
    
    # 1. Build dacă nu există deja
    if not os.path.exists(os.path.join(cwd, ".unikraft/build/nginx-native_qemu-x86_64")):
        dprint(">> Imaginea nativă lipsește. Se rulează 'kraft build'...")
        try:
            subprocess.run(["kraft", "build"], cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            dprint(f"[EROARE] 'kraft build' a eșuat!")
            return {}
    else:
        dprint(">> Imaginea nativă există deja, sărim peste compilare.")
    
    flags = teardown.get_isolation_flags("unikraft")
    cmd = ["kraft", "run", "-p", "8080:80", "--rm", "--name", "nginx-native"] + flags

    start_time = time.time()
    process = subprocess.Popen(cmd, cwd = cwd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.DEVNULL, text = True)

    # Boot time
    boot_data = {}
    log_thread = threading.Thread(target = monitor_boot_time, args = (process, start_time, "Interface is up", "Unikraft Native", boot_data))
    log_thread.daemon = True
    log_thread.start()
    
    is_ready = wait_for_port(8080)
    metrics = {}

    if is_ready:
        time.sleep(0.5)

        # Image size
        image_path = os.path.join(cwd, ".unikraft/build/nginx-native_qemu-x86_64")
        image_size = get_image_size_mb(image_path)

        # Ram
        idle_ram_mb = measure_ram_usage(process)
        stop_ram_event = threading.Event()
        ram_data = {}
        ram_thread = threading.Thread(target=monitor_peak_ram, args=(process, stop_ram_event, ram_data))
        ram_thread.daemon = True
        ram_thread.start()

        # Latency & rps
        wrk_metrics = run_wrk_benchmark()

        stop_ram_event.set()
        ram_thread.join()
        peak_ram_mb = ram_data.get("peak_ram_mb", idle_ram_mb)

        metrics = {
            "target": "unikraft-native",
            "idle_ram_mb": round(idle_ram_mb, 2),
            "peak_ram_mb": round(peak_ram_mb, 2),
            "image_size_mb": round(image_size, 2),
            "host_boot_time": boot_data.get("host_boot_time"),
            "internal_boot_time": boot_data.get("internal_boot_time"),
            "rps": wrk_metrics["rps"],
            "latency": wrk_metrics["latency"]
        }

        dprint(f"[Metrică Finală] {metrics}")

    return metrics

def run_unikraft_bincompat():
    dprint("\n=== Rulare Benchmark: Unikraft Bincompat ===")
    cwd = "unikraft/nginx-bincompat"
    clean_kraft_instance("nginx-bincompat")
    
    dprint(">> Verificare și deduplicare cache imagine de bază ...")
    base_image = "unikraft.org/base:latest"
    subprocess.run(["kraft", "pkg", "rm", base_image], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["kraft", "pkg", "pull", base_image], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    flags = teardown.get_isolation_flags("unikraft")
    cmd = ["kraft", "run", "--no-prompt", "-p", "8080:80", "--rm", "--name", "nginx-bincompat", 
       "--rootfs", "./rootfs"] + flags + [base_image, "--", "/nginx", "-c", "/etc/nginx/nginx.conf"]
    dprint(">> Se rulează QEMU:", " ".join(cmd))

    start_time = time.time()
    process = subprocess.Popen(cmd, cwd = cwd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.DEVNULL, text = True)

    # Boot time
    boot_data = {}
    log_thread = threading.Thread(target = monitor_boot_time, args = (process, start_time, "Interface is up", "Unikraft Bincompat", boot_data))
    log_thread.daemon = True
    log_thread.start()

    is_ready = wait_for_port(8080)
    metrics = {}

    if is_ready:
        time.sleep(0.5)

        # Image size
        base_image_size = get_kraft_base_image_size(base_image)
        image_path = os.path.join(cwd, "rootfs/nginx")
        nginx_size = get_image_size_mb(image_path)
        total_image_size = base_image_size + nginx_size

        # Ram
        idle_ram_mb = measure_ram_usage(process)
        stop_ram_event = threading.Event()
        ram_data = {}
        ram_thread = threading.Thread(target=monitor_peak_ram, args=(process, stop_ram_event, ram_data))
        ram_thread.daemon = True
        ram_thread.start()

        # Latency & rps
        wrk_metrics = run_wrk_benchmark()

        stop_ram_event.set()
        ram_thread.join()
        peak_ram_mb = ram_data.get("peak_ram_mb", idle_ram_mb)

        metrics = {
            "target": "unikraft-bincompat",
            "idle_ram_mb": round(idle_ram_mb, 2),
            "peak_ram_mb": round(peak_ram_mb, 2),
            "image_size_mb": round(total_image_size, 2),
            "host_boot_time": boot_data.get("host_boot_time"),
            "internal_boot_time": boot_data.get("internal_boot_time"),
            "rps": wrk_metrics["rps"],
            "latency": wrk_metrics["latency"]
        }
        dprint(f"[Metrică Finală] {metrics}")

    return metrics

def run_nanovms():
    dprint("\n=== Rulare Benchmark: NanoVMs ===")
    cwd = "nanovms/nginx"
    
    flags = teardown.get_isolation_flags("nanovms")
    # ops mapează automat porturile prin opțiunea -p
    cmd = ["ops", "pkg", "load", "eyberg/nginx:1.18.0", "-c", "config.json", "-p", "8080"] + flags
    dprint(">> Se rulează QEMU (prin ops):", " ".join(cmd))

    start_time = time.time()
    process = subprocess.Popen(cmd, cwd = cwd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.DEVNULL, text = True,)

    # Boot time
    boot_data = {}
    log_thread = threading.Thread(target = monitor_boot_time, args = (process, start_time, "assigned", "NanoVMs", boot_data))
    log_thread.daemon = True
    log_thread.start()
    
    is_ready = wait_for_port(8080)
    metrics = {}

    if is_ready:
            time.sleep(0.5)

            # Image size
            image_path = os.path.expanduser("~/.ops/images/nginx")
            image_size = get_image_size_mb(image_path)

            # Ram
            idle_ram_mb = measure_ram_usage(process)
            stop_ram_event = threading.Event()
            ram_data = {}
            ram_thread = threading.Thread(target=monitor_peak_ram, args=(process, stop_ram_event, ram_data))
            ram_thread.daemon = True
            ram_thread.start()

            # Latency & rps
            wrk_metrics = run_wrk_benchmark()

            stop_ram_event.set()
            ram_thread.join()
            peak_ram_mb = ram_data.get("peak_ram_mb", idle_ram_mb)

            metrics = {
                "target": "nanovms",
                "idle_ram_mb": round(idle_ram_mb, 2),
                "peak_ram_mb": round(peak_ram_mb, 2),
                "image_size_mb": round(image_size, 2),
                "host_boot_time": boot_data.get("host_boot_time"),
                "internal_boot_time": boot_data.get("internal_boot_time"),
                "rps": wrk_metrics["rps"],
                "latency": wrk_metrics["latency"]
            }
            dprint(f"[Metrică Finală] {metrics}")
    
    return metrics

