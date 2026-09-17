import time

HEARTBEAT_FILE = 'menestrel_heartbeat.txt'


def escrever_heartbeat():
    """Sinaliza ao watchdog externo que o processo não está travado.

    Usado tanto pelo loop principal do menestrel.py quanto por dentro de
    tasks com múltiplas rodadas internas (ex.: indirect_procurement),
    para que o watchdog meça progresso real e não a duração total da task.
    """
    with open(HEARTBEAT_FILE, 'w') as f:
        f.write(str(time.time()))
