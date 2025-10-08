from saplogin import SAPLogin
from datetime import date, timedelta
import pandas as pd
import time
import os
sap = SAPLogin()
# Função f normaliza os números em formato texto
def f(num):
    return f"0{num}" if num < 10 else str(num)
try:
    print("Login Efetuado :: SAP4HANA")
    primeira_data = date.today() + timedelta(days=-31)
    dates_range = pd.date_range(primeira_data, pd.Timestamp.now(), freq='D')
    dt_comp = [date.strftime('%Y-%m-%d') for date in dates_range]
    werks = ['E60*', 'E89*', 'E90*', 'P60*', 'P90*']
    # Data Inicial para começo da iteração :: começo do sistema
    # Considerar posting dates antigas
    for day in dt_comp:
        dt = date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2]))

        # Iterando através das plantas
        
        try:
        
            for werk in werks:
                session = sap.login_to_s4hana()
                session.findById("wnd[0]").maximize()
                session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_QNTY_PIVB"
                session.findById("wnd[0]").sendVKey (0)
                session.findById("wnd[0]/usr/ctxtSO_WERKS-LOW").text = f"{werk}"
                session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = f"{f(dt.day)}.{f(dt.month)}.{dt.year}"
                session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = f"{f(dt.day)}.{f(dt.month)}.{dt.year}"
                session.findById("wnd[0]/usr/chkP_SB").selected = True
                session.findById("wnd[0]/usr/btn%_SO_MATNR_%_APP_%-VALU_PUSH").press()
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL").select()
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-ILOW_I[1,0]").text = "1000000000"
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-IHIGH_I[2,0]").text = "1999999999"
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-ILOW_I[1,1]").text = "2000000000"
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-IHIGH_I[2,1]").text = "2999999999"
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-ILOW_I[1,2]").text = "4000000000"
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-IHIGH_I[2,2]").text = "4999999999"
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-ILOW_I[1,3]").text = "7000000000"
                session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpINTL/ssubSCREEN_HEADER:SAPLALDB:3020/tblSAPLALDBINTERVAL/ctxtRSCSEL_255-IHIGH_I[2,3]").text = "7999999999"
                session.findById("wnd[1]/tbar[0]/btn[8]").press()
                session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "DATAINSIGHTS"
                session.findById("wnd[0]/usr/ctxtP_DISVAR").setFocus()
                session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
                session.findById("wnd[0]/tbar[1]/btn[8]").press()

                try:
                    session.findById("wnd[1]/usr/btnBUTTON_1").press()
                except:
                    pass

                session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
                session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
                session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
                session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
                session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Estoque"
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{dt.year}-{f(dt.month)}-{f(dt.day)} ZMM_QNTY_PIVB_{werk[:3]}_ALL.XLSX"
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
                session.findById("wnd[1]/tbar[0]/btn[11]").press()


                # Encerrar sessão do SAP
                os.system('taskkill /f /im saplogon.exe')
                os.system('taskkill /f /im saplogon.exe')
                os.system('taskkill /f /im cmd.exe')
                os.system('taskkill /f /im notepad.exe')
            print(f'{dt.year}-{f(dt.month)}-{f(dt.day)} :: DADOS GRAVADOS!')
        
        except Exception as erro:
            print(f"Erro ao processar dados na data {dt.year}-{f(dt.month)}-{f(dt.day)}")
            print(f"Mensagem de erro :: {str(erro)}")

finally:
    sap.cleanup()

now = time.localtime()
end_day = f(now.tm_mday)
end_month = f(now.tm_mon)
end_year = f(now.tm_year)

try:
    session = sap.login_to_s4hana()
    print("Login Efetuado :: SAP4HANA")  
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "ZMB5T"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/ctxtP_ALVDEF").text = "/Z2"
    session.findById("wnd[0]/usr/ctxtP_ALVDEF").setFocus()
    session.findById("wnd[0]/usr/ctxtP_ALVDEF").caretPosition = 3
    session.findById("wnd[0]").sendVKey (0)
    session.findById("wnd[0]").sendVKey (0)
    session.findById("wnd[0]").sendVKey (8)
    session.findById("wnd[0]/tbar[1]/btn[43]").press()
    session.findById("wnd[0]/mbar/menu[3]/menu[2]/menu[1]").select()
    session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_LAYOUT_CHOOSE:0500/cntlD500_CONTAINER/shellcont/shell").clickCurrentCell()
    session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").select()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Estoque"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year}-{end_month}-{end_day} ZMB5T.XLSX"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 21
    session.findById("wnd[1]/tbar[0]/btn[11]").press()

    # Encerrar sessão do SAP
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im cmd.exe')
    os.system('taskkill /f /im notepad.exe')
    
finally:
    sap.cleanup()

# Extrair MCHB
try:
    session = sap.login_to_s4hana()
    print("Logged in successfully!")
    now = time.localtime()
    session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
    session.findById("wnd[0]").sendVKey (0)
    session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MCHB"
    session.findById("wnd[0]").sendVKey (0)
    session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
    session.findById("wnd[0]/usr/txtGD-MAX_LINES").setFocus
    session.findById("wnd[0]/usr/txtGD-MAX_LINES").caretPosition = 0
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 1
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 2
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 3
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 4
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 5
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 6
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 7
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 8
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 9
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
    session.findById("wnd[1]").sendVKey (12)
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
    session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = f"{now.tm_year}"
    session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").caretPosition = 4
    session.findById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").setFocus()
    session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").press()
    session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = f"{now.tm_mon}"
    session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = f"{now.tm_mon - 1}"
    session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = f"{now.tm_mon - 2}"
    session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = f"{now.tm_mon - 3}"
    session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]").text = f"{now.tm_mon - 4}"
    session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]").setFocus()
    session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,4]").caretPosition = 1
    session.findById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
    session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "MCHB.XLSX"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
    session.findById("wnd[1]/tbar[0]/btn[11]").press()
    # Encerrar sessão do SAP
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im cmd.exe')
    os.system('taskkill /f /im notepad.exe')      

finally:
    sap.cleanup()

time.sleep(30)
sap.trigger_airflow_dag(dag_name="engdds_estoque")