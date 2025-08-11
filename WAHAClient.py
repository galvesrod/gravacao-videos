import requests
import json
import time
from typing import Optional

class WAHAClient:
    def __init__(self, base_url: str, session_name: str = "default"):
        """
        Inicializa o cliente WAHA
        
        Args:
            base_url: URL base do WAHA (ex: http://localhost:3000)
            session_name: Nome da sessão do WhatsApp
        """

        self.base_url = base_url.rstrip('/')
        self.session_name = session_name
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def start_session(self) -> bool:
        """
        Inicia uma sessão do WhatsApp
        
        Returns:
            bool: True se a sessão foi iniciada com sucesso
        """
        try:
            url = f"{self.base_url}/api/sessions/start"
            data = {
                "name": self.session_name,
                "config": {
                    "webhooks": []
                }
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 201:
                print(f"Sessão '{self.session_name}' iniciada com sucesso!")
                return True
            elif response.status_code == 422:
                response_data = response.json()
                if "already started" in response_data.get("message","").lower():
                    return True
                else:
                    return False
                
            else:
                print(f"Erro ao iniciar sessão: {response.status_code} - {response.text}")                
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
            return False
    
    def get_session_status(self) -> Optional[str]:
        """
        Verifica o status da sessão
        
        Returns:
            str: Status da sessão (STARTING, SCAN_QR_CODE, WORKING, FAILED, etc.)
        """
        try:
            url = f"{self.base_url}/api/sessions/{self.session_name}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('status')
            else:
                print(f"Erro ao verificar status: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
            return None
    
    def get_qr_code(self) -> Optional[str]:
        """
        Obtém o QR code para autenticação
        
        Returns:
            str: QR code em base64 ou None se não disponível
        """
        try:
            url = f"{self.base_url}/api/sessions/{self.session_name}/auth/qr"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('qr')
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter QR code: {e}")
            return None
    
    def send_text_message(self, chat_id: str, message: str) -> bool:
        """
        Envia mensagem de texto para um contato ou grupo
        
        Args:
            chat_id: ID do chat (contato: 5511999999999@c.us ou grupo: 120363027111111111@g.us)
            message: Texto da mensagem
            
        Returns:
            bool: True se a mensagem foi enviada com sucesso
        """
        try:
            # Formatar chat_id se necessário
            if '@' not in chat_id:
                # Se não tem @, assume que é um número de telefone
                chat_id = f"{chat_id}@c.us"
            
            url = f"{self.base_url}/api/sendText"
            data = {
                "session": self.session_name,
                "chatId": chat_id,
                "text": message
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 201:
                chat_type = "grupo" if "@g.us" in chat_id else "contato"
                print(f"Mensagem enviada com sucesso para {chat_type}: {chat_id}")
                return True
            else:
                print(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
            return False

    
    def wait_for_ready(self, timeout: int = 120) -> bool:
        """
        Aguarda a sessão ficar pronta (status WORKING)
        
        Args:
            timeout: Tempo limite em segundos
            
        Returns:
            bool: True se a sessão ficou pronta
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_session_status()
            
            if status == "WORKING":
                print("Sessão pronta para uso!")
                return True
            elif status == "SCAN_QR_CODE":
                qr_code = self.get_qr_code()
                if qr_code:
                    print("Escaneie o QR code no WhatsApp:")
                    print(f"QR Code: {qr_code}")
            elif status == "FAILED":
                print("Falha na sessão!")
                return False
            
            print(f"Status atual: {status}")
            time.sleep(5)
        
        print("Timeout: Sessão não ficou pronta no tempo esperado")
        return False
