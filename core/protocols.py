import time

from core.jarvis_bridge import JarvisBridge


class JarvisProtocols:
    def __init__(self, config, logger, actions):
        self.config = config
        self.logger = logger
        self.actions = actions
        self.jarvis_bridge = JarvisBridge(logger)

    def protocolo_inicial(self):
        self.logger.info("Executando Protocolo Inicial.")

        self.actions.abrir_spotify_principal()

        tempo_antes_opera = float(self.config["tempo_antes_opera"])
        self.logger.info(f"Aguardando {tempo_antes_opera} segundo(s) antes de abrir o Opera.")
        time.sleep(tempo_antes_opera)

        self.actions.abrir_opera()

        tempo_antes_audio = float(self.config["tempo_antes_audio"])
        self.logger.info(f"Aguardando {tempo_antes_audio} segundo(s) antes do áudio de ativação.")
        time.sleep(tempo_antes_audio)

        self.actions.tocar_audio(
            self.config["audio_ativacao"],
            "áudio de ativação"
        )

        self.logger.info("Protocolo Inicial concluído.")
        return False

    def protocolo_fnb(self):
        self.logger.info("Executando Protocolo FNB.")

        self.actions.tocar_audio(
            self.config["audio_protocolo_fnb"],
            "áudio do Protocolo FNB"
        )

        self.actions.abrir_playlist_fnb()

        self.logger.info("Protocolo FNB concluído.")
        return False

    def protocolo_perguntar_jarvis(self):
        self.logger.info("Executando Protocolo Perguntar ao Jarvis.")

        pergunta = self.config.get(
            "pergunta_jarvis",
            "Me dê uma dica rápida e útil pra agora."
        )
        resposta = self.jarvis_bridge.perguntar(pergunta)
        self.jarvis_bridge.mostrar_resposta(resposta)

        self.logger.info("Protocolo Perguntar ao Jarvis concluído.")
        return False

    def executar_por_palmas(self, quantidade_palmas):
        self.logger.info(f"Quantidade de palmas identificada: {quantidade_palmas}")

        if quantidade_palmas == int(self.config["palmas_protocolo_inicial"]):
            return self.protocolo_inicial()

        if quantidade_palmas == int(self.config["palmas_protocolo_fnb"]):
            return self.protocolo_fnb()

        if quantidade_palmas == int(self.config.get("palmas_perguntar_jarvis", 0)):
            return self.protocolo_perguntar_jarvis()

        self.logger.info(f"Nenhum protocolo associado a {quantidade_palmas} palma(s).")
        return True