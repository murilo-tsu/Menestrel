from saplogin import SAPLogin
from Minio import MinioConnector
import json
import time
import os
import logging

def f(num):
    return f"0{num}" if num < 10 else str(num)

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


def engdds_zfi_nf_pivb_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_ZFI_NF_PIVB.PY ----")

    erros = []

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')

    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)

    def extrair_zfi_nf_pivb():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        now = time.localtime()
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/NZFI_NF_PIVB"
        session.findById("wnd[0]").sendVKey (0)

        session.findById("wnd[0]/usr/ctxtS_DOCDAT-HIGH").Text = ""
        session.findById("wnd[0]/usr/ctxtS_PSTDAT-LOW").Text = f(now.tm_mday) + "." + f(now.tm_mon) + "." + str(now.tm_year)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").Text = "/CONCILIACAO"
        session.findById("wnd[0]/usr/btn%_S_MATKL_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[16]").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpNOSV").Select()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpNOSV/ssubSCREEN_HEADER:SAPLALDB:3030/tblSAPLALDBSINGLE_E/ctxtRSCSEL_255-SLOW_E[1,0]").Text = "01"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpNOSV/ssubSCREEN_HEADER:SAPLALDB:3030/tblSAPLALDBSINGLE_E/ctxtRSCSEL_255-SLOW_E[1,1]").Text = "SERVICE"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]").sendVKey (8)

        caminho_arquivo = meta_arquivos['engdds_zfi_nf_pivb.py']['path']
        nome_arquivo = meta_arquivos['engdds_zfi_nf_pivb.py']['files']

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = (16)
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)

        sap.limpar_processos()
        sap.cleanup()

    executar_com_retry(erros=erros, etapa="ZFI_NF_PIVB", funcao=extrair_zfi_nf_pivb, tentativas=3, intervalo=60)

    time.sleep(10)
    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de ZFI_NF_PIVB:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_ZFI_NF_PIVB.PY finalizado com sucesso ----")

if __name__ == "__main__":
    engdds_zfi_nf_pivb_main()
