from saplogin import SAPLogin
import datetime
import time
import os
sap = SAPLogin()

def engdds_cockpit_main():
    try:

        session = sap.login_to_s4hana()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_COCKPIT"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/btn%_S_ZSTEP_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "3"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "5"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "6"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,3]").text = "7"
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,4]").text = "8"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/shellcont/shell").selectColumn ("ZSTEP")
        session.findById("wnd[0]/shellcont/shell").contextMenu()
        session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]").sendVKey (4)
        session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Cockpit"
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "ZPP_COCKPIT.XLSX"
        session.findById("wnd[2]/tbar[0]/btn[11]").press()
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        sap.limpar_processos()
        sap.upload_files(f"Shared Documents/Hadoop/SAP4HANA/Cockpit/",
                         f"C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Cockpit/ZPP_COCKPIT.XLSX")
        sap.cleanup()
    
    except Exception as erro:
        print('Erro ao exportar o ZPP_COCKPIT.XLSX')
        sap.limpar_processos()
        sap.cleanup()

if __name__ == "__main__":
    engdds_cockpit_main()