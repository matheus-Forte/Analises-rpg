from motor_jogadores import analisar_jogador


def criterio_agressivo(resultado):
    acertos, desafios, adaptacoes = resultado

    return (
        acertos,
        adaptacoes,
        -desafios
    )


def analisar_agressivo():
    return analisar_jogador(
        nome_estrategia="Agressivo",
        criterio=criterio_agressivo,
        nome_arquivo="jogador_agressivo.xlsx"
    )


if __name__ == "__main__":
    analisar_agressivo()
