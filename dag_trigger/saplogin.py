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
            print('---> SAP4HANA logado com sucesso!')
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
    
    def cleanup(self):
        """
        Reseta os parâmentros de conexão com o SAP4HANA: sessão, conexão, aplicação, etc.
        """
        self.session = None
        self.connection = None
        self.application = None
        self.sap_gui = None


    def limpar_processos(self, silent = True):
        """ 
        Encerrar os processos em execução e limpar a sessão do SAP4HANA.
        Dessa forma, o processo é liberado para uma nova execução.
        """
        processos = ['saplogon.exe', 'notepad.exe', 'cmd.exe', 'excel.exe', 'sublime_text.exe']
        for processo in processos:

            subprocess.run(f'taskkill /f /im {processo}',
                            shell = True, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, timeout = 2)
        
        print('---> SAP4HANA e processos correlatos encerrados!')
                    

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
        airflow_url = f"http://10.91.5.107:8080/api/v1/dags/{dag_name}/dagRuns" 
        username = "MRibeiro"
        password = "desafio102030"
        

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "conf": {},  
            "dag_run_id": "manual__" + datetime.now().isoformat() 
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