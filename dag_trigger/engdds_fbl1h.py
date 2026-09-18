from saplogin import SAPLogin
from Minio import MinioConnector
import json
import time
import os
import logging

# Instaciador de SAP Session
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


def engdds_fbl1h_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_FBL1H.PY ----")

    minio = MinioConnector()
    erros = []

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')

    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)

    def extrair_fbl1h():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        now = time.localtime()
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/NFBL1H"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/btn%_S_CCODE_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").Text = "E900"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").SetFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").Text = "/PCP_DADOS"
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").SetFocus()
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").caretPosition = 12

        session.findById("wnd[0]/usr/radP_AI").SetFocus()
        session.findById("wnd[0]/usr/radP_AI").Select()
        session.findById("wnd[0]/usr/ctxtS_PDATE-LOW").Text = "01.01.2025"
        session.findById("wnd[0]/usr/ctxtS_PDATE-HIGH").Text = f"{now.tm_mday:02d}.{now.tm_mon:02d}.{now.tm_year}"
        session.findById("wnd[0]/usr/ctxtS_PDATE-HIGH").SetFocus()
        session.findById("wnd[0]/usr/ctxtS_PDATE-HIGH").caretPosition = 8
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        session.findById("wnd[1]/usr/btnBUTTON_1").press()
        session.findById("wnd[0]").sendVKey (8)

        caminho_arquivo = meta_arquivos['engdds_fbl1h.py']['path']
        nome_arquivo = f"{now.tm_year}_{meta_arquivos['engdds_fbl1h.py']['files']}"

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarButton("SHOWBUT")
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[1]/tbar[0]/btn[0]").press()

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)

        sap.limpar_processos()
        sap.cleanup()

    executar_com_retry(erros=erros, etapa="FBL1H", funcao=extrair_fbl1h, tentativas=3, intervalo=60)

    time.sleep(10)
    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de FBL1H:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_FBL1H.PY finalizado com sucesso ----")

if __name__ == "__main__":
    engdds_fbl1h_main()
