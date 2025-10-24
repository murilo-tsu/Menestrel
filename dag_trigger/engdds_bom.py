# Create an instance of the SAPLogin class
from saplogin import SAPLogin
import datetime
import time
from dateutil.relativedelta import relativedelta
import os
sap = SAPLogin()

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)

def engdds_bom_main():
    
    end_year_bom = f(datetime.date.today().year)
    end_month_bom = f(datetime.date.today().month)
    end_day_bom = f(datetime.date.today().day)

    first_date = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1)
    last_date = first_date + relativedelta(months=+12)
    first_date = first_date.strftime("%d.%m.%Y")
    last_date = last_date.strftime("%d.%m.%Y")


    # E890 :: COMPLEXO MINEROINDUSTRIAL DE SERRA DO SALITRE
    try:
        
        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_BOMREP"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "E89*"
        session.findById("wnd[0]/usr/ctxtS_STLAN-LOW").text = "1"
        session.findById("wnd[0]/usr/ctxtS_DATUV-LOW").text = first_date
        session.findById("wnd[0]/usr/ctxtS_VAL_TO-LOW").text = last_date
        session.findById("wnd[0]/usr/ctxtP_VARI").text = "DATAINSIGHTS"
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").setFocus()
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").caretPosition = 0
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\BOM"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E890.XLSX"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
        session.findById("wnd[1]").sendVKey (0)
        print('ZPP_BOM_REP_E890.XLSX salvo com sucesso!')

        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.upload_files(f"Shared Documents/Hadoop/SAP4HANA/BOM/",
                         f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/BOM/{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E890.XLSX")
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZPP_BOMREP para E890 :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    # E600 :: EUROCHEM FERTILIZANTES TOCANTINS
    try:

        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_BOMREP"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "E60*"
        session.findById("wnd[0]/usr/ctxtS_STLAN-LOW").text = "1"
        session.findById("wnd[0]/usr/ctxtS_DATUV-LOW").text = first_date
        session.findById("wnd[0]/usr/ctxtS_VAL_TO-LOW").text = last_date
        session.findById("wnd[0]/usr/ctxtP_VARI").text = "DATAINSIGHTS"
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").setFocus()
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").caretPosition = 0
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\BOM"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E600.XLSX"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
        session.findById("wnd[1]").sendVKey (0)
        print('ZPP_BOM_REP_E600.XLSX salvo com sucesso!')

        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.upload_files(f"Shared Documents/Hadoop/SAP4HANA/BOM/",
                         f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/BOM/{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E600.XLSX")
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZPP_BOMREP para E600 :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    # E900 :: EUROCHEM FERTILIZANTES HERINGER
    try:

        session = sap.login_to_s4hana()
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_BOMREP"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "E90*"
        session.findById("wnd[0]/usr/ctxtS_STLAN-LOW").text = "1"
        session.findById("wnd[0]/usr/ctxtS_DATUV-LOW").text = first_date
        session.findById("wnd[0]/usr/ctxtS_VAL_TO-LOW").text = last_date
        session.findById("wnd[0]/usr/ctxtP_VARI").text = "DATAINSIGHTS"
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").setFocus()
        session.findById("wnd[0]/usr/txtS_STLAL-LOW").caretPosition = 0
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\BOM"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E900.XLSX"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
        session.findById("wnd[1]").sendVKey (0)
        print('ZPP_BOM_REP_E900.XLSX salvo com sucesso!')

        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.upload_files(f"Shared Documents/Hadoop/SAP4HANA/BOM/",
                         f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/BOM/{end_year_bom}-{end_month_bom}-{end_day_bom} ZPP_BOMREP_E900.XLSX")
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZPP_BOMREP para E900 :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(10)


if __name__ == "__main__":
    engdds_bom_main()
