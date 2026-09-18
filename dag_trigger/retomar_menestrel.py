"""
Retoma o menestrel.py depois de uma pausa manual (pausar_menestrel.py):
limpa o flag de pausa e relança o processo.

Uso: python retomar_menestrel.py
"""

import os
import sys
import subprocess

from pause_utils import limpar_pausa

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENESTREL_SCRIPT = os.path.join(BASE_DIR, 'menestrel.py')


def main():
    limpar_pausa()
    subprocess.Popen(
        [sys.executable, MENESTREL_SCRIPT],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print("Pausa removida — Menestrel relançado.")


if __name__ == '__main__':
    main()
