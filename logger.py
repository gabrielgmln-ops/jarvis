import os
from datetime import datetime


class JarvisLogger:
    def __init__(self, config):
        self.pasta_projeto = config["pasta_projeto"]
        self.caminho_log = os.path.join(self.pasta_projeto, config["arquivo_log"])
        self.tamanho_maximo_mb = float(config["tamanho_maximo_log_mb"])

    def _limpar_log_se_necessario(self):
        if not os.path.exists(self.caminho_log):
            return

        tamanho_mb = os.path.getsize(self.caminho_log) / (1024 * 1024)

        if tamanho_mb >= self.tamanho_maximo_mb:
            with open(self.caminho_log, "w", encoding="utf-8") as arquivo:
                arquivo.write("")

    def _registrar(self, mensagem, nivel):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linha = f"[{agora}] [{nivel}] {mensagem}"

        print(linha)

        try:
            self._limpar_log_se_necessario()

            with open(self.caminho_log, "a", encoding="utf-8") as arquivo:
                arquivo.write(linha + "\n")

        except Exception as erro:
            print(f"Erro ao escrever no log: {erro}")

    def info(self, mensagem):
        self._registrar(mensagem, "INFO")

    def error(self, mensagem):
        self._registrar(mensagem, "ERRO")