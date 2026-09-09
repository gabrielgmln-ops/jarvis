import time
import pyautogui
import pygetwindow as gw


print("Calibrador do botão Play da playlist FNB.")
print("Abra o Spotify na playlist FNB.")
print("Depois coloque o mouse exatamente em cima do botão Play verde.")
print("Você terá 8 segundos.")
print()

time.sleep(8)

x, y = pyautogui.position()

janela_spotify = None

for janela in gw.getAllWindows():
    if janela.title and "Spotify" in janela.title:
        janela_spotify = janela
        break

if not janela_spotify:
    print("Não encontrei a janela do Spotify.")
    print(f"Posição absoluta do mouse: x={x}, y={y}")
else:
    offset_x = x - janela_spotify.left
    offset_y = y - janela_spotify.top

    print("Janela do Spotify encontrada.")
    print(f"Posição absoluta do mouse: x={x}, y={y}")
    print(f"Offset relativo à janela:")
    print(f"play_fnb_offset_x = {offset_x}")
    print(f"play_fnb_offset_y = {offset_y}")
    print()
    print("Coloque esses valores no config.json.")