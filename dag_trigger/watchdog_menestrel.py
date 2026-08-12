"""
Watchdog externo do menestrel.py.

Roda como uma tarefa curta e recorrente (Task Scheduler, a cada N minutos),
separada do processo do menestrel. Detecta dois cenários:

1. DOWN   :: o processo cujo PID está em menestrel.pid não existe mais.
2. TRAVADO:: o processo existe, mas o loop principal parou de escrever o
             heartbeat (sinal de que uma chamada COM/SAP GUI travou a thread
             única e o `while True` nunca mais itera).

Em qualquer um dos dois casos, mata o processo (se ainda existir) + os
processos satélite que costumam travar junto (saplogon.exe, excel.exe) e
relança o menestrel.py do zero.

STALE_THRESHOLD_MINUTES é intencionalmente alto: algumas tasks (ex.:
INDIRECT_PROCUREMENT) já levaram ~45min em execução normal. O objetivo aqui
não é detectar lentidão, é detectar travamento permanente.
"""

import os
import sys
import time
import logging
import subprocess
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENESTREL_SCRIPT = os.path.join(BASE_DIR, 'menestrel.py')
PID_FILE = os.path.join(BASE_DIR, 'menestrel.pid')
HEARTBEAT_FILE = os.path.join(BASE_DIR, 'menestrel_heartbeat.txt')

STALE_THRESHOLD_MINUTES = 60
PROCESSOS_SATELITE = ['saplogon.exe', 'excel.exe']

# Webhook de "Incoming Webhook" de um canal do Teams. Deixe em branco para
# desativar a notificação e depender só do watchdog_song.log.
TEAMS_WEBHOOK_URL = ""

logging.basicConfig(
    filename=os.path.join(BASE_DIR, 'watchdog_song.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)


def ler_pid():
    try:
        with open(PID_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def processo_vivo(pid, imagem='python.exe'):
    resultado = subprocess.run(
        ['tasklist', '/FI', f'PID eq {pid}', '/FI', f'IMAGENAME eq {imagem}', '/NH'],
        capture_output=True, text=True, timeout=10
    )
    return str(pid) in resultado.stdout


def idade_heartbeat_minutos():
    try:
        return (time.time() - os.path.getmtime(HEARTBEAT_FILE)) / 60
    except FileNotFoundError:
        return None


def matar_processo(pid):
    subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)


def matar_satelites():
    for imagem in PROCESSOS_SATELITE:
        subprocess.run(['taskkill', '/F', '/IM', imagem],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)


def relancar_menestrel():
    subprocess.Popen(
        [sys.executable, MENESTREL_SCRIPT],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )


def notificar_teams(mensagem):
    if not TEAMS_WEBHOOK_URL:
        return
    try:
        requests.post(TEAMS_WEBHOOK_URL, json={"text": mensagem}, timeout=10)
    except Exception as erro:
        logging.error(f"Falha ao enviar notificação ao Teams: {erro}")


def main():
    pid = ler_pid()
    vivo = pid is not None and processo_vivo(pid)
    idade = idade_heartbeat_minutos()

    if not vivo:
        motivo = f"processo (PID {pid}) não encontrado" if pid else "menestrel.pid ausente"
    elif idade is None:
        # Processo recém-criado: ainda não passou pela 1ª iteração do loop
        # (que é quem escreve o heartbeat). Não é travamento — apenas aguarda.
        return
    elif idade > STALE_THRESHOLD_MINUTES:
        motivo = f"heartbeat parado há {idade:.0f} min (limite: {STALE_THRESHOLD_MINUTES}min)"
    else:
        return  # saudável — nada a fazer

    logging.warning(f"Menestrel considerado travado/parado :: {motivo}. Reiniciando...")

    if vivo:
        matar_processo(pid)
    matar_satelites()
    relancar_menestrel()

    logging.info("Menestrel relançado pelo watchdog.")
    notificar_teams(
        f"Menestrel Watchdog :: reinício automático em {datetime.now():%Y-%m-%d %H:%M:%S}.\n"
        f"Motivo: {motivo}."
    )


if __name__ == '__main__':
    main()
