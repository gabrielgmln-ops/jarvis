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

    def abrir_spotify_por_link(self, link_spotify, nome_acao):
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
            self.logger.error("Não consegui capturar a janela ativa do Spotify.")
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
            self.logger.error("Não consegui capturar a janela ativa da playlist FNB.")
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