import os


class AcoesSimuladas:
    """Substitui JarvisActions no modo seguro: anuncia, nao executa.

    Usada tanto pelo --simular do executar_protocolo.py quanto pelo
    "modo_seguro" do config.json, para as palmas em jarvis.py.
    """

    def __init__(self, config, logger, windows):
        self.config = config
        self.logger = logger

    def _anunciar(self, texto):
        print("  [simulado] " + texto)
        self.logger.info("[simulado] " + texto)

    def tocar_audio(self, nome_arquivo, nome_audio):
        caminho = os.path.join(self.config["pasta_projeto"], nome_arquivo)
        existe = "existe" if os.path.exists(caminho) else "NAO ENCONTRADO"
        self._anunciar("tocaria o {0}: {1} ({2})".format(nome_audio, nome_arquivo, existe))
        return True

    def abrir_spotify_principal(self):
        self._anunciar("abriria a musica principal e moveria para a tela {0}".format(
            self.config["tela_spotify"]))

    def abrir_playlist_fnb(self):
        self._anunciar("abriria a playlist FNB e clicaria no play calibrado")

    def abrir_opera(self):
        self._anunciar("abriria o Opera na tela {0}".format(self.config["tela_opera"]))

    def abrir_url(self, url, nome_acao):
        self._anunciar("abriria {0}: {1}".format(nome_acao, url))
        return True

    def abrir_vault(self):
        self._anunciar("abriria o vault no explorador de arquivos: {0}".format(
            self.config.get("caminho_vault", r"C:\SegundoCerebro")))
        return True

    def abrir_nota_vault(self, caminho_relativo):
        self._anunciar("abriria a nota do vault: {0}".format(caminho_relativo))
        return True

    def abrir_teams(self):
        return self.abrir_url("msteams:", "Microsoft Teams")

    def abrir_gmail(self):
        return self.abrir_url("https://mail.google.com", "Gmail")

    def abrir_linkedin(self):
        return self.abrir_url("https://www.linkedin.com", "LinkedIn")
