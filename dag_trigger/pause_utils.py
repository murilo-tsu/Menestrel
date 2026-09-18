import json
import os
import time
from datetime import datetime

PAUSE_FILE = 'menestrel.pause'
PAUSE_EXPIRY_MINUTES = 40


def esta_pausado():
    """True se existe uma pausa manual ativa (não expirada).

    Uma pausa esquecida expira sozinha após PAUSE_EXPIRY_MINUTES, para não
    desativar o monitoramento do watchdog indefinidamente.
    """
    try:
        with open(PAUSE_FILE, 'r', encoding='utf-8') as f:
            estado = json.load(f)
        paused_at = estado['paused_at']
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False

    idade_minutos = (time.time() - datetime.fromisoformat(paused_at).timestamp()) / 60
    if idade_minutos > PAUSE_EXPIRY_MINUTES:
        limpar_pausa()
        return False

    return True


def escrever_pausa(nota=None):
    with open(PAUSE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'paused_at': datetime.now().isoformat(), 'nota': nota}, f)


def limpar_pausa():
    try:
        os.remove(PAUSE_FILE)
    except FileNotFoundError:
        pass
