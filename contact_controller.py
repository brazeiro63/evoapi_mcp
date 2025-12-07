import os
from datetime import datetime
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient

from contact import Contact
from contact_service import ContactService
from instance_config import InstanceConfig
from message_sandeco import MessageSandeco

# Load env variables
load_dotenv()


class ContactController:
    def __init__(self, instance_id: str | None = None):
        """
        Controller for Evolution API contacts using a configurable instance.
        """
        creds = InstanceConfig.resolve_instance(instance_id)

        self.instance_id = creds.id
        self.instance_token = creds.token
        self.base_url = creds.url
        self.api_token = os.getenv(f"EVO_INSTANCE_{self.instance_id}_APIKEY", os.getenv("EVO_API_TOKEN"))

        if not all([self.base_url, self.api_token, self.instance_id, self.instance_token]):
            raise ValueError("Variáveis de ambiente necessárias não configuradas corretamente para a instância.")

        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
        self.contacts = []

    def fetch_contacts(self):
        contact_service = ContactService(self.client)
        contacts_data = contact_service.fetch_all_contacts(
            instance_id=self.instance_id, instance_token=self.instance_token
        )

        self.contacts = []
        for contact in contacts_data:
            self.contacts.append(
                Contact(
                    id=contact.get("id"),
                    remote_jid=contact.get("remoteJid"),
                    push_name=contact.get("pushName"),
                )
            )

        return self.contacts

    def fetch_contacts_by_name(self, name: str):
        if not self.contacts:
            self.fetch_contacts()

        filtered = []
        name_lower = name.lower()
        for contact in self.contacts:
            if contact.push_name and name_lower in contact.push_name.lower():
                filtered.append(contact)
        return filtered

    def fetch_contacts_by_phone_number(self, phone_number: str):
        contact_service = ContactService(self.client)
        contacts_data = contact_service.fetch_contacts_by_phone_number(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            phone_number=phone_number,
        )

        self.contacts = []
        for contact in contacts_data:
            self.contacts.append(
                Contact(
                    id=contact.get("id"),
                    remote_jid=contact.get("remoteJid"),
                    push_name=contact.get("pushName"),
                    profile_pic_url=contact.get("profilePicUrl"),
                    created_at=contact.get("createdAt"),
                    updated_at=contact.get("updatedAt"),
                    instance_id=contact.get("instanceId"),
                )
            )

        return self.contacts

    def get_contacts(self):
        if not self.contacts:
            self.fetch_contacts()
        return self.contacts

    def find_contact_by_id(self, contact_id):
        if not self.contacts:
            self.contacts = self.fetch_contacts()

        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None

    def find_contact_by_jid(self, remote_jid):
        if not self.contacts:
            self.contacts = self.fetch_contacts()

        for contact in self.contacts:
            if contact.remote_jid == remote_jid:
                return contact
        return None

    def find_contact_by_number(self, number):
        if not self.contacts:
            self.contacts = self.fetch_contacts()

        normalized_number = "".join(filter(str.isdigit, number))
        search_jid = f"{normalized_number}@c.us"

        for contact in self.contacts:
            if contact.remote_jid == search_jid:
                return contact
            if contact.number == normalized_number:
                return contact

        return None

    def get_profile_picture(self, remote_jid):
        result = self.client.contact.get_profile_picture(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            remote_jid=remote_jid,
        )

        if result and "profilePictureUrl" in result:
            contact = self.find_contact_by_jid(remote_jid)
            if contact:
                contact.profile_pic_url = result["profilePictureUrl"]
            return result["profilePictureUrl"]
        return None

    def get_common_groups(self, remote_jid):
        result = self.client.contact.get_common_groups(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            remote_jid=remote_jid,
        )

        messages = MessageSandeco.get_messages(result.get("messages", []))
        unique_group_ids = list({msg.group_id for msg in messages if msg.group_id})
        return unique_group_ids

    def check_contact_exists(self, phone_number: str):
        contact_service = ContactService(self.client)
        return contact_service.check_contact_exists(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            phone_number=phone_number,
        )
