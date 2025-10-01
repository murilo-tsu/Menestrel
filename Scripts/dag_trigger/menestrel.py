import schedule
import logging
from datetime import datetime
from datetime import time as t
from colorama import init, Fore, Style
import time
import os
from position_files import position_files_main
from engdds_estoque import engdds_estoque_main
from engdds_compras import engdds_compras_main
from engdds_custos import engdds_custos_main
from engdds_faturamento import engdds_faturamento_main
from engdds_faturamento_hourly import engdds_faturamento_hourly_main
from engdds_bom import engdds_bom_main
from engdds_sku import engdds_sku_main
from engdds_werkish import engdds_werkish_main

# Inicializando o COLORAMA
init()

# HEADER = f"""{Fore.CYAN}
# ┳┳┓┏┓┳┓┏┓┏┓┏┳┓┳┓┏┓┓   
# ┃┃┃┣ ┃┃┣ ┗┓ ┃ ┣┫┣ ┃   
# ┛ ┗┗┛┛┗┗┛┗┛ ┻ ┛┗┗┛┗┛  
# {Style.RESET_ALL}"""

HEADER = f"""{Fore.CYAN}
███╗   ███╗███████╗███╗   ██╗███████╗███████╗████████╗██████╗ ███████╗██╗         
████╗ ████║██╔════╝████╗  ██║██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║         
██╔████╔██║█████╗  ██╔██╗ ██║█████╗  ███████╗   ██║   ██████╔╝█████╗  ██║         
██║╚██╔╝██║██╔══╝  ██║╚██╗██║██╔══╝  ╚════██║   ██║   ██╔══██╗██╔══╝  ██║         
██║ ╚═╝ ██║███████╗██║ ╚████║███████╗███████║   ██║   ██║  ██║███████╗███████╗    
╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝    
{Style.RESET_ALL}"""                                                                                 

