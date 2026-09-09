import queue

import keyboard


class AtalhoTeclado:
    """Atalhos de teclado globais como alternativa as palmas - util quando ha
    gente dormindo em casa e bater palma nao e opcao.

    Cada combinacao Ctrl+Alt+<N> dispara o mesmo protocolo que N palmas,
    lendo direto do mapa_palmas do config - nao precisa tocar aqui pra
    adicionar um protocolo novo.
    """

    def __init__(self, logger, mapa_palmas):
        self.logger = logger
        self.mapa_palmas = mapa_palmas
        self._pedidos = queue.Queue()
        self._combinacoes_ativas = []

    def iniciar(self):
        for chave in self.mapa_palmas:
            combinacao = f"ctrl+alt+{chave}"
            try:
                keyboard.add_hotkey(combinacao, self._disparar, args=(chave,))
                self._combinacoes_ativas.append(combinacao)
            except Exception as erro:
                self.logger.error(f"Não consegui registrar o atalho {combinacao}: {erro}")

        if self._combinacoes_ativas:
            descricao = ", ".join(
                f"Ctrl+Alt+{chave} = {self.mapa_palmas[chave]}" for chave in self.mapa_palmas
            )
            self.logger.info(f"Atalhos de teclado ativos: {descricao}.")

    def _disparar(self, chave):
        self.logger.info(f"Atalho Ctrl+Alt+{chave} pressionado (equivale a {chave} palmas).")
        self._pedidos.put(int(chave))

    def obter_pedido(self):
        try:
            return self._pedidos.get_nowait()
        except queue.Empty:
            return None

    def parar(self):
        for combinacao in self._combinacoes_ativas:
            try:
                keyboard.remove_hotkey(combinacao)
            except Exception:
                pass
        self._combinacoes_ativas = []
