from __future__ import annotations

import logging
import sys
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable


SHARED_MODULES_PATH = Path(
    r"C:\scripts\_modules"
)

if str(SHARED_MODULES_PATH) not in sys.path:
    sys.path.insert(
        0,
        str(SHARED_MODULES_PATH),
    )


from excel_automation_lock import (
    ExcelAutomationLock,
    read_lock_state,
)


logger = logging.getLogger(
    "menestrel.excel_guard"
)


@dataclass
class _PendingJob:
    key: str
    owner: str
    label: str
    function: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    queued_at: str


_PENDING_JOBS: OrderedDict[
    str,
    _PendingJob,
] = OrderedDict()


def _now() -> str:
    return (
        datetime.now()
        .astimezone()
        .isoformat(timespec="seconds")
    )


def _describe_lock_owner() -> str:
    state = read_lock_state()

    if not state:
        return "outro processo"

    owner = (
        state.get("owner")
        or "desconhecido"
    )

    details = [str(owner)]

    pid = state.get("pid")

    if pid:
        details.append(
            f"PID {pid}"
        )

    started_at = state.get(
        "started_at"
    )

    if started_at:
        details.append(
            f"desde {started_at}"
        )

    return " | ".join(details)


def _run_if_available(
    job: _PendingJob,
) -> tuple[bool, Any]:
    """
    Executa o job somente se a trava do Excel estiver livre.

    Retorna:
        (False, None)
            caso outro processo possua a trava.

        (True, resultado)
            quando o job foi realmente iniciado.
    """

    lock = ExcelAutomationLock(
        owner=job.owner,
        requested_by="menestrel",
        metadata={
            "source": "menestrel",
            "job_key": job.key,
            "label": job.label,
        },
    )

    acquired = lock.acquire(
        timeout_seconds=0
    )

    if not acquired:
        return False, None

    # Se este job já estava pendente,
    # a execução atual passa a satisfazê-lo.
    _PENDING_JOBS.pop(
        job.key,
        None,
    )

    logger.info(
        "%s adquiriu a trava compartilhada do Excel.",
        job.label,
    )

    try:
        result = job.function(
            *job.args,
            **job.kwargs,
        )

        return True, result

    finally:
        lock.release()

        logger.info(
            "%s liberou a trava compartilhada do Excel.",
            job.label,
        )


def _queue_job(
    job: _PendingJob,
) -> None:
    if job.key in _PENDING_JOBS:
        return

    _PENDING_JOBS[
        job.key
    ] = job

    logger.warning(
        "%s adiada porque o recurso Excel está ocupado por %s. "
        "A execução permanecerá pendente.",
        job.label,
        _describe_lock_owner(),
    )


def excel_guarded(
    *,
    owner: str,
    job_key: str,
    label: str,
):
    """
    Protege um job do Menestrel com a trava compartilhada
    de automação do Excel.
    """

    def decorator(
        function: Callable[..., Any],
    ):
        @wraps(function)
        def wrapper(
            *args,
            **kwargs,
        ):
            job = _PendingJob(
                key=job_key,
                owner=owner,
                label=label,
                function=function,
                args=args,
                kwargs=kwargs,
                queued_at=_now(),
            )

            acquired, result = (
                _run_if_available(
                    job
                )
            )

            if acquired:
                return result

            _queue_job(job)

            return False

        return wrapper

    return decorator


def retry_pending_excel_jobs() -> None:
    """
    Tenta novamente o job pendente mais antigo.

    Apenas um é iniciado por chamada para preservar
    a ordem em que as solicitações ficaram pendentes.
    """

    if not _PENDING_JOBS:
        return

    _, job = next(
        iter(
            _PENDING_JOBS.items()
        )
    )

    try:
        acquired, _ = (
            _run_if_available(
                job
            )
        )

    except Exception:
        # O job chegou a ser iniciado e falhou.
        # Não o repetimos indefinidamente.
        _PENDING_JOBS.pop(
            job.key,
            None,
        )

        logger.exception(
            "Erro ao executar job pendente: %s",
            job.label,
        )

        return

    if not acquired:
        return

    logger.info(
        "%s pendente foi executada após liberação do Excel.",
        job.label,
    )


def pending_job_keys() -> list[str]:
    """
    Função de diagnóstico/teste.
    """

    return list(
        _PENDING_JOBS.keys()
    )