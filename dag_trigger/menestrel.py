import schedule
import logging
import threading
from datetime import datetime
from colorama import init, Fore, Style
import time
import os
from position_files import position_files_main
from engdds_estoque import engdds_estoque_main
from engdds_estoque_full import engdds_estoque_full_main
from engdds_compras import engdds_compras_main
from engdds_custos import engdds_custos_main
from engdds_faturamento import engdds_faturamento_main
from engdds_faturamento_hourly import engdds_faturamento_hourly_main
from engdds_bom import engdds_bom_main
from engdds_sku import engdds_sku_main
from engdds_werkish import engdds_werkish_main
from engdds_cockpit import engdds_cockpit_main
from engdds_text_info import engdds_text_info_main
from engdds_vbak import engdds_vbak_main
from engdds_gl_accounts import engdds_gl_accounts_main
from engdds_indirect_procurement import engdds_indirect_procurement_main

# Inicializando o COLORAMA
init()

HEADER = f"""{Fore.CYAN}
███╗   ███╗███████╗███╗   ██╗███████╗███████╗████████╗██████╗ ███████╗██╗         
████╗ ████║██╔════╝████╗  ██║██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║         
██╔████╔██║█████╗  ██╔██╗ ██║█████╗  ███████╗   ██║   ██████╔╝█████╗  ██║         
██║╚██╔╝██║██╔══╝  ██║╚██╗██║██╔══╝  ╚════██║   ██║   ██╔══██╗██╔══╝  ██║         
██║ ╚═╝ ██║███████╗██║ ╚████║███████╗███████║   ██║   ██║  ██║███████╗███████╗    
╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝    
{Style.RESET_ALL}"""

# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ LOCK GLOBAL :: Impede concorrência entre extração diária e incremental           ║
# ║ NOTA: Sem threading nas tasks — COM/SAP GUI exige mesma thread.                  ║
# ║       O lock serve apenas para o schedule não sobrepor diária + incremental.     ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

sap_lock = threading.Lock()

# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ CONSTANTES DE RESILIÊNCIA                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

TASK_RETRIES = 2      # tentativas por task
RETRY_DELAY = 60      # segundos entre tentativas

# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ FUNÇÕES UTILITÁRIAS                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def print_header():
    """ ASCII :: ARTE DE CABEÇALHO """
    print(HEADER)
    print(f"{Fore.LIGHTWHITE_EX}╔══════════════════════════════════════════════════════════════════════════════════╗")
    print(f"║ {'Orquestrador de scripts de extração do SAP4HANA :: v2.2.0':^80} ║")
    print(f"║ {f'Inicializado: {datetime.now()} @10.88.55.26':^80} ║")
    print(f"╠══════════════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"{Fore.LIGHTWHITE_EX}║                           {Fore.LIGHTGREEN_EX}Aguardando scripts agendados{Style.RESET_ALL}{Fore.LIGHTWHITE_EX}                           ║")
    print(f"╚══════════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")


def clear_terminal_print_logo():
    """Limpar o terminal para manter a LOGO do menestrel"""
    os.system('cls')
    print_header()


def run_with_retry(func, max_retries=TASK_RETRIES, delay=RETRY_DELAY, task_name="TASK"):
    """
    Retry simples na MESMA THREAD — compatível com COM/SAP GUI Scripting.
    Sem threading: objetos COM são vinculados à thread que os criou.
    
    As tasks devem fazer raise após logar o erro para que o retry funcione.
    """
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"{task_name} — tentativa {attempt}/{max_retries}")
            func()
            logging.info(f"{task_name} executado com sucesso (tentativa {attempt})")
            return True
        except Exception as e:
            logging.error(f"{task_name} falhou tentativa {attempt}/{max_retries}: {e}")
            if attempt < max_retries:
                logging.info(f"{task_name} — aguardando {delay}s antes de re-tentar...")
                time.sleep(delay)

    logging.error(f"{task_name} falhou após {max_retries} tentativas")
    return False


def limpar_variaveis():
    """Limpar variáveis externas ao menestrel.py"""
    protected_vars = {

        # Tasks declaradas
        'pre_task', 'task01', 'task02', 'task03', 'task04', 'task05', 'task06', 'task07',
        'task08', 'task09', 'task10', 'task11', 'task12', 'task13',
        'hourly_task01', 'hourly_task02', 'hourly_task03', 'hourly_task04', 'position_files',

        # Funções de RPA com objetivos específicos
        'engdds_estoque_main', 'engdds_compras_main', 'engdds_faturamento_main',
        'engdds_faturamento_daily_main', 'engdds_sku_main', 'engdds_bom_main',
        'engdds_custos_main', 'engdds_vbak', 'engdds_werkish_main', 'engdds_text_info_main',
        'engdds_cockpit_main', 'engdds_faturamento_hourly_main', 'position_files_main',
        'engdds_vbak_main', 'engdds_gl_accounts_main', 'engdds_indirect_procurement_main',
        'engdds_estoque_full_main',

        # Bibliotecas a serem protegidas a cada execução de limpeza de variáveis
        'schedule', 'logging', 'datetime', 'Fore', 'Style', 'init', 'time', 'threading',
        'json', 'os', 't', 'sap', 'schedule_time', 'minio', 'Minio', 'MinioConnector',

        # Funções e variáveis auxiliares
        'extracao_diaria', 'extracoes_incrementais', 'HEADER', 'print_header', 'schedule_time',
        'clear_terminal_print_logo', 'limpar_variaveis', 'SAPLogin', 'trigger',

        # Resiliência — lock, retry, constantes
        'run_with_retry', 'sap_lock',
        'TASK_RETRIES', 'RETRY_DELAY',
    }

    # Obter variáveis locais
    current_globals = list(globals().keys())

    # Deletar todas as variáveis não protegidas
    for var in current_globals:
        if not var.startswith('_') and var not in protected_vars:
            del globals()[var]

    import gc
    gc.collect()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK LIST :: Lista de tarefas de extração                                        ║
