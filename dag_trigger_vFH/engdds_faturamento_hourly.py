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

def remover_arquivo_local(caminho_arquivo):
    """
    Remove o arquivo local antes de uma nova exportação.

    Isso evita que o SAP tente sobrescrever um XLSX antigo ou que o Python leia
    um arquivo antigo que ficou na pasta de saída.
    """
    if not os.path.exists(caminho_arquivo):
        return

    print(f"Arquivo local já existe e será removido: {caminho_arquivo}")

    try:
        os.remove(caminho_arquivo)
        print("Arquivo local antigo removido com sucesso.")
    except PermissionError as erro:
        raise PermissionError(
            f"Não foi possível remover o arquivo local porque ele está em uso: "
            f"{caminho_arquivo}. Verifique se ele está aberto no Excel ou preso "
            f"por algum processo do SAP."
        ) from erro


def aguardar_arquivo_disponivel(caminho_arquivo, tentativas=20, intervalo=3):
    """
    Aguarda o arquivo existir e estar liberado para leitura.

    Mesmo após o SAP informar que exportou, o arquivo XLSX pode continuar sendo
    gravado ou ficar temporariamente bloqueado pelo Excel/SAP.
    """
    for tentativa in range(1, tentativas + 1):
        if not os.path.exists(caminho_arquivo):
            print(
                f"Arquivo ainda não encontrado. "
                f"Tentativa {tentativa}/{tentativas}: {caminho_arquivo}"
            )
            time.sleep(intervalo)
            continue

        try:
            with open(caminho_arquivo, "rb") as file:
                file.read(1)

            print("Arquivo encontrado e liberado para leitura.")
            return

        except PermissionError:
            print(
                f"Arquivo ainda está bloqueado. "
                f"Tentativa {tentativa}/{tentativas}. "
                f"Aguardando {intervalo} segundos..."
            )
            time.sleep(intervalo)

    raise TimeoutError(
        f"O arquivo foi exportado, mas continuou bloqueado para leitura após "
        f"{tentativas * intervalo} segundos: {caminho_arquivo}"
    )


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INICIANDO PROCESSAMENTO :: EXTRAÇÃO SAP4HANA FATURAMENTO HOURLY
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def engdds_faturamento_hourly_main():
    """
    Executa a extração incremental/hourly do relatório de faturamento no SAP S/4HANA.

    Fluxo:
        1. Carrega os metadados do files.json.
        2. Define o intervalo dinâmico dos últimos 2 dias até a data atual.
        3. Acessa a transação ZSD_PIVB.
        4. Parametriza a extração para a organização E900.
        5. Filtra o tipo de documento ZSFO.
        6. Exporta o relatório em XLSX para a pasta TEMP da VM.
        7. Envia o arquivo gerado para o bucket tmp do MinIO.
    """
    print(" ---------- Iniciando extração SAP4HANA :: Faturamento Hourly ---------- ")

    minio = MinioConnector()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # CARREGANDO METADADOS DOS ARQUIVOS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print("Carregando metadados do arquivo files.json...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, "files.json")

    with open(files_json_path, "r", encoding="utf-8") as file:
        meta_arquivos = json.load(file)

    pasta_destino = meta_arquivos["engdds_faturamento_hourly.py"]["path"]
    nome_arquivo = meta_arquivos["engdds_faturamento_hourly.py"]["files"][0]

    print(f"Pasta destino configurada: {pasta_destino}")
    print(f"Arquivo configurado para exportação: {nome_arquivo}")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # DEFININDO INTERVALO DINÂMICO DE DATAS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Regra atual:
    #     - Extrai da data atual - 2 dias até a data atual.
    print("Definindo intervalo de datas para extração hourly...")

    now = time.localtime()

    start_date = datetime.datetime(
        now.tm_year,
        now.tm_mon,
        now.tm_mday,
    ) + datetime.timedelta(days=-2)

    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year

    end_day = now.tm_mday
    end_month = now.tm_mon
    end_year = now.tm_year

    data_inicial_sap = f"{start_day:02d}.{start_month:02d}.{start_year}"
    data_final_sap = f"{end_day:02d}.{end_month:02d}.{end_year}"

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
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZSD_PIVB"
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
        # Opção ativa :: XLSX
        # ----------------------------------------------------------------------
        print("Selecionando exportação em XLSX...")

        session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&XXL")
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # EXPORTAÇÃO DO RELATÓRIO PARA EXCEL
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Validando pasta destino local...")

        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino, exist_ok=True)
            print(f"Pasta criada: {pasta_destino}")
        else:
            print(f"Pasta já existente: {pasta_destino}")

        caminho_arquivo_local = os.path.join(pasta_destino, nome_arquivo)

        remover_arquivo_local(caminho_arquivo_local)

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
        print("Aguardando arquivo exportado ficar disponível para leitura...")

        aguardar_arquivo_disponivel(
            caminho_arquivo_local,
            tentativas=20,
            intervalo=3,
        )

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

        print(" ---------- Extração SAP4HANA :: Faturamento Hourly concluída com sucesso! ---------- ")

    except Exception as e:
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # TRATAMENTO DE ERRO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print(f"Erro durante a execução da extração Faturamento Hourly: {str(e)}")

        try:
            sap.encerrar_sap()
        except:
            pass

        raise

    time.sleep(5)


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# EXECUÇÃO DIRETA DO SCRIPT
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if __name__ == "__main__":
    engdds_faturamento_hourly_main()