J.A.R.V.I.S. - Manual do Sistema

Projeto: assistente local ativado por palmas
Pasta principal: C:\JARVIS


1. COMANDO PARA TESTAR MANUALMENTE

Abrir PowerShell e rodar:

cd "C:\JARVIS"
.\venv\Scripts\python.exe jarvis.py


2. PROTOCOLOS

2 palmas:
- Ativa o Protocolo Inicial
- Abre musica principal no Spotify
- Move Spotify para a tela configurada
- Abre Opera
- Move Opera para a tela configurada
- Toca o audio principal do J.A.R.V.I.S.
- Encerra o sistema

3 palmas:
- Ativa o Protocolo FNB
- Toca o audio do Protocolo FNB
- Abre a playlist FNB no Spotify
- Clica no botao Play calibrado
- Nao abre o Opera
- Encerra o sistema

4 palmas:
- Chama o OpenJarvis (comando "jarvis ask") com a pergunta configurada em
  "pergunta_jarvis" no config.json.
- Mostra a resposta numa caixinha de mensagem do Windows.
- Encerra o sistema.
- Precisa do OpenJarvis instalado, no PATH, e do Ollama rodando.
- Se o Ollama estiver fora do ar, a caixinha explica o que fazer em vez de
  dizer so "nao respondeu".


3. DISPARAR UM PROTOCOLO SEM PALMAS

cd "C:\JARVIS"
.\venv\Scripts\python.exe executar_protocolo.py inicial
.\venv\Scripts\python.exe executar_protocolo.py fnb

Ver o que existe, sem executar:
.\venv\Scripts\python.exe executar_protocolo.py --listar

Ensaiar sem abrir nada nem tocar audio:
.\venv\Scripts\python.exe executar_protocolo.py inicial --simular

Codigos de saida: 0 = feito, 2 = nome desconhecido, 3 = erro na execucao.

Este script tambem e o que a skill "protocolos-jarvis" do OpenJarvis chama,
para o assistente disparar os protocolos por voz ou por texto. A skill fica em
%USERPROFILE%\.openjarvis\skills\protocolos-jarvis\SKILL.md


4. ARQUIVOS PRINCIPAIS

jarvis.py                  Laco principal: microfone -> palmas -> protocolo.
executar_protocolo.py      Dispara um protocolo sob demanda, sem palmas.
config.json                Musicas, telas, tempos e sensibilidade das palmas.
core/clap_detector.py      Deteccao de palma (pico, ataque, duracao, queda).
core/protocols.py          Os tres protocolos e o mapa palmas -> protocolo.
core/actions.py            Abre apps, move janelas, toca audio, clica no play.
core/jarvis_bridge.py      Ponte com o OpenJarvis, com checagem do Ollama.
core/window_control.py     Controle de janelas e telas.
core/lockscreen.py         Impede ativacao na tela de bloqueio.
core/logger.py             Log de erros.
core/single_instance.py    Impede duas instancias ao mesmo tempo.
calibrar_palma.py          Calibra "limiar_palma" e "ataque_minimo_palma".
calibrar_play_fnb.py       Calibra as coordenadas do play da playlist FNB.
frase_jarvis.mp3           Audio principal.
audio_protocolo_fnb.mp3    Audio do Protocolo FNB.
logs_jarvis.txt            Registro de erros e de execucoes.
iniciar_jarvis.bat         Ativa o venv e executa o jarvis.py.
iniciar_jarvis_oculto.vbs  Executa o .bat sem abrir tela preta.
requirements.txt           Bibliotecas do projeto.


5. COMO ALTERAR CONFIGURACOES

notepad config.json

limiar_palma               Sensibilidade. Maior = mais dificil ativar.
tela_spotify / tela_opera  Tela 0 = 1920x1080, tela 1 = 1360x768.
tempo_antes_audio          Espera antes do audio principal.
link_musica_spotify        Musica do Protocolo Inicial.
link_playlist_fnb          Playlist do Protocolo FNB.
play_fnb_offset_x / _y     Coordenadas calibradas do play da playlist FNB.


6. COMO VER ERROS

notepad logs_jarvis.txt

Se estiver vazio, nenhum erro foi registrado.


7. VERSIONAMENTO (recomendado no lugar do backup manual)

cd "C:\JARVIS"
git init
git add .
git commit -m "estado atual do sistema"

O .gitignore ja exclui o venv, os logs e as sobras. Com o historico no lugar,
da para voltar a uma versao boa sem perder o trabalho novo - que era o motivo
da pasta backup_estavel.


8. COMO REINSTALAR BIBLIOTECAS

cd "C:\JARVIS"
.\venv\Scripts\python.exe -m pip install -r requirements.txt


9. INICIALIZACAO COM WINDOWS

O sistema inicia pelo atalho de iniciar_jarvis_oculto.vbs, que deve ficar na
pasta de inicializacao. Para abrir a pasta:

explorer shell:startup


10. OBSERVACOES

- O J.A.R.V.I.S. nao ativa na tela de bloqueio.
- Voz continua nao deve ativar o sistema.
- O sistema encerra automaticamente depois de executar um protocolo pelas
  palmas. O executar_protocolo.py nao encerra nada: ele roda e sai.

---
Atualizado em 09/09/2026.
