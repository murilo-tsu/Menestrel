# BIBLIOTECAS PRINCIPAIS
from saplogin import SAPLogin
from Minio import MinioConnector
import pandas as pd
import datetime
import json
import time
import os
import csv
from pathlib import Path
sap = SAPLogin()
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

# FUNÇÃO: NORMALIZA OS NÚMEROS PARA FORMATO TEXTO
def f(num):
    """Função f() normaliza os números em formato texto"""
    return f"0{num}" if num < 10 else str(num)
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

# FUNÇÃO: ABRE OS DETALHES DA ORDEM DE COMPRA
def detalhe_ordem_compra(session):
    """
    Abrir os detalhes do cabeçalho da ordem de compra
    """
    try:
        try:
            session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000/btnDYN_4000-BUTTON").press()
        except:
            try:
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000/btnDYN_4000-BUTTON").press()                    
            except:
                try:
                    session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000/btnDYN_4000-BUTTON").press()
                except:
                    session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0019/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000/btnDYN_4000-BUTTON").press()
    except:
        pass
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

# FUNÇÃO: NAVEGA ATÉ ONDE ESTÃO OS DETALHES DA ORDEM DE COMPRA
def navega_ordem_compra(session):
    """
    Navegar até a aba em que estão os detalhes da ordem de compra
    """
    try:
        try:
            session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
        except:
            try:
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()                    
            except:
                try:
                    session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
                except:
                    session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0019/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
    except:
        pass
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------- MAIN ---------------------------------------------------------------------------------
# FUNÇÃO: EXECUÇÃO PRINCIPAL DA LÓGICA DE EXTRAÇÃO
def engdds_text_info_main():

    minio = MinioConnector()
    with open('files.json', 'rb') as file:
        meta_arquivos = json.load(file)

    t0 = time.time()
    dia = f(datetime.datetime.today().day)
    mes = f(datetime.datetime.today().month)
    ano = f(datetime.datetime.today().year)
    dt = ano + '-' + mes + '-' + dia
    # path_to_po = 'C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Compras/'
    path_to_po = meta_arquivos['engdds_text_info.py']['path'][0]
    file = meta_arquivos['engdds_text_info.py']['files'][0]
    path_to_lastest_po = f'{path_to_po}/{dt} {file}'
    latest_po = pd.read_excel(path_to_lastest_po, 
                usecols = ['Purchasing Document', 'Purchasing Doc. Type','Price condition', 'Quantity IR'])
    
    # latest_po = latest_po[(latest_po['Purchasing Doc. Type'] == 'YIMP')&\
    #                       (latest_po['Price condition'] == 'Provision')&\
    #                       (latest_po['Quantity IR'] ==  0.0)]
    latest_po = latest_po[(latest_po['Purchasing Doc. Type'] == 'YIMP')&(latest_po['Price condition'] == 'Provision')]
    
    purchase_orders_list = latest_po['Purchasing Document'].to_list()
    purchase_orders_list = list(set(purchase_orders_list))

    # path = 'C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/TXT/PO/'
    path = meta_arquivos['engdds_text_info.py']['path'][1]
    # final_path = 'C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/TXT/'
    final_path = meta_arquivos['engdds_text_info.py']['path'][2]
    arquivos = [filename.replace('.txt','') for filename in os.listdir(path)]  

    session = sap.login_to_s4hana()
    for order in purchase_orders_list:
        
        session.findById("wnd[0]/tbar[0]/okcd").text = "ME23N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").text = order
        session.findById("wnd[1]").sendVKey (0)

        # Checar se os detalhes do cabeçalho da ordem estão abertos
        try:
            session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
        except:
                try:
                    session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
                except:
                     try:
                         session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
                     except:
                         detalhe_ordem_compra(session)
                         navega_ordem_compra(session)
                         
        try:
            session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
        except:
            session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()


        try:
            try:
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1230/subTEXTS:SAPLMMTE:0100/cntlTEXT_TYPES_0100/shell").selectedNode = "F21"
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1230/subTEXTS:SAPLMMTE:0100/cntlTEXT_TYPES_0100/shell").topNode = "F17"
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1230/subTEXTS:SAPLMMTE:0100/subEDITOR:SAPLMMTE:0101/cntlTEXT_EDITOR_0101/shellcont/shell").setSelectionIndexes (14,14)
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1230/subTEXTS:SAPLMMTE:0100/subEDITOR:SAPLMMTE:0101/cntlTEXT_EDITOR_0101/shellcont/shell").doubleClick() 
            except:
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1230/subTEXTS:SAPLMMTE:0100/cntlTEXT_TYPES_0100/shell").selectedNode = "F21"
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1230/subTEXTS:SAPLMMTE:0100/cntlTEXT_TYPES_0100/shell").topNode = "F18"
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1230/subTEXTS:SAPLMMTE:0100/subEDITOR:SAPLMMTE:0101/cntlTEXT_EDITOR_0101/shellcont/shell").setSelectionIndexes (0,0)
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1230/subTEXTS:SAPLMMTE:0100/subEDITOR:SAPLMMTE:0101/cntlTEXT_EDITOR_0101/shellcont/shell").doubleClick()                
        

            session.findById("wnd[0]/mbar/menu[0]/menu[4]").select()
            session.findById("wnd[1]/usr/radITCTK-TDASCII").select()
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[2]").sendVKey (4)
            # session.findById("wnd[3]/usr/ctxtDY_PATH").text = r"C:\Users\murilo.ribeiro\OneDrive - EUROCHEM FERTILIZANTES TOCANTINS\03 - Data Insight\Hadoop\SAP4HANA\TXT\PO"
            session.findById("wnd[3]/usr/ctxtDY_PATH").text = path
            session.findById("wnd[3]/usr/ctxtDY_FILENAME").text = f"{order}.txt"
            
            if order not in arquivos:
                session.findById("wnd[3]/tbar[0]/btn[11]").press()
                session.findById("wnd[2]/tbar[0]/btn[0]").press()
                try:
                    session.findById("wnd[2]/tbar[0]/btn[5]").press()
                except:
                    pass
                session.findById("wnd[0]/tbar[0]/btn[15]").press()
                session.findById("wnd[0]/tbar[0]/btn[15]").press()
            print(f"Textos do pedido {order} processados!")
            time.sleep(1)

        except Exception as erro:
            print(f'Erro ao buscar cabeçalho do pedido {order}')
            sap.limpar_processos()
            sap.cleanup()
            time.sleep(5)
            session = sap.login_to_s4hana()
            time.sleep(1)
            pass
        
        time.sleep(0.2)

    arquivos = [filename.replace('.txt','') for filename in os.listdir(path)]
    arquivos = os.listdir(path)
    sap.limpar_processos()
    sap.cleanup()

    with open(f'{final_path}/purchase_order_header_text.csv', mode = 'w', newline='') as purchase_order_header_text:
        writer = csv.writer(purchase_order_header_text)
        writer.writerow(['PURCHASE_ORDER','PRICING_FORMULA_TXT'])
        for arquivo in arquivos:

            with open(f'{path}/{arquivo}', mode = 'r',encoding='utf-8-sig') as arquivos_txt:
                info = arquivos_txt.read().strip('')
                writer.writerow([arquivo, info])
    
    arquivo = minio.buffer_creator(final_path, meta_arquivos['engdds_text_info.py']['files'][1])
    minio.upload_from_bytesIO(arquivo,'tmp',meta_arquivos['engdds_text_info.py']['files'][1])
    t1 = time.time()
    print(f'O script durou {round((t1-t0)/60,2)} minutos')

if __name__ == "__main__":
    engdds_text_info_main()