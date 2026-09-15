#!/usr/bin/env python3
import os
import sys
import time
import argparse
import json
import threading
import itertools
import subprocess
from tabulate import tabulate

import orchestrator
import teardown

os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.local/bin")
os.environ["KRAFTKIT_NO_CHECK_UPDATES"] = "true"

DEBUG_GLOBAL = False

# print() doar la --debug
class HiddenPrints:
    def __enter__(self):
        if not DEBUG_GLOBAL:
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not DEBUG_GLOBAL:
            sys.stdout.close()
            sys.stdout = self._original_stdout

def animate_spinner(message, stop_event):
    """Afișează un spinner de așteptare pentru a indica progresul."""
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stop_event.is_set():
        sys.__stdout__.write(f'\r\033[1;36m{next(spinner)}\033[0m \033[37m{message}\033[0m')
        sys.__stdout__.flush()
        time.sleep(0.1)
    sys.__stdout__.write('\r\033[K')

def run_target(target_name, run_func):
    print(f"\n\033[1;33m>>> Inițializare benchmark:\033[0m \033[1;37m{target_name}\033[0m")
    
    stop_spinner = threading.Event()
    if not DEBUG_GLOBAL:
        spinner_thread = threading.Thread(
            target=animate_spinner, 
            args=(f"Se execută (bootare, izolare, load testing)...", stop_spinner)
        )
        spinner_thread.start()

    metrics = None
    try:
        # Folosim context manager-ul ca sa "stergem" output-ul de la orchestrator
        with HiddenPrints():
            teardown.teardown_qemu()
            metrics = run_func()
            teardown.teardown_qemu()
    except Exception as e:
        if not DEBUG_GLOBAL:
            stop_spinner.set()
            spinner_thread.join()
        print(f"\033[1;31m[EROARE]\033[0m A apărut o problemă la {target_name}: {e}")
        return None

    if not DEBUG_GLOBAL:
        stop_spinner.set()
        spinner_thread.join()
    
    if metrics:
        print(f"\033[1;32m[SUCCES]\033[0m Benchmark finalizat pentru {target_name}!")
    else:
        print(f"\033[1;31m[EȘUAT]\033[0m Nu s-au putut extrage datele pentru {target_name}.")
    
    return metrics

def display_menu():
    print("\n\033[1;34m========================================================\033[0m")
    print("\033[1;37m         UNIKERNEL NGINX BENCHMARK FRAMEWORK        \033[0m")
    print("\033[1;34m========================================================\033[0m")
    print(" Selectează ținta pe care dorești să o testezi:")
    print("   \033[1;32m1)\033[0m Unikraft Nginx-Native")
    print("   \033[1;32m2)\033[0m Unikraft Nginx-Bincompat")
    print("   \033[1;32m3)\033[0m NanoVMs Nginx")
    print("   \033[1;32m4)\033[0m Toate cele de mai sus")
    print("   \033[1;31m0)\033[0m Ieșire din program")
    print("\033[1;34m========================================================\033[0m")
    
    choice = input("\033[1;37mAlegerea ta (0-4): \033[0m").strip()
    return choice

def print_metrics_table(results):
    print("\n\033[1;35m REZULTATE BENCHMARK:\033[0m")
    headers = ["Target", "Idle RAM (MB)", "Peak RAM (MB)", "Size (MB)", "Host Boot (s)", "Intern Boot (s)", "RPS", "Latency"]
    rows = []
    for r in results:
        rows.append([
            r.get("target", "N/A"),
            r.get("idle_ram_mb", "N/A"),
            r.get("peak_ram_mb", "N/A"),
            r.get("image_size_mb", "N/A"),
            r.get("host_boot_time", "N/A"),
            r.get("internal_boot_time", "N/A"),
            r.get("rps", "N/A"),
            r.get("latency", "N/A")
        ])
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

def main():
    parser = argparse.ArgumentParser(
        description="Unikernel Benchmark Interactive CLI",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--target", 
        choices=["unikraft-native", "unikraft-bincompat", "nanovms", "all"], 
        help="Skip the interactive menu and run directly (for automation).\n"
             "Available targets:\n"
             "  unikraft-native,\n"
             "  unikraft-bincompat,\n"
             "  nanovms,\n"
             "  all"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (shows internal logs from orchestrator and teardown)."
    )
    args = parser.parse_args()

    if args.debug:
        global DEBUG_GLOBAL
        DEBUG_GLOBAL = True
        orchestrator.DEBUG_MODE = True
        teardown.DEBUG_MODE = True

    targets_to_run = []
    
    # Meniu interactiv CLI
    if args.target:
        if args.target == "all":
            targets_to_run = [
                ("Unikraft Native", orchestrator.run_unikraft_native),
                ("Unikraft Bincompat", orchestrator.run_unikraft_bincompat),
                ("NanoVMs", orchestrator.run_nanovms)
            ]
        elif args.target == "unikraft-native":
            targets_to_run = [("Unikraft Native", orchestrator.run_unikraft_native)]
        elif args.target == "unikraft-bincompat":
            targets_to_run = [("Unikraft Bincompat", orchestrator.run_unikraft_bincompat)]
        elif args.target == "nanovms":
            targets_to_run = [("NanoVMs", orchestrator.run_nanovms)]
    else:
        while True:
            choice = display_menu()
            if choice == '1':
                targets_to_run = [("Unikraft Native", orchestrator.run_unikraft_native)]
                break
            elif choice == '2':
                targets_to_run = [("Unikraft Bincompat", orchestrator.run_unikraft_bincompat)]
                break
            elif choice == '3':
                targets_to_run = [("NanoVMs", orchestrator.run_nanovms)]
                break
            elif choice == '4':
                targets_to_run = [
                    ("Unikraft Native", orchestrator.run_unikraft_native),
                    ("Unikraft Bincompat", orchestrator.run_unikraft_bincompat),
                    ("NanoVMs", orchestrator.run_nanovms)
                ]
                break
            elif choice == '0':
                print("O zi bună!")
                sys.exit(0)
            else:
                print("\033[1;31mSelecție invalidă! Te rog alege o opțiune între 0 și 4.\033[0m")

    # Rulare
    all_results = []
    for name, func in targets_to_run:
        res = run_target(name, func)
        if res:
            all_results.append(res)
        time.sleep(1)

    # Afisare & salvarea datelor
    if all_results:
        print_metrics_table(all_results)
        with open("benchmark_results.json", "w") as f:
            json.dump(all_results, f, indent=4)
        print("\n\033[1;32m[SUCCES]\033[0m Datele detaliate au fost salvate în 'benchmark_results.json'.\n")
        
        # Generarea automata a graficelor
        print("\033[1;33m>>> Generare automată a graficelor...\033[0m")
        try:
            res = subprocess.run(["python3", "plot_metrics.py"], capture_output=True, text=True)
            if res.returncode == 0:
                print("\033[1;32m[SUCCES]\033[0m Graficele au fost salvate în folderul 'graphs/'.")
            else:
                print(f"\033[1;31m[EROARE]\033[0m Eroare la grafice:\n{res.stderr}")
        except Exception as e:
            print(f"\033[1;31m[EROARE]\033[0m Nu am putut rula scriptul de grafice: {e}")

if __name__ == "__main__":
    main()

