# Unikernel Nginx Benchmarking Framework

Acest proiect este un cadru de testare automatizată (*Benchmarking Framework*) complet, construit în Python, destinat măsurării și comparării performanțelor aplicațiilor web (Nginx) rulate sub formă de Unikernel-uri. 

Framework-ul evaluează și compară direct următoarele trei arhitecturi de virtualizare:
1. **Unikraft Nginx-Native** (Compilare directă din cod sursă Nginx pentru Unikraft)
2. **Unikraft Nginx-Bincompat** (Execuție prin elfloader folosind binarul standard de Linux)
3. **NanoVMs (OPS)** (Execuție rapidă folosind ecosistemul NanoVMs)

## Metrici Colectate Automat

Pe parcursul testării (care izolează strict fiecare mașină virtuală la **1 vCPU și 512MB RAM**), sistemul colectează următoarele date:
* **Host Boot Time:** Timpul real (End-to-End) de când se trimite comanda către hypervisor (QEMU) până când portul 8080 este gata să primească trafic.
* **Internal Boot Time:** Timpul de boot raportat de nucleul intern al unikernel-ului.
* **Idle RAM vs Peak RAM:** Memoria consumată în stare de repaus imediat după boot, versus vârful de consum înregistrat asincron sub un trafic extrem de mare.
* **Image Size:** Spațiul real pe disc ocupat de imaginea compilată (inclusiv kernelul de bază).
* **RPS & Latency:** Măsurate folosind utilitarul `wrk` (Requests Per Second și Latența medie de răspuns).

---

## Instalare și Configurare (Setup)

Proiectul necesită instalarea unor dependențe la nivel de sistem (Hypervisor, `wrk`, Python, KraftKit, ops). Pentru a automatiza complet procesul, a fost creat un script de setup care va pregăti calculatorul automat.

Rulează pur și simplu în terminal:
```bash
./setup.sh
```
*(Acesta va cere parola de `sudo` pentru pachetele `apt` și va descărca automat utilitarele necesare pentru mediul de virtualizare).*

---

## Modul de Utilizare

Proiectul beneficiază de un **CLI Interactiv**, complet decuplat de logica de orchestrator (pentru un output curat și elegant, fără avalanșe de log-uri). 

Punctul unic de intrare în framework este comanda:
```bash
./uni_benchmark
```

### 1. Modul Interactiv (Meniu)
Dacă rulezi comanda fără niciun parametru, vei fi întâmpinat de un meniu ASCII de unde poți selecta cu cifrele `1`, `2`, `3` ce componentă dorești să testezi, sau `4` pentru a testa complet toată suita. În timpul rulării, o animație (`Spinner`) va indica stadiul.

### 2. Modul Automat (Selective Target)
Dacă folosești framework-ul într-un pipeline CI/CD sau dorești să sari peste meniul interactiv, poți rula un test specific folosind flag-ul `--target`:
```bash
./uni_benchmark --target nanovms
./uni_benchmark --target all
```
*Opțiuni valide:* `unikraft-native`, `unikraft-bincompat`, `nanovms`, `all`.

### 3. Modul de Debugging (Erori și Log-uri)
În mod implicit, fișierul `uni_benchmark` ascunde complet toate output-urile utilitarelor de fundal (`orchestrator.py` și `teardown.py`) pentru a păstra consola vizual curată. 

Dacă un unikernel eșuează (ex: eroare de compilare GCC), interfața va "prinde" eroarea și va trece mai departe afișând un mesaj de EȘEC. Dacă dorești să analizezi exact **ce s-a stricat**, adaugă flag-ul `--debug`:
```bash
./uni_benchmark --debug
./uni_benchmark --target unikraft-native --debug
```
*Acest flag va opri spinner-ul și va elibera în consolă absolut tot fluxul original de log-uri (comenzile rulate, output-ul compilatorului, timpii extrași din regex, log-urile wrk).*

Poți vedea lista de instrucțiuni oricând cu: `./uni_benchmark --help` sau `-h`.

---

## 📈 Rezultate și Grafice Automate

La finalul unui benchmark de succes:
1. Datele sunt formatate pe ecran sub forma unui tabel frumos structurat.
2. Datele brute sunt exportate în fișierul `benchmark_results.json` (care este protejat de Git pentru a nu stârni conflicte între calculatoare cu hardware diferit).
3. Scriptul apelează **automat** modulul `plot_metrics.py`. Acesta analizează JSON-ul și va desena / genera imediat scheme grafice comparative `.png` de înaltă rezoluție în folderul `graphs/`, gata de a fi atașate în rapoarte de cercetare sau lucrări de licență!
