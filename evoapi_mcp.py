# Path: evoapi_mcp\evoapi_mcp.py

from mcp.server.fastmcp import FastMCP
from group_controller import GroupController
from datetime import datetime
from send_message import SendMessage
from instance_config import InstanceConfig

# Inicializa o servidor FastMCP com nome "pong"
mcp = FastMCP("evoapi_mcp")


@mcp.tool(name="list_instances")
def list_instances() -> str:
    """
    Lista as instâncias Evolution API disponíveis (sem expor tokens).
    """
    instances = InstanceConfig.load_instances()

    if not instances:
        return (
            "Nenhuma instância configurada. Defina EVO_INSTANCES com ids separados por "
            "vírgula e, para cada id, as variáveis EVO_INSTANCE_<ID>_URL, "
            "EVO_INSTANCE_<ID>_TOKEN e opcionalmente EVO_INSTANCE_<ID>_NAME. "
            "Caso use o formato legado, defina EVO_API_URL e EVO_API_TOKEN."
        )

    default_id = InstanceConfig.get_default_id()
    result = "Instâncias disponíveis:\n"
    for inst in instances:
        default_mark = " (padrão)" if inst.id == default_id else ""
        result += f"- id: {inst.id}, nome: {inst.name}, url: {inst.url}{default_mark}\n"

    return result


@mcp.tool(name="get_groups")
def get_groups(instance_id: str | None = None) -> str:
    """
    Recupera e retorna uma lista formatada de grupos do WhatsApp disponíveis.

    Esta ferramenta permite ao agente obter os grupos cadastrados, exibindo
    informações relevantes como o ID do grupo e seu nome, em formato textual.
    A resposta pode ser usada para seleção posterior de um grupo para envio
    de mensagens.

    Returns:
        str: Lista de grupos no formato:
            "Grupo ID: <id>, Nome: <nome>\n"
    """
    controller = GroupController(instance_id)
    groups = controller.fetch_groups()

    string_groups = ""
    for grupo in groups:
        string_groups += f"Grupo ID: {grupo.group_id}, Nome: {grupo.name}\n"

    return string_groups


@mcp.tool(name="get_group_messages")
def get_group_messages(group_id: str, start_date: str, end_date: str, instance_id: str | None = None) -> str:
    """
    Recupera as mensagens enviadas em um grupo do WhatsApp dentro de um intervalo de datas especificado.

    Esta ferramenta permite ao agente acessar o histórico de conversas de um grupo,
    retornando as mensagens publicadas entre `start_date` e `end_date`, com detalhes
    como remetente, horário, tipo da mensagem e conteúdo textual.

    Args:
        group_id (str): Identificador único do grupo do WhatsApp.
        start_date (str): Data e hora de início no formato 'YYYY-MM-DD HH:MM:SS'.
        end_date (str): Data e hora de término no formato 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        str: Lista de mensagens formatadas, com os campos:
            - Usuário
            - Data e hora
            - Tipo da mensagem
            - Texto

        Cada mensagem é separada por um delimitador visual.
    """
    controller = GroupController(instance_id)
    messages = controller.get_messages(group_id, start_date, end_date)

    messages_string = ""
    for message in messages:
        messages_string += f"Mensagem -----------------------------------\n"
        messages_string += f"Usuário: {message.push_name}\n"
        messages_string += f"Data e hora: {datetime.fromtimestamp(message.message_timestamp).strftime('%d/%m/%Y %H:%M:%S')}\n"
        messages_string += f"Tipo: {message.message_type}\n"
        messages_string += f"Texto: {message.get_text()}\n"

    return messages_string


def _send_message(recipient: str, message: str, instance_id: str | None = None) -> str:
    """
    Método privado que encapsula a lógica comum de envio de mensagens.

    Args:
        recipient (str): ID do destinatário (grupo ou número de telefone)
        message (str): Conteúdo da mensagem

    Returns:
        str: Mensagem de sucesso ou erro
    """
    send = SendMessage(instance_id)

    send.textMessage(recipient, message)
    return "Mensagem enviada com sucesso"


