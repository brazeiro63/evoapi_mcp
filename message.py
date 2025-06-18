# Path: evoapi_mcp/message.py
from datetime import datetime

class Message:
    def __init__(
        self,
        id,
        remote_jid,
        from_me,
        message_type,
        text=None,
        media_url=None,
        media_mimetype=None,
        media_filename=None,
        timestamp=None,
        ack=None,
        instance_id=None,
        sender_name=None,
        quoted_msg_id=None,
        quoted_msg_text=None
    ):
        """
        Inicializa uma mensagem com base na estrutura da Evolution API.

        :param id: ID único da mensagem.
        :param remote_jid: JID do contato ou grupo da conversa.
        :param from_me: Booleano indicando se a mensagem foi enviada pelo próprio número.
        :param message_type: Tipo da mensagem (e.g., text, image, audio, video, document).
        :param text: Texto da mensagem, se aplicável.
        :param media_url: URL da mídia, se aplicável.
        :param media_mimetype: Tipo MIME da mídia.
        :param media_filename: Nome do arquivo de mídia.
        :param timestamp: Data/hora em formato timestamp (UNIX).
        :param ack: Status de entrega (0=sent, 1=received, 2=read, etc.).
        :param instance_id: ID da instância à qual a mensagem pertence.
        :param sender_name: Nome do remetente (push name).
        :param quoted_msg_id: ID da mensagem citada, se houver.
        :param quoted_msg_text: Texto da mensagem citada, se aplicável.
        """
        self.id = id
        self.remote_jid = remote_jid
        self.from_me = from_me
        self.message_type = message_type
        self.text = text
        self.media_url = media_url
        self.media_mimetype = media_mimetype
        self.media_filename = media_filename
        self.timestamp = datetime.fromtimestamp(timestamp) if timestamp else None
        self.ack = ack
        self.instance_id = instance_id
        self.sender_name = sender_name
        self.quoted_msg_id = quoted_msg_id
        self.quoted_msg_text = quoted_msg_text

        # Propriedades derivadas
        self.number = self._extract_number_from_jid(remote_jid)

    def _extract_number_from_jid(self, jid):
        """
        Extrai o número de telefone do JID.
        """
        if jid and "@" in jid:
            return jid.split("@")[0]
        return jid

    def __repr__(self):
        """
        Retorna uma representação legível da mensagem.
        """
        direction = "Sent" if self.from_me else "Received"
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else "N/A"
        return (
            f"Message(id={self.id}, remote_jid={self.remote_jid}, type={self.message_type}, "
            f"text={self.text or 'None'}, {direction}, timestamp={time_str})"
        )
