# Create an instance of the SAPLogin class
from saplogin import SAPLogin
import logging
import time
import os
sap = SAPLogin()

def engdds_sku_main():
    # Extrair tabela MARA
    try:
        # Login to S/4HANA
        session = sap.login_to_s4hana()
        print("Login ao SAP4HANA com sucesso.")
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MARA"
        session.findById("wnd[0]/usr/ctxtGD-TAB").caretPosition = 4
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey (18)
        
        #session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/chkGS_SELFIELDS-MARK[5,1]").selected = True
        #session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/chkGS_SELFIELDS-MARK[5,2]").selected = True
        #session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/chkGS_SELFIELDS-MARK[5,3]").selected = True
        
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC").columns.elementAt(1).width = 31
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
        session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
        session.findById("wnd[1]").sendVKey (4)
        session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "MARA.XLSX"
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[2]/tbar[0]/btn[11]").press()
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        
        # Encerrar sessão do SAP
        os.system('taskkill /f /im saplogon.exe')
        #os.system('taskkill /f /im saplogon.exe')
        os.system('taskkill /f /im cmd.exe')
        os.system('taskkill /f /im notepad.exe')
        sap.cleanup()
        
    except Exception as e:
        print(f'Erro ao exportar dados do relatório SE16N :: MARA :: {str(e)}')
        # Encerrar sessão do SAP
        os.system('taskkill /f /im saplogon.exe')
        #os.system('taskkill /f /im saplogon.exe')
        os.system('taskkill /f /im cmd.exe')
        os.system('taskkill /f /im notepad.exe')
        sap.cleanup()

    # Extrair tabela MAKT
    try:
        # Login to S/4HANA
        session = sap.login_to_s4hana()
        print("Login ao SAP4HANA com sucesso.")
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "MAKT"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey (18)
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").firstVisibleRow = 36
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "MAKT.XLSX"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        # Encerrar sessão do SAP
        os.system('taskkill /f /im saplogon.exe')
        #os.system('taskkill /f /im saplogon.exe')
        os.system('taskkill /f /im cmd.exe')
        os.system('taskkill /f /im notepad.exe')
        sap.cleanup()
        
    except Exception as e:
        print(f'Erro ao exportar dados do relatório SE16N :: MAKT :: {str(e)}')
        # Encerrar sessão do SAP
        os.system('taskkill /f /im saplogon.exe')
        #os.system('taskkill /f /im saplogon.exe')
        os.system('taskkill /f /im cmd.exe')
        os.system('taskkill /f /im notepad.exe')
        sap.cleanup()

    # Extrair tabela MAT_CLASS
    try:
        # Login to S/4HANA
        session = sap.login_to_s4hana()
        print("Login ao SAP4HANA com sucesso.")   
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass   
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "SE16N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtGD-TAB").text = "ZVMM_MAT_CLASS"
        session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
        session.findById("wnd[0]").sendVKey (18)
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,1]").press()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = "2000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,2]").text = "4000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,3]").text = "7000000000"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "1999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,1]").text = "2999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,2]").text = "4999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").text = "7999999999"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,3]").caretPosition = 10
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").firstVisibleRow = 36
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
        session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "ZVMM_MAT_CLASS.XLSX"
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()
        
        # Encerrar sessão do SAP
        os.system('taskkill /f /im saplogon.exe')
        #os.system('taskkill /f /im saplogon.exe')
        os.system('taskkill /f /im cmd.exe')
        os.system('taskkill /f /im notepad.exe')
        sap.cleanup()
        
    except Exception as e:
        print(f'Erro ao exportar dados do relatório SE16N :: ZVMM_MAT_CLASS :: {str(e)}')
        # Encerrar sessão do SAP
        os.system('taskkill /f /im saplogon.exe')
        #os.system('taskkill /f /im saplogon.exe')
        os.system('taskkill /f /im cmd.exe')
        os.system('taskkill /f /im notepad.exe')
        sap.cleanup()

    # time.sleep(10)
    # sap.trigger_airflow_dag(dag_name="engdds_sku")

if __name__ == "__main__":
    engdds_sku_main()