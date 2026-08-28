import schedule
import psycopg2
import logging
from datetime import datetime, time as t
from colorama import init, Fore, Style
import time

from menestrel_excel_guard import (
    excel_guarded as _excel_guarded,
    retry_pending_excel_jobs as _retry_pending_excel_jobs,
)

import os
from engdds_position_files import position_files_main
from engdds_estoque import engdds_estoque_main
from engdds_compras import engdds_compras_main
from engdds_custos import engdds_custos_main
from engdds_faturamento import engdds_faturamento_main
from engdds_faturamento_hourly import engdds_faturamento_hourly_main
from engdds_bom import engdds_bom_main
from engdds_sku import engdds_sku_main
from engdds_werkish import engdds_werkish_main
from engdds_cockpit import engdds_cockpit_main
from engdds_mb51_quebra import engdds_mb51_quebra_main
from engdds_text_info import engdds_text_info_main
from engdds_fbl1h import engdds_fbl1h_main
from engdds_cooispi_seg import engdds_cooispi_seg_main
from engdds_cooispi_varredura import engdds_cooispi_varredura_main
from engdds_cooispi_varredura_mp import engdds_cooispi_varredura_mp_main
from engdds_zfi_nf_pivb import engdds_zfi_nf_pivb_main
from engdds_vl06i import engdds_vl06i_main
from engdds_cogi import engdds_cogi_main
from engdds_zfi_gl_pivb import engdds_zfi_gl_pivb_main
from engdds_zmb5t import engdds_zmb5t_main
from engdds_mb52 import engdds_mb52_main
from _modulos import limpar_pasta
from engdds_mb51_consumo import engdds_mb51_consumo_main
from engdds_fbl3h import engdds_fbl3h_main
from engdds_fbl5h import engdds_fbl5h_main
from engdds_nf_01 import engdds_nf_01_main
#from engdds_chamadas import main


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

