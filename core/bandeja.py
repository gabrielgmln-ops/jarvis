import threading

import pystray
from PIL import Image, ImageDraw


COR_ATIVO = (71, 216, 232)     # ciano - mesma linguagem visual das paginas HUD
COR_PAUSADO = (240, 166, 60)   # ambar


def _desenhar_icone(cor):
    imagem = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    desenho = ImageDraw.Draw(imagem)
    desenho.ellipse((6, 6, 58, 58), fill=cor)
    desenho.ellipse((22, 22, 42, 42), fill=(10, 15, 20, 255))
    return imagem


class IconeBandeja:
    """Icone na bandeja do Windows: mostra se o sistema esta ativo ou pausado,
    com "pausar escuta"/"retomar escuta" e "sair" no menu do botao direito.

    `pausado` e `sair` sao threading.Event compartilhados com o laco principal
    em jarvis.py - o icone roda numa thread separada.
    """

    def __init__(self, logger, nome_sistema="J.A.R.V.I.S."):
        self.logger = logger
        self.nome_sistema = nome_sistema
        self.pausado = threading.Event()
        self.sair = threading.Event()
        self._icone = pystray.Icon(
            "jarvis",
            icon=_desenhar_icone(COR_ATIVO),
            title=self._titulo(),
            menu=pystray.Menu(
                pystray.MenuItem(self._texto_pausar, self._alternar_pausa),
                pystray.MenuItem("Sair", self._pedir_saida),
            ),
        )
        self._thread = None

    def _titulo(self):
        estado = "pausado" if self.pausado.is_set() else "ativo"
        return f"{self.nome_sistema} - {estado}"

    def _texto_pausar(self, item):
        return "Retomar escuta" if self.pausado.is_set() else "Pausar escuta"

    def _alternar_pausa(self, icone, item):
        if self.pausado.is_set():
            self.pausado.clear()
            self.logger.info("Escuta retomada pela bandeja.")
        else:
            self.pausado.set()
            self.logger.info("Escuta pausada pela bandeja.")

        icone.icon = _desenhar_icone(COR_PAUSADO if self.pausado.is_set() else COR_ATIVO)
        icone.title = self._titulo()

    def _pedir_saida(self, icone, item):
        self.logger.info("Saída pedida pela bandeja.")
        self.sair.set()
        icone.stop()

    def iniciar(self):
        self._thread = threading.Thread(target=self._icone.run, daemon=True)
        self._thread.start()

    def parar(self):
        try:
            self._icone.stop()
        except Exception:
            pass
