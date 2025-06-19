# Path: evoapi_mcp/message_controller.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from datetime import datetime
from message_service import MessageService
from evolutionapi.client import EvolutionClient

# Carrega variáveis de ambiente
load_dotenv()

class MessageController:
    def __init__(self):
        """
        Inicializa o controlador de mensagens, carregando as configurações de ambiente.
        """
        self.base_url = os.getenv("EVO_API_URL")
        self.api_token = os.getenv("EVO_API_TOKEN")
        self.instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.instance_token = os.getenv("EVO_INSTANCE_TOKEN")

        if not all([self.base_url, self.api_token, self.instance_id, self.instance_token]):
            raise ValueError(
                "As variáveis de ambiente necessárias (EVO_API_URL, EVO_API_TOKEN, EVO_INSTANCE_NAME, EVO_INSTANCE_TOKEN) não estão configuradas corretamente."
            )

        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
        self.message_service = MessageService(self.client)

    def fetch_all_messages(self, remote_jid: str):
        """
        Busca todas as mensagens de um contato e retorna o caminho do arquivo JSON salvo.

        :param remote_jid: JID remoto (e.g., '5511999999999@s.whatsapp.net')
        :return: Caminho do arquivo salvo com as mensagens.
        """
        return self.message_service.fetch_all_messages(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            remoteJid=remote_jid
        )

    def fetch_interval_messages(self, remote_jid: str, start: str, end: str):
        """
        Busca mensagens de um contato entre duas datas e retorna o caminho do arquivo JSON salvo.

        :param remote_jid: JID remoto (e.g., '5511999999999@s.whatsapp.net')
        :param start: Data/hora inicial (formato 'YYYY-MM-DD HH:MM:SS')
        :param end: Data/hora final (formato 'YYYY-MM-DD HH:MM:SS')
        :return: Caminho do arquivo salvo com as mensagens filtradas.
        """
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
            remoteJid=remote_jid
        )
