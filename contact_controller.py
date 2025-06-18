# Path: evoapi_mcp\contact_controller.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from datetime import datetime
from contact_service import ContactService
from evolutionapi.client import EvolutionClient
from contact import Contact
from message_sandeco import MessageSandeco

# Carregar variáveis de ambiente
load_dotenv()

class ContactController:
    def __init__(self):
        """
        Inicializa o controlador de contatos para a API Evolution, carregando configurações do ambiente.
        """
        self.base_url = os.getenv("EVO_API_URL")
        self.api_token = os.getenv("EVO_API_TOKEN")
        self.instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.instance_token = os.getenv("EVO_INSTANCE_TOKEN")
        
        paths_this = os.path.dirname(__file__)
        
        self.csv_file = os.path.join(paths_this, "contacts_data.csv")

        if not all([self.base_url, self.api_token, self.instance_id, self.instance_token]):
            raise ValueError(
                "As variáveis de ambiente necessárias (EVO_API_URL, EVO_API_TOKEN, EVO_INSTANCE_NAME, EVO_INSTANCE_TOKEN) não estão configuradas corretamente."
            )

        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
        self.contacts = []

    def fetch_contacts(self):
        """
        Busca todos os contatos da instância e atualiza a lista interna de contatos.
        
        :return: Lista de objetos `Contact`.
        """
        # Busca os contatos da API
        contact_service = ContactService(self.client)
        contacts_data = contact_service.fetch_all_contacts(
            instance_id=self.instance_id,
            instance_token=self.instance_token
        )

        # Atualiza a lista de contatos com objetos `Contact`
        self.contacts = []
        for contact in contacts_data:
            # Dados básicos do contato
            contact_id = contact.get("id")
            remote_jid = contact.get("remoteJid")
            
            # Criação do objeto Contact
            self.contacts.append(
                Contact(
                    id=contact_id,
                    remote_jid=remote_jid,
                    push_name=contact.get("pushName"),
                )
            )
            
        return self.contacts


    def fetch_contacts_by_phone_number(self, phone_number: str):
        """
        Busca todos os contatos da instância e atualiza a lista interna de contatos.
        
        :return: Lista de objetos `Contact`.
        """
        # Busca os contatos da API
        contact_service = ContactService(self.client)
        contacts_data = contact_service.fetch_contacts_by_phone_number(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            phone_number=phone_number
        )

        # Atualiza a lista de contatos com objetos `Contact`
        self.contacts = []
        for contact in contacts_data:
            # Dados básicos do contato
            contact_id = contact.get("id")
            remote_jid = contact.get("remoteJid")
            
            # Criação do objeto Contact
            self.contacts.append(
                Contact(
                    id=contact_id,
                    remote_jid=remote_jid,
                    push_name=contact.get("pushName"),
                    profile_pic_url=contact.get("profilePicUrl"),
                    created_at=contact.get("createdAt"),
                    updated_at=contact.get("updatedAt"),
                    instance_id=contact.get("instanceId")
                )
            )
            
        return self.contacts

    def get_contacts(self):
        """
        Retorna a lista de contatos.

        :return: Lista de objetos `Contact`.
        """
        if not self.contacts:
            self.fetch_contacts()
        return self.contacts

    def find_contact_by_id(self, contact_id):
        """
        Encontra um contato pelo ID.

        :param contact_id: ID do contato a ser encontrado.
        :return: Objeto `Contact` correspondente ou `None` se não encontrado.
        """
        if not self.contacts:
            self.contacts = self.fetch_contacts()
        
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None
    
    def find_contact_by_jid(self, remote_jid):
        """
        Encontra um contato pelo JID remoto.

        :param remote_jid: JID remoto do contato.
        :return: Objeto `Contact` correspondente ou `None` se não encontrado.
        """
        if not self.contacts:
            self.contacts = self.fetch_contacts()
        
        for contact in self.contacts:
            if contact.remote_jid == remote_jid:
                return contact
        return None
    
    def find_contact_by_number(self, number):
        """
        Encontra um contato pelo número de telefone.

        :param number: Número de telefone do contato.
        :return: Objeto `Contact` correspondente ou `None` se não encontrado.
        """
        if not self.contacts:
            self.contacts = self.fetch_contacts()
        
        # Normaliza o número removendo caracteres não numéricos
        normalized_number = ''.join(filter(str.isdigit, number))
        
        # Adiciona o sufixo @c.us se não estiver presente
        search_jid = f"{normalized_number}@c.us"
        
        for contact in self.contacts:
            if contact.remote_jid == search_jid:
                return contact
            
            # Tenta comparar apenas o número extraído
            if contact.number == normalized_number:
                return contact
                
        return None
    
    def get_profile_picture(self, remote_jid):
        """
        Obtém a foto de perfil de um contato.

        :param remote_jid: JID remoto do contato.
        :return: URL da imagem de perfil ou None se não disponível.
        """
        result = self.client.contact.get_profile_picture(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            remote_jid=remote_jid
        )
        
        if result and "profilePictureUrl" in result:
            # Atualiza a URL da imagem na lista local
            contact = self.find_contact_by_jid(remote_jid)
            if contact:
                contact.profile_pic_url = result["profilePictureUrl"]
            return result["profilePictureUrl"]
        return None
    
    def get_common_groups(self, remote_jid):
        """
        Obtém os grupos em comum com um contato.

        :param remote_jid: JID remoto do contato.
        :return: Lista de IDs de grupos em comum.
        """
        result = self.client.contact.get_common_groups(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            remote_jid=remote_jid
        )
        
        if result and "groups" in result:
            return result["groups"]
        return []
    
    def get_messages(self, remote_jid, start_date, end_date):
        """
        Obtém mensagens trocadas com um contato em um período específico.

        :param remote_jid: JID remoto do contato.
        :param start_date: Data de início no formato 'YYYY-MM-DD HH:MM:SS'.
        :param end_date: Data de fim no formato 'YYYY-MM-DD HH:MM:SS'.
        :return: Lista de mensagens filtradas.
        """
        # Convertendo as datas para o formato ISO 8601 com T e Z
        def to_iso8601(date_str):
            # Parseando a data no formato 'YYYY-MM-DD HH:MM:SS'
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            # Convertendo para o formato ISO 8601 com Z
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Ajustando os parâmetros de data
        timestamp_start = to_iso8601(start_date)
        timestamp_end = to_iso8601(end_date)

        # Buscando as mensagens do chat com o contato
        contact_messages = self.client.chat.get_messages(
            instance_id=self.instance_id,
            remote_jid=remote_jid,
            instance_token=self.instance_token,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
            page=1,
            offset=1000
        )
        
        msgs = MessageSandeco.get_messages(contact_messages)
        
        data_obj = datetime.strptime(timestamp_start, "%Y-%m-%dT%H:%M:%SZ")
        # Obter o timestamp
        timestamp_limite = int(data_obj.timestamp())
        
        msgs_filtradas = []
        for msg in msgs:
            if msg.message_timestamp >= timestamp_limite:
                msgs_filtradas.append(msg)
        
        return msgs_filtradas
    
    def check_contact_exists(self, number):
        """
        Verifica se um número de telefone existe no WhatsApp.

        :param number: Número de telefone a verificar.
        :return: Booleano indicando se o número existe no WhatsApp.
        """
        # Normaliza o número removendo caracteres não numéricos
        normalized_number = ''.join(filter(str.isdigit, number))
        
        # Verifica se o número existe no WhatsApp
        result = self.client.contact.check_exists(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            phone_number=normalized_number
        )
        
        return result.get("exists", False) if result else False