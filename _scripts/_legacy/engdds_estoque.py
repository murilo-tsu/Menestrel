# Create an instance of the SAPLogin class
from saplogin import SAPLogin
from datetime import date, timedelta
import time
import os
sap = SAPLogin()

       
# Definindo datas dinâmicas
today = date.today()
ano = today.year

dt = date(end_year,int(month),int(day))
dt_first = dt + timedelta(days=-5)

werks = ['E601','E60B','E60C','E60D','E60E','E60F','E60G','E60H','E60I','E60J','E60K','E60L','E60N',
         'E890','E89A','E89B','E89C','E89Z',
         'E901','E90A','E90B','E90C','E90D','E90E','E90F','E90G','E90H','E90I','E90J','E90K','E90L','E90M','E90N','E90P','E90R',
         'P60B','P60C','P60D','P60E','P60F','P60G','P60H','P60I','P60J','P60L',
         'P90A','P90C','P90F','P90G','P90I','P90J','P90K','P90L','P90M','P90N']

# for werk in werks:
#     session = sap.login_to_s4hana()
#     session.findById("wnd[0]").maximize()
#     session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_QNTY_PIVB"
#     session.findById("wnd[0]").sendVKey (0)
#     session.findById("wnd[0]/usr/ctxtSO_WERKS-LOW").text = f"{werk}"
#     session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = start_date
#     session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = f"{end_day}.{end_month}.{end_year}"
#     session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "ZSOP"
#     session.findById("wnd[0]/usr/ctxtP_DISVAR").setFocus()
#     session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
#     session.findById("wnd[0]/tbar[1]/btn[8]").press()

#     try:
#         session.findById("wnd[1]/usr/btnBUTTON_1").press()
#     except:
#         pass

#     session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
#     session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
#     session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
#     session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
#     session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Estoque"
#     session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year}-{end_month}-{end_day} ZMM_QNTY_PIVB_{werk}.XLSX"
#     session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
#     session.findById("wnd[1]/tbar[0]/btn[11]").press()   

#     # Encerrar sessão do SAP
#     os.system('taskkill /f /im saplogon.exe')
#     os.system('taskkill /f /im saplogon.exe')
#     os.system('taskkill /f /im cmd.exe')
#     os.system('taskkill /f /im notepad.exe')

try:
    # Login to S/4HANA
    session = sap.login_to_s4hana()
    print("Logged in successfully!")
    

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
    # Always clean up
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
    # Always clean up
    sap.cleanup()

# time.sleep(30)
# sap.trigger_airflow_dag(dag_name="engdds_estoque")