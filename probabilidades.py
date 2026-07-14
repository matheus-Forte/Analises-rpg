from itertools import product, combinations
from math import comb

import pandas as pd

from configuracao import DADOS_ROLADOS, DADOS_MANTIDOS, LADOS
from faces import FACES
from utilidades import (
    calcular_resultado,
    criar_contador,
    criar_tabela_resultados,
    salvar_csv,
    salvar_excel
)


def validar_configuracao():
    if DADOS_ROLADOS < 1:
        raise ValueError("DADOS_ROLADOS deve ser pelo menos 1.")

    if DADOS_MANTIDOS < 1:
        raise ValueError("DADOS_MANTIDOS deve ser pelo menos 1.")

    if DADOS_MANTIDOS > DADOS_ROLADOS:
        raise ValueError(
            "DADOS_MANTIDOS nao pode ser maior que DADOS_ROLADOS."
        )

    faces_esperadas = set(range(1, LADOS + 1))
    faces_definidas = set(FACES.keys())

    if faces_definidas != faces_esperadas:
        faltando = sorted(faces_esperadas - faces_definidas)
        sobrando = sorted(faces_definidas - faces_esperadas)

        partes = [
            "A configuracao de FACES nao corresponde ao numero de lados."
        ]

        if faltando:
            partes.append(f"Faces ausentes: {faltando}.")

        if sobrando:
            partes.append(f"Faces excedentes: {sobrando}.")

        raise ValueError(" ".join(partes))


def gerar_distribuicao_conjunta():
    contador = criar_contador()

    indices_possiveis = list(
        combinations(range(DADOS_ROLADOS), DADOS_MANTIDOS)
    )

    total_rolagens = LADOS ** DADOS_ROLADOS
    combinacoes_por_rolagem = len(indices_possiveis)
    total_ocorrencias = total_rolagens * combinacoes_por_rolagem

    for rolagem in product(
        range(1, LADOS + 1),
        repeat=DADOS_ROLADOS
    ):
        for indices in indices_possiveis:
            dados_mantidos = tuple(
                rolagem[indice] for indice in indices
            )

            resultado = calcular_resultado(
                dados_mantidos=dados_mantidos,
                faces=FACES
            )

            contador[resultado] += 1

    ocorrencias_contadas = sum(contador.values())

    if ocorrencias_contadas != total_ocorrencias:
        raise RuntimeError(
            "Erro de contagem: o total contado nao corresponde "
            "ao total esperado. "
            f"Esperado: {total_ocorrencias}; "
            f"contado: {ocorrencias_contadas}."
        )

    tabela = criar_tabela_resultados(
        contador=contador,
        total_ocorrencias=total_ocorrencias
    )

    soma_probabilidades = tabela["Probabilidade_percentual"].sum()

    if abs(soma_probabilidades - 100.0) > 0.000001:
        raise RuntimeError(
            "Erro de probabilidade: a soma nao resultou em 100%. "
            f"Resultado obtido: {soma_probabilidades:.10f}%."
        )

    return tabela, total_rolagens, combinacoes_por_rolagem


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


def criar_resumo(
    tabela_conjunta,
    total_rolagens,
    combinacoes_por_rolagem
):
    total_ocorrencias = tabela_conjunta["Ocorrencias"].sum()

    media_acertos = (
        tabela_conjunta["Acertos"]
        * tabela_conjunta["Ocorrencias"]
    ).sum() / total_ocorrencias

    media_desafios = (
        tabela_conjunta["Desafios"]
        * tabela_conjunta["Ocorrencias"]
    ).sum() / total_ocorrencias

    media_adaptacoes = (
        tabela_conjunta["Adaptacoes"]
        * tabela_conjunta["Ocorrencias"]
    ).sum() / total_ocorrencias

    soma_probabilidades = tabela_conjunta[
        "Probabilidade_percentual"
    ].sum()

    return pd.DataFrame([
        {
            "Dados_rolados": DADOS_ROLADOS,
            "Dados_mantidos": DADOS_MANTIDOS,
            "Lados_do_dado": LADOS,
            "Rolagens_possiveis": total_rolagens,
            "Combinacoes_por_rolagem": combinacoes_por_rolagem,
            "Ocorrencias_totais": total_ocorrencias,
            "Media_acertos": media_acertos,
            "Media_desafios": media_desafios,
            "Media_adaptacoes": media_adaptacoes,
            "Soma_probabilidades_percentual": soma_probabilidades
        }
    ])


def analisar_probabilidades():
    validar_configuracao()

    (
        tabela_conjunta,
        total_rolagens,
        combinacoes_por_rolagem
    ) = gerar_distribuicao_conjunta()

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

    tabela_resumo = criar_resumo(
        tabela_conjunta,
        total_rolagens,
        combinacoes_por_rolagem
    )

    sufixo = f"{DADOS_ROLADOS}d{LADOS}_mantem{DADOS_MANTIDOS}"

    caminhos = {
        "Distribuicao_conjunta": salvar_csv(
            tabela_conjunta,
            f"probabilidades_conjuntas_{sufixo}.csv"
        ),
        "Distribuicao_acertos": salvar_csv(
            tabela_acertos,
            f"probabilidades_acertos_{sufixo}.csv"
        ),
        "Distribuicao_desafios": salvar_csv(
            tabela_desafios,
            f"probabilidades_desafios_{sufixo}.csv"
        ),
        "Distribuicao_adaptacoes": salvar_csv(
            tabela_adaptacoes,
            f"probabilidades_adaptacoes_{sufixo}.csv"
        ),
        "Resumo": salvar_csv(
            tabela_resumo,
            f"probabilidades_resumo_{sufixo}.csv"
        ),
        "Distribuicao_conjunta": salvar_excel(
          tabela_conjunta,
          f"probabilidades_conjuntas_{sufixo}.xlsx"
        ),
        "Distribuicao_acertos": salvar_excel(
            tabela_acertos,
            f"probabilidades_acertos_{sufixo}.xlsx"
        ),
        "Distribuicao_desafios": salvar_excel(
            tabela_desafios,
            f"probabilidades_desafios_{sufixo}.xlsx"
        ),
        "Distribuicao_adaptacoes": salvar_excel(
            tabela_adaptacoes,
           f"probabilidades_adaptacoes_{sufixo}.xlsx"
        ),
        "Resumo": salvar_excel(
            tabela_resumo,
            f"probabilidades_resumo_{sufixo}.xlsx"
        )
    }

    print("Analise concluida.")
    print(f"Rolagens possiveis: {total_rolagens}")
    print(
        "Combinacoes mantidas por rolagem: "
        f"{combinacoes_por_rolagem}"
    )
    print(
        "Ocorrencias totais analisadas: "
        f"{total_rolagens * combinacoes_por_rolagem}"
    )
    print(
        "Soma das probabilidades: "
        f"{tabela_conjunta['Probabilidade_percentual'].sum():.10f}%"
    )
    print()

    for nome, caminho in caminhos.items():
        print(f"{nome}: {caminho}")

    return {
        "conjunta": tabela_conjunta,
        "acertos": tabela_acertos,
        "desafios": tabela_desafios,
        "adaptacoes": tabela_adaptacoes,
        "resumo": tabela_resumo
    }


if __name__ == "__main__":
    analisar_probabilidades()
