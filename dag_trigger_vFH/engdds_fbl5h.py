# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# IMPORTAR BIBLIOTECAS
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Bibliotecas :: Gerais
from datetime import date, timedelta
import json
import time
import os

# Bibliotecas :: Específicas
from saplogin import SAPLogin
from Minio import MinioConnector


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# FUNÇÕES AUXILIARES
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def datas_para_processar():
    """
    Define automaticamente quais datas serão extraídas.

    Regras:

    Segunda a sexta:
        - baixa somente D0 (dia atual)

    Sábado e domingo:
        - reconstrói:
            S0 = semana atual
            S-1 = semana anterior
    """

    hoje = date.today()

    # 5 = sábado | 6 = domingo
    # final_de_semana = 6
    final_de_semana = hoje.weekday() in (5, 6)

    datas = []

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # FINAL DE SEMANA -> REBUILD S0 + S-1
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    if final_de_semana:

        # Segunda-feira da semana atual
        inicio_semana_atual = hoje - timedelta(days=hoje.weekday())

        # Segunda-feira da semana anterior
        inicio_semana_anterior = inicio_semana_atual - timedelta(days=7)

        data_loop = inicio_semana_anterior

        while data_loop <= hoje:

            datas.append(data_loop)

            data_loop += timedelta(days=1)

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # SEGUNDA A SEXTA -> SOMENTE D0
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    else:

        datas.append(hoje)

    # Remove duplicidades e ordena
    return sorted(list(set(datas)))

def data_sap(data_ref):
    """
    Converte a data de referência para o formato esperado pelo SAP.

    Exemplo:
        2026-04-23 -> 23.04.2026
    """
    return data_ref.strftime("%d.%m.%Y")


def nome_arquivo_fbl5h(data_ref):
    """
    Monta o nome do arquivo de saída com a data da extração.

    Exemplo:
        2026-04-23 -> FBL5H_20260423.XLSX
    """
    return f"FBL5H_{data_ref:%Y%m%d}.XLSX"


