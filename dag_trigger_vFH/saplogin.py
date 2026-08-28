import win32com.client
import subprocess
import requests
from datetime import datetime
from menestrel_encryptor import sap_crypto, sp_crypto
from requests.auth import HTTPBasicAuth
from graph_api_connector import sharepoint
import time

class SAPLogin:
    def __init__(self):
        
        self.username, self.password = sap_crypto().obter_credencias()
        self.sp_user, self.sp_pass = sp_crypto().credenciais_sharepoint() # << NOVA
        self.connection = None
        self.application = None
        self.session = None
        self.sap_gui = None
    
    def _initialize_sap_gui(self):
        path = r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe"
        subprocess.Popen(path)
        time.sleep(10)
        
        self.sap_gui = win32com.client.GetObject('SAPGUI')
        if not isinstance(self.sap_gui, win32com.client.CDispatch):
            raise Exception("SAP GUI não encontrado")
            
        self.application = self.sap_gui.GetScriptingEngine
    
    def _perform_login(self, connection_name, lang):
        self.connection = self.application.OpenConnection(connection_name, True)
        self.session = self.connection.Children(0)
        
        self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = self.username
        self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = self.password

        self.session.findById("wnd[0]/usr/txtRSYST-LANGU").text = lang
        self.session.findById("wnd[0]").sendVKey(0)
        return self.session
    
    def login_to_s4hana(self, lang = 'EN'):
        """Login SAP4HANA"""
        try:
            self._initialize_sap_gui()
            #print('---> SAP4HANA logado com sucesso!')
            return self._perform_login("SAP S/4 HANA PROD", lang)
        except Exception as e:
            self.cleanup()
            raise Exception(f"Falha ao realizar o login no SAP4HANA: {str(e)}")

    def login_to_s4hana_pt(self, lang = 'PT'):
        """Login SAP4HANA"""
        try:
            self._initialize_sap_gui()
            #print('---> SAP4HANA logado com sucesso!')
            return self._perform_login("SAP S/4 HANA PROD", lang)
        except Exception as e:
            self.cleanup()
            raise Exception(f"Falha ao realizar o login no SAP4HANA: {str(e)}")
    
    # ---------------------------------------------------------------------------------------
    # DEPRECADO :: O SISTEMA SAP ECC FOI CONGELADO E USA-SE APENAS O SAP4HANA
    # def login_to_ecc(self, username="mribeiro.fto", password="*********"):
    #     """Login ECC"""
    #     try:
    #         self._initialize_sap_gui()
    #         return self._perform_login(".SAP ECC Heringer PROD", username, password)
    #     except Exception as e:
    #         self.cleanup()
    #         raise Exception(f"ECC login failed: {str(e)}")
    # ---------------------------------------------------------------------------------------
    
    # def cleanup(self):
    #     """
    #     Reseta os parâmentros de conexão com o SAP4HANA: sessão, conexão, aplicação, etc.
    #     """
    #     self.session = None
    #     self.connection = None
    #     self.application = None
    #     self.sap_gui = None

    def encerrar_sessao_sap(self, silent=True):
        """
        Fecha a aba (sessão) atual do SAP via SAP GUI Scripting
        """
        try:
            if self.session is not None:
                # Fecha a janela principal
                self.session.findById("wnd[0]").close()

                # Confirma popup de saída, se existir
                try:
                    self.session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
                except:
                    pass

            if not silent:
                print("---> Sessão SAP encerrada com sucesso")

        except Exception as e:
            if not silent:
                print(f"Erro ao encerrar sessão SAP: {e}")


    def safe_cleanup(self):
        """
        Cleanup seguro que funciona independente do idioma do SAP
        """
        import win32com.client
        
        # Método 1: Tenta fechar via comando
        try:
            if self.session:
                self.session.SendCommand("/nex")  # Comando universal para sair
        except:
            pass
        
        # Método 2: Usa força bruta via processo do Windows
        try:
            import os
            os.system('taskkill /f /im saplogon.exe 2>nul')
            os.system('taskkill /f /im sapgui.exe 2>nul')
        except:
            pass
        
        # Método 3: Limpa referências COM
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except:
            pass
        
        # Finalmente limpa as referências
        self.session = None
        self.connection = None
        self.application = None
        self.sap_gui = None


    # def limpar_processos(self, silent = True):
    #     """ 
    #     Encerrar os processos em execução e limpar a sessão do SAP4HANA.
    #     Dessa forma, o processo é liberado para uma nova execução.
    #     """
    #     processos = ['saplogon.exe', 'notepad.exe', 'cmd.exe', 'excel.exe', 'sublime_text.exe']
    #     for processo in processos:

    #         subprocess.run(f'taskkill /f /im {processo}',
    #                         shell = True, stdout=subprocess.DEVNULL,
    #                         stderr=subprocess.DEVNULL, timeout = 2)
        
    #     print('---> SAP4HANA e processos correlatos encerrados!')
                    

    def upload_files(self, sharepoint_folder,local_file_path, ):
        time.sleep(3)
        try:
            sp = sharepoint(self.sp_user, self.sp_pass)
            sp.connect()
            sp.upload(sharepoint_folder, local_file_path)
            print(f'SUCESSO :: {local_file_path} → {sharepoint_folder}')
            return True
        except Exception as erro:
            print(f'FALHA - {erro}')
            return False


    def trigger_airflow_dag(self,dag_name):
        """
        Cria um módulo capaz de gatilhar uma [D][A][G] através de seu nome no servidor
        """
        # Dados do Servidor
        airflow_url = f"http://10.91.5.108:8080/api/v1/dags/{dag_name}/dagRuns" 
        username = "datainsights_fh"
        password = "Heringer123"
        

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # run_id = "menestrel__" + datetime.now().isoformat()
        run_id = "menestrel__" + datetime.now().strftime("%Y-%m-%dT%H-%M-%S_%f")

        payload = {
            "conf": {},
            "dag_run_id": run_id,
        }
        
        try:
            response = requests.post(
                airflow_url,
                json=payload,
                headers=headers,
                auth=HTTPBasicAuth(username, password),
                timeout=10 
            )
            response.raise_for_status()
            print("[D][A][G] iniciada com sucesso:", response.json())
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.text}")
        except Exception as e:
            print("Falha em iniciar a [D][A][G]:", str(e))

    def limpar_variaveis():
        """Limpa variáveis para evitar conflitos entre scripts"""
        for var in list(globals().keys()):
            if not var.startswith('_') and var not in ['SAPLogin', 'date', 'timedelta', 'pd', 'time', 'os', 'end', 'dt']:
                del globals()[var]
        import gc
        gc.collect()


