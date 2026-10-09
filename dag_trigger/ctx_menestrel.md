# menestrel — contexto

> Gerado em 2026-10-01 pela sessão Claude Code "menestrel" (repo `murilo-tsu/Menestrel`, branch `main`, HEAD `11fda71`, último commit 2026-09-21; versão impressa no banner: **v6.1.0**). Fontes: memória persistente da sessão (2026-08-06 → 2026-09-30) + leitura do código atual. Itens não confirmados estão marcados "(não verificado)".

## 1. Papel e escopo

- **Menestrel** é um orquestrador Python de RPA que extrai relatórios do **SAP S/4HANA (PRD)** via **SAP GUI Scripting** (win32com), exporta para Excel (`&XXL`) e sobe os arquivos para o **MinIO** (bucket `tmp`, camada *stage*), disparando em seguida DAGs no **Airflow** que carregam o pipeline de dados consumido pelo time de Data Insights.
- Não é API/RFC: é automação de GUI real, sem modo headless. Exige sessão Windows interativa, desbloqueada, sempre logada.
- Operador/dono: **Murilo Ribeiro** (git `murilo-tsu`). Ele aplica pessoalmente correções pequenas e faz os commits/deploy manualmente; a sessão Claude diagnostica e implementa mudanças maiores quando pedido.
- Escopo do código: `dag_trigger/` (produção, unificado). `dag_trigger_vFH/`, `dag_trigger_vFTO/`, `dag_trigger_vFTO_new/` e `_legacy/` são cópias de referência do merge — **não versionadas** (no `.gitignore`), não rodam em produção a partir deste repo.
- Abrange **dois sites** desde o merge de 2026-08-28 ("Unificação: Tocantins e Heringer"): EuroChem Fertilizantes Tocantins (FTO) e Heringer (FH).

## 2. Ambiente

| Item | Valor | Obs. |
|---|---|---|
| Repo (dev) | `C:\Users\murilo.ribeiro\Documents\GitHub\Menestrel` | GitHub **público** (`github.com/murilo-tsu/Menestrel`) |
| VM de execução (watchdog / sessão sempre logada) | `10.91.5.85` | Windows; SAP GUI + Excel instalados |
| Host exibido no banner do console | `10.88.55.26` | relação com 10.91.5.85 não reconciliada (não verificado) |
| Caminhos de deploy já vistos | `C:\SAP4HANA-Scripts\dag_trigger` (miniconda), `C:\Users\murilo.ribeiro\Desktop\Scripts\dag_trigger\` (Python310, `.bat` antigo) | qual é o atual em produção: não verificado |
| Python | 3.13 em dev (pycache `cpython-313`); 3.10 em artefatos antigos | versão exata em prod não verificada |
| SAP | S/4HANA **PRD**, via `saplogon.exe` + SAP GUI Scripting | idioma ajustado via `SAPGUI_LANGUAGE` (commit `22a337e`) |
| MinIO | FTO: `10.91.5.107:20000` (user `datainsights`); FH: `10.91.5.108:9000` (user `datainsights_fh`) | **Atenção:** o default atual do construtor em `dag_trigger/Minio.py` aponta para `10.91.5.108:9000`/`datainsights_fh` — memória de 2026-08/09 registrava `107`/`datainsights`. Se é intencional, não foi verificado. |
| Airflow | `http://10.91.5.108:8080/api/v1/dags/{dag}/dagRuns` (REST, `saplogin.py:211`) | |
| SharePoint / MS Graph | site `fertilizantes.sharepoint.com/sites/DataInsight` via `graph_api_connector.py` | uso em produção hoje: não verificado |
| Pasta local de exportação | raiz `C:/Temp/t1/<categoria>` (definida em `files.json` desde 2026-08-28) | existência em prod confirmada só indiretamente (rodando) |
| Credenciais | `.enc` + `key.key` (Fernet via `menestrel_encryptor.py`), fora do git | ver riscos (§5) |

## 3. Componentes e fluxos de dados

**Fluxo:** SAP S/4HANA (transações/Z-reports) → SAP GUI Scripting → Excel `.XLSX` local (`C:/Temp/t1/...`) → MinIO bucket `tmp` (`upload_or_queue`, retry 3× + fila em memória) → trigger REST de DAG no Airflow → pipeline (Airflow/Hadoop, outras sessões) → dashboards.

