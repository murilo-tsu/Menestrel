from saplogin import SAPLogin
from Minio import MinioConnector
import datetime
from datetime import date
import logging
import json
import time
import os
sap = SAPLogin()

def engdds_vbak_main():
    
    minio = MinioConnector()
    with open('files.json', 'r') as file:
        meta_arquivos = json.load(file)

    # Definindo datas dinâmicas
    hoje = date.today().weekday()
    domingo = (hoje == 6)

    now = time.localtime()
    if domingo:
        lag = 300
    else:
        lag = 60

    start_date = datetime.datetime(now.tm_year,now.tm_mon,now.tm_mday) + datetime.timedelta(days=-lag)
    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year
    end_day = now.tm_mday
    end_month = now.tm_mon
    end_year = now.tm_year

    # Extrair tabela VBAK - Sales Document Header
    try:

        session = sap.login_to_s4hana()

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass

        # --- MAIN ETL ---

        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "VBAK"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/ctxtGS_SELFIELDS-LOW[2,2]").text = f"{start_day}.{start_month}.{start_year}"
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/ctxtGS_SELFIELDS-HIGH[3,2]").text = f"{end_day}.{end_month}.{end_year}"
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 9
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "ZSFO"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "ZSFC"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")

        # --- MAIN ETL ---

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
        session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
        session.findById("wnd[1]").sendVKey (4)
        
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
        session.findById("wnd[2]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_vbak.py']['path']
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = meta_arquivos['engdds_vbak.py']['files'][0]
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[2]/tbar[0]/btn[11]").press()
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        
        # Encerrar sessão do SAP
        sap.limpar_processos()

        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Tabelas",
        #                  r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Tabelas/MARA.xlsx")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_vbak.py']['path'], meta_arquivos['engdds_vbak.py']['files'][0])
        minio.upload_from_bytesIO(arquivo,'tmp',meta_arquivos['engdds_vbak.py']['files'][0])
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()
        
    except Exception as e:
        print(f'Erro ao exportar dados do relatório SE16N :: VBAK :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()
    
    time.sleep(10)

if __name__ == "__main__":
    engdds_vbak_main()