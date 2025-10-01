import win32com.client
import subprocess
import requests
from datetime import datetime
from menestrel_encryptor import sap_crypto
from requests.auth import HTTPBasicAuth
import time

class SAPLogin:
    def __init__(self):
        
        self.username, self.password = sap_crypto().obter_credencias()
        self.lang = "EN"
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
            raise Exception("SAP GUI not found")
            
        self.application = self.sap_gui.GetScriptingEngine
    
    def _perform_login(self, connection_name):
        self.connection = self.application.OpenConnection(connection_name, True)
        self.session = self.connection.Children(0)
        
        self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = self.username
        self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = self.password
        self.session.findById("wnd[0]/usr/txtRSYST-LANGU").text = self.lang
        self.session.findById("wnd[0]").sendVKey(0)
        return self.session
    
    def login_to_s4hana(self):
        """Login S/4HANA"""
        try:
            self._initialize_sap_gui()
            return self._perform_login("SAP S/4 HANA PROD")
        except Exception as e:
            self.cleanup()
            raise Exception(f"S/4HANA login failed: {str(e)}")
    
    # DEPRECADO :: O SISTEMA SAP ECC FOI CONGELADO E USA-SE APENAS O SAP4HANA
    # def login_to_ecc(self, username="mribeiro.fto", password="*********"):
    #     """Login ECC"""
    #     try:
    #         self._initialize_sap_gui()
    #         return self._perform_login(".SAP ECC Heringer PROD", username, password)
    #     except Exception as e:
    #         self.cleanup()
    #         raise Exception(f"ECC login failed: {str(e)}")
    
    def cleanup(self):
        self.session = None
        self.connection = None
        self.application = None
        self.sap_gui = None


    def trigger_airflow_dag(self,dag_name="engdds_sku"):
        # Dados do Servidor
        airflow_url = f"http://10.91.5.84:8080/api/v1/dags/{dag_name}/dagRuns" 
        username = "datainsights_dev"
        password = "Eurochem123@"
        

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
            print("DAG triggered successfully:", response.json())
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.text}")
        except Exception as e:
            print("Failed to trigger DAG:", str(e))

    def limpar_variaveis():
        """Limpa variáveis para evitar conflitos entre scripts"""
        for var in list(globals().keys()):
            if not var.startswith('_') and var not in ['SAPLogin', 'date', 'timedelta', 'pd', 'time', 'os', 'end', 'dt']:
                del globals()[var]
        import gc
        gc.collect()

if __name__ == "__main__":
    SAPLogin().trigger_airflow_dag()