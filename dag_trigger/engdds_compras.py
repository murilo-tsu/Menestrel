from saplogin import SAPLogin
from Minio import MinioConnector
import datetime
import json
import time
import os
import logging
sap = SAPLogin()

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)


def registrar_erro(erros, etapa, erro):
    """
    Registra erro definitivo de uma etapa.

    Essa função só deve ser chamada depois que todas as tentativas da etapa
    falharem.
    """
    mensagem = f"{etapa} :: {str(erro)}"

    logging.error(f"Erro definitivo na etapa {etapa}: {str(erro)}", exc_info=erro)
    erros.append(mensagem)

    try:
        sap.limpar_processos()
        sap.cleanup()
    except Exception as erro_cleanup:
        logging.debug(f"Falha ao limpar processos após erro definitivo em {etapa}: {erro_cleanup}")


def executar_com_retry(erros, etapa, funcao, tentativas=3, intervalo=60):
    """
    Executa uma etapa com tentativas.

    Regra:
        - Se a etapa funcionar em qualquer tentativa, segue o fluxo normalmente.
        - Se falhar, encerra o SAP, aguarda e tenta novamente.
        - Se todas as tentativas falharem, registra o erro na lista 'erros'.
        - O script não para imediatamente, permitindo executar os próximos blocos.
    """
    ultimo_erro = None

    for tentativa in range(1, tentativas + 1):
        try:
            logging.info(f"{etapa} :: tentativa {tentativa}/{tentativas}")

            funcao()

            logging.info(f"{etapa} :: concluído com sucesso")
            return True

        except Exception as erro:
            ultimo_erro = erro

            logging.error(
                f"Erro na etapa {etapa} durante tentativa "
                f"{tentativa}/{tentativas}: {str(erro)}",
                exc_info=erro
            )

            try:
                sap.limpar_processos()
                sap.cleanup()
            except Exception as erro_cleanup:
                logging.debug(f"Falha ao limpar processos após tentativa de {etapa}: {erro_cleanup}")

            if tentativa < tentativas:
                logging.info(f"{etapa} será tentado novamente em {intervalo} segundos...")
                time.sleep(intervalo)

    registrar_erro(erros, etapa, ultimo_erro)
    return False


