import requests
import json
import logging
from typing import Optional, Dict, Any

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str, enable_logging: bool = True):
        """
        Inicializa o notificador do Telegram.
        
        Args:
            token: Token do bot do Telegram
            chat_id: ID do chat/usuário/grupo
            enable_logging: Se True, registra logs das operações
        """
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.enable_logging = enable_logging
        
        if enable_logging:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
    
    def send_message(self, text: str, parse_mode: str = "HTML", 
                    disable_notification: bool = False) -> Dict[str, Any]:
        """
        Envia uma mensagem para o chat do Telegram.
        
        Args:
            text: Texto da mensagem
            parse_mode: "HTML" ou "Markdown"
            disable_notification: Se True, não envia notificação sonora
        
        Returns:
            Resposta da API do Telegram
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            if self.enable_logging:
                self.logger.info(f"Mensagem enviada com sucesso para o chat {self.chat_id}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if self.enable_logging:
                self.logger.error(f"Erro ao enviar mensagem no Telegram: {e}")
            return {"ok": False, "error": str(e)}
    
    def send_error_notification(self, script_name: str, error_message: str, 
                               additional_info: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia uma notificação de erro formatada.
        
        Args:
            script_name: Nome do script que falhou
            error_message: Mensagem de erro
            additional_info: Informações adicionais (opcional)
        
        Returns:
            Resposta da API do Telegram
        """
        message = f"""
🚨 <b>ERRO NO PROCESSO DE EXTRAÇÃO</b>

📄 <b>Script:</b> {script_name}
❌ <b>Erro:</b> <code>{error_message}</code>

⏰ <b>Hora do erro:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if additional_info:
            message += f"\n📝 <b>Informações adicionais:</b>\n{additional_info}"
        
        message += "\n\n⚠️ <i>A intervenção manual pode ser necessária.</i>"
        
        return self.send_message(message)
    
    def send_success_notification(self, script_name: str, 
                                 execution_time: Optional[float] = None,
                                 records_processed: Optional[int] = None) -> Dict[str, Any]:
        """
        Envia uma notificação de sucesso.
        
        Args:
            script_name: Nome do script executado
            execution_time: Tempo de execução em segundos (opcional)
            records_processed: Número de registros processados (opcional)
        """
        message = f"""
✅ <b>PROCESSO CONCLUÍDO COM SUCESSO</b>

📄 <b>Script:</b> {script_name}
"""
        
        if execution_time:
            message += f"⏱️ <b>Tempo de execução:</b> {execution_time:.2f} segundos\n"
        
        if records_processed is not None:
            message += f"📊 <b>Registros processados:</b> {records_processed:,}\n"
        
        message += f"\n🕒 <b>Hora de conclusão:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message, disable_notification=True)