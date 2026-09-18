from dateutil.relativedelta import relativedelta
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


def engdds_gl_accounts_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_GL_ACCOUNTS.PY ----")

    # Instanciando o Minio para utilizar buffer e uploader a partir dos arquivos do json
    minio = MinioConnector()
    erros = []
    with open('files.json','rb') as file:
        meta_arquivos = json.load(file)

    # ---------------------------------- GL ACCOUNT BALANCE [ INICIO ] ----------------------------------
    # Ano Fiscal: 2025
    def extrair_gl_account_balance_2025():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/tbar[0]/okcd").text = "ZFI_GL_PIVB"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/GLACCOUNT_SUM"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/txtSO_GJAHR-LOW").text = "2025"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = "01.01.2025"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = "31.12.2025"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[0]").sendVKey(0)

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            # folder_path = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\04 - Data Dump\_stage"
            folder_path = meta_arquivos['engdds_gl_accounts.py']['path']
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = folder_path
            nome_arquivo = f"{meta_arquivos['engdds_gl_accounts.py']['files'][0]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        time.sleep(5)
        # arquivo = minio.buffer_creator(meta_arquivos['engdds_gl_accounts.py']['path'][0], nome_arquivo)
        arquivo = minio.buffer_creator(folder_path, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()
        logging.info(f'Dados exportados com sucesso: {nome_arquivo}')

    # Ano Fiscal: 2026
    def extrair_gl_account_balance_2026():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/tbar[0]/okcd").text = "ZFI_GL_PIVB"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/GLACCOUNT_SUM"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/txtSO_GJAHR-LOW").text = "2026"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = "01.01.2026"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = "31.12.2026"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[0]").sendVKey(0)

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #folder_path = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\04 - Data Dump\_stage"
            folder_path = meta_arquivos['engdds_gl_accounts.py']['path']
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = folder_path
            nome_arquivo = f"{meta_arquivos['engdds_gl_accounts.py']['files'][1]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        time.sleep(5)
        # arquivo = minio.buffer_creator(meta_arquivos['engdds_gl_accounts.py']['path'][0], nome_arquivo)
        arquivo = minio.buffer_creator(folder_path, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()
        logging.info(f'Dados exportados com sucesso: {nome_arquivo}')

    # ---------------------------------- GL ACCOUNT BALANCE [ FIM ] ----------------------------------

    # ---------------------------------- POAC [ INICIO ] ----------------------------------
    # Ano Fiscal: 2025
    def extrair_poac_2025():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/tbar[0]/okcd").text = "ZFI_GL_PIVB"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/POAC2026"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/txtSO_GJAHR-LOW").text = "2025"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = "01.01.2025"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = "31.12.2025"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[0]").sendVKey(0)

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            folder_path = meta_arquivos['engdds_gl_accounts.py']['path']
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = folder_path
            nome_arquivo = f"{meta_arquivos['engdds_gl_accounts.py']['files'][2]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        time.sleep(5)
        arquivo = minio.buffer_creator(folder_path, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()
        logging.info(f'Dados exportados com sucesso: {nome_arquivo}')

    # Ano Fiscal: 2026
    def extrair_poac_2026():
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/tbar[0]/okcd").text = "ZFI_GL_PIVB"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/txtV-LOW").text = "/POAC2026"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/txtSO_GJAHR-LOW").text = "2026"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = "01.01.2026"
        session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = "31.12.2026"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[0]").sendVKey(0)

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            folder_path = meta_arquivos['engdds_gl_accounts.py']['path']
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = folder_path
            nome_arquivo = f"{meta_arquivos['engdds_gl_accounts.py']['files'][3]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        time.sleep(5)
        arquivo = minio.buffer_creator(folder_path, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        sap.cleanup()
        logging.info(f'Dados exportados com sucesso: {nome_arquivo}')

    executar_com_retry(erros=erros, etapa="ZFI_GL_PIVB_GLACCOUNT_2025", funcao=extrair_gl_account_balance_2025, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZFI_GL_PIVB_GLACCOUNT_2026", funcao=extrair_gl_account_balance_2026, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZFI_GL_PIVB_POAC_2025", funcao=extrair_poac_2025, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZFI_GL_PIVB_POAC_2026", funcao=extrair_poac_2026, tentativas=3, intervalo=60)

    time.sleep(2)
    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de GL_ACCOUNTS:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_GL_ACCOUNTS.PY finalizado com sucesso ----")


if __name__ == "__main__":
    engdds_gl_accounts_main()
