import time

import numpy as np
import sounddevice as sd

from core.acoes_simuladas import AcoesSimuladas
from core.actions import JarvisActions
from core.clap_detector import ClapDetector
from core.config_loader import carregar_configuracao
from core.lockscreen import LockScreenChecker
from core.logger import JarvisLogger
from core.maquina_estados import MaquinaEstados
from core.protocols import JarvisProtocols
from core.single_instance import impedir_multiplas_instancias
from core.window_control import WindowController


NOME_SISTEMA = "J.A.R.V.I.S."


def iniciar_sistema():
    impedir_multiplas_instancias()

    config = carregar_configuracao()

    logger = JarvisLogger(config)
    bloqueio = LockScreenChecker()
    detector = ClapDetector(config, logger)
    janelas = WindowController(config, logger)
    estado = MaquinaEstados(logger)

    modo_seguro = bool(config.get("modo_seguro", False))
    if modo_seguro:
        acoes = AcoesSimuladas(config, logger, janelas)
    else:
        acoes = JarvisActions(config, logger, janelas)

    protocolos = JarvisProtocols(config, logger, acoes)

    logger.info("=" * 50)
    logger.info(f"{NOME_SISTEMA} online.")
    logger.info("Configuração carregada com sucesso.")
    logger.info("Telas detectadas:")
    janelas.listar_telas_detectadas()

    mapa_palmas = config.get("mapa_palmas", {})
    for palmas, protocolo in sorted(mapa_palmas.items(), key=lambda item: int(item[0])):
        logger.info(f"{palmas} palmas: {protocolo}.")

    logger.info("Detector de palmas ativo.")
    logger.info("Filtro contra voz contínua ativo.")
    logger.info("Proteção contra dupla instância ativa.")
    if modo_seguro:
        logger.info("MODO SEGURO ativo: protocolos só vão anunciar os passos, sem abrir nem tocar nada.")
    logger.info(f"Estado inicial: {estado.estado}.")

    def callback(indata, frames, callback_time, status):
        if status:
            logger.error(f"Status do microfone: {status}")

        # Só ouve palma de verdade enquanto DORMINDO - durante EXECUTANDO o
        # próprio áudio dos protocolos (ou o barulho de abrir apps) não deve
        # virar palma falsa, e nunca pode haver dois protocolos ao mesmo tempo.
        if estado.estado != MaquinaEstados.DORMINDO:
            return

        if not bloqueio.pode_escutar_palmas():
            detector.resetar_contagem()
            return

        volume = np.linalg.norm(indata) * 10
        agora = time.time()

        detector.analisar_volume(volume, agora)

    try:
        with sd.InputStream(callback=callback):
            logger.info("Laço persistente: o sistema volta a escutar depois de cada protocolo.")

            while True:
                quantidade_palmas = detector.obter_quantidade_se_pronta()

                if quantidade_palmas:
                    estado.transicionar(MaquinaEstados.EXECUTANDO)

                    try:
                        protocolos.executar_por_palmas(quantidade_palmas)
                    except Exception as erro:
                        logger.error(f"Protocolo falhou: {erro}")

                    # Descarta qualquer coisa que o próprio protocolo tenha
                    # feito o microfone captar antes de voltar a escutar.
                    detector.resetar_contagem()
                    estado.transicionar(MaquinaEstados.DORMINDO)

                time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Sistema encerrado manualmente.")

    except Exception as erro:
        logger.error(f"Erro crítico no sistema: {erro}")

    logger.info(f"{NOME_SISTEMA} offline.")
    logger.info("=" * 50)


if __name__ == "__main__":
    iniciar_sistema()
