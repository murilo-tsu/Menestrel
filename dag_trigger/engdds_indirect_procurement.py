from saplogin import SAPLogin
from Minio import MinioConnector
from heartbeat_utils import escrever_heartbeat
import datetime
import json
import time
import os
import logging
sap = SAPLogin()


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


def engdds_indirect_procurement_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_INDIRECT_PROCUREMENT.PY ----")

    minio = MinioConnector()
    erros = []
    with open('files.json', 'rb') as file:
        meta_arquivos = json.load(file)

    # RELATÓRIO 1: ME5A ---------------------------------------------------------------------------------------------------------------------------------------------------------
    def extrair_me5a():
        escrever_heartbeat()
        session = sap.login_to_s4hana(lang="PT")

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/tbar[0]/okcd").text = "ME5A"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/EUROCHEMBI26"
        session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[33]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").currentCellRow = -1
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectColumn ("VARIANT")
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectedRows = ""
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").contextMenu()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectContextMenuItem ("&FILTER")
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = "/EUROCHEMRC"
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").caretPosition = 11
        session.findById("wnd[2]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_indirect_procurement.py']['path']
        nome_arquivo = f"{meta_arquivos['engdds_indirect_procurement.py']['files'][0]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()

        # Gravar no MinIO
        arquivo = minio.buffer_creator(meta_arquivos['engdds_indirect_procurement.py']['path'],nome_arquivo)
        minio.upload_or_queue(arquivo,'tmp',nome_arquivo)
        sap.cleanup()

    # RELATÓRIO 2: ME2L ---------------------------------------------------------------------------------------------------------------------------------------------
    def extrair_me2l():
        escrever_heartbeat()
        session = sap.login_to_s4hana(lang="PT")

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/tbar[0]/okcd").text = "ME2L"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/EUROCHEMBI26"
        session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
        session.findById("wnd[1]/usr/txtV-LOW").caretPosition = 13
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        # session.findById("wnd[0]/usr/ctxtS_EBELN-LOW").text = "4500815559"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # session.findById("wnd[0]/usr/ctxtS_EBELN-LOW").setFocus()
        # session.findById("wnd[0]/usr/ctxtS_EBELN-LOW").caretPosition = 10
        # session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[23]").press()

        # session.findById("wnd[0]/tbar[1]/btn[23]").press()
        session.findById("wnd[0]/tbar[1]/btn[33]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").currentCellRow = -1
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectColumn ("VARIANT")
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectedRows = ""
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").contextMenu()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectContextMenuItem ("&FILTER")
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = "/COMPRASBI"
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").caretPosition = 11
        session.findById("wnd[2]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_indirect_procurement.py']['path']
        nome_arquivo = f"{meta_arquivos['engdds_indirect_procurement.py']['files'][1]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()

        # Gravar no MinIO
        arquivo = minio.buffer_creator(meta_arquivos['engdds_indirect_procurement.py']['path'],nome_arquivo)
        minio.upload_or_queue(arquivo,'tmp',nome_arquivo)
        sap.cleanup()

    # RELATÓRIO 3: ME3L ---------------------------------------------------------------------------------------------------------------------------------
    def extrair_me3l():
        escrever_heartbeat()
        session = sap.login_to_s4hana(lang="PT")

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/tbar[0]/okcd").text = "ME3L"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtLISTU").text = "ALV"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[33]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").currentCellRow = -1
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectColumn ("VARIANT")
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectedRows = ""
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").contextMenu()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").selectContextMenuItem ("&FILTER")
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = "/CONTRATOSBI"
        session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").caretPosition = 11
        session.findById("wnd[2]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()

        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_indirect_procurement.py']['path']
        nome_arquivo = f"{meta_arquivos['engdds_indirect_procurement.py']['files'][2]}"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()

        # Gravar no MinIO
        arquivo = minio.buffer_creator(meta_arquivos['engdds_indirect_procurement.py']['path'],nome_arquivo)
        minio.upload_or_queue(arquivo,'tmp',nome_arquivo)
        sap.cleanup()

    executar_com_retry(erros=erros, etapa="ME5A", funcao=extrair_me5a, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ME2L", funcao=extrair_me2l, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ME3L", funcao=extrair_me3l, tentativas=3, intervalo=60)

    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de INDIRECT_PROCUREMENT:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_INDIRECT_PROCUREMENT.PY finalizado com sucesso ----")

if __name__ == "__main__":
    engdds_indirect_procurement_main()
