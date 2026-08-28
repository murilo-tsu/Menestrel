# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# IMPORTAR BIBLIOTECAS
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Bibliotecas :: Gerais
from dateutil.relativedelta import relativedelta
import datetime
import json
import time
import os

# Bibliotecas :: Específicas
from saplogin import SAPLogin
from Minio import MinioConnector


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INSTANCIANDO VARIÁVEIS DE AMBIENTE :: SAP
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Instanciador de SAP Session
sap = SAPLogin()


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# FUNÇÕES AUXILIARES
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def fmt(num: int) -> str:
    """
    Normaliza números menores que 10 com zero à esquerda.

    Exemplo:
        1 -> "01"
        10 -> "10"
    """
    return f"0{num}" if num < 10 else str(num)


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INICIANDO PROCESSAMENTO :: EXTRAÇÃO SAP4HANA BOM
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def engdds_bom_main():
    """
    Executa a extração do relatório ZPP_BOMREP no SAP S/4HANA.

    Fluxo:
        1. Carrega os metadados do files.json.
        2. Calcula o período do relatório.
        3. Acessa a transação ZPP_BOMREP.
        4. Parametriza planta, tipo de lista técnica e período.
        5. Aplica o layout /DATAINSIGHT.
        6. Exporta o relatório em XLSX para a pasta local da VM.
        7. Envia o arquivo gerado para o bucket tmp do MinIO.
    """
    print(" ---------- Iniciando extração SAP4HANA :: BOM ---------- ")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # INSTANCIANDO CONECTOR MINIO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print("Instanciando conector MinIO...")

    minio = MinioConnector()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # CARREGANDO METADADOS DOS ARQUIVOS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print("Carregando metadados do arquivo files.json...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, "files.json")

    with open(files_json_path, "r", encoding="utf-8") as file:
        meta_arquivos = json.load(file)

    print("Metadados carregados com sucesso.")

    try:
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # DEFININDO DATAS PARA EXTRAÇÃO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Calculando período de extração do relatório BOM...")

        today = datetime.date.today()

        end_year_bom = fmt(today.year)
        end_month_bom = fmt(today.month)
        end_day_bom = fmt(today.day)

        # Regra atual:
        #     - Data inicial: primeiro dia do mês atual.
        #     - Data final: primeiro dia do mês atual + 12 meses.
        first_date_dt = datetime.datetime(today.year, today.month, 1)
        last_date_dt = first_date_dt + relativedelta(months=+12)

        first_date = first_date_dt.strftime("%d.%m.%Y")
        last_date = last_date_dt.strftime("%d.%m.%Y")

        print(
            f"Período definido para o relatório ZPP_BOMREP_E900: "
            f"{first_date} até {last_date}"
        )

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # DEFININDO CAMINHO E NOME DO ARQUIVO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        export_path = meta_arquivos["engdds_bom.py"]["path"]
        export_name = (
            f"{end_year_bom}-{end_month_bom}-{end_day_bom} "
            f"{meta_arquivos['engdds_bom.py']['files'][0]}"
        )

        print(f"Pasta destino configurada: {export_path}")
        print(f"Arquivo configurado para exportação: {export_name}")

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # LOGIN E ACESSO À TRANSAÇÃO ZPP_BOMREP
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Realizando login no SAP S/4HANA...")

        session = sap.login_to_s4hana()

        print("Login no SAP S/4HANA realizado com sucesso.")

        # Segurança ao primeiro Enter.
        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Acessando transação ZPP_BOMREP...")

        session.findById("wnd[0]/tbar[0]/okcd").text = "/NZPP_BOMREP"
        session.findById("wnd[0]").sendVKey(0)

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # PARAMETRIZAÇÃO DO RELATÓRIO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Parametrizando relatório ZPP_BOMREP...")

        session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "E90*"
        session.findById("wnd[0]/usr/ctxtS_STLAN-LOW").text = "1"
        session.findById("wnd[0]/usr/ctxtS_DATUV-LOW").text = first_date
        session.findById("wnd[0]/usr/ctxtS_VAL_TO-LOW").text = last_date
        session.findById("wnd[0]/usr/ctxtP_VARI").setFocus()

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # APLICAÇÃO DO LAYOUT
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Aplicando layout /DATAINSIGHT...")

        session.findById("wnd[0]/usr/ctxtP_VARI").text = "/DATAINSIGHT"

        # Layout alternativo mantido como referência.
        # session.findById("wnd[0]/usr/ctxtP_VARI").text = "/SALITRE1"

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # EXECUÇÃO DO RELATÓRIO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Executando relatório ZPP_BOMREP...")

        session.findById("wnd[0]/usr/txtS_STLAL-LOW").setFocus()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # EXPORTAÇÃO DO RELATÓRIO PARA EXCEL
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Iniciando exportação do relatório para XLSX...")

        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        print(f"Exportando arquivo para: {export_path}")
        print(f"Nome do arquivo: {export_name}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = export_path
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = export_name
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 9
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print(f"Arquivo salvo localmente com sucesso: {export_name}")

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # UPLOAD DO ARQUIVO PARA O MINIO :: BUCKET TMP
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print(f"Criando buffer do arquivo exportado: {export_name}")

        arquivo = minio.buffer_creator(
            export_path,
            export_name,
        )

        print(f"Enviando arquivo para o MinIO: tmp/{export_name}")

        minio.upload_from_bytesIO(
            arquivo,
            "tmp",
            export_name,
        )

        print(f"Upload para MinIO concluído com sucesso: tmp/{export_name}")

        print(" ---------- Extração SAP4HANA :: BOM concluída com sucesso! ---------- ")

    except Exception as e:
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # TRATAMENTO DE ERRO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print(f"Erro ao gerar/baixar relatório ZPP_BOMREP_E900: {str(e)}")

        raise

    finally:
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # ENCERRAMENTO DA SESSÃO SAP
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Encerrando sessão SAP...")

        try:
            sap.encerrar_sap()
        except:
            pass

        time.sleep(10)


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# EXECUÇÃO DIRETA DO SCRIPT
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if __name__ == "__main__":
    engdds_bom_main()