**Componentes principais (`dag_trigger/`):**
- `menestrel.py` — loop único `schedule.run_pending()` a cada 10s; escreve `menestrel.pid` e `menestrel_heartbeat.txt`; log em `menestrel_song.log` (+ `menestrel_verbose.log` para incrementais).
- `saplogin.py` (`SAPLogin`) — login/logout SAP, `login_watchdog(120s)` (mata `saplogon.exe`), `export_watchdog(180s)` + `kill_excel()` (mata `excel.exe`), `trigger_airflow_dag()`.
- `Minio.py` (`MinioConnector`) — upload com retry/fila.
- `engdds_*.py` (~30 scripts) + `position_files.py` — um por relatório/transação.
- `watchdog_menestrel.py` — processo externo via Task Scheduler (registrado 2026-09-16): se PID morto ou heartbeat > 60 min, mata menestrel + `saplogon`/`excel` e relança. Log `watchdog_song.log`. Hook Teams desativado.
- `heartbeat_utils.py`, `daily_state.py` (`daily_state.json`: tasks diárias concluídas hoje, reset automático no rollover), `pause_utils.py` + `pausar_menestrel.py`/`retomar_menestrel.py` (pausa manual que o watchdog respeita, expira em 40 min).
- Ferramentas ad-hoc não agendadas: `_carga_faturamento.py`, `_carga_matmov.py`, `spot_runner.py`.

**Agenda (código atual, `menestrel.py:850-857`, horário local):**
| Hora | Job | DAG Airflow disparada |
|---|---|---|
| 00:05 | `extracao_diaria` — cadeia sequencial de ~25 tasks: POSITION_FILES, SKU, WERKISH, CUSTOS, FATURAMENTO, BOM, COMPRAS, COCKPIT, VBAK, GL_ACCOUNTS (inclui POAC), INDIRECT_PROCUREMENT, ESTOQUE, MB51_QUEBRA, FBL1H, COOISPI_SEG/VARREDURA/VARREDURA_MP, ZFI_NF_PIVB, VL06I, COGI, ZFI_GL_PIVB, MB51_CONSUMO, FBL3H, FBL5H, NF_01 | `daily_chained_dags` (+ `engdds_faturamento`, `engdds_units` em tasks específicas) |
| 00:15 | `armar_incrementais` — arma o kickoff do dia | — |
| 05:00 | TEXT_INFO (textos de cabeçalho de pedido) | — |
| 06:00–19:00, de hora em hora (`:30`, `.until(19:00)`), exceto domingo | `executar_incrementais`: FATURAMENTO, COMPRAS, GL_ACCOUNTS, INDIRECT_PROCUREMENT, ZMB5T, MB52 | `minio_incremental_hourly` (uma DAG combinada se ≥1 sucesso) |
| 19:05 | ESTOQUE_FULL (`ZMM_QNTY_PIVB`, ~51 dias × 3 BUKRS E600/E900/E890 ≈ 153 exports) | `minio_estoque_refresh_sap4hana` |
| 21:00 | BOM | — |

**Resiliência em camadas:** `executar_com_retry` por bloco dentro do script (3×, 60s) → script levanta `RuntimeError` se algum bloco falhou → `run_with_retry` no orquestrador (2×, 60s) → watchdogs internos de login/export → watchdog externo (heartbeat 60 min).

**Restrição estrutural:** tudo roda em **uma única thread** (COM/SAP GUI exige). Não há paralelismo; um job longo atrasa todos os seguintes.

**Escopo organizacional:** estoque migrou de filtro por planta (WERKS `E60*,E89*,E90*,P60*,P90*`) para **empresa (BUKRS `E600,E900,E890`)** em 2026-09-08. Layout `ZMM_QNTY_PIVB` usa variante `/IT_INV_EXT`; ESTOQUE_FULL força `/ENSURE_CALC`.

## 4. Estado atual (em 2026-10-01)

