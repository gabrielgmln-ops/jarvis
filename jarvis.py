import argparse
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
INTERVALO_RECONEXAO_MICROFONE = 3.0
LIMITE_SILENCIO_SUSPEITO = 5.0


class MicrofoneSumiuError(Exception):
    """O InputStream parou de entregar audio (fone bluetooth desligou, por exemplo)."""


def _executar_laco(config, logger, bloqueio, detector, janelas, estado, protocolos, modo_seguro):
    mapa_palmas = config.get("mapa_palmas", {})
    ultimo_callback = [time.time()]

    def callback(indata, frames, callback_time, status):
        ultimo_callback[0] = time.time()

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

    while True:
        try:
            ultimo_callback[0] = time.time()

            with sd.InputStream(callback=callback):
                logger.info("Microfone aberto. Laço persistente: volta a escutar depois de cada protocolo.")

                while True:
                    if time.time() - ultimo_callback[0] > LIMITE_SILENCIO_SUSPEITO:
                        raise MicrofoneSumiuError(
                            f"Nenhum áudio recebido em {LIMITE_SILENCIO_SUSPEITO:.0f}s."
                        )

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
                        ultimo_callback[0] = time.time()
                        estado.transicionar(MaquinaEstados.DORMINDO)

                    time.sleep(0.1)

        except KeyboardInterrupt:
            raise

        except Exception as erro:
            logger.error(f"O microfone caiu (desconectado ou trocado?): {erro}")
            logger.info(f"Tentando reabrir o microfone em {INTERVALO_RECONEXAO_MICROFONE:.0f}s...")
            detector.resetar_contagem()
            estado.transicionar(MaquinaEstados.DORMINDO)
            time.sleep(INTERVALO_RECONEXAO_MICROFONE)


def iniciar_sistema(dry_run=False, verbose=False):
    impedir_multiplas_instancias()

    config = carregar_configuracao()

    logger = JarvisLogger(config, verbose=verbose)
    bloqueio = LockScreenChecker()
    detector = ClapDetector(config, logger)
    janelas = WindowController(config, logger)
    estado = MaquinaEstados(logger)

    modo_seguro = dry_run or bool(config.get("modo_seguro", False))
    if dry_run:
        logger.info("--dry-run: rodando em modo seguro nesta execução (config.json não muda).")
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
    logger.info("Recuperação automática se o microfone sumir ativa.")
    if modo_seguro:
        logger.info("MODO SEGURO ativo: protocolos só vão anunciar os passos, sem abrir nem tocar nada.")
    logger.info(f"Estado inicial: {estado.estado}.")

    try:
        _executar_laco(config, logger, bloqueio, detector, janelas, estado, protocolos, modo_seguro)

    except KeyboardInterrupt:
        logger.info("Sistema encerrado manualmente.")

    except Exception as erro:
        logger.error(f"Erro crítico no sistema: {erro}")

    logger.info(f"{NOME_SISTEMA} offline.")
    logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. - detector de palmas.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="roda em modo seguro só nesta execução, sem mudar o config.json"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="imprime cada linha do log com o tempo decorrido desde que o sistema ligou"
    )
    args = parser.parse_args()

    iniciar_sistema(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()
