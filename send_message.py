import os
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient
from evolutionapi.models.message import MediaMessage, TextMessage

from instance_config import InstanceConfig


class SendMessage:
    def __init__(self, instance_id: str | None = None) -> None:
        # Load env variables
        load_dotenv()

        creds = InstanceConfig.resolve_instance(instance_id)
        self.evo_instance_id = creds.id
        self.evo_instance_token = creds.token
        self.evo_base_url = creds.url
        self.evo_api_token = os.getenv(f"EVO_INSTANCE_{self.evo_instance_id}_APIKEY", os.getenv("EVO_API_TOKEN"))

        self.client = EvolutionClient(base_url=self.evo_base_url, api_token=self.evo_api_token)

    def textMessage(self, number, msg, mentions=None):
        if mentions is None:
            mentions = []

        text_message = TextMessage(number=str(number), text=msg, mentioned=mentions)
        return self.client.messages.send_text(self.evo_instance_id, text_message, self.evo_instance_token)

    def PDF(self, number, pdf_file, caption=""):
        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"Arquivo '{pdf_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="document",
            mimetype="application/pdf",
            caption=caption,
            fileName=os.path.basename(pdf_file),
            media="",
        )

        self.client.messages.send_media(self.evo_instance_id, media_message, self.evo_instance_token, pdf_file)

    def audio(self, number, audio_file, caption=""):
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Arquivo '{audio_file}' não encontrado.")

        audio_message = {
            "number": number,
            "mediatype": "audio",
            "mimetype": "audio/mpeg",
            "caption": caption,
        }

        self.client.messages.send_whatsapp_audio(
            self.evo_instance_id, audio_message, self.evo_instance_token, audio_file
        )
        return "Áudio enviado"

    def image(self, number, image_file, caption=""):
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"Arquivo '{image_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="image",
            mimetype="image/jpeg",
            caption=caption,
            fileName=os.path.basename(image_file),
            media="",
        )

        self.client.messages.send_media(self.evo_instance_id, media_message, self.evo_instance_token, image_file)

        return "Imagem enviada"

    def video(self, number, video_file, caption=""):
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Arquivo '{video_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="video",
            mimetype="video/mp4",
            caption=caption,
            fileName=os.path.basename(video_file),
            media="",
        )

        self.client.messages.send_media(self.evo_instance_id, media_message, self.evo_instance_token, video_file)

        return "Vídeo enviado"

    def document(self, number, document_file, caption=""):
        if not os.path.exists(document_file):
            raise FileNotFoundError(f"Arquivo '{document_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="document",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            caption=caption,
            fileName=os.path.basename(document_file),
            media="",
        )

        self.client.messages.send_media(self.evo_instance_id, media_message, self.evo_instance_token, document_file)

        return "Documento enviado"