#=======================================================================================================================================================

    def fechar_sessao_sap(self):
        """
        Encerra a sessão SAP corretamente via comando /nex
        """
        try:
            if self.session:
                self.session.findById("wnd[0]/tbar[0]/okcd").text = "/nex"
                self.session.findById("wnd[0]").sendVKey(0)
                time.sleep(2)
        except Exception:
            pass

    def fechar_conexao_sap(self):
        """
        Fecha conexão e aplicação SAP GUI
        """
        try:
            if self.connection:
                self.connection.CloseSession(self.session.Id)
                time.sleep(1)
        except Exception:
            pass

        try:
            if self.application:
                self.application.Quit()
                time.sleep(1)
        except Exception:
            pass

    def cleanup(self):
        """
        Libera corretamente todos os objetos COM
        """
        try:
            self.session = None
            self.connection = None
            self.application = None
            self.sap_gui = None

            pythoncom.CoUninitialize()
            gc.collect()

        except Exception:
            pass

    def limpar_processos(self, silent=True):
        """
        Fallback: mata processos apenas se algo ficou preso
        """
        processos = [
            'saplogon.exe',
            'saplgpad.exe',
            'sapshcut.exe',
            'excel.exe'
        ]

        for processo in processos:
            subprocess.run(
                f'taskkill /f /im {processo}',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        if not silent:
            print('---> Processos SAP finalizados via taskkill')

    def encerrar_sap(self):
        """
        Encerra SAP da forma correta:
        1. Fecha sessão
        2. Fecha conexão
        3. Limpa objetos COM
        4. Mata processos (fallback)
        """
        try:
            self.fechar_sessao_sap()
            self.fechar_conexao_sap()
        finally:
            self.cleanup()
            self.limpar_processos()

