from saplogin import SAPLogin
import time
import os
sap = SAPLogin()

# WERKS :: CADASTRO DE PLANTAS
try:
    session = sap.login_to_s4hana()
    print("Logged in successfully!")

    session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
    session.findById("wnd[0]").sendVKey (0)
    session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_WERKS_I"
    session.findById("wnd[0]/usr/ctxtGD-TAB").setFocus()
    session.findById("wnd[0]/usr/ctxtGD-TAB").caretPosition = 12
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
    session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem("&XXL")
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "WERKS.xlsx"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
    session.findById("wnd[1]/tbar[0]/btn[11]").press()
    
    # Encerrar sessão do SAP
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im cmd.exe')
    os.system('taskkill /f /im notepad.exe')

finally:
    # Always clean up
    sap.cleanup()

# LGORT :: CADASTRO DE DEPÓSITOS
try:
    session = sap.login_to_s4hana()
    print("Logged in sucessfully!")

    session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
    session.findById("wnd[0]").sendVKey (0)
    session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_LGORT_2"
    session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
    session.findById("wnd[0]/usr/txtGD-MAX_LINES").setFocus
    session.findById("wnd[0]/usr/txtGD-MAX_LINES").caretPosition = 0
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
    session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "LGORT.xlsx"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
    session.findById("wnd[1]/tbar[0]/btn[11]").press()

    # Encerrar sessão do SAP
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im cmd.exe')
    os.system('taskkill /f /im notepad.exe')


finally:
    # Always clean up
    sap.cleanup()

# TVSTT :: Descrição de Shipping Points
try:
    session = sap.login_to_s4hana()
    print("Logged in sucessfully!")

    session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
    session.findById("wnd[0]").sendVKey (0)
    session.findById("wnd[0]/usr/ctxtGD-TAB").text = "TVSTT"
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
    session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "TVSTT.xlsx"
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
    session.findById("wnd[1]/tbar[0]/btn[11]").press()

    # Encerrar sessão do SAP
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im saplogon.exe')
    os.system('taskkill /f /im cmd.exe')
    os.system('taskkill /f /im notepad.exe')

finally:
    # Always clean up
    sap.cleanup()

time.sleep(20)
sap.trigger_airflow_dag(dag_name="engdds_units")

