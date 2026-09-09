import time

import pygetwindow as gw
import win32api
from screeninfo import get_monitors


class WindowController:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def obter_tela(self, indice):
        telas = get_monitors()

        if not telas:
            self.logger.error("Nenhuma tela detectada pelo sistema.")
            return None

        if indice >= len(telas):
            self.logger.info(
                f"Tela {indice} não encontrada ({len(telas)} tela(s) detectada(s) agora, "
                f"provavelmente o segundo monitor está desligado). Usando Tela 0 como fallback."
            )
            indice = 0

        return telas[indice]

    def indice_tela_ativa(self):
        """Em qual tela esta o cursor agora - util pra escolher tela sem
        depender so de um indice fixo no config (ex: perfil por horario que
        quer abrir "na tela onde voce esta", nao numa fixa)."""
        telas = get_monitors()
        if not telas:
            return 0

        try:
            x, y = win32api.GetCursorPos()
        except Exception as erro:
            self.logger.error(f"Não consegui ler a posição do cursor: {erro}")
            return 0

        for i, tela in enumerate(telas):
            if tela.x <= x < tela.x + tela.width and tela.y <= y < tela.y + tela.height:
                return i

        return 0

    def listar_telas_detectadas(self):
        for i, tela in enumerate(get_monitors()):
            self.logger.info(
                f"Tela {i}: x={tela.x}, y={tela.y}, largura={tela.width}, altura={tela.height}"
            )

    def encontrar_janela_por_titulo(self, palavra_chave, tentativas=10, intervalo=0.5):
        for _ in range(tentativas):
            for janela in gw.getAllWindows():
                if janela.title and palavra_chave.lower() in janela.title.lower():
                    return janela

            time.sleep(intervalo)

        return None

    def obter_janela_ativa(self, tentativas=10, intervalo=0.5):
        for _ in range(tentativas):
            janela = gw.getActiveWindow()

            if janela and janela.title:
                return janela

            time.sleep(intervalo)

        return None

    def _com_retry(self, acao, tentativas=3, intervalo=0.4):
        """Tenta a acao (moveTo/resizeTo/maximize) de novo em caso de erro.

        O Windows as vezes recusa SetWindowPos com "Acesso negado" enquanto a
        janela ainda esta terminando de abrir/animar - e um erro transitorio,
        nao uma permissao de verdade (testado: mesmo usuario, nada elevado).
        """
        ultimo_erro = None
        for tentativa in range(1, tentativas + 1):
            try:
                acao()
                return True
            except Exception as erro:
                ultimo_erro = erro
                if tentativa < tentativas:
                    time.sleep(intervalo)
        raise ultimo_erro

    def mover_para_tela(self, janela, indice_tela, nome_app):
        tela = self.obter_tela(indice_tela)

        if tela is None:
            return False

        try:
            if janela.isMinimized:
                janela.restore()

            janela.activate()
            time.sleep(0.5)

            try:
                janela.restore()
                time.sleep(0.4)
            except Exception:
                pass

            self._com_retry(lambda: janela.moveTo(tela.x, tela.y))
            time.sleep(0.5)

            self._com_retry(lambda: janela.resizeTo(tela.width, tela.height))
            time.sleep(0.5)

            self._com_retry(lambda: janela.maximize())
            time.sleep(0.5)

            self.logger.info(f"{nome_app} movido e maximizado na Tela {indice_tela}.")
            return True

        except Exception as erro:
            self.logger.error(f"Erro ao mover {nome_app}: {erro}")
            return False