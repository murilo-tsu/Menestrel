import schedule
import logging
import threading
from datetime import datetime, time as t
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
from engdds_mb51_quebra import engdds_mb51_quebra_main
from engdds_fbl1h import engdds_fbl1h_main
from engdds_cooispi_seg import engdds_cooispi_seg_main
from engdds_cooispi_varredura import engdds_cooispi_varredura_main
from engdds_cooispi_varredura_mp import engdds_cooispi_varredura_mp_main
from engdds_zfi_nf_pivb import engdds_zfi_nf_pivb_main
from engdds_vl06i import engdds_vl06i_main
from engdds_cogi import engdds_cogi_main
from engdds_zfi_gl_pivb import engdds_zfi_gl_pivb_main
from engdds_mb51_consumo import engdds_mb51_consumo_main
from engdds_fbl3h import engdds_fbl3h_main
from engdds_fbl5h import engdds_fbl5h_main
from engdds_nf_01 import engdds_nf_01_main
from engdds_zmb5t import engdds_zmb5t_main
from engdds_mb52 import engdds_mb52_main

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
# ║ WATCHDOG EXTERNO :: arquivos de sinal de vida lidos por watchdog_menestrel.py     ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

PID_FILE = 'menestrel.pid'
HEARTBEAT_FILE = 'menestrel_heartbeat.txt'


def escrever_heartbeat():
    """Sinaliza ao watchdog externo que o loop principal não está travado."""
    with open(HEARTBEAT_FILE, 'w') as f:
        f.write(str(time.time()))

# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ FUNÇÕES UTILITÁRIAS                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def print_header():
    """ ASCII :: ARTE DE CABEÇALHO """
    print(HEADER)
    print(f"{Fore.LIGHTWHITE_EX}╔══════════════════════════════════════════════════════════════════════════════════╗")
    print(f"║ {'Orquestrador de scripts de extração do SAP4HANA :: v5.1.1':^80} ║")
    print(f"║ {f'Inicializado: {datetime.now()} @10.91.0.60':^80} ║")
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
        'task14', 'task15', 'task16', 'task17', 'task18', 'task19', 'task20',
        'task21', 'task22', 'task23', 'task24', 'task25', 'task26',
        'hourly_task01', 'hourly_task02', 'hourly_task03', 'hourly_task04',
        'hourly_task05', 'hourly_task06', 'position_files',

        # Funções de RPA com objetivos específicos
        'engdds_estoque_main', 'engdds_compras_main', 'engdds_faturamento_main',
        'engdds_faturamento_daily_main', 'engdds_sku_main', 'engdds_bom_main',
        'engdds_custos_main', 'engdds_vbak', 'engdds_werkish_main', 'engdds_text_info_main',
        'engdds_cockpit_main', 'engdds_faturamento_hourly_main', 'position_files_main',
        'engdds_vbak_main', 'engdds_gl_accounts_main', 'engdds_indirect_procurement_main',
        'engdds_estoque_full_main', 'engdds_mb51_quebra_main', 'engdds_fbl1h_main',
        'engdds_cooispi_seg_main', 'engdds_cooispi_varredura_main', 'engdds_cooispi_varredura_mp_main',
        'engdds_zfi_nf_pivb_main', 'engdds_vl06i_main', 'engdds_cogi_main',
        'engdds_zfi_gl_pivb_main', 'engdds_mb51_consumo_main', 'engdds_fbl3h_main',
        'engdds_fbl5h_main', 'engdds_nf_01_main', 'engdds_zmb5t_main', 'engdds_mb52_main',

        # Bibliotecas a serem protegidas a cada execução de limpeza de variáveis
        'schedule', 'logging', 'datetime', 'Fore', 'Style', 'init', 'time', 'threading',
        'json', 'os', 't', 'sap', 'minio', 'Minio', 'MinioConnector',

        # Funções e variáveis auxiliares
        'extracao_diaria', 'extracoes_incrementais', 'HEADER', 'print_header',
        'clear_terminal_print_logo', 'limpar_variaveis', 'SAPLogin', 'trigger',

        # Resiliência — lock, retry, constantes
        'run_with_retry', 'sap_lock',
        'TASK_RETRIES', 'RETRY_DELAY',

        # Watchdog externo — sinal de vida
        'escrever_heartbeat', 'PID_FILE', 'HEARTBEAT_FILE',

        # Reagendamento dinâmico dos incrementais + log verboso por task
        't', 'MIN_INICIO', 'FIM', 'armar_incrementais', 'kickoff_incrementais',
        'executar_incrementais', 'rodar_com_saida_verbose',
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
    from saplogin import SAPLogin
    trigger = SAPLogin()
    with sap_lock:
        try:
            engdds_estoque_full_main()
            logging.info("ENGDDS_ESTOQUE_FULL_MAIN executado")
            trigger.trigger_airflow_dag(dag_name='minio_estoque_refresh_sap4hana')
        except Exception as erro:
            logging.error(f"ENGDDS_ESTOQUE_FULL_MAIN não executado: {erro}")
            raise
        finally:
            limpar_variaveis()


