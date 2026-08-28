#Extração de dados do relatório COOISPI_VARREDURA do SAP S/4HANA para o MinIO - TRW

from saplogin import SAPLogin
from datetime import date, timedelta
from Minio import MinioConnector
import pandas as pd
import json
import time
import os

def f(num):

    return f"0{num}" if num < 10 else str(num)

# Instaciador de SAP Session
sap = SAPLogin()

def engdds_cogi_main():
    
    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')
    
    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)
    
    #Login no SAP PT
    session = sap.login_to_s4hana_pt()
    
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
        session.findById("wnd[0]/tbar[1]/btn[20]").press()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/ctxtDY_PATH").SetFocus()
        session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
        session.findById("wnd[1]").sendVKey (4)

        caminho_arquivo = meta_arquivos['engdds_estoque.py']['path'][5]
        nome_arquivo = f"{now.tm_year}_{meta_arquivos['engdds_estoque.py']['files'][8]}"

        session.findById("wnd[2]/usr/ctxtDY_PATH").Text = caminho_arquivo
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").Text = nome_arquivo

        session.findById("wnd[2]/usr/ctxtDY_FILE_ENCODING").Text = "0001"
        session.findById("wnd[2]/usr/ctxtDY_FILE_ENCODING").SetFocus()

        session.findById("wnd[2]/tbar[0]/btn[11]").press()
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][5], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)

        # Encerrar sessão do SAP
        sap.encerrar_sap()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório COGI :: {str(e)}')

        # Encerrar sessão do SAP
        sap.encerrar_sap()

    time.sleep(10)
if __name__ == "__main__":
    engdds_cogi_main()