@mcp.tool(name="send_message_to_group")
def send_message_to_group(group_id: str, message: str, instance_id: str | None = None) -> str:
    """
    Envia uma mensagem de texto para um grupo específico do WhatsApp.

    Esta ferramenta permite ao agente enviar mensagens para grupos do WhatsApp
    utilizando a API do WhatsApp. A mensagem será entregue ao grupo identificado
    pelo group_id fornecido.

    Args:
        group_id (str): Identificador único do grupo do WhatsApp no formato
            'XXXXXXXXXXXXXXXXX@g.us'. Este ID pode ser obtido através da
            ferramenta get_groups().
        message (str): Conteúdo da mensagem a ser enviada. Pode conter texto
            formatado, emojis e quebras de linha.

    Returns:
        str: Mensagem indicando o resultado da operação:
            - "Mensagem enviada com sucesso" em caso de êxito
            - "Erro ao enviar mensagem: <descrição>" em caso de falha

    Raises:
        Exception: Possíveis erros durante o envio da mensagem, como:
            - Grupo não encontrado
            - Problemas de conexão
            - Falha na autenticação
            - Formato inválido de mensagem
    """
    return _send_message(group_id, message, instance_id)


@mcp.tool(name="send_message_to_phone")
def send_message_to_phone(cellphone: str, message: str, instance_id: str | None = None) -> str:
    """
    Envia uma mensagem de texto para um número de telefone específico via WhatsApp.
    Somente use para enviar mensagens para números de telefone
    explicitamente. Caso contrario use a função send_message_to_group.
    Esta ferramenta permite ao agente enviar mensagens diretamente para números
    de telefone individuais utilizando a API do WhatsApp. A mensagem será entregue
    ao destinatário somente se o número estiver registrado no WhatsApp.

    Args:
        cellphone (str): Número do telefone no formato internacional, incluindo
            código do país e DDD, sem caracteres especiais.
            se por acaso falta o 55, coloque 55 coloque o 55 na frente do numero.
            Mas o usuário tem que informa o DDD obrigatoriamente.
            Exemplo: '5511999999999' para um número de São Paulo, Brasil.

        message (str): Conteúdo da mensagem a ser enviada. Pode conter texto
            formatado, emojis e quebras de linha.

    Returns:
        str: Mensagem indicando o resultado da operação:
            - "Mensagem enviada com sucesso" em caso de êxito
            - "Erro ao enviar mensagem: <descrição>" em caso de falha

    Raises:
        Exception: Possíveis erros durante o envio da mensagem, como:
            - Número inválido ou mal formatado
            - Número não registrado no WhatsApp
            - Problemas de conexão
            - Falha na autenticação
            - Formato inválido de mensagem
    """
    return _send_message(cellphone, message, instance_id)


# ----------------------------------------------
# acrescimo de ferramentas de contatos
# ----------------------------------------------
from contact_controller import ContactController


@mcp.tool(name="get_contacts")
def get_contacts(instance_id: str | None = None) -> str:
    """
    Recupera e retorna uma lista formatada de contatos do WhatsApp disponíveis.

    Esta ferramenta permite ao agente obter os contatos cadastrados, exibindo
    informações relevantes como o ID do contato, JID e nome, em formato textual.
    A resposta pode ser usada para seleção posterior de um contato para envio
    de mensagens.

    Returns:
        str: Lista de contatos no formato:
            "Contato ID: <id>, JID: <remote_jid>, Nome: <push_name>\n"
    """
    controller = ContactController(instance_id)
    contacts = controller.fetch_contacts()

    string_contacts = ""
    for contato in contacts:
        string_contacts += f"Contato ID: {contato.id}, JID: {contato.remote_jid}, Nome: {contato.push_name or 'Não definido'}\n"

    return string_contacts


@mcp.tool(name="get_contacts_by_name")
def get_contacts_by_name(name: str, instance_id: str | None = None) -> str:
    """
    Recupera e retorna uma lista formatada de contatos do WhatsApp disponíveis.

    Esta ferramenta permite ao agente obter os contatos cadastrados, exibindo
    informações relevantes como o ID do contato, JID e nome, em formato textual.
    A resposta pode ser usada para seleção posterior de um contato para envio
    de mensagens.

    Returns:
        str: Lista de contatos no formato:
            "Contato ID: <id>, JID: <remote_jid>, Nome: <push_name>\n"
    """
    controller = ContactController(instance_id)
    contacts = controller.fetch_contacts_by_name(name)

    string_contacts = ""
    for contato in contacts:
        string_contacts += f"Contato ID: {contato.id}, JID: {contato.remote_jid}, Nome: {contato.push_name or 'Não definido'}\n"

    return string_contacts


