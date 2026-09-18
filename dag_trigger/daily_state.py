import json
import os
import logging
from datetime import date

STATE_FILE = 'daily_state.json'


def _hoje():
    return date.today().isoformat()


def carregar_estado():
    """Lê o estado da diária de hoje. Estado de outro dia (ou ausente) é
    tratado como vazio — reset automático no rollover de dia."""
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            estado = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        estado = {}

    if estado.get('date') != _hoje():
        estado = {'date': _hoje(), 'completed_tasks': [], 'daily_chain_triggered': False}

    return estado


def _salvar(estado):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(estado, f)


def marcar_task_concluida(nome_task):
    estado = carregar_estado()
    if nome_task not in estado['completed_tasks']:
        estado['completed_tasks'].append(nome_task)
    _salvar(estado)


def marcar_daily_concluida():
    estado = carregar_estado()
    estado['daily_chain_triggered'] = True
    _salvar(estado)


def diaria_pendente_hoje():
    """True se a diária de hoje ainda não terminou (nunca começou ou ficou incompleta)."""
    return not carregar_estado()['daily_chain_triggered']


def estado_nunca_existiu():
    """True só no primeiro boot de todos — nenhum daily_state.json foi
    gravado ainda nesta máquina/instalação (diferente de 'existe, mas é de
    outro dia', que é tratado normalmente por carregar_estado())."""
    return not os.path.exists(STATE_FILE)


def marcar_estado_inicial():
    """Grava o estado vazio de hoje sem rodar nada — usado quando o usuário
    opta por não rodar a diária no primeiro deploy, pra que reinícios
    seguintes (watchdog, crash, etc.) não caiam mais no primeiro-deploy."""
    _salvar(carregar_estado())
