from collections import Counter
from itertools import combinations
from pathlib import Path

import pandas as pd


def calcular_resultado(dados_mantidos, faces):
    """
    Soma Acertos, Desafios e Adaptações dos dados mantidos.
    """
    acertos = 0
    desafios = 0
    adaptacoes = 0

    for dado in dados_mantidos:
        resultado_face = faces[dado]
        acertos += resultado_face[0]
        desafios += resultado_face[1]
        adaptacoes += resultado_face[2]

    return acertos, desafios, adaptacoes


def gerar_combinacoes_mantidas(rolagem, quantidade_mantida):
    return combinations(rolagem, quantidade_mantida)


def registrar_resultado(contador, resultado):
    contador[resultado] += 1


def criar_tabela_resultados(contador, total_ocorrencias):
    linhas = []

    for resultado, ocorrencias in contador.items():
        acertos, desafios, adaptacoes = resultado
        probabilidade = ocorrencias / total_ocorrencias

        linhas.append({
            "Acertos": acertos,
            "Desafios": desafios,
            "Adaptações": adaptacoes,
            "Ocorrências": ocorrencias,
            "Probabilidade": probabilidade,
            "Probabilidade (%)": probabilidade * 100
        })

    tabela = pd.DataFrame(linhas)

    if tabela.empty:
        return tabela

    tabela = tabela.sort_values(
        by=["Acertos", "Desafios", "Adaptações"]
    ).reset_index(drop=True)

    return tabela


def salvar_csv(tabela, nome_arquivo, pasta="Resultados"):
    pasta_resultados = Path(pasta)
    pasta_resultados.mkdir(parents=True, exist_ok=True)

    caminho = pasta_resultados / nome_arquivo

    tabela.to_csv(
        caminho,
        index=False,
        sep=";",
        encoding="utf-8-sig",
        decimal=","
    )

    return caminho


def criar_contador():
    return Counter()