def task14():
    try:
        engdds_mb51_quebra_main()
        logging.info("ENGDDS_MB51_QUEBRA_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_MB51_QUEBRA_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task15():
    try:
        engdds_fbl1h_main()
        logging.info("ENGDDS_FBL1H_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_FBL1H_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task16():
    try:
        engdds_cooispi_seg_main()
        logging.info("ENGDDS_COOISPI_SEG_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_COOISPI_SEG_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task17():
    try:
        engdds_cooispi_varredura_main()
        logging.info("ENGDDS_COOISPI_VARREDURA_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_COOISPI_VARREDURA_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task18():
    try:
        engdds_cooispi_varredura_mp_main()
        logging.info("ENGDDS_COOISPI_VARREDURA_MP_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_COOISPI_VARREDURA_MP_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task19():
    try:
        engdds_zfi_nf_pivb_main()
        logging.info("ENGDDS_ZFI_NF_PIVB_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_ZFI_NF_PIVB_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task20():
    try:
        engdds_vl06i_main()
        logging.info("ENGDDS_VL06I_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_VL06I_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task21():
    try:
        engdds_cogi_main()
        logging.info("ENGDDS_COGI_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_COGI_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task22():
    try:
        engdds_zfi_gl_pivb_main()
        logging.info("ENGDDS_ZFI_GL_PIVB_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_ZFI_GL_PIVB_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task23():
    try:
        engdds_mb51_consumo_main()
        logging.info("ENGDDS_MB51_CONSUMO_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_MB51_CONSUMO_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task24():
    try:
        engdds_fbl3h_main()
        logging.info("ENGDDS_FBL3H_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_FBL3H_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task25():
    try:
        engdds_fbl5h_main()
        logging.info("ENGDDS_FBL5H_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_FBL5H_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def task26():
    try:
        engdds_nf_01_main()
        logging.info("ENGDDS_NF_01_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_NF_01_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ HELPERS :: Log verboso por task incremental                                      ║
# ║ ---------------------------------------------                                    ║
# ║ Mantém o CMD e o menestrel_song.log resumidos; os prints internos de cada        ║
# ║ engdds_*_main() incremental vão para menestrel_verbose.log para diagnóstico.     ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def rodar_com_saida_verbose(funcao, nome_task):
    import contextlib

    verbose_path = os.path.join(os.path.dirname(__file__), "menestrel_verbose.log")

    with open(verbose_path, "a", encoding="utf-8") as verbose:
        verbose.write("\n")
        verbose.write("═════════════════════════════════════════════════════════════════════════\n")
        verbose.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} :: INÍCIO VERBOSE :: {nome_task}\n")
        verbose.write("═════════════════════════════════════════════════════════════════════════\n")

        with contextlib.redirect_stdout(verbose), contextlib.redirect_stderr(verbose):
            funcao()

        verbose.write("═════════════════════════════════════════════════════════════════════════\n")
        verbose.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} :: FIM VERBOSE :: {nome_task}\n")
        verbose.write("═════════════════════════════════════════════════════════════════════════\n")


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK LIST :: Lista de tarefas de extração incremental                            ║
# ║ -----------------------------------------------------                            ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def hourly_task01():
    try:
        rodar_com_saida_verbose(engdds_faturamento_hourly_main, "HOURLY_FATURAMENTO")
        logging.info("ENGDDS_FATURAMENTO_HOURLY_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_FATURAMENTO_HOURLY_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def hourly_task02():
    try:
        rodar_com_saida_verbose(engdds_compras_main, "HOURLY_COMPRAS")
        logging.info("ENGDDS_COMPRAS_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_COMPRAS_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def hourly_task03():
    try:
        rodar_com_saida_verbose(engdds_gl_accounts_main, "HOURLY_GL_ACCOUNTS")
        logging.info("ENGDDS_GL_ACCOUNTS_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_GL_ACCOUNTS_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def hourly_task04():
    try:
        rodar_com_saida_verbose(engdds_indirect_procurement_main, "HOURLY_INDIRECT_PROCUREMENT")
        logging.info("ENGDDS_INDIRECT_PROCUREMENT_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_INDIRECT_PROCUREMENT_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def hourly_task05():
    try:
        rodar_com_saida_verbose(engdds_zmb5t_main, "HOURLY_ZMB5T")
        logging.info("ENGDDS_ZMB5T_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_ZMB5T_MAIN não executado: {erro}")
        raise
    finally:
        limpar_variaveis()


def hourly_task06():
    try:
        rodar_com_saida_verbose(engdds_mb52_main, "HOURLY_MB52")
        logging.info("ENGDDS_MB52_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_MB52_MAIN não executado: {erro}")
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
        run_with_retry(task14,    task_name="MB51_QUEBRA")
        run_with_retry(task15,    task_name="FBL1H")
        run_with_retry(task16,    task_name="COOISPI_SEG")
        run_with_retry(task17,    task_name="COOISPI_VARREDURA")
        run_with_retry(task18,    task_name="COOISPI_VARREDURA_MP")
        run_with_retry(task19,    task_name="ZFI_NF_PIVB")
        run_with_retry(task20,    task_name="VL06I")
        run_with_retry(task21,    task_name="COGI")
        run_with_retry(task22,    task_name="ZFI_GL_PIVB")
        run_with_retry(task23,    task_name="MB51_CONSUMO")
        run_with_retry(task24,    task_name="FBL3H")
        run_with_retry(task25,    task_name="FBL5H")
        run_with_retry(task26,    task_name="NF_01")

        trigger.trigger_airflow_dag(dag_name='daily_chained_dags')
        logging.info("Final do Processamento :: EXTRACAO DIARIA")
        logging.info("═" * 75)

    except Exception as e:
        logging.error(f"Erro crítico na EXTRACAO DIARIA: {e}")
    finally:
        sap_lock.release()


def executar_incrementais():
    """
    Executa uma rodada das extrações incrementais e o lock global
    anti-sobreposição com a diária. Chamada de hora em hora pelo agendamento
    criado em extracoes_incrementais().

    Sem janela de horário por task — a janela de negócio é uma só, aplicada
    externamente (MIN_INICIO–FIM) pelo reagendamento dinâmico: um tick só
    existe dentro de 06:00–19:00, então todas as tasks abaixo já rodam só
    dentro dela. Estrutura de resultados + trigger único de DAG combinada
    (minio_incremental_hourly) adotada do dag_trigger_vFH.
    """
    if not sap_lock.acquire(blocking=False):
        logging.warning("INCREMENTAIS ignoradas — outra extração já está em andamento")
        return

    try:
        from saplogin import SAPLogin

        logging.info("Agendamento de extrações :: Hourly Update")

        resultados = {}
        resultados["FATURAMENTO"] = run_with_retry(hourly_task01, task_name="HOURLY_FATURAMENTO")
        resultados["COMPRAS"] = run_with_retry(hourly_task02, task_name="HOURLY_COMPRAS")
        resultados["GL_ACCOUNTS"] = run_with_retry(hourly_task03, task_name="HOURLY_GL_ACCOUNTS")
        resultados["INDIRECT_PROCUREMENT"] = run_with_retry(hourly_task04, task_name="HOURLY_INDIRECT_PROCUREMENT")
        resultados["ZMB5T"] = run_with_retry(hourly_task05, task_name="HOURLY_ZMB5T")
        resultados["MB52"] = run_with_retry(hourly_task06, task_name="HOURLY_MB52")

        sucessos = [nome for nome, ok in resultados.items() if ok]
        falhas = [nome for nome, ok in resultados.items() if not ok]

        if sucessos:
            logging.info("Extrações incrementais com sucesso: " + ", ".join(sucessos))

            if falhas:
                logging.error("Extrações incrementais com falha: " + ", ".join(falhas))

            trigger = SAPLogin()
            trigger.trigger_airflow_dag(dag_name='minio_incremental_hourly')
            logging.info(
                "DAG minio_incremental_hourly disparada — pelo menos uma "
                "extração incremental foi executada com sucesso."
            )
        else:
            logging.error(
                "Nenhuma extração incremental foi executada com sucesso. "
                "DAG minio_incremental_hourly não será disparada."
            )

        logging.info("Aguardando execução dos próximos jobs...")

    except Exception as e:
        logging.error(f"Erro crítico nas INCREMENTAIS: {e}")
    finally:
        sap_lock.release()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ REAGENDAMENTO DINÂMICO :: substitui o poll fixo de 120min                        ║
# ║ -------------------------------------------------------                          ║
# ║ Uma única janela de negócio (06:00–19:00) para todas as tasks horárias — sem     ║
# ║ janela individual por task (estrutura adotada do dag_trigger_vFH). Este          ║
# ║ mecanismo se re-arma a cada hora cheia dentro da janela, garantindo que a        ║
# ║ 1ª checagem do dia caia bem no início do slot (06:00), sem depender de um        ║
# ║ poll de intervalo fixo que poderia perder a borda da janela.                     ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

MIN_INICIO = t(6, 0)
FIM = t(19, 0)


def _proximo_kickoff(now):
    """Calcula o próximo horário xx:00 dentro da janela MIN_INICIO–FIM."""
    if now.weekday() == 6:
        return "06:00"

    if now.time() < MIN_INICIO:
        return "06:00"

    if now.time() >= FIM:
        return "06:00"

    next_hour = now.hour + 1
    if next_hour >= 19:
        return "06:00"
    return f"{next_hour:02d}:00"


def kickoff_incrementais():
    schedule.clear('incremental_start')
    extracoes_incrementais()


def armar_incrementais():
    schedule.clear('incremental_start')
    now = datetime.now()
    hhmm = _proximo_kickoff(now)
    schedule.every().day.at(hhmm).do(kickoff_incrementais).tag('incremental_start')
    logging.info(f"Kickoff incrementais armado para {hhmm}.")


def extracoes_incrementais():
    """
    Arma o ciclo de incrementais do dia: roda uma vez imediatamente e agenda
    novas rodadas de hora em hora até as 19:00. Disparada pelo kickoff dinâmico
    (armar_incrementais), não por um poll de intervalo fixo.
    """
    now = datetime.now()

    # Sempre limpa qualquer agendamento incremental pendurado antes de recriar
    schedule.clear('incremental')

    if now.weekday() == 6:
        logging.info("Domingo — incrementais desativadas.")
        return

    if now.time() >= FIM:
        logging.info("Após 19:00 — incrementais não serão agendadas hoje.")
        return

    executar_incrementais()

    schedule.every(60).minutes.until(FIM).do(executar_incrementais).tag('incremental')
    logging.info("Incrementais agendadas de hora em hora até as 19:00.")


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ MAIN :: Inicialização e agendamento                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menestrel_song.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler()
    ],
    force=True
)

with open(PID_FILE, 'w') as f:
    f.write(str(os.getpid()))

logging.info(f"Menestrel iniciado — PID {os.getpid()}")

print_header()

# Rodadas diárias
schedule.every().day.at("00:01").do(clear_terminal_print_logo)
schedule.every().day.at("00:05").do(extracao_diaria)
schedule.every().day.at("05:00").do(run_with_retry, task09, task_name="TEXT_INFO")
schedule.every().day.at("19:05").do(run_with_retry, task13, task_name="ESTOQUE_FULL")

# Extrações incrementais — reagendamento dinâmico (evita o gap de poll fixo)
schedule.every().day.at("00:15").do(armar_incrementais)
armar_incrementais()

while True:
    escrever_heartbeat()
    schedule.run_pending()
    time.sleep(10)