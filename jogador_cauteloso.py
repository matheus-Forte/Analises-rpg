from motor_jogadores import analisar_jogador


def criterio_cauteloso(resultado):
    acertos, desafios, adaptacoes = resultado

    desafios_restantes = max(
        0,
        desafios - adaptacoes
    )

    protegido = desafios_restantes == 0

    if protegido:
        return (
            1,
            acertos,
            adaptacoes,
            -desafios
        )

    return (
        0,
        -desafios_restantes,
        adaptacoes,
        acertos,
        -desafios
    )


def analisar_cauteloso():
    return analisar_jogador(
        nome_estrategia="Cauteloso",
        criterio=criterio_cauteloso,
        nome_arquivo="jogador_cauteloso.xlsx"
    )


if __name__ == "__main__":
    analisar_cauteloso()
