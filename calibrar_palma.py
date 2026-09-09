import time

import numpy as np
import sounddevice as sd


DURACAO_TESTE = 20  # segundos


print("Calibrador de sensibilidade das palmas.")
print()
print("O teste vai durar 20 segundos.")
print("Durante esse tempo:")
print(" - Bata palma normalmente algumas vezes.")
print(" - Depois fique em silêncio / faça ruídos comuns (digitar, cadeira, passos).")
print()
print("Anote os valores de 'volume' e 'ataque' que aparecerem.")
print("O objetivo é achar um 'limiar_palma' e um 'ataque_minimo_palma'")
print("maiores que o ruído comum, mas menores que a palma real.")
print()
input("Pressione ENTER para começar...")
print()

volume_anterior = 0
inicio = time.time()
maior_pico = 0


def callback(indata, frames, callback_time, status):
    global volume_anterior, maior_pico

    volume = np.linalg.norm(indata) * 10
    ataque = volume - volume_anterior

    # Só imprime picos relevantes, pra não poluir o terminal com o silêncio.
    if ataque >= 1.0 or volume >= 2.0:
        tempo_decorrido = time.time() - inicio
        print(f"[{tempo_decorrido:5.1f}s] volume={volume:6.2f}  ataque={ataque:6.2f}")

        if volume > maior_pico:
            maior_pico = volume

    volume_anterior = volume


with sd.InputStream(callback=callback):
    time.sleep(DURACAO_TESTE)

print()
print("Teste finalizado.")
print(f"Maior pico de volume registrado: {maior_pico:.2f}")
print()
print("Sugestão:")
print(" - Olhe os valores registrados quando você bateu palma de verdade.")
print(" - 'limiar_palma' deve ficar um pouco ABAIXO do volume das suas palmas reais.")
print(" - 'ataque_minimo_palma' deve ficar um pouco ABAIXO do ataque das suas palmas reais,")
print("   mas ACIMA do ataque dos ruídos comuns (digitação, cadeira, etc).")
print(" - Depois é só editar esses dois valores no config.json e testar de novo.")
