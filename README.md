## _MENESTREL_

> README criado originalmente por murilo-tsu; edições e revisões posteriores feitas com o auxílio do Claude.

O *Menestrel* é um orquestrador de scripts para a extração de relatórios do SAP4HANA via SAP GUI Scripting. Roda continuamente numa VM Windows com SAP GUI instalado, navegando as transações no lugar de um usuário humano, exportando os relatórios para Excel e subindo os arquivos para o MinIO — que serve como camada *stage* de entrada de dados para o pipeline (Airflow/Hadoop) consumido pelo time de Data Insights.

### Escopo

- **Ponto de entrada**: `dag_trigger/menestrel.py`. Mantém um loop (`schedule.run_pending()`) que dispara dois grandes grupos de tarefas:
  - **Extração diária** (`extracao_diaria`, 00:05): batelada sequencial — `POSITION_FILES` → `SKU` → `WERKISH` → `CUSTOS` → `FATURAMENTO` → `BOM` → `COMPRAS` → `COCKPIT` → `VBAK` → `GL_ACCOUNTS` → `INDIRECT_PROCUREMENT` → `ESTOQUE` — seguida do disparo da DAG `daily_chained_dags` no Airflow.
  - **Extrações incrementais** (`extracoes_incrementais`, a cada 120 min, dentro de janelas de horário comercial): atualizações mais granulares de Faturamento, Compras, GL Accounts e Indirect Procurement, cada uma disparando sua própria DAG no Airflow.
  - Tarefas isoladas agendadas em horários fixos: `TEXT_INFO` (07:30) e `ESTOQUE_FULL` (18:05).
- **Cada script `engdds_*.py`** (em `dag_trigger/`) automatiza uma transação SAP específica via `win32com`/SAP GUI Scripting, usando `saplogin.py` (classe `SAPLogin`) para login/logout e `Minio.py` para subir o Excel exportado ao bucket de stage.
- **Restrição de concorrência crítica**: todo o scripting COM/SAP GUI roda na **mesma thread** — não há paralelismo entre tarefas. Um `threading.Lock` (`sap_lock`) garante que a extração diária e as incrementais nunca rodem simultaneamente.
- **Resiliência**: `run_with_retry` tenta cada tarefa até 2 vezes (60s de intervalo), logando tudo em `menestrel_song.log`. Falha numa tarefa não interrompe as demais — a orquestração segue para a próxima.

### Mudanças experimentais em teste (`engdds_estoque.py` / `saplogin.py`)

Diagnóstico: o orquestrador travava (sem erro, sem retry — silêncio total no log) durante a exportação `&XXL` do `engdds_estoque.py`, especificamente no passo client-side de OLE entre o SAP GUI e o Excel. O risco é maior nas extrações de domingo (backfill de 46 dias × 5 plantas), onde o script antigo abria/derrubava a sessão SAP até ~230 vezes numa única execução.

Três ajustes estão sendo testados em conjunto, isolados a `engdds_estoque.py` e `saplogin.py` (ainda não replicados nos demais scripts que usam o mesmo padrão `&XXL`):

1. **`sap.kill_excel()`** (`saplogin.py`) — mata qualquer `excel.exe` órfão imediatamente antes de cada exportação, evitando que uma instância travada de uma iteração anterior intercepte a chamada OLE seguinte.
2. **`sap.export_watchdog(timeout=180)`** (`saplogin.py`) — *context manager* que arma um `threading.Timer` de 180s ao redor do trecho de exportação; se a chamada SAP travar além disso, o timer mata o `excel.exe` por fora (sem tocar em objetos COM, por isso é seguro entre threads), forçando a chamada bloqueada a retornar com erro em vez de travar indefinidamente. O valor de 180s foi calibrado a partir do histórico do `menestrel_song.log`: ciclos normais de exportação levam de 30s a ~2min mesmo nos dias mais pesados, então 180s dá margem confortável sem mascarar uma trava real.
3. **Login único por execução** — antes, `engdds_estoque.py` fazia login/logout completo do SAP GUI a cada combinação de dia × planta (até ~230 vezes num domingo). Agora há um único login no início da função, reaproveitado em todos os blocos; a troca de transação usa o prefixo `/n` (ex.: `/nZMM_QNTY_PIVB`) para encerrar a transação corrente antes de abrir a próxima na mesma sessão — sem isso, transações se acumulariam na pilha do SAP GUI. Em caso de erro, a sessão é limpa (`limpar_processos`/`cleanup`) e refeito o login antes de continuar; uma limpeza final roda uma única vez ao término de toda a execução.

**Status**: implementado, ainda não validado em produção — sendo testado pelo autor antes de decidir se o padrão é replicado aos demais scripts `engdds_*.py` que compartilham a mesma exportação `&XXL`.
