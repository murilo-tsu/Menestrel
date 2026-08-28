from saplogin import SAPLogin
from Minio import MinioConnector
import json
import time
import os
import logging
from datetime import datetime, timedelta

hoje = datetime.today().date()
primeiro_dia = (hoje - timedelta(days=30)).strftime("%d.%m.%Y")
ultimo_dia = hoje.strftime("%d.%m.%Y")

# Instaciador de SAP Session
sap = SAPLogin()

def engdds_mb51_consumo_main():
    logging.info("---- INICIANDO PROCESSO: ENGDDS_MB51_CONSUMO.PY ----")

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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/NMB51"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtWERKS-LOW").text = "E90*"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtLGORT-LOW").text = "1001"
        session.findById("wnd[0]/usr/btn%_LGORT_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "B*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "T*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "S*"
        session.findById("wnd[1]").sendVKey (0)
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/btn%_BWART_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "261"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "262"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "102"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "101"
        session.findById("wnd[1]").sendVKey (0)
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/ctxtBUDAT-LOW").text = primeiro_dia
        session.findById("wnd[0]/usr/ctxtBUDAT-HIGH").text = ultimo_dia
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtALV_DEF").text = "/DTFH"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        caminho_base = meta_arquivos['engdds_mb51_consumo.py']['path']
        nome_arquivo = meta_arquivos['engdds_mb51_consumo.py']['files']

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").select()
            session.findById("wnd[1]/tbar[0]/btn[0]").press()

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_base
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(caminho_base, nome_arquivo)
        minio.upload_or_queue(arquivo, 'tmp', nome_arquivo)

        sap.limpar_processos()
        sap.cleanup()

    except Exception as e:
        logging.error(f'Erro ao exportar dados do relatório MB51_consumo :: {str(e)}')
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(10)
    minio.flush_pending_uploads()

if __name__ == "__main__":
    engdds_mb51_consumo_main()
