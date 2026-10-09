import schedule
import logging
from datetime import datetime
from colorama import init, Fore, Style
import time
import os
import gc

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

# ==========================================================
# LIMPEZA SEGURA DE MEMÓRIA
# ==========================================================
def limpar_memoria():
    """Limpa apenas memória, sem apagar símbolos globais"""
    gc.collect()

# ==========================================================
# TASKS
# ==========================================================
def task01():
    try:
        engdds_sku_main()
        logging.info(f"ENGGDS_SKU_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGDDS_SKU_MAIN não executado")
    finally:
        limpar_memoria()

def task02():
    try:
        engdds_werkish_main()
        logging.info(f"ENGGDS_WERKISH_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGDDS_WERKISH_MAIN não executado")
    finally:
        limpar_memoria()

def task03():
    try:
        engdds_custos_main()
        logging.info(f"ENGGDS_CUSTOS_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGDDS_CUSTOS_MAIN não executado")
    finally:
        limpar_memoria()

def task04():
    try:
        engdds_faturamento_main()
        logging.info(f"ENGGDS_FATURAMENTO_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGDDS_FATURAMENTO_MAIN não executado")
    finally:
        limpar_memoria()

def task05():
    try:
        engdds_bom_main()
        logging.info(f"ENGGDS_BOM_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGGDS_BOM_MAIN não executado")
    finally:
        limpar_memoria()

def task06():
    try:
        engdds_compras_main()
        logging.info(f"ENGGDS_COMPRAS_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGGDS_COMPRAS_MAIN não executado")
    finally:
        limpar_memoria()

def task07():
    try:
        engdds_estoque_main()
        logging.info(f"ENGGDS_ESTOQUE_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGGDS_ESTOQUE_MAIN não executado")
    finally:
        limpar_memoria()

def task08():
    try:
        engdds_cockpit_main()
        logging.info(f"ENGGDS_COCKPIT_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGGDS_COCKPIT_MAIN não executado")
    finally:
        limpar_memoria()

def task10():
    try:
        engdds_mb51_quebra_main()
        logging.info(f"ENGGDS_MB51_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGGDS_MB51_MAIN não executado")
    finally:
        limpar_memoria()

def task11():
    try:
        engdds_fbl1h_main()
        logging.info(f"ENGGDS_FBL1H_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGGDS_FBL1H_MAIN não executado")
    finally:
        limpar_memoria()

def task12():
    try:
        engdds_cooispi_seg_main()
        logging.info(f"ENGGDS_COOISPI_SEG_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGGDS_COOISPI_SEG_MAIN não executado")
    finally:
        limpar_memoria()

def task13():
    try:
        engdds_cooispi_varredura_main()
        logging.info(f"ENGGDS_COOISPI_VARREDURA_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGGDS_COOISPI_VARREDURA_MAIN não executado")
    finally:
        limpar_memoria()

def task14():
    try:
        engdds_cooispi_varredura_mp_main()
        logging.info(f"ENGGDS_COOISPI_VARREDURA_MP_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception:
        logging.exception("ENGGDS_COOISPI_VARREDURA_MP_MAIN não executado")
    finally:
        limpar_memoria()

def task15():
    try:
        engdds_zfi_nf_pivb_main() #Novo - 15/12/2025
        logging.info(f"ENGGDS_ZFI_NF_PIVB_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception as erro:
        logging.info("ENGDDS_ZFI_NF_PIVB_MAIN não executado")
    finally:
        limpar_memoria()

def task16():
    try:
        engdds_vl06i_main() #Novo - 15/12/2025
        logging.info(f"ENGGDS_VL06I_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception as erro:
        logging.info("ENGDDS_VL06I não executado")
    finally:
        limpar_memoria()

def task17():
    try:
        engdds_cogi_main() #Novo - 15/12/2025
        logging.info(f"ENGGDS_COGI_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception as erro:
        logging.info("ENGDDS_COGI não executado")
    finally:
        limpar_memoria()

def task17():
    try:
        engdds_zfi_gl_pivb_main() #Novo - 15/12/2025
        logging.info(f"ENGGDS_ZFI_GL_PIVB_MAIN executado em {datetime.now():%d/%m/%Y %H:%M:%S}")
    except Exception as erro:
        logging.info("ENGDDS_ZFI_GL_PIVB não executado")
    finally:
        limpar_memoria()

# ==========================================================
# ORQUESTRADOR
# ==========================================================
def run_tasks_em_ordem():
    tasks = [
        # (1, task01), #SKU
        # (2, task02), #WERKISH
        # (3, task03), #CUSTOS
        (4, task04), #FATURAMENTO
        (5, task05), #BOM
        (6, task06), #COMPRAS
        (7, task07), #ESTOQUE
        (8, task08), #COCKPIT
        (10, task10), #MB51 QUEBRA
        (11, task11), #FBL1H
        (12, task12), #COOISPI SEG
        (13, task13), #COOISPI VARREDURA
        (14, task14), #COOISPI VARREDURA MP
        (15, task15), #ZFI NF PIVB
        (16, task16), #VL06I
        (17, task17), #COGI
        (18, task18), #ZFI_GL_PIVB
    ]

    for numero, task in tasks:
        logging.info(f"Iniciando TASK {numero:02d}")
        try:
            task()
        except Exception:
            logging.exception(f"Falha crítica na TASK {numero:02d}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S"
    )

    run_tasks_em_ordem()

    while True:
        schedule.run_pending()
        time.sleep(30)