def limpar_arquivos_antigos(minio, bucket, datas_validas):
    """
    Remove arquivos antigos do MinIO,
    mantendo apenas arquivos de S0 e S-1.
    """

    objetos = minio.list_objects(bucket)

    arquivos_validos = {
        nome_arquivo_fbl5h(data_ref)
        for data_ref in datas_validas
    }

    for objeto in objetos:

        nome_objeto = objeto.object_name

        # ignora arquivos fora do padrão
        if not nome_objeto.startswith("FBL5H_"):
            continue

        # remove arquivos antigos
        if nome_objeto not in arquivos_validos:

            print(f"Removendo arquivo antigo :: {nome_objeto}")

            minio.remove_object(
                bucket,
                nome_objeto
            )


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INSTANCIANDO VARIÁVEIS DE AMBIENTE :: SAP
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
sap = SAPLogin()


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INICIANDO PROCESSAMENTO :: EXTRAÇÃO SAP4HANA FBL5H
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def engdds_fbl5h_main():

    minio = MinioConnector()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # CARREGANDO METADADOS DOS ARQUIVOS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    script_dir = os.path.dirname(os.path.abspath(__file__))

    files_json_path = os.path.join(
        script_dir,
        "files.json"
    )

    with open(
        files_json_path,
        "r",
        encoding="utf-8"
    ) as file:

        meta_arquivos = json.load(file)

    pasta_destino = meta_arquivos["engdds_fbl5h.py"]["path"]

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # DEFINE DATAS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    datas = datas_para_processar()

    erros = []

    # 5 = sábado | 6 = domingo
    final_de_semana = date.today().weekday() in (5, 6)

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # LOG DAS DATAS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    print("\nDatas programadas para extração:\n")

    for data_ref in datas:

        print(
            data_ref.strftime("%d/%m/%Y")
        )

    print("\n")

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # LOOP DE EXTRAÇÃO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    for data_ref in datas:

        data_formatada = data_sap(data_ref)

        nome_arquivo = nome_arquivo_fbl5h(data_ref)

        print(
            f"Iniciando extração FBL5H "
            f"para {data_formatada} => {nome_arquivo}"
        )

        try:

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # LOGIN SAP
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            session = sap.login_to_s4hana()

            try:

                session.FindById("wnd[0]").SendVKey(0)

            except:

                pass

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # ACESSA FBL5H
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            session.findById(
                "wnd[0]/tbar[0]/okcd"
            ).text = "FBL5H"

            session.findById("wnd[0]").sendVKey(0)

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # PARAMETRIZAÇÃO
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            session.findById(
                "wnd[0]/usr/ctxtS_CCODE-LOW"
            ).text = "E900"

            session.findById(
                "wnd[0]/usr/ctxtP_KEYDO"
            ).text = data_formatada

            session.findById(
                "wnd[0]/usr/ctxtP_LAYOUT"
            ).text = "/AR FI"

            session.findById(
                "wnd[0]/usr/ctxtP_LAYOUT"
            ).setFocus()

            session.findById(
                "wnd[0]/usr/ctxtP_LAYOUT"
            ).caretPosition = 6

            session.findById(
                "wnd[0]/tbar[1]/btn[8]"
            ).press()

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # FILTRO RV
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            session.findById(
                "wnd[0]/shellcont/shell"
            ).setCurrentCell(-1, "BLART")

            session.findById(
                "wnd[0]/shellcont/shell"
            ).selectColumn("BLART")

            session.findById(
                "wnd[0]/shellcont/shell"
            ).pressToolbarButton("&MB_FILTER")

            session.findById(
                "wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW"
            ).text = "RV"

            session.findById(
                "wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW"
            ).caretPosition = 2

            session.findById(
                "wnd[1]/tbar[0]/btn[0]"
            ).press()

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # EXPORTAÇÃO EXCEL
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            session.findById(
                "wnd[0]/shellcont/shell"
            ).pressToolbarButton("SHOWBUT")

            session.findById(
                "wnd[0]/shellcont/shell"
            ).pressToolbarContextButton("&MB_EXPORT")

            session.findById(
                "wnd[0]/shellcont/shell"
            ).selectContextMenuItem("&XXL")

            session.findById(
                "wnd[1]/tbar[0]/btn[0]"
            ).press()

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # SALVA ARQUIVO
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            session.findById(
                "wnd[1]/usr/ctxtDY_PATH"
            ).text = pasta_destino

            session.findById(
                "wnd[1]/usr/ctxtDY_FILENAME"
            ).text = nome_arquivo

            session.findById(
                "wnd[1]/usr/ctxtDY_FILENAME"
            ).caretPosition = len(nome_arquivo)

            session.findById(
                "wnd[1]/tbar[0]/btn[0]"
            ).press()

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # UPLOAD MINIO
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

            
            arquivo = minio.buffer_creator(
                pasta_destino,
                nome_arquivo,
            )

            minio.upload_from_bytesIO(
                arquivo,
                "tmp",
                nome_arquivo,
            )

            print(
                f"FBL5H gravado no bucket tmp "
                f"como {nome_arquivo}"
            )

        except Exception as erro:

            erros.append(
                f"{data_formatada} -> {str(erro)}"
            )

            print(f"Erro ao processar FBL5H")

            print(f"Data :: {data_formatada}")

            print(f"Mensagem :: {str(erro)}")

        finally:

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # ENCERRA SAP
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            try:

                sap.encerrar_sap()

            except:

                pass

            time.sleep(10)

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # LIMPEZA DE HISTÓRICO ANTIGO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    if final_de_semana:

        try:

            limpar_arquivos_antigos(
                minio,
                "tmp",
                datas
            )

            print(
                "Limpeza de arquivos antigos concluída."
            )

        except Exception as erro_limpeza:

            print(
                "Erro ao limpar arquivos antigos."
            )

            print(str(erro_limpeza))

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # VALIDAÇÃO FINAL
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    if erros:

        raise RuntimeError(
            f"Ocorreram erros na extração FBL5H: {erros}"
        )


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# EXECUÇÃO DIRETA
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if __name__ == "__main__":

    engdds_fbl5h_main()