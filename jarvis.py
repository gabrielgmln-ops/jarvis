import time

import numpy as np
import sounddevice as sd

from core.acoes_simuladas import AcoesSimuladas
from core.actions import JarvisActions
from core.clap_detector import ClapDetector
from core.config_loader import carregar_configuracao
from core.lockscreen import LockScreenChecker
from core.logger import JarvisLogger
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

    modo_seguro = bool(config.get("modo_seguro", False))
    if modo_seguro:
        acoes = AcoesSimuladas(config, logger, janelas)
    else:
        acoes = JarvisActions(config, logger, janelas)

    protocolos = JarvisProtocols(config, logger, acoes)

    sistema_ativo = True

    logger.info("=" * 50)
    logger.info(f"{NOME_SISTEMA} online.")
    logger.info("Configuração carregada com sucesso.")
    logger.info("Telas detectadas:")
    janelas.listar_telas_detectadas()
    logger.info("2 palmas: Protocolo Inicial.")
    logger.info("3 palmas: Protocolo FNB.")
    logger.info("4 palmas: Perguntar ao OpenJarvis.")
    logger.info("Detector de palmas ativo.")
    logger.info("Filtro contra voz contínua ativo.")
    logger.info("Proteção contra dupla instância ativa.")
    if modo_seguro:
        logger.info("MODO SEGURO ativo: protocolos só vão anunciar os passos, sem abrir nem tocar nada.")

    def callback(indata, frames, callback_time, status):
        if status:
            logger.error(f"Status do microfone: {status}")

        if not bloqueio.pode_escutar_palmas():
            detector.resetar_contagem()
            return

        volume = np.linalg.norm(indata) * 10
        agora = time.time()

        detector.analisar_volume(volume, agora)

    try:
        with sd.InputStream(callback=callback):
            while sistema_ativo:
                quantidade_palmas = detector.obter_quantidade_se_pronta()

                if quantidade_palmas:
                    sistema_ativo = protocolos.executar_por_palmas(quantidade_palmas)

                time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Sistema encerrado manualmente.")

    except Exception as erro:
        logger.error(f"Erro crítico no sistema: {erro}")

    logger.info(f"{NOME_SISTEMA} offline.")
    logger.info("=" * 50)


if __name__ == "__main__":
    iniciar_sistema()