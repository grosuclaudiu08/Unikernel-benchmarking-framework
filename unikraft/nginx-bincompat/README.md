# Unikraft Bincompat (app-elfloader) - Nginx

Această componentă folosește suportul de compatibilitate binară (Bincompat) oferit de Unikraft pentru a rula un binar standard de Linux (Nginx) direct ca unikernel, fără a necesita compilarea codului sursă, folosind `app-elfloader`.

## Funcționalitate implementată:
- **Rootfs complet**: A fost preluat mediul de sistem Linux (inclusiv librăriile dependente `libc`, `libpcre`, `libssl`, `libz`) din pachetul standard Ubuntu/NanoVMs și integrat în directorul `rootfs/`.
- **Configurație Nginx**: Fișierul `etc/nginx/nginx.conf` a fost adaptat să returneze textul valid `Unikraft Bincompat Validat cu succes!` pe portul 8080.
- **Folosire KraftKit 0.12+**: Permite rularea rapidă descărcând kernelul de bază Unikraft cu elfloader (`unikraft.org/base:latest`).

## Cum se testează manual:
Rulați pur și simplu scriptul inclus în acest director:
```bash
./run.sh
```

Apoi, verificați funcționalitatea prin accesarea paginii:
```bash
curl http://localhost:8080
```

Pentru curățare:
```bash
kraft rm nginx-bincompat
```
