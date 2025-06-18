import requests
import csv
import io

class ContactService:
    def __init__(self, client):
        self.client = client

    def fetch_all_contacts(self, instance_id, instance_token):
        """
        Realiza uma requisição para buscar todos os contatos da instância Evolution API
        e retorna apenas remoteJid e pushName formatados como CSV.

        :param instance_id: ID da instância.
        :param instance_token: Token da instância.
        :return: String CSV com remoteJid e pushName.
        """
        url = f"{self.client.base_url}/chat/findContacts/{instance_id}"
        headers = {
            "Authorization": f"Bearer {self.client.api_token}",
            "apikey": self.client.api_token,
            "Instance-Token": instance_token,
            "Content-Type": "application/json"
        }
        payload = {"where": {"1": 1}}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()

            # Extrair dados relevantes
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["remoteJid", "pushName"])

            for contact in result:
                writer.writerow([
                    contact.get("id", ""),
                    contact.get("remoteJid", ""),
                    contact.get("pushName", "")
                ])

            return output.getvalue()

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar contatos: {e}")
            return ""

    def fetch_contacts_by_phone_number(self, instance_id, instance_token, phone_number: str):
        """
        Realiza uma requisição para buscar o contato correspondente ao phone_number na instância Evolution API.

        :param instance_id: ID da instância.
        :param instance_token: Token da instância.
        :param phone_number: Número do telefone no formato completo com código do país.
        :return: Contato correspondente ao número de telefone fornecido.
        """
        url = f"{self.client.base_url}/chat/findContacts/{instance_id}"
        headers = {
            "Authorization": f"Bearer {self.client.api_token}",
            "apikey": self.client.api_token,
            "Instance-Token": instance_token,
            "Content-Type": "application/json"
        }
        payload = {"where": {"remoteJid": phone_number}}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar contatos: {e}")
            return []
