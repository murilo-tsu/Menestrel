# Extração de dados do relatório FBL1H - Fornecedores BI de Quebra de balança

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

def engdds_fbl1h_main():
    
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
        session.findById("wnd[0]/usr/ctxtS_PDATE-HIGH").Text = f"{f(now.tm_mday)}.{f(now.tm_mon)}.{now.tm_year}"
        session.findById("wnd[0]/usr/ctxtS_PDATE-HIGH").SetFocus()
        session.findById("wnd[0]/usr/ctxtS_PDATE-HIGH").caretPosition = 8
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        session.findById("wnd[1]/usr/btnBUTTON_1").press()
        session.findById("wnd[0]").sendVKey (8)
    
        # Exportar dados
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
        session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")

        #Nome do arquivo e caminho onde será salvo temporariamente
        caminho_arquivo = meta_arquivos['engdds_estoque.py']['path'][3]
        nome_arquivo = f"{now.tm_year}_{meta_arquivos['engdds_estoque.py']['files'][4]}"

        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][3], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        # Encerrar sessão do SAP
        sap.encerrar_sap()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório FBL1H :: {str(e)}')
        # Encerrar sessão do SAP
        sap.encerrar_sap()

    time.sleep(10)

if __name__ == "__main__":
    engdds_fbl1h_main()