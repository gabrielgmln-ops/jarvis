import json
import os


PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_CONFIG = os.path.join(PASTA_PROJETO, "config.json")


CONFIG_PADRAO = {
    "limiar_palma": 5.2,
    "intervalo_minimo": 0.35,
    "tempo_cooldown": 3.0,

    "duracao_minima_palma": 0.02,
    "duracao_maxima_palma": 0.20,
    "fator_queda_palma": 0.45,
    "ataque_minimo_palma": 2.8,

    "tempo_janela_palmas": 1.4,
    "palmas_protocolo_inicial": 2,
    "palmas_protocolo_fnb": 3,
    "palmas_perguntar_jarvis": 4,
    "pergunta_jarvis": "Me dê uma dica rápida e útil pra agora.",

    "link_musica_spotify": "spotify:track:39shmbIHICJ2Wxnk1fPSdz",
    "link_playlist_fnb": "spotify:playlist:48jUfj5azzMkzbkrrCXyK7",

    "audio_ativacao": "frase_jarvis.mp3",
    "audio_protocolo_fnb": "audio_protocolo_fnb.mp3",

    "tela_spotify": 1,
    "tela_opera": 0,

    "tempo_espera_spotify": 4.0,
    "tempo_antes_opera": 1.0,
    "tempo_antes_audio": 1.5,

    "tempo_espera_playlist_fnb": 5.0,
    "clicar_play_playlist_fnb": True,
    "play_fnb_offset_x": 95,
    "play_fnb_offset_y": 305,

    "arquivo_log": "logs_jarvis.txt",
    "tamanho_maximo_log_mb": 1,

    "modo_seguro": False
}


def carregar_configuracao():
    if not os.path.exists(CAMINHO_CONFIG):
        print("config.json não encontrado. Usando configuração padrão.")
        config = CONFIG_PADRAO.copy()
        config["pasta_projeto"] = PASTA_PROJETO
        return config

    try:
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as arquivo:
            config_usuario = json.load(arquivo)

        config_final = CONFIG_PADRAO.copy()
        config_final.update(config_usuario)
        config_final["pasta_projeto"] = PASTA_PROJETO

        return config_final

    except Exception as erro:
        print(f"Erro ao carregar config.json. Usando configuração padrão. Erro: {erro}")
        config = CONFIG_PADRAO.copy()
        config["pasta_projeto"] = PASTA_PROJETO
        return config