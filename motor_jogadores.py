from itertools import product, combinations
from math import comb, sqrt
from random import Random

import pandas as pd

import configuracao
from faces import FACES
from utilidades import (
    calcular_resultado,
    criar_contador,
    criar_tabela_resultados,
    salvar_excel_completo
)


Z_95 = 1.959963984540054


def validar_configuracao():
    if configuracao.DADOS_ROLADOS < 1:
        raise ValueError("DADOS_ROLADOS deve ser pelo menos 1.")

    if configuracao.DADOS_MANTIDOS < 1:
        raise ValueError("DADOS_MANTIDOS deve ser pelo menos 1.")

    if configuracao.DADOS_MANTIDOS > configuracao.DADOS_ROLADOS:
        raise ValueError(
            "DADOS_MANTIDOS nao pode ser maior que DADOS_ROLADOS."
        )


def margem_erro_conservadora_percentual(amostras):
    if amostras <= 0:
        return float("inf")

    return Z_95 * sqrt(0.25 / amostras) * 100


def custo_exato_estimado():
    total_rolagens = (
        configuracao.LADOS ** configuracao.DADOS_ROLADOS
    )

    combinacoes_por_rolagem = comb(
        configuracao.DADOS_ROLADOS,
        configuracao.DADOS_MANTIDOS
    )

    avaliacoes = (
        total_rolagens * combinacoes_por_rolagem
    )

    return (
        total_rolagens,
        combinacoes_por_rolagem,
        avaliacoes
    )


def escolher_metodo():
    (
        total_rolagens,
        combinacoes_por_rolagem,
        avaliacoes
    ) = custo_exato_estimado()

    if configuracao.TIPO_ANALISE == "exata":
        metodo = "Exata"
    elif configuracao.TIPO_ANALISE == "simulacao":
        metodo = "Simulacao"
    elif (
        avaliacoes
        <= configuracao.LIMITE_AVALIACOES_EXATAS
    ):
        metodo = "Exata"
    else:
        metodo = "Simulacao"

    return (
        metodo,
        total_rolagens,
        combinacoes_por_rolagem,
        avaliacoes
    )


def escolher_melhor_combinacao(rolagem, criterio):
    melhor_resultado = None
    melhor_chave = None
    melhores_dados = None

    for indices in combinations(
        range(configuracao.DADOS_ROLADOS),
        configuracao.DADOS_MANTIDOS
    ):
        dados = tuple(
            rolagem[indice] for indice in indices
        )

        resultado = calcular_resultado(
            dados,
            FACES
        )

        chave = criterio(resultado)

        if melhor_chave is None or chave > melhor_chave:
            melhor_chave = chave
            melhor_resultado = resultado
            melhores_dados = dados

    return melhor_resultado, melhores_dados


def criar_distribuicao_individual(tabela_conjunta, coluna):
    tabela = (
        tabela_conjunta
        .groupby(coluna, as_index=False)["Ocorrencias"]
        .sum()
        .sort_values(coluna)
        .reset_index(drop=True)
    )

    total = tabela["Ocorrencias"].sum()

    tabela["Probabilidade_percentual"] = (
        tabela["Ocorrencias"] / total * 100
    )

    return tabela


def calcular_estatisticas(tabela, coluna):
    total = tabela["Ocorrencias"].sum()
    valores = tabela[coluna]
    pesos = tabela["Ocorrencias"]

    media = (valores * pesos).sum() / total

    variancia = (
        ((valores - media) ** 2) * pesos
    ).sum() / total

    acumulado = 0
    q1 = None
    mediana = None
    q3 = None

    for _, linha in tabela.iterrows():
        acumulado += linha["Ocorrencias"]
        proporcao = acumulado / total

        if q1 is None and proporcao >= 0.25:
            q1 = linha[coluna]

        if mediana is None and proporcao >= 0.50:
            mediana = linha[coluna]

        if q3 is None and proporcao >= 0.75:
            q3 = linha[coluna]

    maior_ocorrencia = tabela["Ocorrencias"].max()

    modas = tabela.loc[
        tabela["Ocorrencias"] == maior_ocorrencia,
        coluna
    ].tolist()

    return {
        "Media": media,
        "Mediana": mediana,
        "Moda": ", ".join(str(x) for x in modas),
        "Variancia": variancia,
        "Desvio_padrao": sqrt(variancia),
        "Minimo": valores.min(),
        "Primeiro_quartil": q1,
        "Terceiro_quartil": q3,
        "Maximo": valores.max()
    }


