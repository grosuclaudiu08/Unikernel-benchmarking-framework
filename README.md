# Unikernel Benchmarking Framework

Acest proiect își propune să creeze un cadru de benchmarking automatizat pentru compararea unikernel-urilor, utilizând ca referințe Unikraft și NanoVMs. Aplicația țintă pentru evaluare este un server web Nginx.

## Stadiul Proiectului (Status Curent)

Mai jos este prezentată o analiză detaliată a ceea ce s-a implementat pe fiecare componentă/branch, precum și erorile sau omisiunile care trebuie corectate.

### 1. Partea Persoanei 1 (Unikraft & Orchestrator Core)
*   **Stadiu Nginx Nativ:** ✅ **Implementat**. S-a creat cu succes mediul pentru Nginx Nativ pe Unikraft (în folderul `unikraft/nginx-native/`).
*   **Stadiu Nginx Bincompat (app-elfloader):** ✅ **Finalizat**. S-a implementat varianta de Nginx rulată prin compatibilitate binară folosind Unikraft `app-elfloader`. Tot sistemul de fișiere de Linux și librăriile necesare se află în `unikraft/nginx-bincompat/`.
*   **Stadiu Orchestrator Core:** ❌ **OMISIUNE**. Scriptul principal de orchestrare (`orchestrator.py` sau `.bash`) care preia parametrii din CLI și pornește procesele hipervizoarelor nu a fost creat.

### 2. Partea Persoanei 2 (NanoVMs & Teardown/Isolation)
*   **Stadiu Baseline NanoVMs:** ✅ **Finalizat**. Configurația pentru NanoVMs (fișierele `config.json` și `etc/nginx/nginx.conf` cu redirectare pe portul 8080) a fost implementată cu succes, testată și refactorizată în folderul dedicat `nanovms/nginx/`.
*   **Stadiu Teardown & Izolare:** ✅ **Finalizat**. Scriptul `teardown.py` limitează corect hardware-ul (1 vCPU, 512MB RAM) și distruge curat instanțele QEMU "orfane" folosind `SIGKILL` prin `psutil`.

---

## Ce mai trebuie adăugat / Implementat (Pașii Următori)

### Imediat (Corecturi Faza 1 & 2):
1. **Persoana 1** trebuie să dezvolte **Orchestrator Core** (scriptul de lansare centralizat care integrează funcțiile din `teardown.py`).

### Pașii de Benchmarking & Analiză (Faza 3 & 4 - Nealocați):
1. **Metrici Boot Time:** Extragerea timpului de boot direct din log-urile QEMU.
2. **Dimensiunea Imaginii & RAM:** Salvarea mărimii imaginii compilate și măsurarea consumului de memorie real în sistemul gazdă.
3. **Benchmarking Dinamic:** Integrarea automată a utilitarului de load testing `wrk` (pentru RPS și Latență).
4. **Agregarea Datelor:** Exportarea finală a metricilor (CSV/JSON) și generarea viitoare de grafice (ex. Matplotlib).
