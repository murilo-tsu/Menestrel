from saplogin import SAPLogin
from Minio import MinioConnector
import json
import time
import os
import logging

# Instaciador de SAP Session
sap = SAPLogin()

def engdds_cogi_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_COGI.PY ----")

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')

    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)

    session = sap.login_to_s4hana()

    try:
        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        now = time.localtime()
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/NCOGI"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/btn%_S_WERKS_%_APP_%-VALU_PUSH").press()

        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").Text = "e90*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").SetFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[29]").press()
        session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()

        caminho_arquivo = meta_arquivos['engdds_cogi.py']['path']
        nome_arquivo = f"{now.tm_year}_{meta_arquivos['engdds_cogi.py']['files']}"

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/tbar[1]/btn[20]").press()
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/usr/ctxtDY_PATH").SetFocus()
            session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
            session.findById("wnd[1]").sendVKey (4)

            session.findById("wnd[2]/usr/ctxtDY_PATH").Text = caminho_arquivo
            session.findById("wnd[2]/usr/ctxtDY_FILENAME").Text = nome_arquivo

            session.findById("wnd[2]/usr/ctxtDY_FILE_ENCODING").Text = "0001"
            session.findById("wnd[2]/usr/ctxtDY_FILE_ENCODING").SetFocus()

            session.findById("wnd[2]/tbar[0]/btn[11]").press()
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)

        sap.limpar_processos()
        sap.cleanup()

    except Exception as e:
        logging.error(f'Erro ao exportar dados do relatório COGI :: {str(e)}')
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(10)
    minio.flush_pending_uploads()

if __name__ == "__main__":
    engdds_cogi_main()
