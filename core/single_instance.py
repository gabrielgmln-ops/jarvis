import ctypes
import sys


def impedir_multiplas_instancias():
    error_already_exists = 183
    nome_mutex = "Global\\JARVIS_ASSISTENTE_LOCAL"

    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, nome_mutex)

    if kernel32.GetLastError() == error_already_exists:
        print("J.A.R.V.I.S. já está em execução. Encerrando nova instância.")
        sys.exit(0)

    return mutex