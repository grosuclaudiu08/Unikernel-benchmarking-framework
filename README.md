# Unikernel Benchmarking Framework

Acest proiect își propune să creeze un cadru de benchmarking automatizat pentru compararea unikernel-urilor, utilizând ca referințe Unikraft și NanoVMs. Aplicația țintă pentru evaluare este un server web Nginx.

## Stadiul Proiectului (Status Curent)

Mai jos este prezentată o analiză detaliată a ceea ce s-a implementat pe fiecare componentă/branch, precum și erorile sau omisiunile corectate.

### 1. Partea Persoanei 1 (Unikraft & Orchestrator Core)
*   **Stadiu Nginx Nativ:** ✅ **Finalizat**. S-a creat cu succes mediul pentru Nginx Nativ pe Unikraft (în folderul `unikraft/nginx-native/`). S-a corectat montarea sistemului de fișiere (CPIO Initramfs prin mecanismul CI) și s-a ignorat corect output-ul de build (`.gitignore`).
*   **Stadiu Nginx Bincompat (app-elfloader):** ✅ **Finalizat**. S-a implementat varianta de Nginx rulată prin compatibilitate binară folosind Unikraft `app-elfloader`. Tot sistemul de fișiere de Linux și librăriile necesare se află în `unikraft/nginx-bincompat/`.
*   **Stadiu Orchestrator Core:** ✅ **Finalizat**. A fost creat scriptul central `orchestrator.py` care preia parametrii din CLI (ex. `--target unikraft-native`, `--target all`), rulează procesele (construcție și lansare), execută o validare "health check" pe portul 8080 și gestionează instanțele în fundal, integrând izolarea și curățarea din `teardown.py`.

### 2. Partea Persoanei 2 (NanoVMs & Teardown/Isolation)
*   **Stadiu Baseline NanoVMs:** ✅ **Finalizat**. Configurația pentru NanoVMs (fișierele `config.json` și `etc/nginx/nginx.conf` cu redirectare pe portul 8080) a fost implementată cu succes. Eroarea de boot cauzată de lipsa directoarelor goale la clonarea cu Git a fost remediată (prin adăugarea fișierelor `.gitkeep` în `/tmp`).
*   **Stadiu Teardown & Izolare:** ✅ **Finalizat**. Scriptul `teardown.py` limitează corect hardware-ul (1 vCPU, 512MB RAM) și distruge curat instanțele QEMU "orfane" folosind `SIGKILL` prin `psutil`. A fost integrat cu succes în Orchestrator.

### 3. Faza 3: Colecția de Metrici (Finalizată)
*   **Metrici Boot Time:** ✅ **Finalizat**. S-a implementat extragerea timpului de boot în `orchestrator.py` folosind threads pentru parsarea asincronă a logurilor (colectând atât Timpul Host End-to-End, cât și Timpul Intern pe NanoVMs).
*   **Dimensiunea Imaginii:** ✅ **Finalizat**. Calculată direct de pe disc pentru fiecare arhitectură (inclusiv adunarea imaginii de bază din cache-ul KraftKit pentru Bincompat).
*   **Consum RAM (Idle & Peak):** ✅ **Finalizat**. S-a implementat monitorizarea prin `psutil` pe toate child-procesele, înregistrând atât repausul (Idle) imediat după boot, cât și vârful de sarcină (Peak RAM) în timpul benchmark-ului asincron.
*   **Benchmarking Dinamic & Agregare Date:** ✅ **Finalizat**. Integrarea executabilului `wrk` direct în Python, rularea unui test de trafic Nginx, extragerea metricilor de *RPS* și *Latență* prin expresii regulate, și exportarea tuturor datelor într-un fișier consolidat `benchmark_results.json`.

---

## Ce mai trebuie adăugat / Implementat (Pașii Următori - Faza 4)

Framework-ul este **COMPLET**.
1. **Generarea Graficelor (Faza 4):** ✅ **Finalizat**. A fost creat scriptul `plot_metrics.py` care citește datele din `benchmark_results.json` și generează diagrame vizuale (bar charts) cu Matplotlib. Graficele comparative pentru Boot Time, RAM Usage, Image Size, RPS și Latență sunt salvate automat în folderul `graphs/`.
   - Pentru a rula graficele, trebuie instalate dependențele: `pip install -r requirements.txt`
   - Apoi se execută: `python3 plot_metrics.py`
