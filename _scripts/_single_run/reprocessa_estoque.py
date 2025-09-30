# Create an instance of the SAPLogin class
from saplogin import SAPLogin
from datetime import date, timedelta
import time
import os
sap = SAPLogin()

# DEFINIÇÃO DE DATAS DINÂMICAS =========================================================
days = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15',
       '16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']

months = ['01','02','03','04','05','06']

# Função para normalizar os elementos da data
def f(num):
    if num >= 10:
        num = str(num)
    else:
        num = '0' + str(num)
    return num

# Argumentos fixos para o relatório
today = date.today()
end_year = today.year
# Start date será sempre a própria data em que o report está sendo executado
# start_date = "01.01.2025"
# =====================================================================================

for month in months:
    for day in days:
        try:
            
            # Data Inicial para começo da iteração :: começo do sistema
            # Considerar posting dates antigas
            
            dt = date(end_year,int(month),int(day))
            #dt_new = dt + timedelta(days=1)
            # Criar um filtro de datas para execução do script de recarga
            
            # WERKS representa as plantas que serão segregadas para execução do scripts
            # werks = ['E601','E60B','E60C','E60D','E60E','E60F','E60G','E60H','E60I','E60J','E60K','E60L','E60N',
            #         'E890','E89A','E89B','E89C','E89Z',
            #         'E901','E90A','E90B','E90C','E90D','E90E','E90F','E90G','E90H','E90I','E90J','E90K','E90L','E90M','E90N','E90P','E90R',
            #         'P60B','P60C','P60D','P60E','P60F','P60G','P60H','P60I','P60J','P60L',
            #         'P90A','P90C','P90F','P90G','P90I','P90J','P90K','P90L','P90M','P90N']
            
            # Como o nível de planta é muito granular, utilizar um filtro mais genérico
            werks = ['E60*', 'E89*', 'E90*', 'P60*', 'P90*']
            
            # Encerrar o looping de processamento caso a data de seleção seja maior do que a atual
            if dt > today:
                print("Data futura encontrada, encerrando processamento.")
                break
            
            # Iterando através das plantas
            for werk in werks:
                session = sap.login_to_s4hana()
                session.findById("wnd[0]").maximize()
                session.findById("wnd[0]/tbar[0]/okcd").text = "ZMM_QNTY_PIVB"
                session.findById("wnd[0]").sendVKey (0)
                session.findById("wnd[0]/usr/ctxtSO_WERKS-LOW").text = f"{werk}"
                session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = f"{f(dt.day)}.{f(dt.month)}.{end_year}"
                session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = f"{f(dt.day)}.{f(dt.month)}.{end_year}"
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
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{end_year}-{f(dt.month)}-{f(dt.day)} ZMM_QNTY_PIVB_{werk[:3]}_ALL.XLSX"
                session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
                session.findById("wnd[1]/tbar[0]/btn[11]").press()


                # Encerrar sessão do SAP
                os.system('taskkill /f /im saplogon.exe')
                os.system('taskkill /f /im saplogon.exe')
                os.system('taskkill /f /im cmd.exe')
                os.system('taskkill /f /im notepad.exe')
            print(f'{end_year}-{f(dt.month)}-{f(dt.day)} :: DADOS GRAVADOS!')
        
        except ValueError:
        # Pulando datas inválidas
            continue