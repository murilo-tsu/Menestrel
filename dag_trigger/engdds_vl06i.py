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


def engdds_vl06i_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_VL06I.PY ----")

    erros = []

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')

    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)

    def extrair_vl06i():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        now = time.localtime()
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/NVL06I"
        session.findById("wnd[0]").sendVKey (0)

        session.findById("wnd[0]/usr/btnBUTTON7").press ()
        session.findById("wnd[0]/usr/ctxtIT_LFDAT-LOW").Text = f(now.tm_mday - 1) + "." + f(now.tm_mon) + "." + f(now.tm_year)
        session.findById("wnd[0]/usr/ctxtIT_LFDAT-HIGH").Text = ""

        session.findById("wnd[0]").sendVKey (8)

        caminho_arquivo = meta_arquivos['engdds_vl06i.py']['path']
        nome_arquivo = meta_arquivos['engdds_vl06i.py']['files']

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/mbar/menu[0]/menu[5]/menu[1]").select()
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 16
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)

        sap.limpar_processos()
        sap.cleanup()

    executar_com_retry(erros=erros, etapa="VL06I", funcao=extrair_vl06i, tentativas=3, intervalo=60)

    time.sleep(10)
    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de VL06I:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_VL06I.PY finalizado com sucesso ----")

if __name__ == "__main__":
    engdds_vl06i_main()
