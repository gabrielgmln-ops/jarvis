"""
Testes automatizados do ClapDetector com sinais sinteticos.

Nao precisa de microfone: alimenta detector.analisar_volume() com sequencias
de (volume, delta_t) que imitam palma boa, palma fraca, voz continua e
batida de porta, e confere se o contador de palmas reage como esperado.

E o unico jeito seguro de mexer na sensibilidade (limiar_palma, ataque_minimo,
duracao_minima/maxima, fator_queda) sem quebrar o que ja funciona - rode este
arquivo de novo depois de qualquer ajuste em config.json ou clap_detector.py.

Uso:
    C:\\JARVIS\\venv\\Scripts\\python.exe tests\\test_clap_detector.py

Codigo de saida: 0 se tudo passou, 1 se algum caso falhou.
"""

import os
import sys

PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)

from core.clap_detector import ClapDetector  # noqa: E402


CONFIG_CALIBRADO = {
    "limiar_palma": 5.2,
    "intervalo_minimo": 0.35,
    "tempo_cooldown": 3.0,
    "duracao_minima_palma": 0.02,
    "duracao_maxima_palma": 0.20,
    "fator_queda_palma": 0.45,
    "ataque_minimo_palma": 2.8,
    "tempo_janela_palmas": 1.4,
}


class LoggerSilencioso:
    def info(self, mensagem):
        pass

    def error(self, mensagem):
        pass


def novo_detector():
    return ClapDetector(CONFIG_CALIBRADO, LoggerSilencioso())


def simular(detector, amostras, passo=0.01):
    """Alimenta o detector com uma lista de volumes, um a cada `passo` segundos."""
    agora = 1000.0
    for volume in amostras:
        detector.analisar_volume(volume, agora)
        agora += passo
    return agora


def onda(*trechos):
    """Concatena trechos (volume, quantidade_de_amostras) numa lista de volumes."""
    amostras = []
    for volume, quantidade in trechos:
        amostras.extend([volume] * quantidade)
    return amostras


CASOS = []


def caso(nome):
    def decorador(func):
        CASOS.append((nome, func))
        return func
    return decorador


@caso("palma boa: pico curto e forte -> registra 1 palma")
def teste_palma_boa():
    detector = novo_detector()
    # baseline baixo, pico bem acima do limiar (ataque grande), volta rapido
    # pra baixo do limite de queda - dentro da janela de duracao valida
    # (4 amostras de 0.01s = 0.04s, com folga da borda de 0.02s minima).
    amostras = onda((0.3, 3), (6.0, 4), (0.5, 3))
    simular(detector, amostras, passo=0.01)
    assert detector.contador_palmas == 1, (
        f"esperava 1 palma, contou {detector.contador_palmas}"
    )


@caso("palma fraca: pico nunca alcanca o limiar -> nao registra")
def teste_palma_fraca():
    detector = novo_detector()
    amostras = onda((0.3, 3), (4.0, 2), (0.5, 3))  # 4.0 < limiar_palma (5.2)
    simular(detector, amostras, passo=0.01)
    assert detector.contador_palmas == 0, (
        f"esperava 0 palmas, contou {detector.contador_palmas}"
    )


@caso("palma fraca: ataque gradual (sem estalo) -> nao registra")
def teste_ataque_gradual():
    detector = novo_detector()
    # sobe devagar, incremento por amostra sempre abaixo de ataque_minimo (2.8),
    # mesmo passando do limiar no fim.
    amostras = onda((0.3, 1), (1.5, 1), (2.8, 1), (4.0, 1), (5.5, 1), (0.5, 3))
    simular(detector, amostras, passo=0.01)
    assert detector.contador_palmas == 0, (
        f"esperava 0 palmas (subida gradual), contou {detector.contador_palmas}"
    )


@caso("voz continua: fica acima do limite de queda por muito tempo -> nao registra")
def teste_voz_continua():
    detector = novo_detector()
    # pico com ataque valido, mas fica alto por bem mais que duracao_maxima
    # (0.20s) antes de qualquer coisa - simula fala sustentada, nao um estalo.
    amostras = onda((0.5, 3), (6.0, 60), (0.5, 3))  # 60 * 0.01s = 0.6s alto
    simular(detector, amostras, passo=0.01)
    assert detector.contador_palmas == 0, (
        f"esperava 0 palmas (voz continua), contou {detector.contador_palmas}"
    )


@caso("batida de porta: alta mas com cauda de decaimento longa -> nao registra")
def teste_batida_porta():
    detector = novo_detector()
    # ataque tao forte quanto uma palma, mas o "boom" demora mais que
    # duracao_maxima pra cair abaixo do limite de queda (reverberacao grave
    # de uma porta bate diferente do estalo seco de uma palma).
    amostras = onda((0.3, 3), (7.0, 30), (0.5, 3))  # 30 * 0.01s = 0.3s > 0.20s
    simular(detector, amostras, passo=0.01)
    assert detector.contador_palmas == 0, (
        f"esperava 0 palmas (batida de porta), contou {detector.contador_palmas}"
    )


@caso("duas palmas boas seguidas -> conta 2, respeitando intervalo_minimo")
def teste_duas_palmas():
    detector = novo_detector()
    amostras = onda(
        (0.3, 3), (6.0, 4), (0.5, 40),   # 1a palma, depois baixo por 0.4s (> intervalo_minimo)
        (6.0, 4), (0.5, 3),              # 2a palma
    )
    simular(detector, amostras, passo=0.01)
    assert detector.contador_palmas == 2, (
        f"esperava 2 palmas, contou {detector.contador_palmas}"
    )


def main():
    falhas = 0
    for nome, funcao in CASOS:
        try:
            funcao()
        except AssertionError as erro:
            falhas += 1
            print(f"FALHOU  - {nome}\n          {erro}")
        except Exception as erro:
            falhas += 1
            print(f"ERRO    - {nome}\n          {erro!r}")
        else:
            print(f"OK      - {nome}")

    print()
    if falhas:
        print(f"{falhas} de {len(CASOS)} caso(s) falharam.")
        return 1

    print(f"Todos os {len(CASOS)} casos passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
