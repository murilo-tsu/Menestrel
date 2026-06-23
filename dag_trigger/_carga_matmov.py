from saplogin import SAPLogin
from datetime import date, timedelta
from Minio import MinioConnector
import pandas as pd
import json
import time

# Instaciador de SAP Session
sap = SAPLogin()

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)

def batch_upload():


    lotes_para_procurar =  [
    '*256899*', '*281659*', '*246973*', '*264242*', '*233447*',
    '*529047*', '*529049*', '*529235*', '*529039*', '*529050*',
    '*530404*', '*529046*', '*529045*', '*539248*', '*529236*',
    '*524711*', '*525184*', '*440349*', '*496192*', '*496216*',
    '*420080*', '*497301*', '*496183*', '*418684*', '*420077*',
    '*419945*', '*418678*', '*496190*', '*496217*', '*497304*',
    '*496201*', '*497300*', '*498316*', '*420156*', '*443858*',
    '*418612*', '*419968*', '*420224*', '*496219*', '*418614*',
    '*420074*', '*418664*', '*418158*', '*419967*', '*419949*',
    '*418159*', '*418665*', '*420073*', '*496165*', '*420157*',
    '*419930*', '*524679*', '*418613*', '*419946*', '*420075*',
    '*419950*', '*418663*', '*418629*', '*418160*', '*400288*',
    '*418676*', '*418161*'
        ]

    # "*INIT000024*", "*INIT000386*"
    session = sap.login_to_s4hana()
    for lote in lotes_para_procurar:

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "MB51"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/usr/ctxtCHARG-LOW").text = lote
        session.findById("wnd[0]/usr/ctxtCHARG-LOW").setFocus
        session.findById("wnd[0]/usr/ctxtCHARG-LOW").caretPosition = 7
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[48]").press()
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").select()
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{lote.replace('*','')}.XLSX"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 6
            session.findById("wnd[1]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        session.findById("wnd[0]/tbar[0]/btn[15]").press()
    sap.limpar_processos()

# CARREGAR O ESTOQUE

def get_mat_mov():
    minio = MinioConnector()
    with open('files.json','rb') as file:
        meta_arquivos = json.load(file)

    df_posting_dates = pd.read_excel("C:\Temp\PostingDateToUpload.xlsx")
    df_posting_dates = list(df_posting_dates['Posting Date'].astype(str).str[:10])
    try:
            
            hoje = date.today().weekday()
            domingo = (hoje == 6)

            # Definir datas dinâmicas para extração de dados
            if domingo:
                primeira_data = date.today() + timedelta(days=-45)
            else:
                primeira_data = date.today() + timedelta(days=-14)

            dates_range = pd.date_range(primeira_data, pd.Timestamp.now(), freq='D')
            #dt_comp = [date.strftime('%Y-%m-%d') for date in dates_range]
            dt_comp = df_posting_dates
            
            # werks = ['E60*', 'E89*', 'E90*', 'P60*', 'P90*']
            werks = meta_arquivos['engdds_estoque.py']['werks']

            # Data Inicial para começo da iteração :: começo do sistema
            # Considerar posting dates antigas
            for day in dt_comp:
                dt = date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2]))

                # Iterando através das plantas declaradas em WERKS
                try:
                
                    for werk in werks:
                        session = sap.login_to_s4hana()
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
                        #session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "DATAINSIGHTS"
                        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/DATAINSIGHT"
                        session.findById("wnd[0]/usr/ctxtP_DISVAR").setFocus()
                        session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
                        session.findById("wnd[0]/tbar[1]/btn[8]").press()

                        try:
                            session.findById("wnd[1]/usr/btnBUTTON_1").press()
                        except:
                            pass

                        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("SHOWBUT")
                        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("TECHNAM")
                        sap.kill_excel()
                        with sap.export_watchdog(180):
                            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
                            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")

                            try:
                                session.findById("wnd[1]/tbar[0]/btn[0]").press()
                            except:
                                pass

                            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
                            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
                            # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Estoque"
                            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_estoque.py']['path'][0]
                            # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{dt.year}-{f(dt.month)}-{f(dt.day)} ZMM_QNTY_PIVB_{werk[:3]}_ALL.XLSX"
                            nome_arquivo = f"{dt.year}-{f(dt.month)}-{f(dt.day)} {meta_arquivos['engdds_estoque.py']['files'][0]}{werk[:3]}{meta_arquivos['engdds_estoque.py']['sufixo_files']}"
                            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
                            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
                            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
                            session.findById("wnd[1]/tbar[0]/btn[11]").press()


                        # Encerrar sessão do SAP
                        sap.limpar_processos()
                        time.sleep(5)
                        arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][0], nome_arquivo)
                        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)
                        sap.cleanup()

                    print(f'{dt.year}-{f(dt.month)}-{f(dt.day)} :: DADOS GRAVADOS!')
                
                except Exception as erro:
                    print(f"Erro ao processar dados na data {dt.year}-{f(dt.month)}-{f(dt.day)}")
                    print(f"Mensagem de erro :: {str(erro)}")
                    sap.limpar_processos()
                    sap.cleanup()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZMM_QNTY_PIVB :: {str(e)}')
        # Encerrar sessão do SAP
        sap.limpar_processos()
        sap.cleanup()

if __name__ == '__main__':
    what_to_do = 'batch_upload'
    if what_to_do == 'get_mat_mov':
        get_mat_mov()
    else:
        get_mat_mov()