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
# INICIANDO PROCESSAMENTO :: EXTRAÇÃO SAP4HANA ZPP_COCKPIT
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def engdds_cockpit_main():
    """
    Executa a extração do relatório ZPP_COCKPIT no SAP S/4HANA.

    Fluxo:
        1. Carrega os metadados do files.json.
        2. Busca as configurações específicas do script engdds_cockpit.py.
        3. Acessa a transação ZPP_COCKPIT.
        4. Parametriza centro/planta e etapas desejadas.
        5. Exporta o resultado em XLSX para a pasta local da VM.
        6. Valida se o arquivo foi gerado.
        7. Envia o arquivo para o bucket tmp do MinIO.
    """
    print(" ---------- Iniciando extração SAP4HANA :: ZPP_COCKPIT ---------- ")

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
        # OBTENDO CONFIGURAÇÕES DO SCRIPT
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Obtendo configuração específica para engdds_cockpit.py...")

        script_config = meta_arquivos.get("engdds_cockpit.py", {})

        if not script_config:
            raise ValueError(
                "Configuração para 'engdds_cockpit.py' não encontrada no files.json"
            )

        # Extrair informações de configuração.
        # Caso o path não exista no JSON, mantém o fallback já usado no script original.
        path_local = script_config.get("path", "C:\\Temp\\zpp_cockpit")

        # Nome do arquivo fixo utilizado na exportação e no upload.
        nome_arquivo = "ZPP_COCKPIT.xlsx"
        caminho_completo = os.path.join(path_local, nome_arquivo)

        print(f"Pasta local configurada: {path_local}")
        print(f"Arquivo configurado para exportação: {nome_arquivo}")
        print(f"Caminho completo esperado: {caminho_completo}")

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # GARANTINDO EXISTÊNCIA DO DIRETÓRIO LOCAL
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Validando diretório local de exportação...")

        os.makedirs(path_local, exist_ok=True)

        print("Diretório local validado com sucesso.")

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # LOGIN E ACESSO À TRANSAÇÃO ZPP_COCKPIT 
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Realizando login no SAP S/4HANA...")

        session = sap.login_to_s4hana()

        print("Login no SAP S/4HANA realizado com sucesso.")
        print("Acessando transação ZPP_COCKPIT...")

        session.findById("wnd[0]/tbar[0]/okcd").text = "ZPP_COCKPIT"
        session.findById("wnd[0]").sendVKey(0)

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # PARAMETRIZAÇÃO DO RELATÓRIO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Parametrizando relatório ZPP_COCKPIT...")

        session.findById("wnd[0]/usr/chkP_FULFIL").selected = False
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/DATAINSIGHT"
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").setFocus()
        session.findById("wnd[0]/usr/ctxtP_LAYOUT").caretPosition = 9
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/shellcont/shell").currentCellRow = -1
        session.findById("wnd[0]/shellcont/shell").selectColumn ("WERKS")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("&NAVIGATION_PROFILE_TOOLBAR_EXPAND")
        session.findById("wnd[0]/shellcont/shell").pressToolbarButton ("&MB_FILTER")
        session.findById("wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = "E90*"
        session.findById("wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").caretPosition = 4
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton ("&MB_EXPORT")
        session.findById("wnd[0]/shellcont/shell").selectContextMenuItem ("&XXL")
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
        session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
        session.findById("wnd[1]").sendVKey ("4")

        print("Executando relatório ZPP_COCKPIT...")

        # session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # PREPARAÇÃO DA GRADE PARA EXPORTAÇÃO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # print("Preparando grade para exportação em XLSX...")

        # session.findById("wnd[0]/shellcont/shell").selectColumn("ZSTEP")
        # session.findById("wnd[0]/shellcont/shell").contextMenu()
        # session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&XXL")
        # session.findById("wnd[1]/tbar[0]/btn[0]").press()
        # session.findById("wnd[1]").sendVKey(4)

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # EXPORTAÇÃO DO RELATÓRIO PARA EXCEL 
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print(f"Exportando arquivo para: {path_local}")
        print(f"Nome do arquivo: {nome_arquivo}")

        session.findById("wnd[2]/usr/ctxtDY_PATH").text = path_local
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nome_arquivo
        session.findById("wnd[2]/tbar[0]/btn[11]").press()
        session.findById("wnd[1]/tbar[0]/btn[11]").press()

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # AGUARDANDO DOWNLOAD LOCAL
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Aguardando finalização do download local do arquivo...")

        time.sleep(20)

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # VALIDAÇÃO DO ARQUIVO GERADO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Validando existência do arquivo exportado...")

        if not os.path.exists(caminho_completo):
            print(f"Arquivo não encontrado no caminho esperado: {caminho_completo}")

            # Tentar encontrar arquivos com nome similar no diretório.
            print("Buscando arquivos similares no diretório local...")

            arquivos = [
                f
                for f in os.listdir(path_local)
                if "ZPP_COCKPIT" in f.upper() and f.endswith(".xlsx")
            ]

            if arquivos:
                arquivos.sort(
                    key=lambda x: os.path.getmtime(os.path.join(path_local, x)),
                    reverse=True,
                )

                arquivo_encontrado = os.path.join(path_local, arquivos[0])

                print(f"Arquivo encontrado com nome diferente: {arquivos[0]}")

                # Renomear para o nome padrão esperado pelo fluxo.
                os.rename(arquivo_encontrado, caminho_completo)

                print(f"Arquivo renomeado para: {nome_arquivo}")
            else:
                raise FileNotFoundError(
                    f"Arquivo ZPP_COCKPIT.xlsx não encontrado em {path_local}"
                )
        else:
            print(f"Arquivo encontrado com sucesso: {caminho_completo}")

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # UPLOAD DO ARQUIVO PARA O MINIO :: BUCKET TMP
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print(f"Iniciando upload do arquivo para o MinIO: tmp/{nome_arquivo}")

        arquivo_enviado = False

        # ----------------------------------------------------------------------
        # Método 1 :: buffer_creator + upload_from_bytesIO
        # ----------------------------------------------------------------------
        # Método padrão usado nos demais scripts do ambiente.
        if hasattr(minio, "buffer_creator") and hasattr(minio, "upload_from_bytesIO"):
            print("Tentando upload via buffer_creator + upload_from_bytesIO...")

            try:
                arquivo_buffer = minio.buffer_creator(path_local, nome_arquivo)
                minio.upload_from_bytesIO(arquivo_buffer, "tmp", nome_arquivo)

                arquivo_enviado = True

                print("Upload realizado usando buffer_creator e upload_from_bytesIO.")
            except Exception as e:
                print(f"Erro no método buffer_creator: {str(e)}")

        # ----------------------------------------------------------------------
        # Método 2 :: upload_file
        # ----------------------------------------------------------------------
        # Método alternativo caso exista no MinioConnector.
        if not arquivo_enviado and hasattr(minio, "upload_file"):
            print("Tentando upload via upload_file...")

            try:
                minio.upload_file(caminho_completo, "tmp", nome_arquivo)

                arquivo_enviado = True

                print("Upload realizado usando upload_file.")
            except Exception as e:
                print(f"Erro no método upload_file: {str(e)}")

        # ----------------------------------------------------------------------
        # Método 3 :: cliente MinIO direto
        # ----------------------------------------------------------------------
        # Última alternativa caso o conector exponha o client diretamente.
        if not arquivo_enviado and hasattr(minio, "client"):
            print("Tentando upload via client MinIO direto...")

            try:
                import io

                with open(caminho_completo, "rb") as file:
                    file_data = file.read()

                minio.client.put_object(
                    bucket_name="tmp",
                    object_name=nome_arquivo,
                    data=io.BytesIO(file_data),
                    length=len(file_data),
                    content_type=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                )

                arquivo_enviado = True

                print("Upload realizado usando cliente MinIO diretamente.")
            except Exception as e:
                print(f"Erro no cliente MinIO direto: {str(e)}")

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # VALIDAÇÃO FINAL DO UPLOAD
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        if not arquivo_enviado:
            raise RuntimeError(
                "Nenhum método de upload funcionou. "
                "Verifique a configuração do MinioConnector."
            )
        else:
            print(f"Upload para MinIO concluído com sucesso: tmp/{nome_arquivo}")

        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # ENCERRAMENTO DA SESSÃO SAP
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print("Encerrando sessão SAP...")

        sap.encerrar_sap()

        print(" ---------- Extração SAP4HANA :: ZPP_COCKPIT concluída ---------- ")

    except Exception as erro:
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # TRATAMENTO DE ERRO
        # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        print(f"Erro ao exportar o ZPP_COCKPIT.xlsx: {str(erro)}")

        import traceback

        traceback.print_exc()

        try:
            # Encerra a sessão SAP em caso de erro.
            sap.encerrar_sap()
        except:
            pass

        raise
    
    


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# EXECUÇÃO DIRETA DO SCRIPT
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if __name__ == "__main__":
    engdds_cockpit_main()