def engdds_compras_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_COMPRAS.PY ----")

    minio = MinioConnector()
    erros = []

    with open('files.json', 'rb') as file:
        meta_arquivos = json.load(file)

    # Definindo datas dinâmicas
    end_year_compras = f(datetime.date.today().year)
    end_month_compras = f(datetime.date.today().month)
    end_day_compras = f(datetime.date.today().day)

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO :: ME2W - Extração de Pedidos por Planta Fornecedora
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_me2w():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        logging.info("Iniciando extração: ME2W")
        session.findById("wnd[0]/tbar[0]/okcd").text = "ME2W"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/btn%_EW_EKORG_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "E602"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "E902"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "EBR2"
        session.findById("wnd[1]").sendVKey (0)
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/btn%_S_BSART_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "ZUB"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "UB"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "YIMP"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "YNAC"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "NB"
        session.findById("wnd[1]").sendVKey (0)
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/ctxtLISTU").text = "ALV"
        session.findById("wnd[0]/usr/ctxtLISTU").setFocus()
        session.findById("wnd[0]/usr/ctxtLISTU").caretPosition = 3
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_compras.py']['path'][0]
        nome_arquivo = f"{end_year_compras}-{end_month_compras}-{end_day_compras} {meta_arquivos['engdds_compras.py']['files'][0]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_compras.py']['path'][0], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_compras.py']['path'][0]}/{nome_arquivo}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO :: ME5A - Relatório de Requisições de Compra
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_me5a():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        logging.info("Iniciando extração: ME5A")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ME5A"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/btn%_S_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "P60*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "E60*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "E90*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "P90*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "E89*"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/ctxtS_BSART-LOW").setFocus()
        session.findById("wnd[0]/usr/btn%_S_BSART_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]").sendVKey (2)
        session.findById("wnd[2]").close()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "YES2"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "YES4"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/chkP_ZUGBA").selected = True
        session.findById("wnd[0]/usr/chkP_MEMORY").selected = True
        session.findById("wnd[0]/usr/chkP_ERLBA").selected = True
        session.findById("wnd[0]/usr/chkP_BSTBA").selected = True
        session.findById("wnd[0]/usr/chkP_SELGS").selected = True
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_compras.py']['path'][0]
        nome_arquivo = f"{end_year_compras}-{end_month_compras}-{end_day_compras} {meta_arquivos['engdds_compras.py']['files'][1]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_compras.py']['path'][0], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_compras.py']['path'][0]}/{nome_arquivo}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO :: EBAN
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_eban():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        logging.info("Iniciando extração: EBAN")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "EBAN"
        session.findById("wnd[0]/usr/ctxtGD-TAB").caretPosition = 4
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 1
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 2
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "YES2"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "YES4"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "NB"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[1]").sendVKey (4)

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except Exception as erro:
                logging.debug(f"Pop-up opcional nao tratado: {erro}")

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_compras.py']['path'][1]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = meta_arquivos['engdds_compras.py']['files'][2]
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_compras.py']['path'][1], meta_arquivos['engdds_compras.py']['files'][2])
        minio.upload_or_queue(arquivo, 'tmp', meta_arquivos['engdds_compras.py']['files'][2])
        sap.cleanup()
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_compras.py']['path'][1]}/{meta_arquivos['engdds_compras.py']['files'][2]}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO :: EKKO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_ekko():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        logging.info("Iniciando extração: EKKO")
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "EKKO"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 1
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 2
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").press()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "NB"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "YIMP"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "YNAC"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "ZUB"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]").text = "ZUVR"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,5]").text = "ZMK"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except Exception as erro:
                logging.debug(f"Pop-up opcional nao tratado: {erro}")

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_compras.py']['path'][1]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = meta_arquivos['engdds_compras.py']['files'][3]
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_compras.py']['path'][1], meta_arquivos['engdds_compras.py']['files'][3])
        minio.upload_or_queue(arquivo, 'tmp', meta_arquivos['engdds_compras.py']['files'][3])
        sap.cleanup()
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_compras.py']['path'][1]}/{meta_arquivos['engdds_compras.py']['files'][3]}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO :: EKPO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_ekpo():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        logging.info("Iniciando extração: EKPO")
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "EKPO"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 1
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 2
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 3
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 4
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 5
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 6
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").press()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except Exception as erro:
                logging.debug(f"Pop-up opcional nao tratado: {erro}")

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_compras.py']['path'][1]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = meta_arquivos['engdds_compras.py']['files'][4]
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_compras.py']['path'][1], meta_arquivos['engdds_compras.py']['files'][4])
        minio.upload_or_queue(arquivo, 'tmp', meta_arquivos['engdds_compras.py']['files'][4])
        sap.cleanup()
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_compras.py']['path'][1]}/{meta_arquivos['engdds_compras.py']['files'][4]}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO :: ZMM_PURDOCS_REPORT
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_zmm_purdocs_report():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        logging.info("Iniciando extração: ZMM_PURDOCS_REPORT")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_PURDOCS_REPORT"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/btn%_SO_EKORG_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "E602"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "E902"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "EBR2"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").setFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/btn%_SO_BSART_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "YIMP"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "YNAC"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "NB"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "MK"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "ZMK"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").setFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").caretPosition = 2
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/btn%_SO_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "P6*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "P9*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "E89*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "E6*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "E9*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").setFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").caretPosition = 3
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/DATAINSIGHT"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlGRID/shellcont/shell/shellcont[0]/shell/shellcont[1]/shell").pressButton ("&XXL")
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_compras.py']['path'][0]
            nome_arquivo = f"{end_year_compras}-{end_month_compras}-{end_day_compras} {meta_arquivos['engdds_compras.py']['files'][5]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_compras.py']['path'][0], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_compras.py']['path'][0]}/{nome_arquivo}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO :: ZMM_PURDOCS_REPORT (HEADER TEXT)
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_zmm_purdocs_headertext():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        logging.info("Iniciando extração: ZMM_PURDOCS_REPORT (HEADER TEXT)")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_PURDOCS_REPORT"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/btn%_SO_EKORG_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "E602"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "E902"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "EBR2"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").setFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/btn%_SO_BSART_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "YIMP"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "YNAC"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "NB"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "MK"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "ZMK"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").setFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").caretPosition = 2
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/btn%_SO_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "P6*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "P9*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "E89*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "E6*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "E9*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").setFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").caretPosition = 3
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/chkP_LONGT").selected = True
        session.findById("wnd[0]/usr/chkP_LONGT2").selected = True
        session.findById("wnd[0]/usr/chkP_LONGT3").selected = True
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/HDTXT"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlGRID/shellcont/shell/shellcont[0]/shell/shellcont[1]/shell").pressButton ("&XXL")
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_compras.py']['path'][0]
            nome_arquivo = f"{end_year_compras}-{end_month_compras}-{end_day_compras} {meta_arquivos['engdds_compras.py']['files'][6]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_compras.py']['path'][0], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_compras.py']['path'][0]}/{nome_arquivo}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO :: ZMM_PURDOCS_REPORT (AUXINFO)
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_zmm_purdocs_auxinfo():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        logging.info("Iniciando extração: ZMM_PURDOCS_REPORT (AUXINFO)")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_PURDOCS_REPORT"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/btn%_SO_EKORG_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "E602"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "E902"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "EBR2"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").setFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/btn%_SO_BSART_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "YIMP"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "YNAC"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "NB"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "MK"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "ZMK"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").setFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").caretPosition = 2
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/btn%_SO_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "P6*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "P9*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "E89*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "E6*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "E9*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").setFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").caretPosition = 3
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/chkP_LONGT").selected = True
        session.findById("wnd[0]/usr/chkP_LONGT2").selected = True
        session.findById("wnd[0]/usr/chkP_LONGT3").selected = True
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/AUXINFO"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlGRID/shellcont/shell/shellcont[0]/shell/shellcont[1]/shell").pressButton ("&XXL")
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_compras.py']['path'][0]
            nome_arquivo = f"{end_year_compras}-{end_month_compras}-{end_day_compras} {meta_arquivos['engdds_compras.py']['files'][7]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_compras.py']['path'][0], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_compras.py']['path'][0]}/{nome_arquivo}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO :: DRAD
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_drad():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        logging.info("Iniciando extração: DRAD")
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "DRAD"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except Exception as erro:
                logging.debug(f"Pop-up opcional nao tratado: {erro}")

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_compras.py']['path'][1]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = meta_arquivos['engdds_compras.py']['files'][8]
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_compras.py']['path'][1], meta_arquivos['engdds_compras.py']['files'][8])
        minio.upload_or_queue(arquivo, 'tmp', meta_arquivos['engdds_compras.py']['files'][8])
        sap.cleanup()
        logging.info(f"ATUALIZADO: {meta_arquivos['engdds_compras.py']['path'][1]}/{meta_arquivos['engdds_compras.py']['files'][8]}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # EXECUÇÃO DOS BLOCOS COM RETRY
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    executar_com_retry(erros=erros, etapa="ME2W", funcao=extrair_me2w, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ME5A", funcao=extrair_me5a, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="EBAN", funcao=extrair_eban, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="EKKO", funcao=extrair_ekko, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="EKPO", funcao=extrair_ekpo, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZMM_PURDOCS_REPORT", funcao=extrair_zmm_purdocs_report, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZMM_PURDOCS_HEADERTEXT", funcao=extrair_zmm_purdocs_headertext, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZMM_PURDOCS_AUXINFO", funcao=extrair_zmm_purdocs_auxinfo, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="DRAD", funcao=extrair_drad, tentativas=3, intervalo=60)

    time.sleep(10)
    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de COMPRAS:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_COMPRAS.PY finalizado com sucesso ----")


if __name__ == "__main__":
    engdds_compras_main()
