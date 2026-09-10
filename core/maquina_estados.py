import winsound


class MaquinaEstados:
    """Estado logico do JARVIS: DORMINDO -> EXECUTANDO -> DORMINDO.

    ESCUTANDO existe como estado reservado para a escuta por voz (secao 3 do
    roteiro do mega projeto) - nenhuma transicao entra nele ainda, porque a
    voz nao foi implementada nesta passada.
    """

    DORMINDO = "DORMINDO"
    ESCUTANDO = "ESCUTANDO"
    EXECUTANDO = "EXECUTANDO"

    # (frequencia em Hz, duracao em ms) - um som curto e distinto por transicao.
    _SONS = {
        DORMINDO: (523, 90),
        ESCUTANDO: (784, 90),
        EXECUTANDO: (392, 140),
    }

    def __init__(self, logger, tocar_som=True):
        self.logger = logger
        self.tocar_som = tocar_som
        self.estado = self.DORMINDO

    def transicionar(self, novo_estado):
        anterior = self.estado
        self.logger.info(f"Estado: {anterior} -> {novo_estado}")

        # O beep toca ANTES de trocar self.estado de proposito: o callback do
        # microfone só escuta palma de verdade quando self.estado ==
        # DORMINDO, e o beep sai pela caixa de som. Se o estado já tivesse
        # virado DORMINDO antes do Beep, o sistema ouviria o proprio beep e
        # contaria como palma (era o que estava acontecendo - ver log com
        # "Palma valida detectada" no mesmo segundo do "-> DORMINDO").
        if self.tocar_som:
            frequencia_duracao = self._SONS.get(novo_estado)
            if frequencia_duracao:
                try:
                    winsound.Beep(*frequencia_duracao)
                except (RuntimeError, ValueError) as erro:
                    self.logger.error(f"Não consegui tocar o som de transição: {erro}")

        self.estado = novo_estado
