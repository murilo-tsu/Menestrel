from saplogin import SAPLogin
from Minio import MinioConnector
import time
import json
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


def engdds_werkish_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_WERKISH.PY ----")

    minio = MinioConnector()
    erros = []
    with open('files.json','rb') as file:
        meta_arquivos = json.load(file)

    # WERKS :: CADASTRO DE PLANTAS
    def extrair_werks():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_WERKS_I"
        session.findById("wnd[0]/usr/ctxtGD-TAB").setFocus()
        session.findById("wnd[0]/usr/ctxtGD-TAB").caretPosition = 12
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except Exception as erro:
                logging.debug(f"Pop-up opcional nao tratado: {erro}")

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_werkish.py']['path']
            # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "WERKS.xlsx"
            nome_arquivo = meta_arquivos['engdds_werkish.py']['files'][0]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Tabelas",
        #                  r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Tabelas/WERKS.xlsx")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_werkish.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    # LGORT :: CADASTRO DE DEPÓSITOS
    def extrair_lgort():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_LGORT_2"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").setFocus
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").caretPosition = 0
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except Exception as erro:
                logging.debug(f"Pop-up opcional nao tratado: {erro}")

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_werkish.py']['path']
            # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "LGORT.xlsx"
            nome_arquivo = meta_arquivos['engdds_werkish.py']['files'][1]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Tabelas",
        #                  r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Tabelas/LGORT.xlsx")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_werkish.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    # TVSTT :: Descrição de Shipping Points
    def extrair_tvstt():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "TVSTT"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except Exception as erro:
                logging.debug(f"Pop-up opcional nao tratado: {erro}")

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_werkish.py']['path']
            # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "TVSTT.xlsx"
            nome_arquivo = meta_arquivos['engdds_werkish.py']['files'][2]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Tabelas",
        #                  r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Tabelas/TVSTT.xlsx")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_werkish.py']['path'], nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    executar_com_retry(erros=erros, etapa="WERKS", funcao=extrair_werks, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZVMM_LGORT_2", funcao=extrair_lgort, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="TVSTT", funcao=extrair_tvstt, tentativas=3, intervalo=60)

    time.sleep(10)
    minio.flush_pending_uploads()
    # sap.trigger_airflow_dag(dag_name="engdds_units")

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de WERKISH:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_WERKISH.PY finalizado com sucesso ----")

if __name__ == "__main__":
    engdds_werkish_main()
