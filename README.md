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

### 3. Faza 3: Colecția de Metrici (În Progres)
*   **Metrici Boot Time:** ✅ **Finalizat**. S-a implementat extragerea timpului de boot direct în `orchestrator.py` folosind fire de execuție (Threads) pentru parsarea asincronă a logurilor. Framework-ul colectează acum două metrici:
    * **Timpul Host (End-to-End)**: calculat din Python (Time-to-Network).
    * **Timpul Intern (Pur)**: extras prin expresii regulate direct din output-ul mașinii virtuale (activat cu succes pe NanoVMs; ignorat intenționat pentru Unikraft în favoarea metricii End-to-End pentru a menține stabilitatea pe versiunile *stable*).

---

## Ce mai trebuie adăugat / Implementat (Pașii Următori)

Efortul se va concentra pe finalizarea următoarelor metrici statice și rularea benchmark-urilor dinamice:

1. **Dimensiunea Imaginii & RAM:** Salvarea mărimii imaginilor compilate și implementarea unui mecanism de monitorizare a procesului QEMU direct din sistemul de operare gazdă (host) pentru a înregistra RAM-ul consumat efectiv.
2. **Benchmarking Dinamic (Rețea):** Integrarea automată a utilitarului de load testing `wrk` imediat după boot-area instanțelor (folosind starea de "[OK]" generată de orchestrator) pentru a măsura *Requests Per Second (RPS)* și Latența.
3. **Agregarea Datelor & Export:** Structurarea tuturor metricilor colectate (statice și dinamice) și salvarea acestora într-un format brut standardizat (CSV sau JSON).
4. **Generarea Graficelor (Extensii Viitoare):** Crearea de scripturi adiționale (ex. Matplotlib) pentru parsarea fișierelor exportate și generarea de grafice comparative între Nginx Nativ, Bincompat și NanoVMs.
