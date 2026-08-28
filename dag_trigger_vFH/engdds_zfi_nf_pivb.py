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

def engdds_zfi_nf_pivb_main():
    
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

        caminho_arquivo = meta_arquivos['engdds_estoque.py']['path'][6]
        nome_arquivo = meta_arquivos['engdds_estoque.py']['files'][9]

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
        session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = (16)
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][6], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        
        sap.encerrar_sap()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório MB51 :: {str(e)}')

        sap.encerrar_sap()

    time.sleep(10)

if __name__ == "__main__":
    engdds_zfi_nf_pivb_main()