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
