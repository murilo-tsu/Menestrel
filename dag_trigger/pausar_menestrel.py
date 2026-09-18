"""
Pausa manual do menestrel.py — encerra o processo e sinaliza pro watchdog
externo (watchdog_menestrel.py) não relançar sozinho por um tempo.

Uso: python pausar_menestrel.py ["nota opcional sobre o motivo"]
"""

import os
import sys
import subprocess

from pause_utils import escrever_pausa, PAUSE_EXPIRY_MINUTES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(BASE_DIR, 'menestrel.pid')


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


def matar_processo(pid):
    subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)


def main():
    nota = sys.argv[1] if len(sys.argv) > 1 else None

    pid = ler_pid()
    if pid is not None and processo_vivo(pid):
        matar_processo(pid)
        print(f"Menestrel (PID {pid}) encerrado.")
    else:
        print("Menestrel já não estava rodando.")

    escrever_pausa(nota)
    print(f"Pausa registrada — o watchdog não vai relançar por até {PAUSE_EXPIRY_MINUTES}min.")
    print("Rode retomar_menestrel.py pra voltar antes disso.")


if __name__ == '__main__':
    main()
