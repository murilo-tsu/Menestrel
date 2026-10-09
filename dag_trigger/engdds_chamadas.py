import psycopg2
import pandas as pd
import unicodedata
import re
import os
import win32com.client as win32
import pythoncom
import time
from datetime import datetime
from saplogin import SAPLogin


# ==================================================
# CONEXÃO COM POSTGRES
# ==================================================
def get_connection():
    try:
        conn = psycopg2.connect(
            host="10.91.0.51",
            database="patio_utf8",
            user="postgres",
            password="Admin@2024",
            port=5432,
            options="-c client_encoding=UTF8"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None


# ==================================================
# NORMALIZAÇÃO DE COLUNAS
# ==================================================
def normalizar_nome(nome):
    nome = unicodedata.normalize("NFKD", nome)
    nome = nome.encode("ascii", "ignore").decode("utf-8")
    nome = re.sub(r"[^a-zA-Z0-9]+", "_", nome)
    return nome.lower().strip("_")


# ==================================================
# IMPORTAÇÃO TXT SAP
# ==================================================
def importar_txt_sap(caminho_txt: str, log=None):
    if not os.path.exists(caminho_txt):
        msg = f"[{datetime.now()}] Arquivo não encontrado: {caminho_txt}"
        print(msg)
        if log:
            log.write(msg + "\n")
        return

    try:
        df = pd.read_csv(caminho_txt, sep="\t", skiprows=1, encoding="latin1")
        df = df.dropna(axis=1, how="all")

        if "Ordem de Processo" in df.columns:
            df = df[df["Ordem de Processo"].notna() & (df["Ordem de Processo"] != "")]

        for col in df.columns:
            if "Unnamed" in col:
                df = df.drop(columns=[col])

        df.columns = [normalizar_nome(c) for c in df.columns]

        if "qtd_da_remessa" in df.columns:
            df["qtd_da_remessa"] = (
                df["qtd_da_remessa"]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df["qtd_da_remessa"] = pd.to_numeric(df["qtd_da_remessa"], errors="coerce")

        conn = get_connection()
        if not conn:
            raise Exception("Falha na conexão com o banco")

        cur = conn.cursor()

        ordens_arquivo = (
            df["ordem_de_processo"]
            .dropna()
            .astype(str)
            .map(str.strip)
            .tolist()
        )

        if ordens_arquivo:
            cur.execute("""
                UPDATE tb_sequenciamento
                   SET status_atual = 'Cancelado_SAP'
                 WHERE status_atual IN ('PENDENTE','Chamado','Em Trânsito','Portaria')
                   AND ordem_processo::text NOT IN %s;
            """, (tuple(ordens_arquivo),))
            print(f"{cur.rowcount} OP(s) marcadas como Cancelado_SAP")

        sql = """
            INSERT INTO tb_sequenciamento (
                data_seq, planta, sequencia, equipamento, placa, motorista, telefone,
                ordem_processo, remessa, cod_material, desc_material,
                qtd_remessa, tipo_embalagem, armazem, local_exp, inic_plan, hora, status_atual
            )
            VALUES (
                CURRENT_DATE, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, 'PENDENTE'
            )
            ON CONFLICT (ordem_processo) DO UPDATE
            SET
                data_seq       = EXCLUDED.data_seq,
                planta         = EXCLUDED.planta,
                sequencia      = EXCLUDED.sequencia,
                equipamento    = EXCLUDED.equipamento,
                placa          = EXCLUDED.placa,
                motorista      = EXCLUDED.motorista,
                telefone       = EXCLUDED.telefone,
                remessa        = EXCLUDED.remessa,
                cod_material   = EXCLUDED.cod_material,
                desc_material  = EXCLUDED.desc_material,
                qtd_remessa    = EXCLUDED.qtd_remessa,
                tipo_embalagem = EXCLUDED.tipo_embalagem,
                armazem        = EXCLUDED.armazem,
                local_exp      = EXCLUDED.local_exp,
                inic_plan      = EXCLUDED.inic_plan,
                hora           = EXCLUDED.hora,
                status_atual   = CASE
                    WHEN tb_sequenciamento.status_atual = 'Cancelado_SAP'
                    THEN 'PENDENTE'
                    ELSE tb_sequenciamento.status_atual
                END;
        """

        novos, erros = 0, 0

        for _, row in df.iterrows():
            def get(c):
                return row[c] if c in df.columns and pd.notna(row[c]) else None

            valores = [
                get("planta"),
                get("sequencia"),
                get("equipament"),
                get("placa_do_caminhao"),
                get("mot_caminhao"),
                None,
                get("ordem_de_processo"),
                get("remessa"),
                get("codigo_de_material"),
                get("descricao_do_materia"),
                get("qtd_da_remessa"),
                get("tipo_de_emabalagem"),
                get("armazem"),
                get("local_expedicao"),
                get("inic_plan"),
                get("hora"),
            ]

            try:
                cur.execute(sql, valores)
                novos += 1
            except Exception as ex:
                erros += 1
                print(f"Erro na OP {get('ordem_de_processo')}: {ex}")

        conn.commit()
        print(f"Importação finalizada: {novos} registros, {erros} erros")

        cur.close()
        conn.close()

        if log:
            log.write(f"[{datetime.now()}] Importação concluída ({novos} registros)\n")

    except Exception as e:
        msg = f"[{datetime.now()}] Erro na importação: {e}"
        print(msg)
        if log:
            log.write(msg + "\n")


# ==================================================
# EXTRAÇÃO SAP
# ==================================================
def executar_exportacao_sap():
    caminho_saida = r"C:\Automacao_SAP_Flet\ckp.txt"

    time.sleep(4)

    session = None
    connection = None

    pythoncom.CoInitialize()
  
    # SapGuiAuto = win32.GetObject("SAPGUI")
    # application = SapGuiAuto.GetScriptingEngine
    # connection = application.Children(0)
    # session = connection.Children(0)
    sap = SAPLogin()

    session = sap.login_to_s4hana_pt()

    print("⚙️ Executando /NZPP_COCKPIT ...")
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nzpp_cockpit"
    session.findById("wnd[0]").sendVKey(0)
    time.sleep(2)

    session.findById("wnd[0]/usr/chkP_FULFIL").selected = False
    session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "E60J"
    session.findById("wnd[0]/usr/ctxtP_LAYOUT").text = "/SCREP_CHM1"
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    time.sleep(2)

    session.findById("wnd[0]/shellcont/shell").pressToolbarButton("&NAVIGATION_PROFILE_TOOLBAR_EXPAND")
    session.findById("wnd[0]/shellcont/shell").pressToolbarContextButton("&MB_EXPORT")
    session.findById("wnd[0]/shellcont/shell").selectContextMenuItem("&PC")
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/"
                        "sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = os.path.dirname(caminho_saida)
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = os.path.basename(caminho_saida)
    session.findById("wnd[1]/tbar[0]/btn[11]").press()
    
    sap.encerrar_sap() 
    
    return caminho_saida

    
# ==================================================
# MAIN
# ==================================================
def main():
    PASTA_BASE = r"C:\Automacao_SAP_Flet"
    LOG_PATH = os.path.join(PASTA_BASE, "logs")
    os.makedirs(LOG_PATH, exist_ok=True)

    log_file = os.path.join(
        LOG_PATH,
        f"execucao_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n=== Execução iniciada {datetime.now()} ===\n")

        try:
            caminho_txt = executar_exportacao_sap()
            importar_txt_sap(caminho_txt, log)
            print("Execução concluída com sucesso")
            log.write("Execução concluída com sucesso\n")
        except Exception as e:
            print(f"Erro durante execução: {e}")
            log.write(f"Erro durante execução: {e}\n")

        log.write(f"=== Execução finalizada {datetime.now()} ===\n")


if __name__ == "__main__":
    main()
