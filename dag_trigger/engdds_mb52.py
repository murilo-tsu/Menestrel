from saplogin import SAPLogin
from datetime import date
from Minio import MinioConnector
import json
import time
import os
import logging

# Instaciador de SAP Session
sap = SAPLogin()

def engdds_mb52_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_MB52.PY ----")

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

        session.findById("wnd[0]/tbar[0]/okcd").Text = "/nmb52"
        session.findById("wnd[0]").sendVKey (0)

        session.findById("wnd[0]/usr/radPA_FLT").setFocus()
        session.findById("wnd[0]/usr/radPA_FLT").select()

        session.findById("wnd[0]/usr/btn%_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[16]").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").Text = "E90*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").Text = "P90*"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/btn%_LGORT_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[16]").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpNOSV").Select()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpNOSV/ssubSCREEN_HEADER:SAPLALDB:3030/tblSAPLALDBSINGLE_E/ctxtRSCSEL_255-SLOW_E[1,0]").Text = "302*"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()

        session.findById("wnd[0]/usr/chkXMCHB").Selected = False
        session.findById("wnd[0]/usr/chkNOZERO").Selected = True

        session.findById("wnd[0]/usr/ctxtP_VARI").Text = "/PCP_DADOS"
        session.findById("wnd[0]/usr/ctxtP_VARI").SetFocus()
        session.findById("wnd[0]/usr/ctxtP_VARI").caretPosition = 11
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        caminho_arquivo = meta_arquivos['engdds_mb52.py']['path']
        nome_arquivo = f"{date.today().strftime('%d.%m.%Y')}_{meta_arquivos['engdds_mb52.py']['files']}"

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
            session.findById("wnd[1]/tbar[0]/btn[0]").press()

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 14
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)

        sap.limpar_processos()
        sap.cleanup()

    except Exception as e:
        logging.error(f'Erro ao exportar dados do relatório MB52 :: {str(e)}')
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(10)
    minio.flush_pending_uploads()

if __name__ == "__main__":
    engdds_mb52_main()
