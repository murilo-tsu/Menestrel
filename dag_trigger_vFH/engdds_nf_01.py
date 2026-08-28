from saplogin import SAPLogin
from datetime import date
from dateutil.relativedelta import relativedelta
from Minio import MinioConnector
import json
import os


def f(num):
    return f"0{num}" if num < 10 else str(num)


# Instanciador de SAP Session
sap = SAPLogin()


def engdds_nf_01_main():

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, 'files.json')

    with open(files_json_path, 'r', encoding='utf-8') as file:
        meta_arquivos = json.load(file)

    # === Datas ===
    hoje = date.today()

    # Mês passado (M-1)
    data_m1 = hoje.replace(day=1) - relativedelta(months=0)
    ano_m1 = str(data_m1.year)
    mes_m1 = f(data_m1.month)

    # Mês passado - 1 (M-2)
    data_m2 = hoje.replace(day=1) - relativedelta(months=1)
    ano_m2 = str(data_m2.year)
    mes_m2 = f(data_m2.month)

    # Login no SAP
    session = sap.login_to_s4hana()

    try:
        #============================================================R$ REALR $=====================================================================

        # === Transação SAP ===
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nf.01"
        session.findById("wnd[0]").sendVKey(0)

        session.findById(
            "wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/"
            "ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/radBILAGRID"
        ).select()

        session.findById("wnd[0]/usr/ctxtSD_KTOPL-LOW").text = "CAEC"
        session.findById("wnd[0]/usr/ctxtSD_SAKNR-LOW").text = ""
        session.findById("wnd[0]/usr/ctxtSD_BUKRS-LOW").text = "E900"
        session.findById("wnd[0]/usr/ctxtSD_GSB_S-LOW").text = ""
        session.findById("wnd[0]/usr/ctxtSD_CURTP").text = "10" # Real
        session.findById("wnd[0]/usr/ctxtSD_RLDNR-LOW").text = "0L"

        # === Campos de período ===
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/ctxtBILAVERS").text = "zabr"

        # Exercício / mês base (M-1)
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtBILBJAHR").text = ano_m1
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtB-MONATE-LOW").text = mes_m1
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtB-MONATE-HIGH").text = mes_m1

        # Exercício / mês comparação (M-2)
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtBILVJAHR").text = ano_m2
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtV-MONATE-LOW").text = mes_m2
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtV-MONATE-HIGH").text = mes_m2
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/ctxtBILAGVAR").text = "/P&L"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        # === Arquivo ===
        caminho_arquivo = meta_arquivos['engdds_nf_01.py']['path']
        nome_base = meta_arquivos['engdds_nf_01.py']['files'][0]
        nome_arquivo = f"{ano_m1}_{mes_m1}_{nome_base}"

        # === Exportação ===
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # === Upload MinIO ===
        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)

        #=====================================================================$ DOLAR $=====================================================================

        # === Transação SAP ===
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nf.01"
        session.findById("wnd[0]").sendVKey(0)

        session.findById(
            "wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/"
            "ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/radBILAGRID"
        ).select()

        session.findById("wnd[0]/usr/ctxtSD_KTOPL-LOW").text = "CAEC"
        session.findById("wnd[0]/usr/ctxtSD_SAKNR-LOW").text = ""
        session.findById("wnd[0]/usr/ctxtSD_BUKRS-LOW").text = "E900"
        session.findById("wnd[0]/usr/ctxtSD_GSB_S-LOW").text = ""
        session.findById("wnd[0]/usr/ctxtSD_CURTP").text = "30" # Dólar
        session.findById("wnd[0]/usr/ctxtSD_RLDNR-LOW").text = "0L"

        # === Campos de período ===
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/ctxtBILAVERS").text = "zabr"

        # Exercício / mês base (M-1)
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtBILBJAHR").text = ano_m1
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtB-MONATE-LOW").text = mes_m1
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtB-MONATE-HIGH").text = mes_m1

        # Exercício / mês comparação (M-2)
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtBILVJAHR").text = ano_m2
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtV-MONATE-LOW").text = mes_m2
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/txtV-MONATE-HIGH").text = mes_m2
        session.findById("wnd[0]/usr/tabsTABSTRIP_TABBL1/tabpUCOM1/""ssub%_SUBSCREEN_TABBL1:RFBILA00:0001/ctxtBILAGVAR").text = "/P&L"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
        except:
            pass

        # === Arquivo ===
        caminho_arquivo = meta_arquivos['engdds_nf_01.py']['path']
        nome_base = meta_arquivos['engdds_nf_01.py']['files'][1]
        nome_arquivo = f"{ano_m1}_{mes_m1}_{nome_base}"

        # === Exportação ===
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = caminho_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # === Upload MinIO ===
        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, 'tmp', nome_arquivo)

        sap.encerrar_sap()

    except Exception as e:
        print(f'Erro ao exportar dados do relatório NF_01 :: {str(e)}')
        sap.encerrar_sap()


if __name__ == "__main__":
    engdds_nf_01_main()
