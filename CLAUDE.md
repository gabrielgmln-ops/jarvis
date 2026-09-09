# J.A.R.V.I.S. — contexto do projeto

Assistente pessoal em Python que roda no Windows do Gabriel Moraes Lopes.
Trate-o por **"senhor"**, responda em portugues do Brasil, seja objetivo.

## O que e
Sistema local ativado por **palmas**, capturadas pelo microfone. Faz parte de um
mega projeto com tres pecas: este detector de palmas, o **OpenJarvis** (agente
local com Ollama, modelo `qwen3.5:4b`) e o vault **Sexta-Feira** em
`C:\SegundoCerebro`.

A voz falada se chama **JARVIS**. "Sexta-Feira" e o nome do vault e da memoria.

## Mapa do codigo
- `jarvis.py` — laco principal: `sounddevice` -> volume -> `ClapDetector` -> protocolo.
- `core/clap_detector.py` — pico com ataque minimo, duracao 0,02–0,20 s, queda a 45%.
- `core/protocols.py` — os tres protocolos e o mapa palmas -> protocolo.
- `core/actions.py` — abre Spotify e Opera, move janelas, toca mp3, clica no play.
- `core/jarvis_bridge.py` — ponte com o OpenJarvis (`jarvis ask`), com checagem do
  PATH e da porta 11434 do Ollama antes de perguntar.
- `core/window_control.py`, `core/lockscreen.py`, `core/logger.py`, `core/single_instance.py`.
- `executar_protocolo.py` — dispara `inicial` ou `fnb` sob demanda, sem palmas.
  Flags: `--listar`, `--simular`. Saida 0 = feito, 2 = nome errado, 3 = erro.
- `config.json` — sensibilidade das palmas, telas, tempos, links do Spotify.

## Gatilhos
- 2 palmas: Protocolo Inicial (Spotify + Opera + audio de ativacao).
- 3 palmas: Protocolo FNB (audio + playlist + play calibrado).
- 4 palmas: pergunta fixa ao OpenJarvis, resposta numa caixa de mensagem.

Telas: tela 0 = 1920x1080, tela 1 = 1360x768.

## Como rodar
```
cd C:\JARVIS
.\venv\Scripts\python.exe jarvis.py
.\venv\Scripts\python.exe executar_protocolo.py inicial --simular
```
Sempre use o python do `venv`, nunca o python global.

## Regras deste projeto
- **Nunca dispare um protocolo para testar** sem pedido explicito: eles abrem
  janelas e tocam som alto na maquina dele. Use `--simular`.
- Nao mexa em `config.json` sem avisar: os valores de palma e as coordenadas do
  play foram calibrados a mao.
- O `venv/` nao entra no Git. O `.gitignore` ja cuida disso.
- Codigo e comentarios em portugues, sem acento nos nomes de arquivo.
- Erros vao para `logs_jarvis.txt` — leia antes de adivinhar.

## Pendencias conhecidas
- [ ] `git init` nesta pasta (o `.gitignore` ja esta aqui).
- [ ] Teste de ponta a ponta da skill `protocolos-jarvis`, em
      `%USERPROFILE%\.openjarvis\skills\protocolos-jarvis\`.
- [ ] Todo protocolo devolve `False` e encerra o processo — bloqueia o modo de
      escuta continua que a etapa de voz vai exigir.
- [ ] `jarvis self-update` travado em `0.0.1.dev1+unknown`.
- [ ] Demora para ligar junto com o Windows.
- [ ] Wake word em portugues: **"Acorda Jarvis"**, local e offline. Arquitetura
      decidida: palmas acordam, voz comanda.

A nota completa do projeto vive em `C:\SegundoCerebro\03 - Projetos\JARVIS.md`.
