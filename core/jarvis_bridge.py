import ctypes
import os
import shutil
import socket
import subprocess
import time
from urllib.parse import urlparse


class JarvisBridge:
    """Ponte entre o gatilho de palmas e o OpenJarvis (comando 'jarvis').

    Antes de perguntar, confere duas coisas que costumam falhar em silencio:
    se o comando 'jarvis' existe no PATH e se o Ollama esta de pe.
    Quando algo esta fora do ar, a mensagem que aparece na caixa diz
    exatamente o que fazer, em vez de um generico 'nao respondeu'.
    """

    HOST_OLLAMA_PADRAO = "http://localhost:11434"

    def __init__(self, logger, bandeja=None):
        self.logger = logger
        self.bandeja = bandeja

    # ------------------------------------------------------------------ checks

    def _host_ollama(self):
        return os.environ.get("OLLAMA_HOST") or self.HOST_OLLAMA_PADRAO

    def ollama_no_ar(self, tempo_limite=1.5):
        """True se alguem esta escutando na porta do Ollama."""
        alvo = self._host_ollama()
        if "//" not in alvo:
            alvo = "http://" + alvo
        url = urlparse(alvo)
        host = url.hostname or "localhost"
        porta = url.port or 11434

        try:
            with socket.create_connection((host, porta), timeout=tempo_limite):
                return True
        except OSError:
            return False

    def comando_disponivel(self):
        return shutil.which("jarvis") is not None

    def _caminho_ollama_app(self):
        candidato = os.path.join(
            os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama app.exe"
        )
        return candidato if os.path.exists(candidato) else None

    def tentar_iniciar_ollama(self, tentativas=6, intervalo=1.0):
        """Tenta subir o Ollama sozinho. True se conseguiu (ou já estava no ar)."""
        if self.ollama_no_ar():
            return True

        caminho_app = self._caminho_ollama_app()
        try:
            if caminho_app:
                subprocess.Popen([caminho_app], creationflags=subprocess.CREATE_NO_WINDOW)
                self.logger.info("Ollama não estava no ar - abrindo 'ollama app.exe' sozinho.")
            elif shutil.which("ollama"):
                subprocess.Popen(
                    ["ollama", "serve"],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self.logger.info("Ollama não estava no ar - rodando 'ollama serve' sozinho.")
            else:
                self.logger.error("Ollama não está no ar e não encontrei o executável para abrir sozinho.")
                return False
        except Exception as erro:
            self.logger.error(f"Não consegui iniciar o Ollama sozinho: {erro}")
            return False

        for _ in range(tentativas):
            time.sleep(intervalo)
            if self.ollama_no_ar():
                self.logger.info("Ollama subiu sozinho e já está respondendo.")
                return True

        return False

    def diagnosticar(self):
        """Devolve None se esta tudo pronto, ou o texto do problema."""
        if not self.comando_disponivel():
            return ("O comando 'jarvis' nao esta no PATH deste usuario.\n\n"
                    "Abra o PowerShell e teste:  jarvis --version\n"
                    "Se falhar, reinstale o OpenJarvis ou reabra a sessao do Windows.")

        if not self.ollama_no_ar() and not self.tentar_iniciar_ollama():
            return ("O Ollama nao esta rodando e eu nao consegui subir ele sozinho.\n\n"
                    "Abra o PowerShell e rode:  ollama serve\n"
                    "Ou abra o aplicativo do Ollama e espere o icone aparecer na bandeja.\n\n"
                    "Endereco procurado: " + self._host_ollama())

        return None

    # ----------------------------------------------------------------- pergunta

    def perguntar(self, pergunta, tempo_limite=60):
        problema = self.diagnosticar()
        if problema:
            self.logger.error("Pre-checagem falhou: " + problema.splitlines()[0])
            return problema

        self.logger.info(f"Perguntando ao OpenJarvis: {pergunta}")
        pergunta_escapada = pergunta.replace('"', '\\"')

        try:
            resultado = subprocess.run(
                f'jarvis ask "{pergunta_escapada}"',
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=tempo_limite,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except FileNotFoundError:
            self.logger.error("Comando 'jarvis' nao encontrado no momento da chamada.")
            return ("O comando 'jarvis' sumiu do PATH entre a checagem e a chamada.\n"
                    "Teste no PowerShell:  jarvis --version")
        except subprocess.TimeoutExpired:
            self.logger.error(f"OpenJarvis nao respondeu em {tempo_limite} segundo(s).")
            return (f"O OpenJarvis passou de {tempo_limite} segundos sem responder.\n\n"
                    "Costuma ser o modelo carregando pela primeira vez, ou uma resposta\n"
                    "que exigiu ferramentas. Tente de novo em um minuto.")

        if resultado.returncode != 0:
            erro = (resultado.stderr or "").strip()
            self.logger.error(f"OpenJarvis retornou erro: {erro}")
            if not self.ollama_no_ar():
                return ("O Ollama caiu no meio da pergunta.\n\n"
                        "Rode  ollama serve  no PowerShell e tente de novo.")
            return ("O OpenJarvis respondeu com erro:\n\n" + (erro[:600] or "sem detalhe no stderr"))

        resposta = (resultado.stdout or "").strip()
        if not resposta:
            self.logger.error("OpenJarvis respondeu vazio.")
            return "O OpenJarvis respondeu, mas veio vazio. Vale repetir a pergunta."

        self.logger.info(f"Resposta do OpenJarvis: {resposta}")
        return resposta

    # ------------------------------------------------------------------- saida

    def mostrar_resposta(self, resposta):
        texto = resposta if resposta else "O OpenJarvis nao respondeu dessa vez."

        if self._notificar_pela_bandeja(texto):
            return

        # Sem bandeja disponivel: cai pro MessageBox (rouba o foco, mas sempre funciona).
        # MB_OK (0x0) + icone de informacao (0x40) + sempre no topo (0x40000)
        ctypes.windll.user32.MessageBoxW(0, texto, "J.A.R.V.I.S.", 0x40 | 0x40000)

    def _notificar_pela_bandeja(self, texto):
        icone = getattr(self.bandeja, "_icone", None)
        if icone is None:
            return False

        if not getattr(icone.__class__, "HAS_NOTIFICATION", False):
            return False

        try:
            icone.notify(texto, "J.A.R.V.I.S.")
            return True
        except Exception as erro:
            self.logger.error(f"Notificação da bandeja falhou, caindo pro MessageBox: {erro}")
            return False
