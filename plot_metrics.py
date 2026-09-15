import json
import os
import matplotlib.pyplot as plt
import numpy as np

def parse_latency(lat_str):
    """Converts a latency string like '12.22ms' to milliseconds."""
    if not isinstance(lat_str, str):
        return float(lat_str)
    if lat_str == "N/A":
        return float("nan")
    if lat_str.endswith('ms'):
        return float(lat_str[:-2])
    if lat_str.endswith('us'):
        return float(lat_str[:-2]) / 1000
    if lat_str.endswith('s'):
        return float(lat_str[:-1]) * 1000
    return float(lat_str)

def main():
    if not os.path.exists("benchmark_results.json"):
        print("[EROARE] Fișierul benchmark_results.json nu există. Rulați orchestrator.py mai întâi.")
        return

    with open("benchmark_results.json", "r") as f:
        data = json.load(f)

    if not data:
        print("[EROARE] Nu există date în fișier.")
        return

    os.makedirs("graphs", exist_ok=True)
    targets = [item["target"] for item in data]
    x = np.arange(len(targets))
    width = 0.35

    # 1. Boot Time (Host vs Internal)
    host_boot = [item.get("host_boot_time", 0) for item in data]
    internal_boot = [item.get("internal_boot_time", 0) or 0 for item in data]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars1 = ax.bar(x - width/2, host_boot, width, label='Host Boot Time (s)', color='skyblue')
    bars2 = ax.bar(x + width/2, internal_boot, width, label='Internal Boot Time (s)', color='lightgreen')
    ax.set_ylabel('Secunde')
    ax.set_title('Timp de Boot (Host vs Internal)')
    ax.set_xticks(x)
    ax.set_xticklabels(targets)
    ax.legend()
    plt.tight_layout()
    plt.savefig("graphs/boot_time.png")
    plt.close()

    # 2. RAM Usage (Idle vs Peak)
    idle_ram = [item.get("idle_ram_mb", 0) for item in data]
    peak_ram = [item.get("peak_ram_mb", 0) for item in data]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars1 = ax.bar(x - width/2, idle_ram, width, label='Idle RAM (MB)', color='lightblue')
    bars2 = ax.bar(x + width/2, peak_ram, width, label='Peak RAM (MB)', color='salmon')
    ax.set_ylabel('Megabytes (MB)')
    ax.set_title('Consum RAM (Idle vs Peak)')
    ax.set_xticks(x)
    ax.set_xticklabels(targets)
    ax.legend()
    plt.tight_layout()
    plt.savefig("graphs/ram_usage.png")
    plt.close()

    # 3. Image Size
    image_size = [item.get("image_size_mb", 0) for item in data]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(targets, image_size, color='orchid')
    ax.set_ylabel('Megabytes (MB)')
    ax.set_title('Dimensiune Imagine (Image Size)')
    plt.tight_layout()
    plt.savefig("graphs/image_size.png")
    plt.close()

    # 4. Network Performance: RPS
    rps = [item.get("rps", 0) for item in data]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(targets, rps, color='gold')
    ax.set_ylabel('Requests Per Second')
    ax.set_title('Performanță Rețea (RPS)')
    plt.tight_layout()
    plt.savefig("graphs/rps.png")
    plt.close()

    # 5. Network Performance: Latency
    latency = [parse_latency(item.get("latency", 0)) for item in data]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(targets, latency, color='coral')
    ax.set_ylabel('Milisecunde (ms)')
    ax.set_title('Latență Medie (Latency)')
    plt.tight_layout()
    plt.savefig("graphs/latency.png")
    plt.close()

    print("[SUCCES] Graficele au fost generate în folderul 'graphs/'.")

if __name__ == "__main__":
    main()
