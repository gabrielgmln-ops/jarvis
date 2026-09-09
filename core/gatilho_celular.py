import os


class GatilhoCelular:
    """Alcance pelo celular: uma pasta vigiada dentro do vault (que ja
    sincroniza pelo Google Drive) onde um arquivo com o nome do protocolo
    dispara a execucao. Sem app novo, sem conta nova - so soltar um arquivo
    do celular numa pasta que o computador ja ve.

    Uso: crie um arquivo vazio chamado "inicial.txt" (ou "fnb.txt", etc.) na
    pasta vigiada pelo app do Google Drive no celular. Em ate alguns
    segundos o JARVIS dispara o protocolo e move o arquivo pra
    "processados/", pra nao disparar nem duas vezes nem em loop.
    """

    def __init__(self, logger, pasta_vigiada, protocolos_validos):
        self.logger = logger
        self.pasta_vigiada = pasta_vigiada
        self.pasta_processados = os.path.join(pasta_vigiada, "processados")
        self.protocolos_validos = set(protocolos_validos)

        os.makedirs(self.pasta_vigiada, exist_ok=True)
        os.makedirs(self.pasta_processados, exist_ok=True)

    def verificar(self):
        """Devolve o nome do protocolo pedido, ou None. Move o arquivo pra
        'processados' assim que le, pra nao disparar de novo."""
        try:
            arquivos = sorted(os.listdir(self.pasta_vigiada))
        except OSError as erro:
            self.logger.error(f"Não consegui ler a pasta de gatilhos do celular: {erro}")
            return None

        for nome in arquivos:
            caminho = os.path.join(self.pasta_vigiada, nome)
            if not os.path.isfile(caminho):
                continue

            chave = os.path.splitext(nome)[0].strip().lower()

            if chave not in self.protocolos_validos:
                self.logger.error(
                    f"Gatilho pelo celular com nome desconhecido: '{nome}'. "
                    f"Válidos: {', '.join(sorted(self.protocolos_validos))}."
                )
                self._arquivar(caminho, nome)
                continue

            self._arquivar(caminho, nome)
            self.logger.info(f"Gatilho pelo celular: '{chave}' (arquivo {nome}).")
            return chave

        return None

    def _arquivar(self, caminho, nome):
        try:
            destino = os.path.join(self.pasta_processados, nome)
            if os.path.exists(destino):
                os.remove(destino)
            os.replace(caminho, destino)
        except OSError as erro:
            self.logger.error(f"Não consegui arquivar o gatilho '{nome}': {erro}")
