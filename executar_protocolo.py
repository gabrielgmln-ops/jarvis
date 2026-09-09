"""
Executa um protocolo do J.A.R.V.I.S. sob demanda, sem depender das palmas.

Feito para ser chamado por fora: pela skill do OpenJarvis, por um atalho,
pelo Agendador de Tarefas ou pela mao, no PowerShell.

Uso:
    python executar_protocolo.py inicial
    python executar_protocolo.py fnb
    python executar_protocolo.py --listar
    python executar_protocolo.py inicial --simular

Codigos de saida:
    0  protocolo executado
    2  nome de protocolo desconhecido
    3  erro durante a execucao
"""

import argparse
import os
import sys


PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)

from core.acoes_simuladas import AcoesSimuladas  # noqa: E402
from core.actions import JarvisActions          # noqa: E402
from core.config_loader import carregar_configuracao  # noqa: E402
from core.logger import JarvisLogger            # noqa: E402
from core.protocols import JarvisProtocols      # noqa: E402
from core.window_control import WindowController  # noqa: E402


PROTOCOLOS = {
    "inicial": {
        "metodo": "protocolo_inicial",
        "titulo": "Protocolo Inicial",
        "resumo": "Abre a musica principal no Spotify, move a janela, abre o Opera e toca o audio de ativacao.",
    },
    "fnb": {
        "metodo": "protocolo_fnb",
        "titulo": "Protocolo FNB",
        "resumo": "Toca o audio do FNB, abre a playlist e clica no play calibrado. Nao abre o Opera.",
    },
}


def listar():
    print("Protocolos disponiveis:")
    for chave, info in PROTOCOLOS.items():
        print("  {0:<9} {1}".format(chave, info["titulo"]))
        print("  {0:<9} {1}".format("", info["resumo"]))
    return 0


def executar(nome, simular=False, verbose=False):
    info = PROTOCOLOS.get(nome)
    if info is None:
        print("ERRO: protocolo desconhecido: {0}".format(nome))
        print("Conhecidos: {0}".format(", ".join(sorted(PROTOCOLOS))))
        return 2

    config = carregar_configuracao()
    logger = JarvisLogger(config, verbose=verbose)
    janelas = WindowController(config, logger)

    modo_seguro = bool(config.get("modo_seguro", False))
    if simular or modo_seguro:
        acoes = AcoesSimuladas(config, logger, janelas)
    else:
        acoes = JarvisActions(config, logger, janelas)

    protocolos = JarvisProtocols(config, logger, acoes)

    if modo_seguro and not simular:
        print("modo_seguro ativo no config.json - simulando mesmo sem --simular.")

    origem = "simulacao" if (simular or modo_seguro) else "chamada externa"
    logger.info("=" * 50)
    logger.info("{0} disparado por {1} (executar_protocolo.py).".format(info["titulo"], origem))
    print("{0}: {1}".format("Simulando" if simular else "Executando", info["titulo"]))

    try:
        getattr(protocolos, info["metodo"])()
    except Exception as erro:
        logger.error("Falha ao executar {0}: {1}".format(info["titulo"], erro))
        print("ERRO: {0} falhou: {1}".format(info["titulo"], erro))
        return 3

    logger.info("{0} concluido por {1}.".format(info["titulo"], origem))
    print("OK: {0} concluido.".format(info["titulo"]))
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Executa um protocolo do J.A.R.V.I.S. sob demanda.",
        epilog="Sem argumentos, mostra esta ajuda.")
    parser.add_argument("protocolo", nargs="?", help="inicial ou fnb")
    parser.add_argument("--listar", action="store_true",
                        help="lista os protocolos disponiveis e sai")
    parser.add_argument("--simular", action="store_true",
                        help="anuncia os passos sem abrir nada nem tocar audio")
    parser.add_argument("--verbose", action="store_true",
                        help="imprime cada linha do log com o tempo decorrido")

    args = parser.parse_args()

    if args.listar:
        return listar()

    if not args.protocolo:
        parser.print_help()
        return 0

    return executar(args.protocolo.strip().lower(), simular=args.simular, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
