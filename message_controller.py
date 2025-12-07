import os
from datetime import datetime
from dotenv import load_dotenv

from evolutionapi.client import EvolutionClient
from instance_config import InstanceConfig
from message_service import MessageService

# Load env variables
load_dotenv()


class MessageController:
    def __init__(self, instance_id: str | None = None):
        """
        Controller for Evolution API messages using a configurable instance.
        """
        creds = InstanceConfig.resolve_instance(instance_id)

        self.instance_id = creds.id
        self.instance_token = creds.token
        self.base_url = creds.url
        self.api_token = os.getenv(f"EVO_INSTANCE_{self.instance_id}_APIKEY", os.getenv("EVO_API_TOKEN"))

        if not all([self.base_url, self.api_token, self.instance_id, self.instance_token]):
            raise ValueError("Variáveis de ambiente necessárias não configuradas corretamente para a instância.")

        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
        self.message_service = MessageService(self.client)

    def fetch_all_messages(self, remote_jid: str):
        return self.message_service.fetch_all_messages(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            remoteJid=remote_jid,
        )

    def fetch_interval_messages(self, remote_jid: str, start: str, end: str):
        try:
            dt_start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            dt_end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            print(f"Formato de data inválido: {e}")
            return None

        return self.message_service.fetch_interval_messages(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            date_ini=dt_start,
            date_end=dt_end,
            remoteJid=remote_jid,
        )
