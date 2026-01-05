from saplogin import SAPLogin
from Minio import MinioConnector
import datetime
import json
import time
import os
sap = SAPLogin()

def engdds_faturamento_hourly_main():
    
    minio = MinioConnector()
    with open('files.json', 'rb') as file:
        meta_arquivos = json.load(file)

    # Definindo datas dinâminas
    now = time.localtime()
    start_date = datetime.datetime(now.tm_year,now.tm_mon,now.tm_mday) + datetime.timedelta(days=-2)
    #start_date = datetime.datetime(2025,1,1)
    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year
    end_day = now.tm_mday
    end_month = now.tm_mon
    end_year = now.tm_year

    try:
        # Login to S/4HANA
        session = sap.login_to_s4hana()
        # Extrair E600

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/ctxtSO_VKORG-LOW").text = "E600"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-LOW").text = f"{start_day}.{start_month}.{start_year}"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
        session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
        session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")

        # ----------------------------------------------------------------------------------------------------------------------
        # Opção 1: usado para extrair um arquivo do tipo .txt
        # session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&PC")
        # session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
        # session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
        # session.findById("wnd[1]/tbar[0]/btn[0]").press()
        # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E600 Eurochem Fertilizantes Tocantins\E600 ECFTO - Faturamento\SAP S4 HANA"
        # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E600.txt"
        # session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 12
        # session.findById("wnd[1]/tbar[0]/btn[11]").press()
        # ---------------------------------------------------------------------------------------------------------------------

        # Opção 2: usado para extrair um arquivo do tipo .xlsx
        session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Faturamento"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_faturamento_hourly.py']['path']
        # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E600_HOURLY.XLSX"
        nome_arquivo = meta_arquivos['engdds_faturamento_hourly.py']['files'][0]
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]").close()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Faturamento",
        #                  r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Faturamento/ZSD_PIVB_E600_HOURLY.XLSX")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_faturamento_hourly.py']['path'], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    finally:
        sap.cleanup()

    try:

        session = sap.login_to_s4hana()
        # Extrair E890
        print("Login Efetuado :: SAP4HANA")
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/ctxtSO_VKORG-LOW").text = "E890"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-LOW").text = f"{start_day}.{start_month}.{start_year}"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
        session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
        session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")

        # ------------------------------------------------------------------------------------------
        # Opção 1: usado para extrair um arquivo do tipo .txt
        #session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&PC")
        #session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
        #session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
        #session.findById("wnd[1]/tbar[0]/btn[0]").press()
        #session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E600 Eurochem Fertilizantes Tocantins\E600 ECFTO - Faturamento\SAP S4 HANA"
        #session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E600.txt"
        #session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 12
        #session.findById("wnd[1]/tbar[0]/btn[11]").press()
        # ------------------------------------------------------------------------------------------

        # Opção 2: usado para extrair um arquivo do tipo .xlsx
        session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Faturamento"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_faturamento_hourly.py']['path']
        # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E890_HOURLY.XLSX"
        nome_arquivo = meta_arquivos['engdds_faturamento_hourly.py']['files'][1]
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]").close()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Faturamento",
        #                 r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Faturamento/ZSD_PIVB_E890_HOURLY.XLSX")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_faturamento_hourly.py']['path'], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    finally:
        sap.cleanup()


    try:

        session = sap.login_to_s4hana()
        # Extrair E890
        print("Login Efetuado :: SAP4HANA")
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/ctxtSO_VKORG-LOW").text = "E900"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-LOW").text = f"{start_day}.{start_month}.{start_year}"
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
        session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
        except:
            pass

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
        session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")

        # ------------------------------------------------------------------------------------------
        # Opção 1: usado para extrair um arquivo do tipo .txt
        #session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&PC")
        #session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
        #session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
        #session.findById("wnd[1]/tbar[0]/btn[0]").press()
        #session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\02 - Data Analytics\E600 Eurochem Fertilizantes Tocantins\E600 ECFTO - Faturamento\SAP S4 HANA"
        #session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E600.txt"
        #session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 12
        #session.findById("wnd[1]/tbar[0]/btn[11]").press()
        # ------------------------------------------------------------------------------------------

        # Opção 2: usado para extrair um arquivo do tipo .xlsx
        session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Faturamento"
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_faturamento_hourly.py']['path']
        # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E900_HOURLY.XLSX"
        nome_arquivo = meta_arquivos['engdds_faturamento_hourly.py']['files'][2]
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]").close()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
        # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
        # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Faturamento",
        #                  r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Faturamento/ZSD_PIVB_E900_HOURLY.XLSX")
        arquivo = minio.buffer_creator(meta_arquivos['engdds_faturamento_hourly.py']['path'], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZSD_PIVB :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(5)
    # Os fluxos deixaram de triggar as dags
    #sap.trigger_airflow_dag(dag_name="engdds_faturamento")

if __name__ == "__main__":
    engdds_faturamento_hourly_main()