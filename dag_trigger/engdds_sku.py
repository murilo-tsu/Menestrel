from saplogin import SAPLogin
from Minio import MinioConnector
import logging
import json
import time
import os
sap = SAPLogin()


def registrar_erro(erros, etapa, erro):
    """
    Registra erro definitivo de uma etapa.

    Essa função só deve ser chamada depois que todas as tentativas da etapa
    falharem.
    """
    mensagem = f"{etapa} :: {str(erro)}"

    logging.error(f"Erro definitivo na etapa {etapa}: {str(erro)}")
    erros.append(mensagem)

    try:
        sap.limpar_processos()
        sap.cleanup()
    except:
        pass


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
                f"{tentativa}/{tentativas}: {str(erro)}"
            )

            try:
                sap.limpar_processos()
                sap.cleanup()
            except:
                pass

            if tentativa < tentativas:
                logging.info(f"{etapa} será tentado novamente em {intervalo} segundos...")
                time.sleep(intervalo)

    registrar_erro(erros, etapa, ultimo_erro)
    return False


def engdds_sku_main():
    """
    Executa as extrações de SKU no SAP S/4HANA.

    Fluxo:
        1. Carrega os metadados do files.json.
        2. Extrai a tabela MARA via SE16N.
        3. Extrai a tabela MAKT via SE16N.
        4. Extrai a visão/tabela ZVMM_MAT_CLASS via SE16N.
        5. Envia os arquivos gerados para o bucket tmp do MinIO.

    Observação:
        Cada bloco tem retry próprio (3 tentativas). As etapas são
        independentes entre si — se uma falhar mesmo após o retry, o script
        segue para as próximas e só informa falha ao Menestrel no final.
    """
    logging.info("---- INICIANDO PROCESSO: ENGDDS_SKU.PY ----")

    minio = MinioConnector()
    erros = []

    with open('files.json', 'r') as file:
        meta_arquivos = json.load(file)

    path_sku = meta_arquivos["engdds_sku.py"]["path"]
    files = meta_arquivos["engdds_sku.py"]["files"]

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 1 :: SE16N - MARA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_mara():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MARA"
        session.findById("wnd[0]/usr/ctxtGD-TAB").caretPosition = 4
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(18)

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()

        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC").columns.elementAt(1).width = 31
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
            session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
            session.findById("wnd[1]").sendVKey(4)

            nome_arquivo = files[0]

            session.findById("wnd[2]/usr/ctxtDY_PATH").text = path_sku
            session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 9
            session.findById("wnd[2]/tbar[0]/btn[11]").press()
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(path_sku, files[0])
        minio.upload_or_queue(arquivo, "tmp", files[0])

        sap.limpar_processos()
        sap.cleanup()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 2 :: SE16N - MAKT
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_makt():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MAKT"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(18)

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()

        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").firstVisibleRow = 36

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            nome_arquivo = files[1]

            try:
                session.findById("wnd[2]/usr/ctxtDY_PATH").text = path_sku
                session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nome_arquivo
            except:
                session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_sku
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo

            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
            session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        session.findById("wnd[0]/tbar[0]/btn[15]").press()

        arquivo = minio.buffer_creator(path_sku, files[1])
        minio.upload_or_queue(arquivo, "tmp", files[1])

        sap.limpar_processos()
        sap.cleanup()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # BLOCO 3 :: SE16N - ZVMM_MAT_CLASS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def extrair_mat_class():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_MAT_CLASS"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(18)

        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()

        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").firstVisibleRow = 36

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            nome_arquivo = files[2]

            try:
                session.findById("wnd[2]/usr/ctxtDY_PATH").text = path_sku
                session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nome_arquivo
            except:
                session.findById("wnd[1]/usr/ctxtDY_PATH").text = path_sku
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo

            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(path_sku, files[2])
        minio.upload_or_queue(arquivo, "tmp", files[2])

        sap.limpar_processos()
        sap.cleanup()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # EXECUÇÃO DOS BLOCOS COM RETRY
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    executar_com_retry(erros=erros, etapa="MARA", funcao=extrair_mara, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="MAKT", funcao=extrair_makt, tentativas=3, intervalo=60)
    executar_com_retry(erros=erros, etapa="ZVMM_MAT_CLASS", funcao=extrair_mat_class, tentativas=3, intervalo=60)

    time.sleep(10)
    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de SKU:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_SKU.PY finalizado com sucesso ----")


if __name__ == "__main__":
    engdds_sku_main()