# ║ -----------------------------------------                                        ║
# ║ IMPORTANTE: cada task faz raise após logar o erro, para que o run_with_retry     ║
# ║ saiba que falhou e possa re-tentar.                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def task01():
    try:
        engdds_sku_main()
        logging.info("ENGDDS_SKU_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_SKU_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task02():
    try:
        engdds_werkish_main()
        logging.info("ENGDDS_WERKISH_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_WERKISH_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task03():
    try:
        engdds_custos_main()
        logging.info("ENGDDS_CUSTOS_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_CUSTOS_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task04():
    try:
        engdds_faturamento_main()
        logging.info("ENGDDS_FATURAMENTO_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_FATURAMENTO_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task05():
    try:
        engdds_bom_main()
        logging.info("ENGDDS_BOM_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_BOM_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task06():
    try:
        engdds_compras_main()
        logging.info("ENGDDS_COMPRAS_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_COMPRAS_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task07():
    try:
        engdds_estoque_main()
        logging.info("ENGDDS_ESTOQUE_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_ESTOQUE_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task08():
    try:
        engdds_cockpit_main()
        logging.info("ENGDDS_COCKPIT_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_COCKPIT_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task09():
    with sap_lock:
        from saplogin import SAPLogin
        trigger = SAPLogin()
        try:
            engdds_text_info_main()
            logging.info("ENGDDS_TEXT_INFO_MAIN executado")
        except Exception as erro:
            logging.error(f"ENGDDS_TEXT_INFO_MAIN não executado: {erro}")
            raise
        finally:
            limpar_variaveis()


def task10():
    try:
        engdds_vbak_main()
        logging.info("ENGDDS_VBAK executado")
    except Exception as erro:
        logging.error(f"ENGDDS_VBAK não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task11():
    try:
        engdds_gl_accounts_main()
        logging.info("ENGDDS_GL_ACCOUNTS executado")
    except Exception as erro:
        logging.error(f"ENGDDS_GL_ACCOUNTS não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task12():
    try:
        engdds_indirect_procurement_main()
        logging.info("ENGDDS_INDIRECT_PROCUREMENT executado")
    except Exception as erro:
        logging.error(f"ENGDDS_INDIRECT_PROCUREMENT não executado: {erro}")
        raise
    finally:
        limpar_variaveis()

def task13():
    with sap_lock:
        try:
            engdds_estoque_full_main()
            logging.info("ENGDDS_ESTOQUE_FULL_MAIN executado")
        except Exception as erro:
            logging.error(f"ENGDDS_ESTOQUE_FULL_MAIN não executado: {erro}")
            raise
        finally:
            limpar_variaveis()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK LIST :: Lista de tarefas de extração incremental                            ║
# ║ -----------------------------------------------------                            ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def hourly_task01():
    from saplogin import SAPLogin
    trigger = SAPLogin()
    try:
        engdds_faturamento_hourly_main()
        logging.info("ENGDDS_FATURAMENTO_HOURLY_MAIN executado")
        trigger.trigger_airflow_dag(dag_name='minio_hourly_billing_sap4hana')
    except Exception as erro:
        logging.error(f"ENGDDS_FATURAMENTO_HOURLY_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def hourly_task02():
    from saplogin import SAPLogin
    trigger = SAPLogin()
    try:
        engdds_compras_main()
        logging.info("ENGDDS_COMPRAS_MAIN executado")
        trigger.trigger_airflow_dag(dag_name='minio_hourly_purchase_recap_sap4hana')
    except Exception as erro:
        logging.error(f"ENGDDS_COMPRAS_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def hourly_task03():
    from saplogin import SAPLogin
    trigger = SAPLogin()
    try:
        engdds_gl_accounts_main()
        logging.info("ENGDDS_GL_ACCOUNTS_MAIN executado")
        trigger.trigger_airflow_dag(dag_name='minio_hourly_gl_accounts_sap4hana')
    except Exception as erro:
        logging.error(f"ENGDDS_GL_ACCOUNTS_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def hourly_task04():
    from saplogin import SAPLogin
    trigger = SAPLogin()
    try:
        engdds_indirect_procurement_main()
        logging.info("ENGDDS_INDIRECT_PROCUREMENT_MAIN executado")
        trigger.trigger_airflow_dag(dag_name='minio_hourly_indirect_procurement')
    except Exception as erro:
        logging.error(f"ENGDDS_INDIRECT_PROCUREMENT_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK LIST :: Position Files                                                      ║
# ║ ---------------------------                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def pre_task():
    try:
        position_files_main()
        logging.info("POSITION_FILES executado")
    except Exception as erro:
        logging.error(f"POSITION_FILES não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK GROUPS :: Lista de grupos de tarefas em ordem de execução                   ║
# ║ --------------------------------------------------------------                   ║
# ║ Lock global garante que diária e incremental nunca rodam ao mesmo tempo.          ║
# ║ Retry com 2 tentativas cobre erros transitórios do SAP.                          ║
# ║ Tudo na MESMA THREAD — COM/SAP GUI exige isso.                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def extracao_diaria():
    """
    Executa a batelada inicial de extrações que deve ocorrer obrigatoriamente
    no começo do dia, fazendo um update dos dados até D-1.

    sku (t1) >> units (t2) >> custos (t3) >> faturamento (t4) >> bom (t5) >>
    compras (t6) >> cockpit (t8) >> vbak (t10) >> gl (t11) >> indirect (t12) >> estoque (t7)
    """
    if not sap_lock.acquire(blocking=False):
        logging.warning("EXTRACAO DIARIA ignorada — outra extração já está em andamento")
        return

    try:
        from saplogin import SAPLogin
        trigger = SAPLogin()

        logging.info("═" * 75)
        logging.info("Início do Processamento :: EXTRACAO DIARIA")

        run_with_retry(pre_task,  task_name="POSITION_FILES")
        run_with_retry(task01,    task_name="SKU")
        run_with_retry(task02,    task_name="WERKISH")
        run_with_retry(task03,    task_name="CUSTOS")
        run_with_retry(task04,    task_name="FATURAMENTO")
        run_with_retry(task05,    task_name="BOM")
        run_with_retry(task06,    task_name="COMPRAS")
        run_with_retry(task08,    task_name="COCKPIT")
        # run_with_retry(task09, task_name="TEXT_INFO")
        run_with_retry(task10,    task_name="VBAK")
        run_with_retry(task11,    task_name="GL_ACCOUNTS")
        run_with_retry(task12,    task_name="INDIRECT_PROCUREMENT")
        run_with_retry(task07,    task_name="ESTOQUE")

        trigger.trigger_airflow_dag(dag_name='daily_chained_dags')
        logging.info("Final do Processamento :: EXTRACAO DIARIA")
        logging.info("═" * 75)

    except Exception as e:
        logging.error(f"Erro crítico na EXTRACAO DIARIA: {e}")
    finally:
        sap_lock.release()


def extracoes_incrementais():
    """
    Executa extrações incrementais ao longo do dia para atualizar dados em um
    intervalo mais granular, viabilizando a visualização em tempo mais real.
    """
    if not sap_lock.acquire(blocking=False):
        logging.warning("INCREMENTAIS ignoradas — outra extração já está em andamento")
        return

    try:
        from datetime import time as t

        logging.info("Agendamento de extrações :: Hourly Update")

        # Hourly Task 01 :: Atualiza faturamento
        if t(10, 0) <= datetime.now().time() <= t(18, 0):
            run_with_retry(hourly_task01, task_name="HOURLY_FATURAMENTO")

        # Hourly Task 02 :: Atualiza Purchase Recap
        if t(9, 0) <= datetime.now().time() <= t(18, 0):
            run_with_retry(hourly_task02, task_name="HOURLY_COMPRAS")

        # Hourly Task 03 :: Atualizar GL Account Balance
        if t(10, 0) <= datetime.now().time() <= t(18, 0):
            run_with_retry(hourly_task03, task_name="HOURLY_GL_ACCOUNTS")

        # Hourly Task 04 :: Atualizar Indirect Procurement
        if t(10, 0) <= datetime.now().time() <= t(18, 0):
            run_with_retry(hourly_task04, task_name="HOURLY_INDIRECT_PROCUREMENT")

        logging.info("Aguardando execução dos próximos jobs...")

    except Exception as e:
        logging.error(f"Erro crítico nas INCREMENTAIS: {e}")
    finally:
        sap_lock.release()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ MAIN :: Inicialização e agendamento                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

logging.basicConfig(
    filename='menestrel_song.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

print_header()

# Rodadas diárias
schedule.every().day.at("00:01").do(clear_terminal_print_logo)
schedule.every().day.at("00:05").do(extracao_diaria)
schedule.every().day.at("07:30").do(task09)
schedule.every().day.at("18:05").do(task13)

# Extrações incrementais
schedule_time = 120
schedule.every(schedule_time).minutes.do(extracoes_incrementais)

while True:
    schedule.run_pending()
    time.sleep(10)