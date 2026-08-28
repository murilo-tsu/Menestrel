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

def engdds_zmb5t_main():
    """
    Refresh incremental do ZMB5T — escreve no mesmo destino que o bloco
    ZMB5T embutido em engdds_estoque.py (path[0]/files[1] de
    'engdds_estoque.py' no files.json), mantendo o arquivo mais fresco
    ao longo do dia sem duplicar a chave de configuração.
    """
    logging.info("---- INICIANDO PROCESSO: ENGDDS_ZMB5T.PY ----")

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')

    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)

    now = time.localtime()
    end_day = f(now.tm_mday)
    end_month = f(now.tm_mon)
    end_year = f(now.tm_year)

    session = sap.login_to_s4hana()

    try:
        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

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
            except:
                pass

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 21
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)

        sap.limpar_processos()
        sap.cleanup()

    except Exception as e:
        logging.error(f'Erro ao exportar dados do relatório ZMB5T :: {str(e)}')
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(10)
    minio.flush_pending_uploads()

if __name__ == "__main__":
    engdds_zmb5t_main()
