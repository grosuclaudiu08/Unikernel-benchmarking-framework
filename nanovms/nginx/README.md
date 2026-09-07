# NanoVMs Nginx Baseline - Raport Persoana 2

Acest director conține fișierele și setările necesare pentru rularea aplicației Nginx ca unikernel folosind mediul **NanoVMs** (prin utilitarul `ops`).

## Ce s-a implementat (✅ Done)

1. **Pachet NanoVMs:** S-a descărcat și validat pachetul oficial `eyberg/nginx:1.18.0`.
2. **Configurări de Bază (`config.json`):** Definirea parametrilor asociați execuției pachetului, specificând directoarele necesare.
3. **Setări Rețea (`etc/nginx/nginx.conf`):** Nginx-ul a fost reconfigurat să asculte pe portul `8080` (în loc de 80) pentru a eluda problema permisiunilor de root (QEMU pe host nu are voie să folosească porturi sub 1024 nativ fără drepturi de administrator).
4. **Validare:** Testarea cu succes a răspunsului HTTP din unikernel.
5. **Teardown & Izolare (Script Global):** Fișierul `teardown.py` din rădăcina proiectului a fost creat tot de Persoana 2, limitând resursele NanoVMs la 1 vCPU și 512MB RAM și curățând procesele rătăcite.

## Ce mai rămâne de implementat de către Persoana 2 (⏳ To Do)

Din sarcinile specifice etapei de izolare și baseline atribuite în mod explicit, Persoana 2 a finalizat totul. Următoarele etape necesită finalizarea muncii Persoanei 1 și colaborarea la modulele globale:

- **Integrarea cu Orchestratorul (Blocat de Persoana 1):** Lansarea `ops pkg load` cu fișierul de configurare NanoVMs va trebui introdusă automat în scriptul central pe care Persoana 1 urmează să îl creeze.
- **Participarea la Faza 3 și Faza 4:** După ce Orchestratorul este gata, se vor prelua sarcinile de măsurare (Boot Time, RAM) și Load Testing (`wrk`), care urmează să fie împărțite între Persoana 1 și Persoana 2.
