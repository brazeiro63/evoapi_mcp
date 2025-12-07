import requests


class ContactService:
    def __init__(self, client):
        self.client = client

    def fetch_all_contacts(self, instance_id, instance_token):
        url = f"{self.client.base_url}/chat/findContacts/{instance_id}"
        headers = {
            "Authorization": f"Bearer {self.client.api_token}",
            "apikey": self.client.api_token,
            "Instance-Token": instance_token,
            "Content-Type": "application/json",
        }
        payload = {"where": {"1": 1}}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar contatos: {e}")
            return []

    def fetch_contacts_by_phone_number(self, instance_id, instance_token, phone_number: str):
        url = f"{self.client.base_url}/chat/findContacts/{instance_id}"
        headers = {
            "Authorization": f"Bearer {self.client.api_token}",
            "apikey": self.client.api_token,
            "Instance-Token": instance_token,
            "Content-Type": "application/json",
        }
        payload = {"where": {"remoteJid": phone_number}}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar contatos: {e}")
            return []

    def check_contact_exists(self, instance_id, instance_token, phone_number: str) -> bool:
        result = self.fetch_contacts_by_phone_number(instance_id, instance_token, phone_number)
        return bool(result)
