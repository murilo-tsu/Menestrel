#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#:::::::::::::::::::::::ADICIONAR NA EXTRAÇÃO ::::::::::::::::::::::::
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

from saplogin import SAPLogin
from datetime import date, timedelta
from Minio import MinioConnector
import pandas as pd
import json
import time
import os

def f(num):
    return f"0{num}" if num < 10 else str(num)

# Instanciador de SAP Session
sap = SAPLogin()

def engdds_ativos_main():

    minio = MinioConnector()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, "files.json")

    with open(files_json_path, "r", encoding="utf-8") as file:
        meta_arquivos = json.load(file)

    session = sap.login_to_s4hana_pt()

    try:
        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        # ==========================
        # ::::::::::IW28::::::::::::
        # ==========================

        session.findById("wnd[0]/tbar[0]/okcd").text = "/niw28"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/ctxtVARIANT").setFocus()
        session.findById("wnd[0]/usr/ctxtVARIANT").caretPosition = 9
        session.findById("wnd[0]").sendVKey(4)

        session.findById("wnd[1]/usr").verticalScrollbar.position = 1
        session.findById("wnd[1]/usr").verticalScrollbar.position = 2
        session.findById("wnd[1]/usr").verticalScrollbar.position = 3

        session.findById("wnd[1]/usr/lbl[1,18]").setFocus()
        session.findById("wnd[1]/usr/lbl[1,18]").caretPosition = 8
        session.findById("wnd[1]").sendVKey(2)

        session.findById("wnd[0]/usr/ctxtSTRNO-LOW").text = "e90*"
        session.findById("wnd[0]/usr/ctxtDATUV").text = "01.01.2025"
        session.findById("wnd[0]/usr/ctxtDATUB").text = "24.02.2026"

        session.findById("wnd[0]/usr/ctxtDATUB").setFocus()
        session.findById("wnd[0]/usr/ctxtDATUB").caretPosition = 10

        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/mbar/menu[0]/menu[6]").select()

        session.findById("wnd[1]/usr/txtRIHEA-KEYCOL").text = "0"
        session.findById("wnd[1]").sendVKey(0)

        session.findById(
            "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/"
            "sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[0,0]"
        ).select()

        session.findById(
            "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/"
            "sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[0,0]"
        ).setFocus()

        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        caminho_arquivo = meta_arquivos["engdds_estoque.py"]["path"][8]
        nome_arquivo = (
            f"{date.today().strftime('%d.%m.%Y')}_"
            f"{meta_arquivos['engdds_estoque.py']['files'][11]}"
        )

        sap.limpar_processos()

        arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
        minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

        sap.encerrar_sap()

        # ==========================
        # ::::::::::IW37N:::::::::::
        # ==========================

        minio = MinioConnector()

        with open(files_json_path, "r", encoding="utf-8") as file:
            meta_arquivos = json.load(file)

        session = sap.login_to_s4hana_pt()

        try:
            try:
                session.FindById("wnd[0]").SendVKey(0)
            except:
                pass

            session.findById("wnd[0]/tbar[0]/okcd").text = "iw37n"
            session.findById("wnd[0]").sendVKey(0)

            session.findById(
                "wnd[0]/usr/tabsTABSTRIP_TABBLOCK1/tabpS_TAB9"
            ).select()

            session.findById(
                "wnd[0]/usr/tabsTABSTRIP_TABBLOCK1/tabpS_TAB9/"
                "ssub%_SUBSCREEN_TABBLOCK1:RI_ORDER_OPERATION_LIST:1900/"
                "ctxtSP_VARI"
            ).setFocus()

            session.findById(
                "wnd[0]/usr/tabsTABSTRIP_TABBLOCK1/tabpS_TAB9/"
                "ssub%_SUBSCREEN_TABBLOCK1:RI_ORDER_OPERATION_LIST:1900/"
                "ctxtSP_VARI"
            ).caretPosition = 10

            session.findById("wnd[0]").sendVKey(4)

            session.findById("wnd[1]/usr").verticalScrollbar.position = 1
            session.findById("wnd[1]/usr").verticalScrollbar.position = 2
            session.findById("wnd[1]/usr").verticalScrollbar.position = 3

            session.findById("wnd[1]/usr/lbl[1,22]").setFocus()
            session.findById("wnd[1]/usr/lbl[1,22]").caretPosition = 3
            session.findById("wnd[1]").sendVKey(2)

            session.findById(
                "wnd[0]/usr/tabsTABSTRIP_TABBLOCK1/tabpS_TAB1"
            ).select()

            session.findById(
                "wnd[0]/usr/tabsTABSTRIP_TABBLOCK1/tabpS_TAB1/"
                "ssub%_SUBSCREEN_TABBLOCK1:RI_ORDER_OPERATION_LIST:1100/"
                "ctxtS_TPLNR-LOW"
            ).text = "e90*"

            session.findById(
                "wnd[0]/usr/tabsTABSTRIP_TABBLOCK1/tabpS_TAB1/"
                "ssub%_SUBSCREEN_TABBLOCK1:RI_ORDER_OPERATION_LIST:1100/"
                "ctxtS_DATUM-LOW"
            ).text = "01.01.2025"

            session.findById(
                "wnd[0]/usr/tabsTABSTRIP_TABBLOCK1/tabpS_TAB1/"
                "ssub%_SUBSCREEN_TABBLOCK1:RI_ORDER_OPERATION_LIST:1100/"
                "ctxtS_DATUM-HIGH"
            ).text = "31.12.2026"

            session.findById("wnd[0]/tbar[1]/btn[8]").press()
            session.findById("wnd[0]/mbar/menu[0]/menu[6]").select()

            session.findById("wnd[1]/usr/txtRIHEA-KEYCOL").text = "0"
            session.findById("wnd[1]").sendVKey(0)

            session.findById(
                "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/"
                "sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[0,0]"
            ).select()

            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/tbar[0]/btn[0]").press()

            caminho_arquivo = meta_arquivos["engdds_estoque.py"]["path"][8]
            nome_arquivo = (
                f"{date.today().strftime('%d.%m.%Y')}_"
                f"{meta_arquivos['engdds_estoque.py']['files'][11]}"
            )

            sap.limpar_processos()

            arquivo = minio.buffer_creator(caminho_arquivo, nome_arquivo)
            minio.upload_from_bytesIO(arquivo, "tmp", nome_arquivo)

            sap.encerrar_sap()

        except Exception as e:
            print(f"Erro ao exportar dados do relatório IW37N :: {str(e)}")
            sap.encerrar_sap()

    except Exception as e:
        print(f"Erro ao exportar dados do relatório IW28 :: {str(e)}")
        sap.encerrar_sap()

    time.sleep(10)


if __name__ == "__main__":
    engdds_ativos_main()