import os
import subprocess
import threading
import time

from core.acoes_simuladas import AcoesSimuladas
from core.jarvis_bridge import JarvisBridge


class JarvisProtocols:
    def __init__(self, config, logger, actions, bandeja=None):
        self.config = config
        self.logger = logger
        self.actions = actions
        self.jarvis_bridge = JarvisBridge(logger, bandeja=bandeja)
        self._protocolos = {
            "inicial": self.protocolo_inicial,
            "fnb": self.protocolo_fnb,
            "perguntar": self.protocolo_perguntar_jarvis,
            "estudo": self.protocolo_estudo,
            "candidatura": self.protocolo_candidatura,
            "desligar": self.protocolo_desligar,
        }

    def protocolo_inicial(self):
        self.logger.info("Executando Protocolo Inicial.")

        self.actions.abrir_spotify_principal()

        tempo_antes_opera = float(self.config["tempo_antes_opera"])
        self.logger.info(f"Aguardando {tempo_antes_opera} segundo(s) antes de abrir o Opera.")
        time.sleep(tempo_antes_opera)

        self.actions.abrir_opera()

        tempo_antes_audio = float(self.config["tempo_antes_audio"])
        self.logger.info(f"Aguardando {tempo_antes_audio} segundo(s) antes do áudio de ativação.")
        time.sleep(tempo_antes_audio)

        self.actions.tocar_audio(
            self.config["audio_ativacao"],
            "áudio de ativação"
        )

        self.logger.info("Protocolo Inicial concluído.")
        return True

    def protocolo_fnb(self):
        self.logger.info("Executando Protocolo FNB.")

        self.actions.tocar_audio(
            self.config["audio_protocolo_fnb"],
            "áudio do Protocolo FNB"
        )

        self.actions.abrir_playlist_fnb()

        self.logger.info("Protocolo FNB concluído.")
        return True

    def protocolo_perguntar_jarvis(self):
        self.logger.info("Executando Protocolo Perguntar ao Jarvis.")

        pergunta = self.config.get(
            "pergunta_jarvis",
            "Me dê uma dica rápida e útil pra agora."
        )
        resposta = self.jarvis_bridge.perguntar(pergunta)
        self.jarvis_bridge.mostrar_resposta(resposta)

        self.logger.info("Protocolo Perguntar ao Jarvis concluído.")
        return True

    def protocolo_estudo(self):
        self.logger.info("Executando Protocolo de Estudo.")

        self.actions.abrir_vault()
        self.actions.abrir_teams()
        self._iniciar_pomodoro()

        self.logger.info("Protocolo de Estudo concluído.")
        return True

    def protocolo_candidatura(self):
        self.logger.info("Executando Protocolo de Candidatura.")

        self.actions.abrir_gmail()
        self.actions.abrir_linkedin()
        self.actions.abrir_nota_vault(os.path.join("04 - Carreira", "Rotina de candidatura.md"))
        self.actions.abrir_nota_vault(os.path.join("04 - Carreira", "Banco de Respostas.md"))

        self.logger.info("Protocolo de Candidatura concluído.")
        return True

    def protocolo_desligar(self):
        self.logger.info("Executando Protocolo de Desligar.")

        # So o commit do dia - fechar janelas de terceiros fica de fora de
        # proposito: um "fecha tudo" as cegas arrisca perder trabalho nao
        # salvo em outro programa. Ver Roteiro do mega projeto, secao 6.
        if isinstance(self.actions, AcoesSimuladas):
            self.logger.info("[simulado] commitaria C:\\JARVIS e o vault, se houvesse mudança.")
        else:
            self._commit_se_precisar(self.config["pasta_projeto"], "JARVIS")
            self._commit_se_precisar(self.config.get("caminho_vault", r"C:\SegundoCerebro"), "vault")

        self.logger.info("Protocolo de Desligar concluído.")
        return True

    def _iniciar_pomodoro(self):
        minutos = float(self.config.get("duracao_pomodoro_min", 25))
        self.logger.info(f"Pomodoro de {minutos:.0f} minuto(s) iniciado.")

        def avisar_depois():
            time.sleep(minutos * 60)
            self.jarvis_bridge.notificar(
                f"Pomodoro de {minutos:.0f} minutos terminou. Hora de uma pausa.",
                "J.A.R.V.I.S. — Pomodoro",
            )
            self.logger.info("Pomodoro terminou, notificação enviada.")

        threading.Thread(target=avisar_depois, daemon=True).start()

    def _commit_se_precisar(self, caminho_repo, nome):
        try:
            status = subprocess.run(
                ["git", "-C", caminho_repo, "status", "--porcelain"],
                capture_output=True, text=True, timeout=15,
            )
        except Exception as erro:
            self.logger.error(f"Não consegui checar o status do git em {nome}: {erro}")
            return False

        if status.returncode != 0:
            self.logger.error(f"'{caminho_repo}' não parece um repositório git válido.")
            return False

        if not status.stdout.strip():
            self.logger.info(f"Nada para commitar em {nome}.")
            return True

        try:
            subprocess.run(["git", "-C", caminho_repo, "add", "-A"], check=True, timeout=30)
            subprocess.run(
                ["git", "-C", caminho_repo, "commit", "-m", "Commit automatico do Protocolo de Desligar"],
                check=True, timeout=30,
            )
            self.logger.info(f"Commit automático feito em {nome}.")
            return True
        except Exception as erro:
            self.logger.error(f"Falha ao commitar {nome}: {erro}")
            return False

    def executar_por_palmas(self, quantidade_palmas):
        self.logger.info(f"Quantidade de palmas identificada: {quantidade_palmas}")

        mapa_palmas = self.config.get("mapa_palmas", {})
        chave_protocolo = mapa_palmas.get(str(quantidade_palmas))

        if chave_protocolo is None:
            self.logger.info(f"Nenhum protocolo associado a {quantidade_palmas} palma(s).")
            return None

        return self.executar_por_nome(chave_protocolo)

    def executar_por_nome(self, chave_protocolo):
        """Dispara um protocolo pelo nome - usado pelas palmas (via
        mapa_palmas) e por outros gatilhos, como o GatilhoCelular."""
        metodo = self._protocolos.get(chave_protocolo)
        if metodo is None:
            self.logger.error(f"'{chave_protocolo}' não é um protocolo conhecido.")
            return None

        return metodo()

    def nomes_protocolos(self):
        return list(self._protocolos.keys())
