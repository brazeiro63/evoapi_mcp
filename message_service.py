import requests
import csv
import io
from datetime import datetime

class MessageService:
    def __init__(self, client):
        self.client = client

    def _convert_to_csv(self, data):
        """
        Converte os dados para formato CSV e retorna como string.
        """
        if not data:
            return ""
        
        # Criar um buffer de string para o CSV
        output = io.StringIO()
        
        # Definir os cabeçalhos baseados nas chaves do primeiro item
        if data:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            # Escrever cabeçalho
            writer.writeheader()
            
            # Escrever dados
            writer.writerows(data)
        
        # Obter o conteúdo CSV como string
        csv_content = output.getvalue()
        output.close()
        
        return csv_content

    def fetch_all_messages(self, instance_id, instance_token, remoteJid: str):
        """
        Busca todas as mensagens associadas ao remoteJid, extrai apenas propriedades relevantes,
        e retorna o conteúdo CSV como string.
        """
        url = f"{self.client.base_url}/chat/findMessages/{instance_id}"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.client.api_token,
            "Authorization": f"Bearer {self.client.api_token}",
            "Instance-Token": instance_token
        }
        payload = {"where": {"key": {"remoteJid": remoteJid}}}

        all_messages = []
        current_page = 1

        try:
            while True:
                params = {"limit": 100, "page": current_page}
                response = requests.post(url, json=payload, headers=headers, params=params)
                response.raise_for_status()
                result = response.json()

                records = result.get("messages", []).get("records", [])
                for msg in records:
                    simplified = {
                        "fromMe": msg.get("key", {}).get("fromMe"),
                        "remoteJid": msg.get("key", {}).get("remoteJid"),
                        "messageType": msg.get("messageType"),
                        "text": msg.get("message", {}).get("conversation"),
                        "timestamp": msg.get("messageTimestamp"),
                        "pushName": msg.get("pushName"),
                        "source": msg.get("source")
                    }
                    all_messages.append(simplified)

                if current_page >= result.get("messages").get("pages"):
                    break

                current_page += 1

            return self._convert_to_csv(all_messages)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar mensagens: {e}")
            return None

    def fetch_interval_messages(self, instance_id, instance_token, date_ini: datetime, date_end: datetime, remoteJid: str):
        """
        Retorna o conteúdo CSV contendo mensagens de um remoteJid dentro de um intervalo de datas.
        Apenas as propriedades relevantes são mantidas.
        """
        url = f"{self.client.base_url}/chat/findMessages/{instance_id}"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.client.api_token,
            "Authorization": f"Bearer {self.client.api_token}",
            "Instance-Token": instance_token
        }
        payload = {"where": {"key": {"remoteJid": remoteJid}}}

        all_messages = []
        current_page = 1

        try:
            # Buscar todas as mensagens
            while True:
                params = {"limit": 100, "page": current_page}
                response = requests.post(url, json=payload, headers=headers, params=params)
                response.raise_for_status()
                result = response.json()

                records = result.get("messages", []).get("records", [])
                for msg in records:
                    try:
                        timestamp = int(msg.get("messageTimestamp", 0))
                        msg_time = datetime.fromtimestamp(timestamp)
                        
                        # Filtrar por intervalo de datas
                        if date_ini <= msg_time <= date_end:
                            simplified = {
                                "fromMe": msg.get("key", {}).get("fromMe"),
                                "remoteJid": msg.get("key", {}).get("remoteJid"),
                                "messageType": msg.get("messageType"),
                                "text": msg.get("message", {}).get("conversation"),
                                "timestamp": msg.get("messageTimestamp"),
                                "pushName": msg.get("pushName"),
                                "source": msg.get("source")
                            }
                            all_messages.append(simplified)
                    except Exception:
                        continue

                if current_page >= result.get("messages").get("pages"):
                    break

                current_page += 1

            return self._convert_to_csv(all_messages)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar mensagens: {e}")
            return None