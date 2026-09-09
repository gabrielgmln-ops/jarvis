import os
import subprocess
import time

import pyautogui
from playsound import playsound


class JarvisActions:
    def __init__(self, config, logger, windows):
        self.config = config
        self.logger = logger
        self.windows = windows

        self.pasta_projeto = config["pasta_projeto"]

    def tocar_audio(self, nome_arquivo, nome_audio):
        caminho_audio = os.path.join(self.pasta_projeto, nome_arquivo)

        if not os.path.exists(caminho_audio):
            self.logger.error(f"Arquivo de {nome_audio} não encontrado: {caminho_audio}")
            return False

        try:
            self.logger.info(f"Reproduzindo {nome_audio}.")
            playsound(caminho_audio)
            return True

        except Exception as erro:
            self.logger.error(f"Erro ao reproduzir {nome_audio}: {erro}")
            return False

    def _spotify_instalado(self):
        caminho_padrao = os.path.join(
            os.environ.get("APPDATA", ""), "Spotify", "Spotify.exe"
        )
        return os.path.exists(caminho_padrao)

    def abrir_spotify_por_link(self, link_spotify, nome_acao):
        if not self._spotify_instalado():
            self.logger.error(
                f"{nome_acao}: não encontrei o Spotify em %APPDATA%\\Spotify\\Spotify.exe. "
                "Vou tentar abrir mesmo assim (pode estar em outro lugar), mas se não "
                "abrir, instale em spotify.com/download ou abra manualmente."
            )

        try:
            subprocess.Popen(f'start "" "{link_spotify}"', shell=True)
            self.logger.info(f"{nome_acao} aberto no Spotify.")
            return True

        except Exception as erro:
            self.logger.error(f"Erro ao abrir {nome_acao}: {erro}")
            return False

    def abrir_spotify_principal(self):
        if not self.abrir_spotify_por_link(
            self.config["link_musica_spotify"],
            "Música principal"
        ):
            return

        time.sleep(float(self.config["tempo_espera_spotify"]))

        janela_spotify = self.windows.obter_janela_ativa(tentativas=8, intervalo=0.5)

        if not janela_spotify:
            self.logger.error(
                "Spotify não abriu a tempo (nenhuma janela nova apareceu). "
                "Confira se está instalado e se o link do protocolo é válido."
            )
            return

        self.logger.info(f"Janela ativa capturada para Spotify: {janela_spotify.title}")

        self.windows.mover_para_tela(
            janela=janela_spotify,
            indice_tela=int(self.config["tela_spotify"]),
            nome_app="Spotify"
        )

    def clicar_play_playlist_fnb(self, janela_spotify):
        if not bool(self.config["clicar_play_playlist_fnb"]):
            self.logger.info("Clique automático no play da playlist FNB está desativado.")
            return

        try:
            if janela_spotify.isMinimized:
                janela_spotify.restore()

            janela_spotify.activate()
            time.sleep(0.5)

            x = janela_spotify.left + int(self.config["play_fnb_offset_x"])
            y = janela_spotify.top + int(self.config["play_fnb_offset_y"])

            self.logger.info(f"Clicando no Play da playlist FNB em x={x}, y={y}.")
            pyautogui.click(x, y)

        except Exception as erro:
            self.logger.error(f"Erro ao clicar no Play da playlist FNB: {erro}")

    def abrir_playlist_fnb(self):
        if not self.abrir_spotify_por_link(
            self.config["link_playlist_fnb"],
            "Playlist FNB"
        ):
            return

        time.sleep(float(self.config["tempo_espera_playlist_fnb"]))

        janela_spotify = self.windows.obter_janela_ativa(tentativas=8, intervalo=0.5)

        if not janela_spotify:
            self.logger.error(
                "Spotify não abriu a tempo para a playlist FNB (nenhuma janela nova "
                "apareceu). Confira se está instalado e se o link da playlist é válido."
            )
            return

        self.logger.info(f"Janela ativa capturada para playlist FNB: {janela_spotify.title}")

        self.windows.mover_para_tela(
            janela=janela_spotify,
            indice_tela=int(self.config["tela_spotify"]),
            nome_app="Spotify FNB"
        )

        time.sleep(1.0)
        self.clicar_play_playlist_fnb(janela_spotify)

    def abrir_opera(self):
        janela_opera = self.windows.encontrar_janela_por_titulo(
            "Opera",
            tentativas=5,
            intervalo=0.5
        )

        if not janela_opera:
            try:
                subprocess.Popen("start opera", shell=True)
                self.logger.info("Opera aberto.")
                time.sleep(3)

            except Exception as erro:
                self.logger.error(f"Erro ao abrir Opera: {erro}")
                return

            janela_opera = self.windows.encontrar_janela_por_titulo(
                "Opera",
                tentativas=12,
                intervalo=0.5
            )

        if not janela_opera:
            self.logger.error("Não encontrei a janela do Opera.")
            return

        self.windows.mover_para_tela(
            janela=janela_opera,
            indice_tela=int(self.config["tela_opera"]),
            nome_app="Opera"
        )

    def abrir_url(self, url, nome_acao):
        try:
            subprocess.Popen(f'start "" "{url}"', shell=True)
            self.logger.info(f"{nome_acao} aberto.")
            return True
        except Exception as erro:
            self.logger.error(f"Erro ao abrir {nome_acao}: {erro}")
            return False

    def abrir_vault(self):
        caminho_vault = self.config.get("caminho_vault", r"C:\SegundoCerebro")
        if not os.path.isdir(caminho_vault):
            self.logger.error(f"Pasta do vault não encontrada: {caminho_vault}")
            return False
        return self.abrir_url(caminho_vault, "Vault (explorador de arquivos)")

    def abrir_nota_vault(self, caminho_relativo):
        caminho_vault = self.config.get("caminho_vault", r"C:\SegundoCerebro")
        caminho = os.path.join(caminho_vault, caminho_relativo)
        if not os.path.exists(caminho):
            self.logger.error(f"Nota não encontrada: {caminho}")
            return False
        return self.abrir_url(caminho, f"Nota '{caminho_relativo}'")

    def abrir_teams(self):
        return self.abrir_url("msteams:", "Microsoft Teams")

    def abrir_gmail(self):
        return self.abrir_url("https://mail.google.com", "Gmail")

    def abrir_linkedin(self):
        return self.abrir_url("https://www.linkedin.com", "LinkedIn")