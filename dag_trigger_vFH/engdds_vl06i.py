
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

def engdds_vl06i_main():
    
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
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/NVL06I"
        session.findById("wnd[0]").sendVKey (0)
        
        session.findById("wnd[0]/usr/btnBUTTON7").press ()
        session.findById("wnd[0]/usr/ctxtIT_LFDAT-LOW").Text = f(now.tm_mday -1) + "." + f(now.tm_mon) + "." + f(now.tm_year)
        session.findById("wnd[0]/usr/ctxtIT_LFDAT-HIGH").Text = ""

        session.findById("wnd[0]").sendVKey (8)

        caminho_arquivo = meta_arquivos['engdds_estoque.py']['path'][7]
        nome_arquivo = meta_arquivos['engdds_estoque.py']['files'][10]

        session.findById("wnd[0]/mbar/menu[0]/menu[5]/menu[1]").select()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 16
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][7], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        
        sap.encerrar_sap()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório VL06I :: {str(e)}')

        sap.encerrar_sap()

    time.sleep(10)

if __name__ == "__main__":
    engdds_vl06i_main()