def print_header():
    """Print the ASCII art header and version info"""
    print(HEADER)
    print(f"{Fore.LIGHTWHITE_EX}╔══════════════════════════════════════════════════════════════════════════════════╗")
    print(f"║ {'Orquestrador de scripts de extração do SAP4HANA :: v2.0.0':^80} ║")
    print(f"║ {f'Inicializado: {datetime.now()}':^80} ║")
    print(f"╠══════════════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"║                           {Fore.LIGHTGREEN_EX}Aguardando scripts agendados{Style.RESET_ALL}                           ║")
    print(f"╚══════════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

def clear_terminal_print_logo():
    """Limpar o terminal para manter a LOGO do menestrel"""
    os.system('cls')
    print_header()

def limpar_variaveis():
    """Limpar variáveis externas ao menestrel.py"""
    protected_vars = {
        'schedule', 'logging', 'datetime', 'Fore', 'Style', 'init', 'time', 'os',
        'engdds_estoque_main', 'engdds_compras_main', 'engdds_custos_main',
        'engdds_faturamento_main', 'engdds_faturamento_daily_main', 'engdds_bom_main',
        'engdds_sku_main', 'engdds_werkish_main', 'HEADER', 'print_header',
        'clear_terminal_print_logo', 'task01', 'task02', 'task03', 'task04',
        'task05', 'task06', 'task07', 'extracao_diaria', 'extracoes_incrementals',
        'limpar_variaveis',

        # Vars para serem protegidas devido a execuções posteriores ao longo do dia
        't', 'engdds_faturamento_hourly_main', 'position_files'

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
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def task01():
    try:
        engdds_sku_main()
        logging.info(f"ENGGDS_SKU_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_SKU_MAIN não executado")
    finally:
        limpar_variaveis()
    
def task02():
    try:
        engdds_werkish_main()
        logging.info(f"ENGGDS_WERKISH_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_WERKISH_MAIN não executado")
    finally:
        limpar_variaveis()

def task03():
    try:
        engdds_custos_main()
        logging.info(f"ENGGDS_CUSTOS_MAIN  executado")
    except Exception as erro:
        logging.error(f"ENGDDS_CUSTOS_MAIN  não executado")
    finally:
        limpar_variaveis()


def task04():
    try:
        engdds_faturamento_main()
        logging.info(f"ENGGDS_FATURAMENTO_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_FATURAMENTO_MAIN não executado")
    finally:
        limpar_variaveis()

def task05():
    try:
        engdds_bom_main()
        logging.info(f"ENGGDS_BOM_MAIN  executado")
    except Exception as erro:
        logging.error(f"ENGDDS_BOM_MAIN  não executado")
    finally:
        limpar_variaveis()

def task06():
    try:
        engdds_compras_main()
        logging.info(f"ENGGDS_COMPRAS_MAIN  executado")
    except Exception as erro:
        logging.error(f"ENGDDS_COMPRAS_MAIN  não executado")
    finally:
        limpar_variaveis()

def task07():
    try:
        engdds_estoque_main()
        logging.info(f"ENGGDS_ESTOQUE_MAIN executado")
    except Exception as erro:
        logging.error(f"ENGDDS_ESTOQUE_MAIN não executado")
    finally:
        limpar_variaveis()

# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK LIST :: Lista de tarefas de extração incremental                            ║
# ║ -----------------------------------------------------                            ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def hourly_task01():
    try:
        engdds_faturamento_hourly_main()
        logging.info("ENGDDS_FATURAMENTO_HOURLY_MAIN executado")
    except Exception as erro:
        logging.error("ENGDDS_FATURAMENTO_HOURLY_MAIN não executado")
    finally:
        limpar_variaveis()

# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK LIST :: Position Files                                                      ║
# ║ ---------------------------                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def pre_task():
    try:
        position_files_main()
        logging.info(f"POSITION_FILES executado")
    except Exception as erro:
        logging.error(f"POSITON_FILES não executado")
    finally:
        limpar_variaveis()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║ TASK GROUPS :: Lista de grupos de tarefas em ordem de execução                   ║
# ║ --------------------------------------------------------------                   ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

def extracao_diaria():
    """
    Executa a batelada inicial de extrações que deve ocorrer obrigatoriamente
    no começo do dia, fazendo um update dos dados até D-1. Separado logicamente
    dos dados que precisarão ser atualizados incrementalmente ao longo do dia.
    
    sku (t1) >> units (t2) >> custos (t3) >> faturamento (t4) >> bom (t5) >> compras (t6) >> estoque (t7)
    """
    logging.info("═════════════════════════════════════════════════════════════════════════")
    logging.info(f"Início do Processamento :: EXTRACAO DIARIA")
    pre_task() # arquivos do position
    task01() # sku
    task02() # units
    task03() # custos
    task04() # faturamento
    task05() # bom
    task06() # compras
    task07() # estoque
    logging.info(f"Final do Processamento :: EXTRACAO DIARIA")
    logging.info("═════════════════════════════════════════════════════════════════════════")

def extracoes_incrementais():
    """
    Executa extrações incrementais ao longo do dia para atualizar dados em um
    intervalo mais granular, viabilizando a visualização em tempo mais real.

    Faturamento (t1) 
    """
    logging.info("═════════════════════════════════════════════════════════════════════════")
    logging.info("Início do Processamento :: Hourly Update")
    schedule.clear('incremental')
    # Hourly Task 01 :: Atualiza faturamento
    try:
        schedule.every(60).minutes.until(t(21,30)).do(engdds_faturamento_hourly_main).tag('incremental')
        logging.info("Faturamento Atualizado!")
    except Exception as erro:
        logging.info(f"Faturamento não atualizado: {erro}")
    logging.info("Final do Processamento :: Hourly Update")
    logging.info("═════════════════════════════════════════════════════════════════════════")
    logging.info("Aguardando agendamento do próximos job...")

logging.basicConfig(filename='menestrel_song.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    encoding='utf-8')

print_header()
schedule.every().day.at("00:01").do(clear_terminal_print_logo)
schedule.every().day.at("00:05").do(extracao_diaria)
# schedule.every().day.at("08:30").do(extracoes_incrementais)

while True:
    
    schedule.run_pending()
    time.sleep(10)