import requests
import json
import os
from datetime import datetime

class MessageService:
    def __init__(self, client):
        self.client = client

    def _save_to_json(self, data, method_name):
        """
        Salva os dados em um arquivo JSON no diretório 'outputs/mensagens/' com base no nome do método e hora atual.
        Retorna o caminho do arquivo salvo.
        """

        os.makedirs("G:\\Projetos\\evoapi_mcp\\outputs\\mensagens", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{method_name}_{timestamp}.json"
        path = os.path.join("outputs\\mensagens", filename)

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Arquivo salvo: {path}")
            return path
        except Exception as e:
            print(f"Erro ao salvar arquivo {path}: {e}")
            return None

    def fetch_all_messages(self, instance_id, instance_token, remoteJid: str):
        """
        Busca todas as mensagens associadas ao remoteJid, extrai apenas propriedades relevantes,
        e retorna o caminho do arquivo JSON salvo.
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

            return self._save_to_json(all_messages, "fetch_all_messages")

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar mensagens: {e}")
            return None

    def get_interval_messages(self, instance_id, instance_token, date_ini: datetime, date_end: datetime, remoteJid: str):
        """
        Retorna o caminho do arquivo JSON contendo mensagens de um remoteJid dentro de um intervalo de datas.
        Apenas as propriedades relevantes são mantidas.
        """
        all_messages = self.fetch_all_messages(instance_id, instance_token, remoteJid)
        if not all_messages:
            return None

        try:
            with open(all_messages, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
        except Exception as e:
            print(f"Erro ao ler mensagens: {e}")
            return None

        filtered = []
        for msg in messages_data:
            try:
                timestamp = int(msg.get("timestamp", 0))
                msg_time = datetime.fromtimestamp(timestamp)
                if date_ini <= msg_time <= date_end:
                    filtered.append(msg)
            except Exception:
                continue

        return self._save_to_json(filtered, "interval_messages")
