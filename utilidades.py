from collections import Counter
from itertools import combinations
from pathlib import Path

import pandas as pd


def calcular_resultado(dados_mantidos, faces):
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
        probabilidade_percentual = ocorrencias / total_ocorrencias * 100

        linhas.append({
            "Acertos": acertos,
            "Desafios": desafios,
            "Adaptacoes": adaptacoes,
            "Ocorrencias": ocorrencias,
            "Probabilidade_percentual": probabilidade_percentual
        })

    tabela = pd.DataFrame(linhas)

    if tabela.empty:
        return tabela

    tabela = tabela.sort_values(
        by=["Acertos", "Desafios", "Adaptacoes"]
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
        decimal=",",
        float_format="%.10f"
    )

    return caminho


def salvar_excel(tabela, nome_arquivo, pasta="Resultados"):
    pasta_resultados = Path(pasta)
    pasta_resultados.mkdir(parents=True, exist_ok=True)

    caminho = pasta_resultados / nome_arquivo

    with pd.ExcelWriter(
        caminho,
        engine="openpyxl"
    ) as writer:
        tabela.to_excel(
            writer,
            index=False,
            sheet_name="Resultados"
        )

        planilha = writer.sheets["Resultados"]

        for coluna in planilha.columns:
            maior_tamanho = 0
            letra_coluna = coluna[0].column_letter

            for celula in coluna:
                if celula.value is not None:
                    maior_tamanho = max(
                        maior_tamanho,
                        len(str(celula.value))
                    )

            planilha.column_dimensions[letra_coluna].width = (
                maior_tamanho + 2
            )

    return caminho


def criar_contador():
    return Counter()
