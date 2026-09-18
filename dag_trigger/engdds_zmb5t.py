from saplogin import SAPLogin
from Minio import MinioConnector
import json
import time
import os
import logging

def f(num):
    """Função f() normaliza os números em formato texto"""
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


def engdds_zmb5t_main():
    """
    Refresh incremental do ZMB5T — escreve no mesmo destino que o bloco
    ZMB5T embutido em engdds_estoque.py (path[0]/files[1] de
    'engdds_estoque.py' no files.json), mantendo o arquivo mais fresco
    ao longo do dia sem duplicar a chave de configuração.
    """
    logging.info("---- INICIANDO PROCESSO: ENGDDS_ZMB5T.PY ----")

    erros = []

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')

    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)

    now = time.localtime()
    end_day = f(now.tm_mday)
    end_month = f(now.tm_mon)
    end_year = f(now.tm_year)

    def extrair_zmb5t():
        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except Exception as erro:
            logging.debug(f"Pop-up opcional nao tratado: {erro}")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZMB5T"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtP_ALVDEF").text = "/Z2"
        session.findById("wnd[0]/usr/ctxtP_ALVDEF").setFocus()
        session.findById("wnd[0]/usr/ctxtP_ALVDEF").caretPosition = 3
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]").sendVKey (8)
        session.findById("wnd[0]/tbar[1]/btn[43]").press()
        session.findById("wnd[0]/mbar/menu[3]/menu[2]/menu[1]").select()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()

        caminho_arquivo = meta_arquivos['engdds_estoque.py']['path'][0]
        nome_arquivo = f"{end_year}-{end_month}-{end_day} {meta_arquivos['engdds_estoque.py']['files'][1]}"

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").select()
            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except Exception as erro:
                logging.debug(f"Pop-up opcional nao tratado: {erro}")

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 21
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)

        sap.limpar_processos()
        sap.cleanup()

    executar_com_retry(erros=erros, etapa="ZMB5T", funcao=extrair_zmb5t, tentativas=3, intervalo=60)

    time.sleep(10)
    minio.flush_pending_uploads()

    if erros:
        raise RuntimeError(
            "Ocorreram erros em uma ou mais extrações de ZMB5T:\n"
            + "\n".join(erros)
        )

    logging.info("---- ENGDDS_ZMB5T.PY finalizado com sucesso ----")

if __name__ == "__main__":
    engdds_zmb5t_main()
