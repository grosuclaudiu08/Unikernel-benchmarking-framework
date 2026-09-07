import os
import signal
import psutil
import atexit
import time

# Limite globale configurabile
VCPUS = 1
RAM_MB = 512

def get_isolation_flags(engine: str) -> list:
    """
    Returnează flag-urile de linie de comandă necesare pentru a impune
    limitele de resurse pentru hypervisor în funcție de engine-ul folosit.
    """
    engine = engine.lower()
    if engine == "unikraft":
        # kraftkit folosește -M pentru memorie
        return ["-M", f"{RAM_MB}M"]
    elif engine == "nanovms":
        # ops folosește -m pentru memorie și --smp pentru CPU cores
        return ["-m", f"{RAM_MB}M", "--smp", str(VCPUS)]
    else:
        raise ValueError(f"Engine necunoscut: {engine}")

def teardown_qemu():
    """
    Identifică și ucide procesele QEMU rulate, asigurând curățarea după benchmark.
    Folosește SIGKILL pentru oprire forțată.
    """
    print("Se execută teardown: căutare procese QEMU rămase...")
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name']
            cmdline = proc.info['cmdline']
            
            # Căutăm procesul QEMU
            if name and 'qemu-system' in name:
                print(f"S-a găsit procesul QEMU cu PID {proc.info['pid']}. Se trimite SIGKILL...")
                os.kill(proc.info['pid'], signal.SIGKILL)
                killed_count += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if killed_count == 0:
        print("Nu s-au găsit procese QEMU de curățat.")
    else:
        print(f"S-au ucis {killed_count} procese QEMU.")

# Înregistrăm funcția de teardown pentru a rula la ieșirea scriptului
atexit.register(teardown_qemu)

if __name__ == "__main__":
    # Testare manuală simplă
    print("Flag-uri NanoVMs:", get_isolation_flags("nanovms"))
    print("Flag-uri Unikraft:", get_isolation_flags("unikraft"))
