from saplogin import SAPLogin
from Minio import MinioConnector
import datetime
import json
import time
import os
sap = SAPLogin()

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)

def engdds_custos_main():

    # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
    minio = MinioConnector()
    with open('files.json', 'rb') as file:
        meta_arquivos = json.load(file)
    
    end_year_custos = f(datetime.date.today().year)
    end_month_custos = f(datetime.date.today().month)
    end_day_custos = f(datetime.date.today().day)
    #dt_custos = f"01.{end_month_custos}.{end_year_custos}"
    dt_custos = f"{end_day_custos}.{end_month_custos}.{end_year_custos}"
    dt_name_custos = f"{end_year_custos}-{end_month_custos}-{end_day_custos}"

    # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
    # cost_comp = {
        
    #     "$":"_AGG_COST.xlsx", "0":"_FOB_PRICE.xlsx", "1":"_FREIGHT.xlsx",
    #     "2":"_PORT_CHARGE.xlsx", "3":"_DEMURRAGE.xlsx", "4":"_COST_ADJ.xlsx",
    #     "5":"_ICMS.xlsx", "6":"_PERC_LOSSES.xlsx", "7":"_WAREHOUSE_COST.xlsx",
    #     "8":"_PRODUCTION_COST.xlsx", "9":"_PACKAGING_COST.xlsx", "A":"_FREIGHT_TO_CMISS.xlsx",
    #     "B":"_PREMIUM_ADJ.xlsx", "C":"_IMPORT_TAX.xlsx", "D":"_TOLLING_COST.xlsx",
    #     "E":"_UNIT_VARIABLE_COST.xlsx", "#":"_INTERNAL_TOLLING.xlsx"}

    cost_comp = meta_arquivos['engdds_custos.py']['cost_comp']
    
    for key, value in cost_comp.items():
        nome_arquivo = dt_name_custos + " " + meta_arquivos['engdds_custos.py']['files'] + value
        try:
            session = sap.login_to_s4hana()
            try:
                session.FindById("wnd[0]").SendVKey (0)
            except:
                pass
            session.findById("wnd[0]").maximize()
            session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_RPLCMNT_COST"
            session.findById("wnd[0]").sendVKey (0)
            session.findById("wnd[0]/usr/ctxtS_LCOST-LOW").text = key
            #session.findById("wnd[0]/usr/ctxtP_DATAB").text = f"01.07.2025"
            session.findById("wnd[0]/usr/ctxtP_DATAB").text = dt_custos
            session.findById("wnd[0]").sendVKey (0)
            session.findById("wnd[0]/tbar[1]/btn[8]").press()
            session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
            #session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus
            #session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
            session.findById("wnd[1]").sendVKey (4)
            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------            
            # session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Custos"
            session.findById("wnd[2]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_custos.py']['path']
            # session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = dt_name_custos + " ZSD_RPLCMNT" + value
            session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nome_arquivo
            #session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 12
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[2]/tbar[0]/btn[11]").press()
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

            # Encerrar a sessão SAP
            sap.limpar_processos()
            time.sleep(10)

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # caminho_arquivo = f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Custos/{nome_arquivo}"
            caminho_arquivo = meta_arquivos['engdds_custos.py']['path'] +"/"+nome_arquivo
            print(f"ATUALIZADO: {caminho_arquivo}")
            # sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Custos/",
            #                 caminho_arquivo)
            arquivo = minio.buffer_creator(meta_arquivos['engdds_custos.py']['path'], nome_arquivo)
            minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
            # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
            sap.cleanup()
        
        except Exception as erro:
            print(f'Erro ao exportar dados do relatório ZSD_RPLCMNT_COST{value} :: {str(erro)}')

if __name__ == "__main__":
    engdds_custos_main()