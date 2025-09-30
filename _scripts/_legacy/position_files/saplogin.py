import win32com.client
import subprocess
import requests
from datetime import datetime  # Fixed import
from requests.auth import HTTPBasicAuth
import time

class SAPLogin:
    def __init__(self):
        """Constructor - initialize all instance variables"""
        self.session = None
        self.connection = None
        self.application = None
        self.sap_gui = None
    
    def _initialize_sap_gui(self):
        """Private method for common initialization"""
        path = r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe"
        subprocess.Popen(path)
        time.sleep(10)
        
        self.sap_gui = win32com.client.GetObject('SAPGUI')
        if not isinstance(self.sap_gui, win32com.client.CDispatch):
            raise Exception("SAP GUI not found")
            
        self.application = self.sap_gui.GetScriptingEngine
    
    def _perform_login(self, connection_name, username, password):
        """Private method for common login steps"""
        self.connection = self.application.OpenConnection(connection_name, True)
        self.session = self.connection.Children(0)
        
        self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = username
        self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
        self.session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "PT"
        self.session.findById("wnd[0]").sendVKey(0)
        return self.session
    
    def login_to_s4hana(self, username="U0000753", password="@H1MuR4_2025_s4"):
        """Login to S/4HANA system"""
        try:
            self._initialize_sap_gui()
            return self._perform_login("SAP S/4 HANA PROD", username, password)
        except Exception as e:
            self.cleanup()
            raise Exception(f"S/4HANA login failed: {str(e)}")
    
    def login_to_ecc(self, username="mribeiro.fto", password="@Himura2025s4hana"):
        """Login to ECC system"""
        try:
            self._initialize_sap_gui()
            return self._perform_login(".SAP ECC Heringer PROD", username, password)
        except Exception as e:
            self.cleanup()
            raise Exception(f"ECC login failed: {str(e)}")
    
    def cleanup(self):
        """Clean up resources"""
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
        # Clean up all temporary variables
        for var in list(globals().keys()):
            if not var.startswith('_') and var not in ['SAPLogin', 'date', 'timedelta', 'pd', 'time', 'os', 'end', 'dt']:
                del globals()[var]
        import gc
        gc.collect()

    if __name__ == "__main__":
        trigger_airflow_dag()