@mcp.tool(name="get_contacts_by_phone_number")
def get_contacts_by_phone_number(phone_number: str, instance_id: str | None = None) -> str:
    """
    Recupera e retorna uma lista formatada de contatos do WhatsApp disponíveis.

    Esta ferramenta permite ao agente obter os contatos cadastrados, exibindo
    informações relevantes como o ID do contato, JID e nome, em formato textual.
    A resposta pode ser usada para seleção posterior de um contato para envio
    de mensagens.

    Returns:
        str: Lista de contatos no formato:
            "Contato ID: <id>, JID: <remote_jid>, Nome: <push_name>\n"
    """
    controller = ContactController(instance_id)
    contacts = controller.fetch_contacts_by_phone_number(phone_number)

    string_contacts = ""
    for contato in contacts:
        string_contacts += f"Contato ID: {contato.id}, JID: {contato.remote_jid}, Nome: {contato.push_name or 'Não definido'}\n"

    return string_contacts


@mcp.tool(name="find_contact_by_number")
def find_contact_by_number(phone_number: str, instance_id: str | None = None) -> str:
    """
    Localiza um contato pelo número de telefone e retorna suas informações detalhadas.

    Esta ferramenta permite ao agente buscar informações de um contato específico
    usando seu número de telefone, facilitando a identificação do contato para
    interações posteriores.

    Args:
        phone_number (str): Número de telefone a ser pesquisado, preferencialmente
            no formato internacional (ex: '5511999999999').

    Returns:
        str: Informações detalhadas do contato no formato:
            "ID: <id>
             JID: <remote_jid>
             Nome: <push_name>
             Número: <número extraído do JID>
             Foto de Perfil: <URL da foto ou 'Não disponível'>
             Criado em: <data de criação>
             Última atualização: <data de atualização>"

        Se o contato não for encontrado, retorna uma mensagem informativa.
    """
    controller = ContactController(instance_id)
    contact = controller.find_contact_by_number(phone_number)

    if not contact:
        return f"Nenhum contato encontrado com o número {phone_number}."

    # Formatando as datas
    created_at = "Não disponível"
    if contact.created_at:
        if isinstance(contact.created_at, str):
            created_at = contact.created_at
        else:
            created_at = contact.created_at.strftime("%d/%m/%Y %H:%M:%S")

    updated_at = "Não disponível"
    if contact.updated_at:
        if isinstance(contact.updated_at, str):
            updated_at = contact.updated_at
        else:
            updated_at = contact.updated_at.strftime("%d/%m/%Y %H:%M:%S")

    contact_info = f"ID: {contact.id}\n"
    contact_info += f"JID: {contact.remote_jid}\n"
    contact_info += f"Nome: {contact.push_name or 'Não definido'}\n"
    contact_info += f"Número: {contact.number}\n"
    contact_info += f"Foto de Perfil: {contact.profile_pic_url or 'Não disponível'}\n"
    contact_info += f"Criado em: {created_at}\n"
    contact_info += f"Última atualização: {updated_at}\n"

    return contact_info


@mcp.tool(name="get_contact_profile_picture")
def get_contact_profile_picture(remote_jid: str, instance_id: str | None = None) -> str:
    """
    Recupera a URL da foto de perfil de um contato específico.

    Esta ferramenta permite ao agente obter a imagem de perfil atual de um contato,
    retornando a URL onde a imagem está hospedada.

    Args:
        remote_jid (str): JID remoto do contato no formato 'número@c.us'.

    Returns:
        str: URL da imagem de perfil do contato ou uma mensagem informativa caso
             não seja possível obter a imagem.
    """
    controller = ContactController(instance_id)
    picture_url = controller.get_profile_picture(remote_jid)

    if picture_url:
        return f"URL da foto de perfil: {picture_url}"
    else:
        return "Não foi possível obter a foto de perfil deste contato. O contato pode não ter uma imagem definida ou as permissões podem estar restritas."


