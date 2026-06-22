from saplogin import SAPLogin
from datetime import date, timedelta
from Minio import MinioConnector
import pandas as pd
import json
import time
import os

def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)

# Instaciador de SAP Session
sap = SAPLogin()

def engdds_estoque_main():
    
    minio = MinioConnector()
    with open('files.json','rb') as file:
        meta_arquivos = json.load(file)

    session = sap.login_to_s4hana()

    try:
        
        hoje = date.today().weekday()
        domingo = (hoje == 6)

        # Definir datas dinâmicas para extração de dados
        if domingo:
            primeira_data = date.today() + timedelta(days=-45)
        else:
            primeira_data = date.today() + timedelta(days=-3)

        dates_range = pd.date_range(primeira_data, pd.Timestamp.now(), freq='D')
        dt_comp = [date.strftime('%Y-%m-%d') for date in dates_range]
        
        # werks = ['E60*', 'E89*', 'E90*', 'P60*', 'P90*']
        werks = meta_arquivos['engdds_estoque.py']['werks']

        # Data Inicial para começo da iteração :: começo do sistema
        # Considerar posting dates antigas
        for day in dt_comp:
            dt = date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2]))

            # Iterando através das plantas declaradas em WERKS
            try:
            
                for werk in werks:
                    session.findById("wnd[0]/tbar[0]/okcd").text = "/nZMM_QNTY_PIVB"
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


                    time.sleep(1)
                    arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][0], nome_arquivo)
                    minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)

                print(f'{dt.year}-{f(dt.month)}-{f(dt.day)} :: DADOS GRAVADOS!')

            except Exception as erro:
                print(f"Erro ao processar dados na data {dt.year}-{f(dt.month)}-{f(dt.day)}")
                print(f"Mensagem de erro :: {str(erro)}")
                sap.limpar_processos()
                sap.cleanup()
                session = sap.login_to_s4hana()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZMM_QNTY_PIVB :: {str(e)}')
        sap.limpar_processos()
        sap.cleanup()
        session = sap.login_to_s4hana()

    now = time.localtime()
    end_day = f(now.tm_mday)
    end_month = f(now.tm_mon)
    end_year = f(now.tm_year)

    try:
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZMB5T"
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
        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").select()
            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass

            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Estoque"
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_estoque.py']['path'][0]
            nome_arquivo = f"{end_year}-{end_month}-{end_day} {meta_arquivos['engdds_estoque.py']['files'][1]}"
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 21
            session.findById("wnd[1]/tbar[0]/btn[11]").press()

        arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][0], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)

    except Exception as e:
        print(f'Erro ao exportar dados do relatório ZMB5T :: {str(e)}')
        sap.limpar_processos()
        sap.cleanup()
        session = sap.login_to_s4hana()

    # Extrair MCHB
    try:
        try:
            session.FindById("wnd[0]").SendVKey (0)
        except:
            pass

        now = time.localtime()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nSE16N"
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
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,1]").text = f"{now.tm_year-1}"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").setFocus()
        session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").press()
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "1"
        session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-HIGH[2,0]").text = "12"
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        try:
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnOPTION[1,8]").setFocus()
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnOPTION[1,8]").press()
            session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").currentCellRow = 5
            session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").selectedRows = "5"
            session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").doubleClickCurrentCell()
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").columns.elementAt(1).width = 2
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/ctxtGS_SELFIELDS-LOW[2,8]").text = "0"
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/ctxtGS_SELFIELDS-LOW[2,8]").setFocus()
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/ctxtGS_SELFIELDS-LOW[2,8]").caretPosition = 1
            session.findById("wnd[0]").sendVKey (0)
            session.findById("wnd[0]/tbar[1]/btn[8]").press()
            session.findById("wnd[0]/tbar[1]/btn[8]").press()
        except:
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 12
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC").verticalScrollbar.position = 15
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnOPTION[1,2]").setFocus()
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnOPTION[1,2]").press()
            session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").currentCellRow = 5
            session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").selectedRows = "5"
            session.findById("wnd[1]/usr/cntlGRID/shellcont/shell").doubleClickCurrentCell()
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").setFocus()
            session.findById("wnd[0]/usr/tblSAPLSE16NSELFIELDS_TC/btnPUSH[4,2]").press()
            session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").text = "0"
            session.findById("wnd[1]/usr/tblSAPLSE16NMULTI_TC/ctxtGS_MULTI_SELECT-LOW[1,0]").caretPosition = 1
            session.findById("wnd[1]/tbar[0]/btn[8]").press()
            session.findById("wnd[0]/tbar[1]/btn[8]").press()

        sap.kill_excel()
        with sap.export_watchdog(180):
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
            session.findById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").selectContextMenuItem ("&XXL")
            try:
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
            except:
                pass
            # 2025-11-18: Remover a dependência do upload para o sharepoint e mapear arquivos através de um json
            # DEPRECADO --------------------------------------------------------------------------------------------------------------------------------------------------------
            # session.findById("wnd[1]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\Tabelas"
            session.findById("wnd[1]/usr/ctxtDY_PATH").text = meta_arquivos['engdds_estoque.py']['path'][1]
            # session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "MCHB.XLSX"
            nome_arquivo = meta_arquivos['engdds_estoque.py']['files'][2]
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
            session.findById("wnd[1]/tbar[0]/btn[11]").press()
        
        arquivo = minio.buffer_creator(meta_arquivos['engdds_estoque.py']['path'][1], nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)

    except Exception as e:
        print(f'Erro ao exportar dados do relatório SE16N :: MCHB :: {str(e)}')
        sap.limpar_processos()
        sap.cleanup()

    # Limpeza final única, ao fim de toda a execução
    sap.limpar_processos()
    sap.cleanup()
    time.sleep(1)

if __name__ == "__main__":
    engdds_estoque_main()
