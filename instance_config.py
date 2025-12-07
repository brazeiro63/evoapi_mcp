import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class InstanceInfo:
    """Stores public (non-secret) info about an Evolution API instance."""

    id: str
    name: str
    url: str


@dataclass
class InstanceCredentials:
    """Full credentials for an Evolution API instance (includes token)."""

    id: str
    name: str
    url: str
    token: str


class InstanceConfig:
    """Loads Evolution API instances from environment variables."""

    @staticmethod
    def _parse_instance_ids() -> List[str]:
        raw = os.getenv("EVO_INSTANCES", "")
        ids = [i.strip() for i in raw.split(",") if i.strip()]
        return ids

    @staticmethod
    def load_instances() -> List[InstanceInfo]:
        ids = InstanceConfig._parse_instance_ids()
        instances: List[InstanceInfo] = []

        if ids:
            for instance_id in ids:
                prefix = f"EVO_INSTANCE_{instance_id}_"
                url = os.getenv(prefix + "URL")
                token = os.getenv(prefix + "TOKEN")  # token not exposed, only used to validate presence
                name = os.getenv(prefix + "NAME", instance_id)

                if url and token:
                    instances.append(InstanceInfo(instance_id, name, url))
            return instances

        # Fallback to legacy single-instance env vars
        legacy_url = os.getenv("EVO_API_URL")
        legacy_token = os.getenv("EVO_API_TOKEN")
        legacy_name = os.getenv("EVO_INSTANCE_NAME", "default")

        if legacy_url and legacy_token:
            instances.append(InstanceInfo("default", legacy_name, legacy_url))

        return instances

    @staticmethod
    def get_default_id() -> Optional[str]:
        if InstanceConfig._parse_instance_ids():
            default_id = os.getenv("EVO_INSTANCE_DEFAULT")
            if default_id:
                return default_id
        return "default"

    @staticmethod
    def resolve_instance(instance_id: Optional[str] = None) -> InstanceCredentials:
        """
        Returns credentials for the given instance id or the default one.

        Raises:
            ValueError: if the instance is not configured.
        """
        ids = InstanceConfig._parse_instance_ids()

        # Select instance id
        if ids:
            target_id = instance_id or InstanceConfig.get_default_id()
            if target_id not in ids:
                raise ValueError(f"Instância '{target_id}' não configurada. IDs disponíveis: {', '.join(ids)}")

            prefix = f"EVO_INSTANCE_{target_id}_"
            url = os.getenv(prefix + "URL")
            token = os.getenv(prefix + "TOKEN")
            name = os.getenv(prefix + "NAME", target_id)

            if not (url and token):
                raise ValueError(
                    f"Instância '{target_id}' incompleta. Defina {prefix}URL e {prefix}TOKEN (opcional {prefix}NAME)."
                )

            return InstanceCredentials(target_id, name, url, token)

        # Legacy single-instance fallback
        url = os.getenv("EVO_API_URL")
        token = os.getenv("EVO_API_TOKEN")
        name = os.getenv("EVO_INSTANCE_NAME", "default")
        instance_token = os.getenv("EVO_INSTANCE_TOKEN")

        if url and token and instance_token:
            target_id = instance_id or "default"
            if target_id != "default":
                raise ValueError("Somente a instância legado 'default' está configurada.")
            return InstanceCredentials(target_id, name, url, instance_token)

        raise ValueError(
            "Nenhuma instância configurada. Defina EVO_INSTANCES com os blocos EVO_INSTANCE_<ID>_URL/TOKEN "
            "ou use o formato legado EVO_API_URL, EVO_API_TOKEN, EVO_INSTANCE_NAME, EVO_INSTANCE_TOKEN."
        )