def criar_chance_acumulada(tabela_acertos):
    tabela = tabela_acertos.copy()
    total = tabela["Ocorrencias"].sum()

    tabela["Chance_exatamente_percentual"] = (
        tabela["Ocorrencias"] / total * 100
    )

    tabela["Chance_menos_que_percentual"] = (
        tabela["Ocorrencias"]
        .cumsum()
        .shift(fill_value=0)
        / total
        * 100
    )

    tabela["Chance_pelo_menos_percentual"] = (
        tabela["Ocorrencias"][::-1]
        .cumsum()[::-1]
        / total
        * 100
    )

    return tabela[
        [
            "Acertos",
            "Ocorrencias",
            "Chance_exatamente_percentual",
            "Chance_pelo_menos_percentual",
            "Chance_menos_que_percentual"
        ]
    ]


def criar_tabela_faces_mantidas(
    contador_faces,
    total_rolagens
):
    linhas = []

    for face in range(1, configuracao.LADOS + 1):
        ocorrencias = contador_faces[face]

        linhas.append({
            "Face": face,
            "Vezes_mantida": ocorrencias,
            "Media_por_rolagem": (
                ocorrencias / total_rolagens
            ),
            "Participacao_percentual": (
                ocorrencias
                / (
                    total_rolagens
                    * configuracao.DADOS_MANTIDOS
                )
                * 100
            )
        })

    return pd.DataFrame(linhas)


def executar_rolagens(criterio, metodo):
    contador_resultados = criar_contador()
    contador_faces = criar_contador()

    if metodo == "Exata":
        rolagens = product(
            range(1, configuracao.LADOS + 1),
            repeat=configuracao.DADOS_ROLADOS
        )

        total = (
            configuracao.LADOS
            ** configuracao.DADOS_ROLADOS
        )

        for rolagem in rolagens:
            resultado, dados = escolher_melhor_combinacao(
                rolagem,
                criterio
            )

            contador_resultados[resultado] += 1

            for face in dados:
                contador_faces[face] += 1

        return (
            contador_resultados,
            contador_faces,
            total,
            0.0
        )

    rng = Random(configuracao.SEMENTE_SIMULACAO)
    total = 0
    margem = float("inf")

    while total < configuracao.MAXIMO_SIMULACOES:
        lote = min(
            configuracao.TAMANHO_LOTE_SIMULACAO,
            configuracao.MAXIMO_SIMULACOES - total
        )

        for _ in range(lote):
            rolagem = tuple(
                rng.randint(1, configuracao.LADOS)
                for _ in range(configuracao.DADOS_ROLADOS)
            )

            resultado, dados = escolher_melhor_combinacao(
                rolagem,
                criterio
            )

            contador_resultados[resultado] += 1

            for face in dados:
                contador_faces[face] += 1

        total += lote

        margem = margem_erro_conservadora_percentual(
            total
        )

        if (
            total >= configuracao.MINIMO_SIMULACOES
            and margem
            <= configuracao.ERRO_MAXIMO_PERCENTUAL
        ):
            break

    return (
        contador_resultados,
        contador_faces,
        total,
        margem
    )


