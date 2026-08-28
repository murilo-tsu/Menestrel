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

def engdds_mb51_quebra_main():
    
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
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/NMB51"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/btn%_WERKS_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[16]").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").Text = "e90*"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").SetFocus
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/ctxtWERKS-LOW").SetFocus()
        session.findById("wnd[0]/usr/ctxtWERKS-LOW").caretPosition = 4
        session.findById("wnd[0]/usr/btn%_BWART_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").Text = "702"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").Text = "701"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").Text = "Z06"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").Text = "Z05"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").Text = "Z04"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,5]").Text = "Z03"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,5]").SetFocus()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,5]").caretPosition = 3
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/radRHIER_L").SetFocus()
        session.findById("wnd[0]/usr/radRHIER_L").Select()
        session.findById("wnd[0]/usr/radRFLAT_L").SetFocus()
        session.findById("wnd[0]/usr/radRFLAT_L").Select()
        session.findById("wnd[0]/usr/ctxtALV_DEF").Text = "/PCP_DADOS"
        
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
    
        session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").select()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        caminho_base = meta_arquivos['engdds_estoque.py']['path'][2]
        nome_arquivo = meta_arquivos['engdds_estoque.py']['files'][3]

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_base
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][2], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        
        sap.encerrar_sap()
        # sap.limpar_processos()
        # sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório MB51 :: {str(e)}')

        sap.encerrar_sap()
        # sap.limpar_processos()
        # sap.cleanup()

    time.sleep(10)

if __name__ == "__main__":
    engdds_mb51_quebra_main()