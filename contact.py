# Path: evoapi_mcp\contact.py
import datetime


class Contact:
    def __init__(
        self,
        id,
        remote_jid,
        push_name=None,
        profile_pic_url=None,
        created_at=None,
        updated_at=None,
        instance_id=None,
    ):
        """
        Inicializa um contato com as propriedades conforme a estrutura do banco de dados.

        :param id: ID único do contato.
        :param remote_jid: JID remoto do contato no formato 'número@c.us'.
        :param push_name: Nome definido pelo próprio contato no WhatsApp.
        :param profile_pic_url: URL da imagem de perfil do contato.
        :param created_at: Data de criação do registro.
        :param updated_at: Data da última atualização do registro.
        :param instance_id: ID da instância à qual o contato pertence.
        """
        self.id = id
        self.remote_jid = remote_jid
        self.push_name = push_name
        self.profile_pic_url = profile_pic_url
        self.created_at = created_at
        self.updated_at = updated_at
        self.instance_id = instance_id

        # Propriedades derivadas
        self.number = self._extract_number_from_jid(remote_jid)

        # Metadados adicionais (não presentes diretamente na tabela)
        self.is_business = None
        self.is_enterprise = None
        self.is_verified = None
        self.status = None
        self.status_timestamp = None

    def _extract_number_from_jid(self, jid):
        """
        Extrai o número de telefone do JID.

        :param jid: JID no formato 'número@c.us' ou 'número-número@g.us'
        :return: Número de telefone extraído
        """
        if jid and "@" in jid:
            return jid.split("@")[0]
        return jid

    def update_profile_pic(self, new_pic_url):
        """
        Atualiza a URL da imagem de perfil do contato.

        :param new_pic_url: Nova URL da imagem de perfil.
        """
        self.profile_pic_url = new_pic_url
        self.updated_at = datetime.now()

    def __repr__(self):
        """
        Retorna uma representação legível do contato.
        """
        return (
            f"Contact(id={self.id}, remote_jid={self.remote_jid}, "
            f"push_name={self.push_name or 'None'}, number={self.number})"
        )