- Em produção com o código unificado (v6.1.0). Merge vFTO/vFH fases 01–06 + backport WERKS→BUKRS: **concluídos e commitados**.
- Watchdog externo **registrado** no Task Scheduler em 2026-09-16 (antes nunca tinha rodado). Se `watchdog_song.log` está sendo gerado regularmente: não verificado.
- 2026-09-18: logging padronizado (print→logging, `exc_info=True`, `except:` nu estreitado no caminho login/export) e correção do bug "falha engolida sem raise" em 25 de 27 scripts — scripts agora realmente re-tentam e falham de forma visível. Validação foi só sintática/estrutural (contagem de `findById`/`.press()` inalterada + `py_compile`); comportamento contra SAP real não foi observado pela sessão.
- 2026-09-21: fix do watchdog matando ESTOQUE_FULL saudável ~20:03 (faltava refresh de heartbeat no loop de 153 exports) — 2 linhas em `engdds_estoque_full.py`; commit `11fda71`. Causou de 2026-09-18 a 2026-09-21 a ausência de `ZMM_QNTY_PIVB_{E600,E900,E890}_ALL.XLSX` no MinIO (detectado por ag01_data_eng; cascata em material_movements/produção/compras/inventory_report e Ghost Stock em dobro no dashboard).
- Commits recentes (09-21 → hoje): "Protetores de Execução" v1/v2, "Persistência de script + logging" (`daily_state` / pausa), "Kill silencioso de schedule saudável".

## 5. Problemas conhecidos e riscos

1. **Repo público + credenciais hardcoded.** Histórico purgado em 2026-09-10 (`.enc`, `key.key`, `SENHA.txt`, `*.log`, incl. re-apontamento de 13 tags). Mas `Minio.py` ainda tem credencial MinIO em texto como default do construtor e `saplogin.py` tem a do Airflow — deve ser considerada **exposta**; recomenda-se rotação. Débito adiado pelo usuário (2026-08-28) antes de se saber que o repo era público.
2. **ESTOQUE_FULL pode passar da meia-noite** e atrasar toda a cadeia diária do dia seguinte (single-thread). Também não tem rastreio de conclusão diária: se morrer por motivo real após 19:05, só roda no dia seguinte.
3. **Tick incremental interrompido não é retomado** no boot (só arma a próxima hora). Um tick que vence após `FIM` (19:00) com a thread ocupada é **cancelado**, não atrasado (semântica de `.until()` da lib `schedule`).
4. **Navegação SAP sem watchdog:** só login (120s) e export (180s) têm timeout; travamento em `findById` durante navegação só é pego pelo watchdog externo após 60 min.
5. **Popups modais inesperados** (`wnd[1]`) ainda tratados por `except` genérico em `saplogin._perform_login` — hipótese principal das falhas noturnas, junto com possível janela de manutenção Basis (não verificado com Basis).
6. **Log congelado pós-deploy:** em 2026-09-02 `menestrel_song.log` parou de receber linhas sem o processo travar — teoria: FileHandler órfão após o deploy recriar o arquivo (não verificado em prod). Mitigação operacional: reiniciar `menestrel.py` após todo deploy.
7. `engdds_estoque_full.py` e `engdds_text_info.py` ainda não seguem o padrão `executar_com_retry`/raise (text_info é tolerante por design: um PO ruim não derruba o lote).
8. Divergência do default de host MinIO em `Minio.py` (ver §2) — verificar se os uploads FTO estão indo para o MinIO certo (não verificado).
9. Aumento de tempo-até-falha aceito (retries 3×60s por bloco + 2×60s por task) em troca de não perder dados silenciosamente.
10. Dependência de RPA de GUI: alternativas (RFC/BAPI, Z-report gravando no servidor via `OPEN DATASET` + job SM36) discutidas e não iniciadas.

## 6. Decisões tomadas

| Data | Decisão | Quem |
|---|---|---|
| 2026-08-12 | Watchdog externo por heartbeat/PID + `login_watchdog`; sem Windows Service (exige desktop interativo); alertas só por log (Teams indisponível) | Murilo |
| 2026-08-19 | Janelas incrementais ajustadas manualmente pelo usuário; depois substituídas por janela única dinâmica | Murilo |
| 2026-08-26/28 | Merge vFTO+vFH como backport bidirecional, mantendo literais de ambiente separados por site; triggers Airflow individuais na diária; sem `menestrel_excel_guard.py`; `files.json` com raiz `C:/Temp/t1/`; deletados `saplogin_p.py` e `engdds_profitability.py` | Murilo |
| 2026-08-28 | Credenciais em `Minio.py` adiadas como débito técnico | Murilo |
| 2026-09-08 | Estoque por BUKRS (E600/E900/E890) em vez de WERKS; `/ENSURE_CALC` no ESTOQUE_FULL; seção legada ZMB5T+MCHB do estoque_full deprecada | Murilo |
| 2026-09-10 | Purga de histórico git (creds + logs) com force-push de branch e tags | Murilo (executado com Claude) |
| 2026-09-18 | Retry + raise em 25 scripts; aceito o maior tempo-até-falha | Murilo |
| 2026-09-21 | Fix mínimo (2 linhas) para o kill do ESTOQUE_FULL; rejeitados rastreio de estado e resume-on-boot por complexidade | Murilo |
| 2026-09-30 | Correções pequenas: Claude só diagnostica (arquivo:linha), Murilo aplica | Murilo |
| (vigente) | Janela incremental 06:00–19:00, ESTOQUE_FULL 19:05, BOM 21:00, TEXT_INFO 05:00; incrementais com 1 DAG combinada | Murilo |

