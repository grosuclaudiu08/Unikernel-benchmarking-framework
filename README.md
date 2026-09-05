# Unikernel Benchmarking Framework - Raport Persoana 2

Acest document reflectă exclusiv stadiul sarcinilor și funcționalităților alocate către **Persoana 2**.

## 1. Baseline NanoVMs (Nginx) - `feature/nanovms-baseline`
**Stadiu:** ✅ **Implementat**

- **Utilitar instalat:** `ops` a fost instalat local.
- **Pachet NanoVMs:** S-a descărcat și validat pachetul oficial `eyberg/nginx:1.18.0`.
- **Configurări (`config.json` și `nginx.conf`):** 
  - Fișierul `etc/nginx/nginx.conf` a fost ajustat (setat să asculte pe portul `8080` pentru a eluda necesitatea permisiunilor de root pe host la pornirea prin QEMU).
  - Testul a fost validat la nivel de HTTP cu `curl` returnând confirmarea succesului din interiorul unikernel-ului.

## 2. Modulul de Izolare și Teardown - `feature/teardown-and-isolation`
**Stadiu:** ✅ **Implementat**

- **Izolarea Resurselor:** S-a scris scriptul Python (`teardown.py`) care conține funcția `get_isolation_flags(engine)`. Aceasta asamblează și trimite corect argumentele necesare hipervizorului pentru o izolare strictă a resurselor per instanță (**1 vCPU** și **512MB RAM**) atât pentru Unikraft (`kraft run`) cât și pentru NanoVMs (`ops pkg load`).
- **Funcția de Teardown:** A fost implementat mecanismul `teardown_qemu()`, înregistrat la oprirea execuției prin `atexit`. Acest modul folosește librăria `psutil` pentru a identifica automat un hipervizor (QEMU) abia lansat și forțează distrugerea sa prin `SIGKILL`, eliminând riscul interferenței instanțelor de benchmark blocate.

## 3. Ce mai trebuie implementat (Pașii Următori / Neasignați încă)
**Stadiu:** ⏳ **Urmează**

Pe baza etapelor globale 3 și 4 din `Plan.md`, care încă nu au fost împărțite nominal:
- **Metrici și Boot Time:** Monitorizarea și agregarea timpului de boot direct din jurnale, extragerea mărimii imaginii create, precum și profilarea hipervizorului pentru măsurarea memoriei alocate în regim real.
- **Integrarea utilitarului `wrk`:** Automatizarea load testing-ului la boot pentru a testa instanțele, monitorizând Requests Per Second și Latența.
- **Analiza Datelor:** Exportarea metricilor colectate și scrierea scripturilor pentru a exporta diagrame (CSV la Grafice).
