import os
from datetime import datetime
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient

from group import Group
from instance_config import InstanceConfig
from message_sandeco import MessageSandeco

# Load env variables
load_dotenv()


class GroupController:
    def __init__(self, instance_id: str | None = None):
        """
        Controller for Evolution API groups using a configurable instance.
        """
        creds = InstanceConfig.resolve_instance(instance_id)

        self.instance_id = creds.id
        self.instance_token = creds.token
        self.base_url = creds.url
        self.api_token = os.getenv(f"EVO_INSTANCE_{self.instance_id}_APIKEY", os.getenv("EVO_API_TOKEN"))

        if not all([self.base_url, self.api_token, self.instance_id, self.instance_token]):
            raise ValueError("Variáveis de ambiente necessárias não configuradas corretamente para a instância.")

        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
        self.groups = []

    def fetch_groups(self):
        """
        Fetches all groups for the instance.
        """
        groups_data = self.client.group.fetch_all_groups(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            get_participants=False,
        )

        self.groups = []
        for group in groups_data:
            group_id = group["id"]
            self.groups.append(
                Group(
                    group_id=group_id,
                    name=group["subject"],
                    subject_owner=group.get("subjectOwner"),
                    subject_time=group["subjectTime"],
                    picture_url=group.get("pictureUrl"),
                    size=group["size"],
                    creation=group["creation"],
                    owner=group.get("owner"),
                    restrict=group["restrict"],
                    announce=group["announce"],
                    is_community=group["isCommunity"],
                    is_community_announce=group["isCommunityAnnounce"],
                )
            )

        return self.groups

    def get_groups(self):
        if not self.groups:
            self.fetch_groups()
        return self.groups

    def find_group_by_id(self, group_id):
        if not self.groups:
            self.groups = self.fetch_groups()

        for group in self.groups:
            if group.group_id == group_id:
                return group
        return None

    def filter_groups_by_owner(self, owner):
        return [group for group in self.groups if group.owner == owner]

    def get_messages(self, group_id, start_date, end_date):
        def to_iso8601(date_str):
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        timestamp_start = to_iso8601(start_date)
        timestamp_end = to_iso8601(end_date)

        group_mensagens = self.client.chat.get_messages(
            instance_id=self.instance_id,
            remote_jid=group_id,
            instance_token=self.instance_token,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
            page=1,
            offset=1000,
        )

        msgs = MessageSandeco.get_messages(group_mensagens)

        data_obj = datetime.strptime(timestamp_start, "%Y-%m-%dT%H:%M:%SZ")
        timestamp_limite = int(data_obj.timestamp())

        msgs_filtradas = []
        for msg in msgs:
            if msg.message_timestamp >= timestamp_limite:
                msgs_filtradas.append(msg)

        return msgs_filtradas
