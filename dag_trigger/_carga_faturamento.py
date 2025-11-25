from saplogin import SAPLogin
import datetime
import time
import os
sap = SAPLogin()

def engdds_faturamento_main():
    # Definindo datas dinâminas
    # now = time.localtime()
    # start_date = datetime.datetime(now.tm_year,now.tm_mon,now.tm_mday) + datetime.timedelta(days=-32)
    start_date = datetime.datetime(2025,10,1)
    end_date = datetime.datetime(start_date.year, start_date.month + 1, 1) - datetime.timedelta(days=1)
    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year
    end_day = end_date.day
    end_month = end_date.month
    end_year = end_date.year

    try:

        session = sap.login_to_s4hana()
        # Extrair E600
        print("LOGIN no SAP4HANA realizado!")
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "ZSOP"
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
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Faturamento"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E600.XLSX"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]").close()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Faturamento",
                         r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Faturamento/ZSD_PIVB_E600.XLSX")
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZSD_PIVB_E600 :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(5)
    try:

        session = sap.login_to_s4hana()
        # Extrair E890

        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "ZSOP"
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
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Faturamento"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E890.XLSX"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]").close()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Faturamento",
                         r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Faturamento/ZSD_PIVB_E890.XLSX")
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZSD_PIVB_E890 :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(5)
    try:

        session = sap.login_to_s4hana()
        # Extrair E900
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        print("LOGIN no SAP4HANA realizado!")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "ZSOP"
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
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Faturamento"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZSD_PIVB_E900.XLSX"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 18
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]").close()

        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.upload_files(r"Shared Documents/Hadoop/SAP4HANA/Faturamento",
                         r"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Faturamento/ZSD_PIVB_E900.XLSX")
        sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZSD_PIVB_E900 :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

    time.sleep(10)
    # sap.trigger_airflow_dag(dag_name="engdds_faturamento")

if __name__ == "__main__":
    engdds_faturamento_main()