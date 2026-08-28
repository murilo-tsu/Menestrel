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


def engdds_text_info_main():

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')
    
    with open(files_json_path, 'r', encoding='utf-8') as file:  # Alterei 'rb' para 'r' e adicionei encoding
        meta_arquivos = json.load(file)

    t0 = time.time()
    dia = datetime.datetime.today().day
    mes = datetime.datetime.today().month
    ano = datetime.datetime.today().year
    # Formatar data com dois dígitos no dia e mês
    dt = str(ano) + '-' + str(mes).zfill(2) + '-' + str(dia).zfill(2)
    # path_to_po = 'C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/Compras/'
    path_to_po = meta_arquivos['engdds_text_info.py']['path'][0]
    file = meta_arquivos['engdds_text_info.py']['files'][0]
    
    # Tentar diferentes combinações de arquivo
    possible_files = [
        f'{path_to_po}/{dt} {file}',  # Sem extensão (como aparece no Windows)
        f'{path_to_po}/{dt} {file}.xlsx',  # Com .xlsx
        f'{path_to_po}/{dt} {file}.XLSX',  # Com .XLSX
        f'{path_to_po}/{dt} {file}.xls',   # Com .xls
    ]
    
    latest_po = None
    for file_path in possible_files:
        if os.path.exists(file_path):
            print(f"Arquivo encontrado: {file_path}")
            latest_po = pd.read_excel(file_path, 
                    usecols = ['Purchasing Document', 'Purchasing Doc. Type','Price condition', 'Quantity IR'])
            break
    
    if latest_po is None:
        # Se não encontrou, listar arquivos disponíveis para debug
        print(f"Arquivos disponíveis em {path_to_po}:")
        for f in os.listdir(path_to_po):
            print(f"  - {f}")
        raise FileNotFoundError(f"Não foi possível encontrar o arquivo ZMM_PURDOCS_REPORT com data {dt}")
    
    latest_po = latest_po[(latest_po['Purchasing Doc. Type'] == 'YIMP')&\
                          (latest_po['Price condition'] == 'Provision')&\
                          (latest_po['Quantity IR'] ==  0.0)]
    
    purchase_orders_list = latest_po['Purchasing Document'].to_list()

    # path = 'C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/TXT/PO/'
    path = meta_arquivos['engdds_text_info.py']['path'][1]
    # final_path = 'C:/Users/murilo.ribeiro/OneDrive - EUROCHEM FERTILIZANTES TOCANTINS/03 - Data Insight/Hadoop/SAP4HANA/TXT/'
    final_path = meta_arquivos['engdds_text_info.py']['path'][2]
    arquivos = [filename.replace('.txt','') for filename in os.listdir(path)]
    
    for order in purchase_orders_list:
        session = sap.login_to_s4hana()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ME23N"
        session.findById("wnd[0]").sendVKey (0)
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        session.findById("wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").text = order
        session.findById("wnd[1]").sendVKey (0)
        
        try:
            try:
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0019/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000/btnDYN_4000-BUTTON").press()
                session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
            except:
                try:
                    session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0015/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000/btnDYN_4000-BUTTON").press()
                    session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()                    
                except:
                    session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000/btnDYN_4000-BUTTON").press()
                    session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
        except:
            pass

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

            if order in arquivos:
                session.findById("wnd[3]/tbar[0]/btn[11]").press()
                time.sleep(0.5)
                session.findById("wnd[2]/tbar[0]/btn[0]").press()
                time.sleep(0.5)
                session.findById("wnd[2]/tbar[0]/btn[5]").press()
                time.sleep(0.5)
                session.findById("wnd[0]/tbar[0]/btn[15]").press()
                session.findById("wnd[0]/tbar[0]/btn[15]").press()
                time.sleep(2)
                pass

            else:
                session.findById("wnd[3]/tbar[0]/btn[11]").press()
                time.sleep(0.5)
                session.findById("wnd[2]/tbar[0]/btn[0]").press()
                time.sleep(0.5)
                session.findById("wnd[0]/tbar[0]/btn[15]").press()
                session.findById("wnd[0]/tbar[0]/btn[15]").press()
                time.sleep(2)

            print(f"Textos do pedido {order} processados!")
            sap.limpar_processos()
            sap.cleanup()

        except Exception as erro:
            print(f'Erro ao buscar cabeçalho do pedido {order}')
            print(erro)
            sap.limpar_processos()
            sap.cleanup()
            pass

        time.sleep(1)

    arquivos = os.listdir(path)
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
    print(f'O script durou {t1-t0} segundos')

if __name__ == "__main__":
    engdds_text_info_main()