@mcp.tool(name="get_contact_common_groups")
def get_contact_common_groups(remote_jid: str, instance_id: str | None = None) -> str:
    """
    Recupera os grupos em comum com um contato específico.

    Esta ferramenta permite ao agente descobrir quais grupos são compartilhados
    entre o usuário e um contato específico, facilitando a compreensão do contexto
    social e organizacional.

    Args:
        remote_jid (str): JID remoto do contato no formato 'número@c.us'.

    Returns:
        str: Lista de grupos em comum no formato:
            "Grupos em comum com <nome do contato>:
             - Grupo JID: <jid>"

        Se nenhum grupo em comum for encontrado, retorna uma mensagem informativa.
    """
    contact_controller = ContactController(instance_id)
    group_controller = GroupController(instance_id)

    # Busca o contato para obter o nome
    contact = contact_controller.find_contact_by_jid(remote_jid)
    if not contact:
        return f"Contato com JID {remote_jid} não encontrado."

    # Busca os grupos em comum
    common_groups_ids = contact_controller.get_common_groups(remote_jid)

    if not common_groups_ids:
        return f"Nenhum grupo em comum encontrado com {contact.push_name or contact.number}."

    # Carrega os grupos para obter os nomes
    group_controller.fetch_groups()

    result = f"Grupos em comum com {contact.push_name or contact.number}:\n"
    for group_id in common_groups_ids:
        group = group_controller.find_group_by_id(group_id)
        if group:
            result += f"- Grupo ID: {group.group_id}, Nome: {group.name}\n"
        else:
            result += f"- Grupo ID: {group_id}, Nome: Não disponível\n"

    return result


@mcp.tool(name="check_phone_exists")
def check_phone_exists(phone_number: str, instance_id: str | None = None) -> str:
    """
    Verifica se um número de telefone está registrado no WhatsApp.

    Esta ferramenta permite ao agente confirmar se um número de telefone específico
    está ativo no WhatsApp antes de tentar enviar mensagens para ele.

    Args:
        phone_number (str): Número de telefone a ser verificado, preferencialmente
            no formato internacional (ex: '5511999999999').

    Returns:
        str: Mensagem indicando se o número existe ou não no WhatsApp.
    """
    controller = ContactController(instance_id)
    exists = controller.check_contact_exists(phone_number)

    if exists:
        return f"O número {phone_number} está registrado no WhatsApp."
    else:
        return f"O número {phone_number} não está registrado no WhatsApp ou não foi possível verificar."


# ----------------------------------------------
# fim dos acrescimos de ferramentas de contatos
# ----------------------------------------------
# acrescimo de ferramentas de mensagens
# ----------------------------------------------

from message_controller import MessageController


@mcp.tool(name="fecth_all_contact_messages")
def fecth_all_contact_messages(remote_jid: str, instance_id: str | None = None) -> str:
    """
    Retorna todas as mensagens trocadas com um contato específico do WhatsApp.

    Esta ferramenta recupera todo o histórico disponível de mensagens de um contato
    retornando as mensagens em formato csv.

    Args:
        remote_jid (str): JID do contato no formato 'número@c.us'.

    Returns:
        str: As mensagens exportadas em formato csv.
    """
    controller = MessageController(instance_id)
    filepath = controller.fetch_all_messages(remote_jid)
    return (
        f"Arquivo de mensagens exportado: {filepath}"
        if filepath
        else "Erro ao exportar mensagens."
    )


@mcp.tool(name="fecth_interval_contact_messages")
def fecth_interval_contact_messages(
    remote_jid: str, start_date: str, end_date: str, instance_id: str | None = None
) -> str:
    """
    Retorna todas as mensagens trocadas com um contato específico do WhatsApp dentro de um intervalo de datas..

    Esta ferramenta busca todas as mensagens trocadas com o contato especificado
    entre `start_date` e `end_date`, retornando as mensagens em formato csv.

    Args:
        remote_jid (str): JID do contato no formato 'número@c.us'.
        start_date (str): Data e hora de início (formato 'YYYY-MM-DD HH:MM:SS').
        end_date (str): Data e hora de término (formato 'YYYY-MM-DD HH:MM:SS').

    Returns:
        str: As mensagens exportadas em formato csv.
    """
    controller = MessageController(instance_id)
    filepath = controller.fetch_interval_messages(remote_jid, start_date, end_date)
    return (
        f"Arquivo de mensagens exportado: {filepath}"
        if filepath
        else "Erro ao exportar mensagens no intervalo."
    )


# ----------------------------------------------
# fim dos acrescimos de ferramentas de mensagens
# ----------------------------------------------


if __name__ == "__main__":

    mcp.run(transport="stdio")
    #print(get_group_messages("120363400095683544@g.us", "2025-05-01 00:00:00", "2025-05-31 23:59:59"))
