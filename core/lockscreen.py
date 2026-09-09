import ctypes
import time


class LockScreenChecker:
    def __init__(self):
        self.ultimo_check = 0
        self.windows_desbloqueado_cache = True

    def windows_esta_desbloqueado(self):
        desktop_switchdesktop = 0x0100
        user32 = ctypes.windll.user32

        h_desktop = user32.OpenInputDesktop(0, False, desktop_switchdesktop)

        if h_desktop == 0:
            return False

        resultado = user32.SwitchDesktop(h_desktop)
        user32.CloseDesktop(h_desktop)

        return resultado != 0

    def pode_escutar_palmas(self):
        agora = time.time()

        if agora - self.ultimo_check >= 1:
            self.windows_desbloqueado_cache = self.windows_esta_desbloqueado()
            self.ultimo_check = agora

        return self.windows_desbloqueado_cache