def print_header():
    """ ASCII :: ARTE DE CABEÇALHO """
    print(HEADER)
    print(f"{Fore.LIGHTWHITE_EX}╔══════════════════════════════════════════════════════════════════════════════════╗")
    print(f"║ {'Orquestrador de scripts de extração do SAP4HANA :: v2.0.0':^80} ║")
    print(f"║ {f'Inicializado: {datetime.now()} @10.88.55.26':^80} ║")
    print(f"╠══════════════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"{Fore.LIGHTWHITE_EX}║                           {Fore.LIGHTGREEN_EX}Aguardando scripts agendados{Style.RESET_ALL}{Fore.LIGHTWHITE_EX}                           ║")
    print(f"╚══════════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

def print_logo_header():
    print_header()

def clear_terminal_print_logo():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_header()

def limpar_variaveis():
    """Limpar variáveis externas ao menestrel.py"""
    protected_vars = {
        # Tasks declaradas
        'pre_task', 'task01', 'task02', 'task03', 'task04', 'task05', 'task06', 
        'task07', 'task08', 'task09', 'task10', 'task11', 'task12', 'task13',
        'task14', 'task15', 'task16', 'task17','task18', 'task19', 'task20',
        'task21', 'task22',
        'hourly_task01', 'hourly_task03', 'hourly_task04', 'hourly_task05', 'executar_incrementais', 
        'position_files', 'kickoff_incrementais', 'armar_incrementais', 'executar_hourly_task', 'rodar_com_saida_verbose',

        # Funções de RPA com objetivos específicos
        'position_files_main',
        'engdds_estoque_main', 'engdds_compras_main', 'engdds_custos_main',
        'engdds_faturamento_main', 'engdds_faturamento_hourly_main',
        'engdds_bom_main', 'engdds_sku_main', 'engdds_werkish_main',
        'engdds_cockpit_main', 'engdds_mb51_quebra_main', 'engdds_text_info_main',
        'engdds_fbl1h_main', 'engdds_cooispi_seg_main', 'engdds_cooispi_varredura_main',
        'engdds_cooispi_varredura_mp_main', 'engdds_zfi_nf_pivb_main',
        'engdds_vl06i_main', 'engdds_cogi_main', 'engdds_zfi_gl_pivb_main', 'engdds_mb51_consumo_main' , 
        'engdds_zmb5t_main', 'engdds_mb52_main', 'engdds_fbl3h_main', 'engdds_fbl5h_main', 'engdds_nf_01_main',

        # Bibliotecas a serem protegidas a cada execução de limpeza de variáveis
        'schedule', 'logging', 'datetime', 't', 'Fore', 'Style', 'init', 'time', 
        'json', 'os', 'sap', 'schedule_time', 'minio', 'Minio', 'MinioConnector',
        'MIN_INICIO', 'FIM', '_proximo_hh40',
        
        # Funções e variáveis auxiliares
        'extracao_diaria', 'extracoes_incrementais', 'HEADER', 'print_header',
        'clear_terminal_print_logo', 'limpar_variaveis', 'SAPLogin', 'trigger',
        'executar_extracao_inicial'
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
# ║ TASK LIST :: Lista de tarefas de extração - DIARIA                               ║
# ║ -----------------------------------------                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def task01():
    try:
        engdds_sku_main() # Revisado 04/12/2025 - 15/12/2025 Ajuste de Layout
        logging.info(f"ENGDDS_SKU_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_SKU_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()
    
def task02():
    try:
        engdds_werkish_main() # Revisado 04/12/2025 - 15/12/2025 Ajuste de Layout
        logging.info(f"ENGDDS_WERKISH_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_WERKISH_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task03():
    try:
        engdds_custos_main() # Revisado 04/12/2025
        logging.info(f"ENGDDS_CUSTOS_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_CUSTOS_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task04():
    try:
        engdds_faturamento_main() # Revisado 03/12/2025
        logging.info(f"ENGDDS_FATURAMENTO_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_FATURAMENTO_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task05():
    try:
        engdds_bom_main() # Revisado 04/12/2025
        logging.info(f"ENGDDS_BOM_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_BOM_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task06():
    try:
        engdds_compras_main() # Revisado 04/12/2025 
        logging.info(f"ENGDDS_COMPRAS_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_COMPRAS_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task07():
    try:
        engdds_estoque_main() # Revisado 04/12/2025 - Alterar Layout
        logging.info(f"ENGDDS_ESTOQUE_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_ESTOQUE_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task08():
    try:
        engdds_cockpit_main() # Revisado 04/12/2025
        logging.info(f"ENGDDS_COCKPIT_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_COCKPIT_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

# def task09(): # Verificar funcionalidade
#     from saplogin import SAPLogin
#     try:
#         trigger = SAPLogin()
#         engdds_text_info_main()
#         logging.info(f"ENGDDS_TEXT_INFO_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
#         trigger.trigger_airflow_dag(dag_name='minio_hourly_purchase_recap_sap4hana')
#     except Exception as erro:
#         logging.error(f"ENGDDS_TEXT_INFO_MAIN não executado: {erro}")
#     finally:
#         limpar_variaveis()

def task10():
    try:
        engdds_mb51_quebra_main() # Novo - 12/12/2025
        logging.info(f"ENGDDS_MB51_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_MB51_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task11():
    try:
        engdds_fbl1h_main() # Novo - 12/12/2025
        logging.info(f"ENGDDS_FBL1H_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_FBL1H_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task12():
    try:
        engdds_cooispi_seg_main() # Novo - 12/12/2025
        logging.info(f"ENGDDS_COOISPI_SEG_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_COOISPI_SEG_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task13():
    try:
        engdds_cooispi_varredura_main() # Novo - 12/12/2025
        logging.info(f"ENGDDS_COOISPI_VARREDURA_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_COOISPI_VARREDURA_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task14():
    try:
        engdds_cooispi_varredura_mp_main() # Novo - 12/12/2025
        logging.info(f"ENGDDS_COOISPI_VARREDURA_MP_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_COOISPI_VARREDURA_MP_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task15():
    try:
        engdds_zfi_nf_pivb_main() # Novo - 15/12/2025
        logging.info(f"ENGDDS_ZFI_NF_PIVB_MAIN executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_ZFI_NF_PIVB_MAIN não executado: {erro}")
    finally:
        limpar_variaveis()

def task16():
    try:
        engdds_vl06i_main() # Novo - 15/12/2025
        logging.info(f"ENGDDS_VL06I executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_VL06I não executado: {erro}")
    finally:
        limpar_variaveis()

def task17():
    try:
        engdds_cogi_main() # Novo - 15/12/2025
        logging.info(f"ENGDDS_COGI executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_COGI não executado: {erro}")
    finally:
        limpar_variaveis()

def task18():
    try:
        engdds_zfi_gl_pivb_main() # 14/01/2026
        logging.info(f"ENGDDS_ZFI_GL_PIVB executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_ZFI_GL_PIVB não executado: {erro}")
    finally:
        limpar_variaveis()

def task19():
    try:
        engdds_mb51_consumo_main() # 26/02/2026
        logging.info(f"ENGDDS_MB51_CONSUMO executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_MB51_CONSUMO não executado: {erro}")
    finally:
        limpar_variaveis()

def task20():
    try:
        engdds_fbl3h_main() # 26/02/2026
        logging.info(f"ENGDDS_FBL3H executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_FBL3H não executado: {erro}")
    finally:
        limpar_variaveis()

def task21():
    try:
        engdds_fbl5h_main() # 26/02/2026
        logging.info(f"ENGDDS_FBL5H executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_FBL5H não executado: {erro}")
    finally:
        limpar_variaveis()

def task22():
    try:
        engdds_nf_01_main() # 26/02/2026
        logging.info(f"ENGDDS_NF_01 executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"ENGDDS_NF_01 não executado: {erro}")
    finally:
        limpar_variaveis()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ HELPERS :: Funções HELPERS para as tasks INCREMENTAIS                            ║
# ║ -----------------------------------------------------                            ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝


def rodar_com_saida_verbose(funcao, nome_task):
    """
    Executa uma função redirecionando prints internos para um log verboso.

    Objetivo:
        - Manter o CMD mais limpo.
        - Manter o menestrel_song.log como log resumido/operacional.
        - Preservar os prints detalhados em menestrel_verbose.log para diagnóstico.
    """
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

def executar_hourly_task(nome_task, funcao_task, usar_log_verbose=True):
    """
    Executa uma task incremental e retorna status booleano.

    Retorno:
        True  = task executada com sucesso.
        False = task falhou.

    Esse retorno é usado pelo executar_incrementais() para decidir se a DAG
    minio_incremental_hourly deve ser disparada.
    """
    try:
        if usar_log_verbose:
            rodar_com_saida_verbose(funcao_task, nome_task)
        else:
            funcao_task()

        logging.info(
            f"{nome_task} executado em "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )

        return True

    except Exception as erro:
        logging.error(f"{nome_task} não executado: {erro}")
        return False


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK LIST :: Lista de tarefas de extração INCREMENTAL                            ║
# ║ -----------------------------------------------------                            ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def hourly_task01():  # Faturamento Hourly
    return executar_hourly_task(
        nome_task="ENGDDS_FATURAMENTO_HOURLY_MAIN",
        funcao_task=engdds_faturamento_hourly_main,
        usar_log_verbose=True,
    )


def hourly_task03():  # ZMB5T
    return executar_hourly_task(
        nome_task="ENGDDS_ZMB5T_MAIN",
        funcao_task=engdds_zmb5t_main,
        usar_log_verbose=True,
    )


def hourly_task04():  # COGI
    return executar_hourly_task(
        nome_task="ENGDDS_COGI_MAIN",
        funcao_task=engdds_cogi_main,
        usar_log_verbose=True,
    )


def hourly_task05():  # MB52
    return executar_hourly_task(
        nome_task="ENGDDS_MB52_MAIN",
        funcao_task=engdds_mb52_main,
        usar_log_verbose=True,
    )

# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK LIST :: Position Files                                                      ║
# ║ ---------------------------                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def pre_task():  # Revisado 26/03/2026
    try:
        # 0 = segunda, 2 = quarta
        if datetime.now().weekday() not in (0, 2):
            logging.info("POSITION_FILES ignorado: hoje não é segunda nem quarta.")
            return

        limpar_pasta(r"C:\Temp\t1")
        position_files_main()
        logging.info(f"POSITION_FILES executado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    except Exception as erro:
        logging.error(f"POSITION_FILES não executado: {erro}")
    finally:
        limpar_variaveis()

# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK GROUPS :: Lista de grupos de tarefas em ordem de execução                   ║
# ║ --------------------------------------------------------------                   ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

#######################################
# BLOCO DIARIAS
#######################################


@_excel_guarded(
    owner="menestrel.diaria",
    job_key="extracao_diaria",
    label="EXTRAÇÃO DIÁRIA",
)
def extracao_diaria():
    """
    Executa a batelada inicial de extrações que deve ocorrer obrigatoriamente
    no começo do dia, fazendo um update dos dados até D-1. Separado logicamente
    dos dados que precisarão ser atualizados incrementalmente ao longo do dia.
    
    sku (t1) >> units (t2) >> custos (t3) >> faturamento (t4) >> bom (t5) >> compras (t6) >> estoque (t7)
    """
    from saplogin import SAPLogin
    logging.info("═════════════════════════════════════════════════════════════════════════")
    logging.info(f"Início do Processamento :: EXTRACAO DIARIA")
    
    try:
        pre_task() # arquivos do position
        task01() # sku
        task02() # units
        task03() # custos
        task04() # faturamento
        task05() # bom
        task06() # compras
        task07() # estoque
        task08() # cockpit
        # task09() # text_info
        task10() # mb51
        task11() # fbl1h
        task12() # cooispi_seg
        task13() # cooispi_varredura
        task14() # cooispi_varredura_mp
        task15() # zfi_nf_pivb
        task16() # vl06i
        task17() # cogi
        task18() # zfi_gl_pivb
        task19() # mb51_consumo
        task20() # fbl3h
        task21() # fbl5h
        task22() # f.01

        
        # Trigger do Airflow
        trigger = SAPLogin()
        trigger.trigger_airflow_dag(dag_name='daily_chained_dags')
        
        logging.info(f"Final do Processamento :: EXTRACAO DIARIA")
    except Exception as erro:
        logging.error(f"Erro durante EXTRACAO DIARIA: {erro}")
    
    logging.info("═════════════════════════════════════════════════════════════════════════")

def executar_extracao_inicial():
    """
    Executa a extração diária imediatamente ao iniciar a aplicação.
    Esta função é chamada uma vez no início do programa.
    """
    print(f"\n{Fore.YELLOW}[INICIANDO EXTRACAÇÃO INICIAL]{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Executando extração diária na inicialização do sistema...{Style.RESET_ALL}")
    
    # Registrar no log
    logging.info("═════════════════════════════════════════════════════════════════════════")
    logging.info("EXECUÇÃO INICIAL :: Extração iniciada ao abrir a aplicação")
    logging.info("═════════════════════════════════════════════════════════════════════════")
    
    # Executar a extração diária
    try:
        extracao_diaria()
        print(f"{Fore.GREEN}[EXTRACAÇÃO INICIAL CONCLUÍDA]{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Extração inicial concluída com sucesso!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Aguardando próximos agendamentos...{Style.RESET_ALL}")
    except Exception as erro:
        print(f"{Fore.RED}[ERRO NA EXTRACAÇÃO INICIAL]{Style.RESET_ALL}")
        print(f"{Fore.RED}Erro durante extração inicial: {erro}{Style.RESET_ALL}")
        logging.error(f"Erro durante extração inicial: {erro}")


#######################################
# BLOCO INCREMENTAIS
#######################################

MIN_INICIO = t(6, 40)
FIM = t(20, 0)

def _proximo_hh40(now: datetime) -> str:
    if now.weekday() == 6:
        return "06:40" 

    if now.time() < MIN_INICIO:
        return "06:40"

    if now.time() >= FIM:
        return "06:40"

    if now.minute < 40:
        hhmm = f"{now.hour:02d}:40"
    else:

        next_hour = now.hour + 1
        if next_hour >= 20:
            return "07:00"
        hhmm = f"{next_hour:02d}:40"

    return hhmm

def kickoff_incrementais():
    schedule.clear('incremental_start')
    extracoes_incrementais()

def armar_incrementais():
    schedule.clear('incremental_start')
    now = datetime.now()
    hhmm = _proximo_hh40(now)

    schedule.every().day.at(hhmm).do(kickoff_incrementais).tag('incremental_start')
    logging.info(f"Kickoff incrementais armado para {hhmm}.")

def extracoes_incrementais():
    """
    Executa imediatamente e agenda até as 20:00
    """

    now = datetime.now()

    # sempre limpa qualquer agenda incremental pendurada
    schedule.clear('incremental')

    # 0=segunda ... 6=domingo
    if now.weekday() == 6:
        logging.info("Domingo — incrementais desativadas.")
        return

    if now.time() < t(20, 0):

        # Executa imediatamente
        executar_incrementais()

        # Agenda próxima execução
        schedule.every(60).minutes.until(t(20, 0))\
            .do(executar_incrementais)\
            .tag('incremental')

        logging.info("Incrementais agendadas até as 20:00.")

    else:
        logging.info("Após 20:00 — não será agendado.")

@_excel_guarded(
    owner="menestrel.incremental",
    job_key="extracoes_incrementais",
    label="EXTRAÇÕES INCREMENTAIS",
)
def executar_incrementais():
    from saplogin import SAPLogin

    logging.info("═════════════════════════════════════════════════════════════════════════")
    logging.info("═════════════════════════════════════════════════════════════════════════")
    logging.info("Início do Processamento :: EXTRAÇÕES INCREMENTAIS")

    resultados = {}

    try:
        resultados["Faturamento Hourly"] = hourly_task01()
        resultados["ZMB5T"] = hourly_task03()
        resultados["COGI"] = hourly_task04()
        resultados["MB52"] = hourly_task05()

        sucessos = [nome for nome, ok in resultados.items() if ok]
        falhas = [nome for nome, ok in resultados.items() if not ok]

        if sucessos:
            logging.info(
                "Extrações incrementais com sucesso: "
                + ", ".join(sucessos)
            )

            if falhas:
                logging.error(
                    "Extrações incrementais com falha: "
                    + ", ".join(falhas)
                )

            trigger = SAPLogin()
            trigger.trigger_airflow_dag(dag_name="minio_incremental_hourly")

            logging.info(
                "DAG minio_incremental_hourly iniciada, pois pelo menos "
                "uma extração incremental foi executada com sucesso."
            )

        else:
            logging.error(
                "Nenhuma extração incremental foi executada com sucesso. "
                "DAG minio_incremental_hourly não será disparada."
            )

    except Exception as erro:
        logging.error(f"Erro geral na execução incremental: {erro}")

    finally:
        logging.info("Final do Processamento :: EXTRAÇÕES INCREMENTAIS")
        logging.info("═════════════════════════════════════════════════════════════════════════")


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ CONFIGURAÇÃO E EXECUÇÃO PRINCIPAL                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

# Configuração do logging
LOG_PATH = os.path.join(os.path.dirname(__file__), "menestrel_song.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True,  # importante
)
logging.info("LOG CONFIGURADO — teste de console e arquivo")

# Limpar terminal e exibir cabeçalho
schedule.every().day.at("00:05").do(clear_terminal_print_logo)
print_logo_header()

extracoes_incrementais()

# Configurar agendamentos
schedule.every().day.at("00:05").do(clear_terminal_print_logo)
schedule.every().day.at("00:10").do(extracao_diaria)

schedule.every().day.at("00:15").do(armar_incrementais)
armar_incrementais()

# Verifica a cada minuto se existe alguma extração que ficou
# pendente aguardando a liberação do recurso compartilhado do Excel.
schedule.every(1).minutes.do(
    _retry_pending_excel_jobs
).tag("excel_lock_retry")

# Loop principal
print(f"\n{Fore.GREEN}[SISTEMA EM OPERAÇÃO]{Style.RESET_ALL}")
print(f"{Fore.CYAN}Aguardando execução de jobs agendados...{Style.RESET_ALL}")
print(f"{Fore.CYAN}Pressione Ctrl+C para encerrar.{Style.RESET_ALL}")

while True:
    try:
        schedule.run_pending()
        time.sleep(10)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[SISTEMA INTERROMPIDO PELO USUÁRIO]{Style.RESET_ALL}")
        logging.info("Sistema interrompido pelo usuário via Ctrl+C")
        break
    except Exception as erro:
        logging.error(f"Erro no loop principal: {erro}")
        time.sleep(30)  # Esperar mais tempo em caso de erro