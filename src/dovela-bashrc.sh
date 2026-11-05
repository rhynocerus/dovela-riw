#!/usr/bin/env bash
# Configuración exclusiva de Dovela RIW.
# Evita imprimir Neofetch dos veces.

neofetch() {
    :
}

if [[ -f "$HOME/.bashrc" ]]; then
    source "$HOME/.bashrc"
fi

unset -f neofetch
