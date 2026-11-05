# Instalación de DOVELA RIW

## Linux Mint / Ubuntu

Dependencias principales:

```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-vte-2.91
```

Descargar el repositorio una vez publicado:

```bash
git clone https://github.com/rhynocerus/dovela-riw.git
cd dovela-riw
/usr/bin/python3 src/main.py
```

## Otras distribuciones

Se necesitan Python 3, PyGObject, GTK 3 y VTE 2.91.

Los nombres de los paquetes varían entre distribuciones.
No se han validado todavía instrucciones específicas
para Fedora, Debian, Arch u otras.

## Observaciones

Ubuntu Mono es la fuente visual preferida.
Neofetch puede utilizarse para mostrar información
del sistema, según su disponibilidad.

No ejecutar Dovela con sudo.
