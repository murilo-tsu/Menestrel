# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# IMPORTAR BIBLIOTECAS
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Bibliotecas :: Gerais
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
# INICIANDO PROCESSAMENTO :: EXTRAÇÃO SAP4HANA FATURAMENTO
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def engdds_faturamento_main():
    """
    Executa a extração do relatório de faturamento no SAP S/4HANA.

    Fluxo:
        1. Carrega os metadados do files.json.
        2. Define o intervalo dinâmico dos últimos 32 dias.
        3. Acessa a transação ZSD_PIVB.
        4. Parametriza a extração para a organização E900.
        5. Exporta o relatório em XLSX para a pasta TEMP da VM.
        6. Envia o arquivo gerado para o bucket tmp do MinIO.
    """
    print(" ---------- Iniciando extração SAP4HANA :: Faturamento ---------- ")

    minio = MinioConnector()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # CARREGANDO METADADOS DOS ARQUIVOS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print("Carregando metadados do arquivo files.json...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, "files.json")

    with open(files_json_path, "r", encoding="utf-8") as file:
        meta_arquivos = json.load(file)

    pasta_destino = meta_arquivos["engdds_faturamento.py"]["path"]
    nome_arquivo = meta_arquivos["engdds_faturamento.py"]["files"][0]

    print(f"Pasta destino configurada: {pasta_destino}")
    print(f"Arquivo configurado para exportação: {nome_arquivo}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # DEFININDO INTERVALO DINÂMICO DE DATAS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Regra atual:
    #     - Extrai os últimos 32 dias até a data atual.
    print("Definindo intervalo de datas para extração...")

    now = time.localtime()

    start_date = datetime.datetime(
        now.tm_year,
        now.tm_mon,
        now.tm_mday,
    ) + datetime.timedelta(days=-32)

    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year

    end_day = now.tm_mday
    end_month = now.tm_mon
    end_year = now.tm_year

    data_inicial_sap = f"{start_day}.{start_month}.{start_year}"
    data_final_sap = f"{end_day}.{end_month}.{end_year}"

    print(f"Período de extração definido: {data_inicial_sap} até {data_final_sap}")

    try:
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # LOGIN E ACESSO À TRANSAÇÃO ZSD_PIVB
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Realizando login no SAP S/4HANA...")

        session = sap.login_to_s4hana()

        print("Login no SAP S/4HANA realizado com sucesso.")

        try:
            session.FindById("wnd[0]").SendVKey(0)
        except:
            pass

        print("Acessando transação ZSD_PIVB...")

        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "ZSD_PIVB"
        session.findById("wnd[0]").sendVKey(0)

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # PARAMETRIZAÇÃO DO RELATÓRIO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Parametrizando relatório ZSD_PIVB...")

        session.findById("wnd[0]/usr/ctxtP_DISVAR").text = "/ZSOP_ECFH"
        session.findById("wnd[0]/usr/ctxtSO_VKORG-LOW").text = "E900"

        print("Aplicando filtro de tipo de documento: ZSFO...")

        session.findById("wnd[0]/usr/btn%_SO_AUART_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[16]").press()
        session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA").Select()
        session.findById(
            "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/"
            "ssubSCREEN_HEADER:SAPLALDB:3010/"
            "tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]"
        ).Text = "ZSFO"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        print("Aplicando intervalo de datas no relatório...")

        session.findById("wnd[0]/usr/ctxtFB_FKDAT-LOW").text = data_inicial_sap
        session.findById("wnd[0]/usr/ctxtFB_FKDAT-HIGH").text = data_final_sap
        session.findById("wnd[0]/usr/ctxtP_DISVAR").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # CONFIRMAÇÃO DE POP-UPS
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Verificando existência de pop-ups de confirmação...")

        try:
            session.findById("wnd[1]/usr/btnBUTTON_1").press()
            print("Pop-up confirmado.")
        except:
            print("Nenhum pop-up de confirmação encontrado.")

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # PREPARAÇÃO DA GRADE PARA EXPORTAÇÃO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Preparando grade do relatório para exportação...")

        session.findById("wnd[0]/shellcont/shell").pressToolbarButton("SHOWBUT")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton("TECHNAM")
        session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")

        # ----------------------------------------------------------------------
        # Opção 1 :: TXT
        # ----------------------------------------------------------------------
        # Não utilizada no momento.
        #
        # session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&PC")

        # ----------------------------------------------------------------------
        # Opção 2 :: XLSX
        # ----------------------------------------------------------------------
        # Exportação ativa utilizada pelo fluxo atual.
        print("Selecionando exportação em XLSX...")

        session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&XXL")
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # EXPORTAÇÃO DO RELATÓRIO PARA EXCEL
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print(f"Exportando arquivo para: {pasta_destino}")
        print(f"Nome do arquivo: {nome_arquivo}")

        session.findById("wnd[1]/usr/ctxtDY_PATH").text = pasta_destino
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = len(nome_arquivo)
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        print("Arquivo exportado pelo SAP.")

        try:
            session.findById("wnd[0]").close()
        except:
            pass

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # UPLOAD DO ARQUIVO PARA O MINIO :: BUCKET TMP
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Criando buffer do arquivo exportado...")

        arquivo = minio.buffer_creator(
            pasta_destino,
            nome_arquivo,
        )

        print("Enviando arquivo para o MinIO no bucket tmp...")

        minio.upload_from_bytesIO(
            arquivo,
            "tmp",
            nome_arquivo,
        )

        print(f"Arquivo enviado para o MinIO com sucesso: tmp/{nome_arquivo}")

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # ENCERRAMENTO DA SESSÃO SAP
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Encerrando sessão SAP...")

        sap.encerrar_sap()

        print(" ---------- Extração SAP4HANA :: Faturamento concluída com sucesso! ---------- ")

    except Exception as e:
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # TRATAMENTO DE ERRO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print(f"Erro ao exportar dados do relatório ZSD_PIVB_E900 :: {str(e)}")

        try:
            sap.encerrar_sap()
        except:
            pass

        raise


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# EXECUÇÃO DIRETA DO SCRIPT
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if __name__ == "__main__":
    engdds_faturamento_main()