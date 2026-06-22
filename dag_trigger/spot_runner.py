
import logging
from datetime import datetime, timedelta

import time
import os
from Minio import MinioConnector
from position_files import position_files_main
from engdds_estoque import engdds_estoque_main
from engdds_compras import engdds_compras_main
from engdds_custos import engdds_custos_main
from engdds_faturamento import engdds_faturamento_main
from engdds_faturamento_hourly import engdds_faturamento_hourly_main
from engdds_bom import engdds_bom_main
from engdds_sku import engdds_sku_main
from engdds_werkish import engdds_werkish_main
from engdds_cockpit import engdds_cockpit_main
from engdds_text_info import engdds_text_info_main


def limpar_variaveis():
    """Limpar variáveis externas ao menestrel.py"""
    protected_vars = {

        # Tasks declaradas
        'pre_task','task01','task02','task03','task04','task05','task06','task07','task08','task09',
        'hourly_task01', 'position_files',

        # Funções de RPA com objetivos específicos
        'engdds_estoque_main', 'engdds_compras_main', 'engdds_faturamento_main',
        'engdds_faturamento_daily_main', 'engdds_sku_main', 'engdds_bom_main',
        'engdds_custos_main', 'engdds_werkish_main', 'engdds_text_info_main',
        'engdds_faturamento_hourly_main','position_files_main',

        # Bibliotecas a serem protegidas a cada execução de limpeza de variáveis
        'schedule', 'logging', 'datetime', 'Fore', 'Style', 'init', 'time', 
        'json','os', 't', 'sap', 'schedule_time', 'minio', 'Minio', 'MinioConnector',
         
        # Funções e variáveis auxiliares
        'extracao_diaria', 'extracoes_incrementais', 'HEADER', 'print_header',
        'clear_terminal_print_logo', 'limpar_variaveis', 'SAPLogin', 'trigger', 'timer'

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

def task08():
    try:
        engdds_cockpit_main()
        logging.info("ENGDDS_COCKPIT_MAIN executado")
    except Exception as erro:
        logging.info("ENGDDS_COCKPIT_MAIN não executado")
    finally:
        limpar_variaveis()

def task09():
    from saplogin import SAPLogin
    trigger = SAPLogin()
    trigger.login_to_s4hana()
    try:
        engdds_text_info_main()
        logging.info("ENGDDS_TEXT_INFO_MAIN executado")
        trigger.trigger_airflow_dag(dag_name='minio_hourly_purchase_recap_sap4hana')
    except:
        logging.info("ENGDDS_TEXT_INFO_MAIN não executado")
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
        logging.error(f"POSITION_FILES não executado")
    
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
    from saplogin import SAPLogin
    trigger = SAPLogin()
    logging.info("═════════════════════════════════════════════════════════════════════════")
    logging.info(f"Início do Processamento :: EXTRACAO DIARIA")
    print('TASK 4')
    task04() # faturamento
    #print('PRE_TASK')
    #pre_task() # arquivos do position
    print('TASK 1')
    task01() # sku
    print('TASK 2')
    task02() # units
    print('TASK 3')
    task03() # custos
    print('TASK 5')
    task05() # bom
    print('TASK6')
    task06() # compras
    print('TASK 7')
    task07() # estoque
    print('TASK 8')
    task08() # cockpit
    trigger.trigger_airflow_dag(dag_name='daily_chained_dags')
    logging.info(f"Final do Processamento :: EXTRACAO DIARIA")
    logging.info("═════════════════════════════════════════════════════════════════════════")

def timer():
    os.system('cls')
    target = datetime.now() + timedelta(days=1)
    target = datetime(target.year,target.month,target.day, 2,0,0)
    print('\n\nNÃO FECHE ESSA JANELA.\n\nEle é uma segunda camada de garantia que as extrações do SAP vão rodar.')
    print(f'\nAguardando até dia {str(target.day).zfill(2)}/{str(target.month).zfill(2)}/{target.year} às {str(target.hour).zfill(2)}:{str(target.minute).zfill(2)}', end='\n')
    while datetime.now() < target:
        time.sleep(10)    

def need_refresh():
    minio = MinioConnector()
    minio._checkConnection()
    mod = [file.last_modified for file in minio.client.list_objects('tmp', 'ZSD_PIVB_E600.XLSX')][0]

    return datetime(mod.year,mod.month,mod.day, mod.hour,mod.minute, mod.second) < datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        
while True:
    timer()
    if need_refresh(): extracao_diaria()