def analisar_jogador(
    nome_estrategia,
    criterio,
    nome_arquivo
):
    validar_configuracao()

    (
        metodo,
        total_rolagens_teoricas,
        combinacoes_por_rolagem,
        avaliacoes_teoricas
    ) = escolher_metodo()

    (
        contador_resultados,
        contador_faces,
        total_analisado,
        margem_erro
    ) = executar_rolagens(
        criterio,
        metodo
    )

    tabela_conjunta = criar_tabela_resultados(
        contador_resultados,
        total_analisado
    )

    tabela_acertos = criar_distribuicao_individual(
        tabela_conjunta,
        "Acertos"
    )

    tabela_desafios = criar_distribuicao_individual(
        tabela_conjunta,
        "Desafios"
    )

    tabela_adaptacoes = criar_distribuicao_individual(
        tabela_conjunta,
        "Adaptacoes"
    )

    tabela_chance = criar_chance_acumulada(
        tabela_acertos
    )

    tabela_faces = criar_tabela_faces_mantidas(
        contador_faces,
        total_analisado
    )

    linhas_resumo = [
        {
            "Secao": "Configuracao",
            "Metrica": "Estrategia",
            "Valor": nome_estrategia
        },
        {
            "Secao": "Configuracao",
            "Metrica": "Dados_rolados",
            "Valor": configuracao.DADOS_ROLADOS
        },
        {
            "Secao": "Configuracao",
            "Metrica": "Dados_mantidos",
            "Valor": configuracao.DADOS_MANTIDOS
        },
        {
            "Secao": "Metodo",
            "Metrica": "Tipo_de_analise",
            "Valor": metodo
        },
        {
            "Secao": "Metodo",
            "Metrica": "Rolagens_teoricas",
            "Valor": total_rolagens_teoricas
        },
        {
            "Secao": "Metodo",
            "Metrica": "Combinacoes_por_rolagem",
            "Valor": combinacoes_por_rolagem
        },
        {
            "Secao": "Metodo",
            "Metrica": "Avaliacoes_teoricas_exatas",
            "Valor": avaliacoes_teoricas
        },
        {
            "Secao": "Metodo",
            "Metrica": "Rolagens_analisadas",
            "Valor": total_analisado
        },
        {
            "Secao": "Metodo",
            "Metrica": "Margem_erro_95_percentual",
            "Valor": margem_erro
        },
        {
            "Secao": "Verificacao",
            "Metrica": "Soma_probabilidades_percentual",
            "Valor": tabela_conjunta[
                "Probabilidade_percentual"
            ].sum()
        }
    ]

    for nome, tabela, coluna in [
        ("Acertos", tabela_acertos, "Acertos"),
        ("Desafios", tabela_desafios, "Desafios"),
        ("Adaptacoes", tabela_adaptacoes, "Adaptacoes")
    ]:
        estatisticas = calcular_estatisticas(
            tabela,
            coluna
        )

        for metrica, valor in estatisticas.items():
            linhas_resumo.append({
                "Secao": nome,
                "Metrica": metrica,
                "Valor": valor
            })

    tabela_resumo = pd.DataFrame(
        linhas_resumo
    )

    nome_pasta = (
        f"{configuracao.DADOS_ROLADOS}"
        f"d{configuracao.LADOS}"
        f"_mantem{configuracao.DADOS_MANTIDOS}"
    )

    caminho = (
        f"Resultados/{nome_pasta}/{nome_arquivo}"
    )

    tabelas = {
        "Resumo": tabela_resumo,
        "Distribuicao_conjunta": tabela_conjunta,
        "Acertos": tabela_acertos,
        "Desafios": tabela_desafios,
        "Adaptacoes": tabela_adaptacoes,
        "Chance_acumulada": tabela_chance,
        "Faces_mantidas": tabela_faces
    }

    percentuais = {
        "Distribuicao_conjunta": [
            "Probabilidade_percentual"
        ],
        "Acertos": ["Probabilidade_percentual"],
        "Desafios": ["Probabilidade_percentual"],
        "Adaptacoes": ["Probabilidade_percentual"],
        "Chance_acumulada": [
            "Chance_exatamente_percentual",
            "Chance_pelo_menos_percentual",
            "Chance_menos_que_percentual"
        ],
        "Faces_mantidas": [
            "Participacao_percentual"
        ]
    }

    arquivo = salvar_excel_completo(
        tabelas,
        caminho,
        percentuais
    )

    print(f"Analise do jogador {nome_estrategia} concluida.")
    print(f"Metodo: {metodo}")
    print(f"Rolagens analisadas: {total_analisado}")
    print(
        f"Margem de erro conservadora: "
        f"+/- {margem_erro:.4f} ponto percentual"
    )
    print(f"Arquivo criado: {arquivo}")

    return {
        "resumo": tabela_resumo,
        "conjunta": tabela_conjunta,
        "acertos": tabela_acertos,
        "desafios": tabela_desafios,
        "adaptacoes": tabela_adaptacoes,
        "chance_acumulada": tabela_chance,
        "faces_mantidas": tabela_faces,
        "caminho": arquivo
    }
