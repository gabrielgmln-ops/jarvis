import threading
import time


class ClapDetector:
    def __init__(self, config, logger):
        self.logger = logger
        self._lock = threading.RLock()

        self.limiar_palma = float(config["limiar_palma"])
        self.intervalo_minimo = float(config["intervalo_minimo"])
        self.tempo_cooldown = float(config["tempo_cooldown"])

        self.duracao_minima = float(config["duracao_minima_palma"])
        self.duracao_maxima = float(config["duracao_maxima_palma"])
        self.fator_queda = float(config["fator_queda_palma"])
        self.ataque_minimo = float(config["ataque_minimo_palma"])

        self.tempo_janela_palmas = float(config["tempo_janela_palmas"])

        self.pico_ativo = False
        self.inicio_pico = 0
        self.volume_anterior = 0

        self.contador_palmas = 0
        self.tempo_ultima_palma = 0
        self.ultimo_pico_valido = 0
        self.ultimo_acionamento = 0

    def resetar_contagem(self):
        with self._lock:
            self.contador_palmas = 0
            self.tempo_ultima_palma = 0
            self.pico_ativo = False
            self.inicio_pico = 0

    def registrar_palma_valida(self, agora):
        if agora - self.ultimo_pico_valido < self.intervalo_minimo:
            return

        self.ultimo_pico_valido = agora
        self.contador_palmas += 1
        self.tempo_ultima_palma = agora

        self.logger.info(f"Palma válida detectada. Total atual: {self.contador_palmas}")

    def analisar_volume(self, volume, agora):
        with self._lock:
            ataque = volume - self.volume_anterior
            limite_queda = self.limiar_palma * self.fator_queda

            if not self.pico_ativo:
                if volume >= self.limiar_palma and ataque >= self.ataque_minimo:
                    self.pico_ativo = True
                    self.inicio_pico = agora

                self.volume_anterior = volume
                return

            duracao_pico = agora - self.inicio_pico

            if duracao_pico > self.duracao_maxima:
                self.pico_ativo = False
                self.inicio_pico = 0
                self.volume_anterior = volume
                return

            if volume <= limite_queda:
                self.pico_ativo = False

                if self.duracao_minima <= duracao_pico <= self.duracao_maxima:
                    self.registrar_palma_valida(agora)

                self.inicio_pico = 0

            self.volume_anterior = volume

    def obter_quantidade_se_pronta(self):
        with self._lock:
            if self.contador_palmas == 0:
                return None

            agora = time.time()

            if agora - self.ultimo_acionamento < self.tempo_cooldown:
                self.resetar_contagem()
                return None

            if agora - self.tempo_ultima_palma >= self.tempo_janela_palmas:
                quantidade = self.contador_palmas

                self.resetar_contagem()
                self.ultimo_acionamento = agora

                return quantidade

            return None