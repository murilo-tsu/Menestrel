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

    Regra:
        - Segunda a sexta: processa apenas D-1.
        - Sábado e domingo: processa os últimos 10 dias fechados, de D-10 até D-1.

    Observação:
        O dia atual nunca é processado, pois a FBL3H trabalha com dados fechados.
    """
    hoje = date.today()
    final_de_semana = hoje.weekday() in (5, 6)  # 5 = sábado | 6 = domingo

    qtd_dias = 10 if final_de_semana else 1

    data_final = hoje - timedelta(days=1)
    data_inicial = data_final - timedelta(days=qtd_dias - 1)

    return [
        data_inicial + timedelta(days=i)
        for i in range(qtd_dias)
    ]


def data_sap(data_ref):
    """
    Converte a data de referência para o formato esperado pelo SAP.

    Exemplo:
        2026-04-23 -> 23.04.2026
    """
    return data_ref.strftime("%d.%m.%Y")


def nome_arquivo_fbl3h(data_ref):
    """
    Monta o nome do arquivo de saída com a data da extração.

    Exemplo:
        2026-04-23 -> FBL3H_20260423.XLSX
    """
    return f"FBL3H_{data_ref:%Y%m%d}.XLSX"


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INSTANCIANDO VARIÁVEIS DE AMBIENTE :: SAP
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Instanciador de SAP Session
sap = SAPLogin()


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# INICIANDO PROCESSAMENTO :: EXTRAÇÃO SAP4HANA FBL3H
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def engdds_fbl3h_main():
    """
    Executa a extração da transação FBL3H no SAP S/4HANA.

    Fluxo:
        1. Identifica as datas a serem processadas.
        2. Para cada data, acessa a transação FBL3H.
        3. Exporta o relatório em Excel para a pasta TEMP da VM.
        4. Envia o arquivo gerado para o bucket tmp do MinIO.
    """
    minio = MinioConnector()

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # CARREGANDO METADADOS DOS ARQUIVOS
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_json_path = os.path.join(script_dir, "files.json")

    with open(files_json_path, "r", encoding="utf-8") as file:
        meta_arquivos = json.load(file)

    pasta_destino = meta_arquivos["engdds_fbl3h.py"]["path"]

    # Define automaticamente se a execução será diária ou backfill de fim de semana
    datas = datas_para_processar()
    erros = []

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # LOOP DE EXTRAÇÃO POR DATA
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    for data_ref in datas:
        data_formatada = data_sap(data_ref)
        nome_arquivo = nome_arquivo_fbl3h(data_ref)

        print(f"Iniciando extração FBL3H para {data_formatada} => {nome_arquivo}")

        try:
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # LOGIN E ACESSO À TRANSAÇÃO FBL3H
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            session = sap.login_to_s4hana()

            try:
                session.FindById("wnd[0]").SendVKey(0)
            except:
                pass

            session.findById("wnd[0]/tbar[0]/okcd").text = "FBL3H"
            session.findById("wnd[0]").sendVKey(0)

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # PARAMETRIZAÇÃO DO RELATÓRIO
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            session.findById("wnd[0]/usr/ctxtS_CCODE-LOW").text = "E900"
            session.findById("wnd[0]/usr/ctxtS_CCODE-HIGH").text = "E900"

            session.findById("wnd[0]/usr/radP_AI").setFocus()
            session.findById("wnd[0]/usr/radP_AI").select()

            session.findById("wnd[0]/usr/ctxtS_PDATE-LOW").text = data_formatada
            session.findById("wnd[0]/usr/ctxtS_PDATE-HIGH").text = data_formatada

            session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/FPA_HRG" #Troca de Layout
            session.findById("wnd[0]/tbar[1]/btn[8]").press()

            try:
                session.findById("wnd[1]/usr/btnBUTTON_1").press()
            except:
                pass
            
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # EXPORTAÇÃO DO RELATÓRIO PARA EXCEL
            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            session.findById("wnd[0]/shellcont/shell").pressToolbarButton("SHOWBUT")
            session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
            session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&XXL")

            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[1]/tbar[0]/btn[0]").press()

            session.findById("wnd[1]/usr/ctxtDY_PATH").text = pasta_destino
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = nome_arquivo
            session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = len(nome_arquivo)

            session.findById("wnd[1]/tbar[0]/btn[0]").press()

            # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
            # UPLOAD DO ARQUIVO PARA O MINIO :: BUCKET TMP
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

            print(f"{data_formatada} :: FBL3H gravado no tmp como {nome_arquivo}")

        except Exception as erro:
            # Guarda os erros para que o script falhe oficialmente ao final,
            # sem interromper imediatamente as próximas datas do backfill.
            print(f"Erro ao processar FBL3H para {data_formatada}")
            print(f"Mensagem de erro :: {str(erro)}")
            erros.append((data_formatada, str(erro)))

        finally:
            # Garante o encerramento da sessão SAP após cada data processada.
            try:
                sap.encerrar_sap()
            except:
                pass

            time.sleep(10)

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # VALIDAÇÃO FINAL DA EXECUÇÃO
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    if erros:
        raise RuntimeError(f"Ocorreram erros na extração FBL3H: {erros}")


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# EXECUÇÃO DIRETA DO SCRIPT
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if __name__ == "__main__":
    engdds_fbl3h_main()