## 7. Pendências e próximos passos

- Rotacionar/remover credenciais hardcoded (MinIO, Airflow) dado repo público.
- Confirmar o host MinIO efetivo usado pelos uploads FTO (divergência em `Minio.py`).
- Confirmar que `watchdog_song.log` está sendo gerado (prova de que a tarefa agendada dispara).
- Consultar Basis sobre janela de manutenção noturna do S/4 PRD.
- Logar conteúdo de popups `wnd[1]` desconhecidos em vez de engolir.
- Decidir tratamento de retry para `engdds_estoque_full.py` e `engdds_text_info.py`.
- Avaliar resiliência do ESTOQUE_FULL (lookback de ~51 dias, duração, rastreio diário) — apenas se pedido.
- Conferir que nenhum dos 25 scripts refatorados em 2026-09-18 regrediu em execução real (validação só foi estática).
- Opcional: `logging.getLogger(__name__)` por módulo; mensagem de log explícita para tasks puladas.

## 8. Dependências com outras sessões

- **ag01_data_eng** — consome os arquivos do bucket MinIO `tmp` e as DAGs disparadas (`daily_chained_dags`, `minio_incremental_hourly`, `minio_estoque_refresh_sap4hana`, `engdds_faturamento`, `engdds_units`). Foi quem detectou a ausência de `ZMM_QNTY_PIVB_*_ALL.XLSX` (2026-09-18→21). Qualquer mudança de nome de arquivo, BUKRS/WERKS, layout de variante ou horário no Menestrel impacta essa sessão.
- **ag02_dash_dev** — impacto indireto: atrasos/falhas de extração viram dados velhos ou duplicados no dashboard (ex.: Ghost Stock em dobro em 2026-09). Contrato direto com Menestrel: nenhum conhecido.
- **sap-odp** — presumivelmente avalia extração SAP via ODP (alternativa/complemento ao RPA de GUI); não houve interação direta registrada (não verificado). Relatórios que o Menestrel cobre hoje via GUI são candidatos naturais a migração — ver lista da diária em §3.

## 9. Glossário

- **Menestrel** — o orquestrador; `menestrel_song.log` é seu log principal.
- **engdds_*.py** — um script de extração por relatório SAP ("engenharia de dados – data source").
- **vFTO / vFH / vFTO_new** — forks pré-merge: FTO = EuroChem Fertilizantes Tocantins; FH = Heringer; `_new` = iteração posterior do FTO.
- **Diária / cadeia diária** — `extracao_diaria` das 00:05.
- **Incrementais / hourly** — extrações de hora em hora 06:00–19:00.
- **ESTOQUE_FULL** — reprocesso de estoque de ~51 dias às 19:05 (`task13`).
- **Heartbeat** — `menestrel_heartbeat.txt`, atualizado pelo loop e por scripts longos; base do watchdog.
- **BUKRS** — código de empresa SAP (E600, E900, E890). **WERKS** — centro/planta SAP (E60*, E89*, E90*, P60*, P90*).
- **&XXL** — exportação de ALV para Excel no SAP GUI.
- **ZMM_QNTY_PIVB** — Z-report de quantidades de estoque; **ZMB5T**, **MB51**, **MB52**, **MCHB** — estoque em trânsito, movimentos, estoque por depósito, tabela de lotes.
- **COOISPI** — relatório de ordens de processo; **COGI** — erros de baixa automática; **VL06I** — remessas de entrada; **FBL1H/3H/5H** — partidas de fornecedor/razão/cliente; **ZFI_GL_PIVB / ZFI_NF_PIVB** — Z-reports financeiros (razão / notas fiscais); **POAC** — seção extra do GL_ACCOUNTS; **VBAK** — cabeçalho de ordens de venda; **ZPP_BOMREP** — BOM.
- **Basis** — time de administração do SAP.
- **`tmp`** — bucket de stage no MinIO onde o Menestrel deposita os arquivos.
