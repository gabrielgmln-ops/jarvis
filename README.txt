J.A.R.V.I.S. - Manual do Sistema

Projeto: assistente local ativado por palmas
Pasta principal: C:\JARVIS


1. COMANDO PARA TESTAR MANUALMENTE

Abrir PowerShell e rodar:

cd "C:\JARVIS"
.\venv\Scripts\python.exe jarvis.py


2. PROTOCOLOS

O laco e PERSISTENTE: depois de qualquer protocolo, o sistema volta a
escutar sozinho (nao encerra mais). So sai com Ctrl+C, pelo menu da
bandeja ("Sair") ou se o Windows fechar o processo. Qual protocolo cada
quantidade de palmas dispara vive no "mapa_palmas" do config.json - hoje:

2 palmas -> inicial:
- Abre musica principal no Spotify, move para a tela configurada
- Abre Opera, move para a tela configurada
- Toca o audio principal do J.A.R.V.I.S.

3 palmas -> fnb:
- Toca o audio do Protocolo FNB
- Abre a playlist FNB no Spotify e clica no botao Play calibrado
- Nao abre o Opera

4 palmas -> perguntar:
- Chama o OpenJarvis (comando "jarvis ask") com a pergunta configurada em
  "pergunta_jarvis" no config.json.
- Mostra a resposta pela bandeja (notificacao nativa) ou, se a bandeja nao
  estiver disponivel, numa caixinha de mensagem do Windows.
- Precisa do OpenJarvis instalado, no PATH, e do Ollama rodando - se o
  Ollama estiver fora do ar, o jarvis_bridge tenta subir ele sozinho antes
  de desistir com uma mensagem explicando o que fazer.

Sem palma associada (disparados por comando, atalho ou gatilho pelo
celular - ver secao 3):

estudo:
- Abre o vault (explorador de arquivos) e o Microsoft Teams
- Inicia um pomodoro (duracao_pomodoro_min no config, 25min por padrao) e
  avisa pela bandeja quando termina

candidatura:
- Abre Gmail e LinkedIn
- Abre as notas "Rotina de candidatura" e "Banco de Respostas" do vault

desligar:
- Commita o dia em C:\JARVIS e no vault (caminho_vault no config), se
  houver mudanca em cada um
- NAO fecha janelas de proposito - risco de perder trabalho nao salvo em
  outro programa


3. DISPARAR UM PROTOCOLO SEM PALMAS

cd "C:\JARVIS"
.\venv\Scripts\python.exe executar_protocolo.py inicial
.\venv\Scripts\python.exe executar_protocolo.py fnb
.\venv\Scripts\python.exe executar_protocolo.py estudo
.\venv\Scripts\python.exe executar_protocolo.py candidatura
.\venv\Scripts\python.exe executar_protocolo.py desligar

Ver o que existe, sem executar:
.\venv\Scripts\python.exe executar_protocolo.py --listar

Ensaiar sem abrir nada nem tocar audio:
.\venv\Scripts\python.exe executar_protocolo.py inicial --simular

Codigos de saida: 0 = feito, 2 = nome desconhecido, 3 = erro na execucao.

Este script tambem e o que a skill "protocolos-jarvis" do OpenJarvis chama,
para o assistente disparar os protocolos por voz ou por texto. A skill fica em
%USERPROFILE%\.openjarvis\skills\protocolos-jarvis\SKILL.md

Tambem da pra disparar por atalho de teclado (Ctrl+Alt+<numero de palmas>,
sempre ativo enquanto o jarvis.py roda) ou pelo celular: solte um arquivo
"<protocolo>.txt" vazio em "C:\SegundoCerebro\99 - Sistema\gatilhos-celular"
(sincronizada pelo Google Drive) e o protocolo dispara sozinho.


4. ARQUIVOS PRINCIPAIS

jarvis.py                  Laco persistente: microfone -> palmas -> protocolo -> volta a escutar.
executar_protocolo.py      Dispara um protocolo sob demanda, sem palmas.
config.json                Musicas, telas, tempos, sensibilidade e mapa_palmas.
core/clap_detector.py      Deteccao de palma (pico, ataque, duracao, queda).
core/maquina_estados.py    Estado DORMINDO/ESCUTANDO/EXECUTANDO, com som por transicao.
core/protocols.py          Os protocolos e o dispatch por nome ou por palmas.
core/actions.py            Abre apps, move janelas, toca audio, clica no play.
core/acoes_simuladas.py    Versao "so anuncia" das acoes, pro modo_seguro/--simular.
core/bandeja.py            Icone na bandeja: pausar escuta, sair, notificacoes.
core/atalho_teclado.py     Atalhos de teclado globais (Ctrl+Alt+<N>).
core/gatilho_celular.py    Pasta vigiada pro gatilho pelo celular.
core/jarvis_bridge.py      Ponte com o OpenJarvis, com checagem e auto-start do Ollama.
core/window_control.py     Controle de janelas, telas e deteccao de tela ativa.
core/lockscreen.py         Impede ativacao na tela de bloqueio.
core/logger.py             Log com rotacao e modo verbose (tempo decorrido).
core/single_instance.py    Impede duas instancias ao mesmo tempo.
tests/test_clap_detector.py Testes automatizados do detector, com sinais sinteticos.
calibrar_palma.py          Calibra "limiar_palma" e "ataque_minimo_palma".
calibrar_play_fnb.py       Calibra as coordenadas do play da playlist FNB.
frase_jarvis.mp3           Audio principal.
audio_protocolo_fnb.mp3    Audio do Protocolo FNB.
logs_jarvis.txt            Registro de erros e de execucoes.
iniciar_jarvis.bat         Ativa o venv e executa o jarvis.py.
iniciar_jarvis_oculto.vbs  Executa o .bat sem abrir tela preta.
requirements.txt           Bibliotecas do projeto.
README.md                  Versao publica/portfolio, sem dados pessoais.


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


7. VERSIONAMENTO

Ja em uso desde 09/09/2026 - "git log" mostra o historico.

cd "C:\JARVIS"
git log --oneline
git add <arquivo>
git commit -m "mensagem"

O .gitignore ja exclui o venv, os logs e as sobras. Repositorio remoto
(GitHub) ainda nao configurado - ver "Roteiro do mega projeto" no vault
Sexta-Feira, secao 0.


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
- O laco e persistente: volta a escutar sozinho depois de qualquer
  protocolo, nao encerra mais. executar_protocolo.py roda um protocolo e
  sai (nunca fica escutando).
- Se o microfone sumir (fone bluetooth desligando, por exemplo), o sistema
  tenta reabrir sozinho em vez de cair.
- Se o Ollama nao estiver rodando quando o protocolo "perguntar" for
  chamado, o jarvis_bridge tenta subir ele sozinho antes de desistir.
- modo_seguro (config.json) ou --dry-run fazem todo protocolo so anunciar
  os passos, sem abrir nada nem tocar audio.
- A voz falada (escuta continua, "Acorda Jarvis") ainda nao foi
  implementada - so as palmas, atalho de teclado e gatilho pelo celular
  disparam protocolo hoje.

---
Atualizado em 09/09/2026.
