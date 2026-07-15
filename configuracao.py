# Configuracao principal dos dados
DADOS_ROLADOS = 7
DADOS_MANTIDOS = 3
LADOS = 8

# Metodo de analise:
# "automatica" = usa analise exata quando viavel e simulacao quando necessario
# "exata" = exige analise exata
# "simulacao" = sempre usa simulacao
TIPO_ANALISE = "automatica"

# Limite aproximado de operacoes para permitir analise exata.
# 7d8 mantendo 3 exige 73.400.320 avaliacoes e fica abaixo deste limite.
LIMITE_AVALIACOES_EXATAS = 100_000_000

# Margem de erro maxima da simulacao, em pontos percentuais.
# Exemplo: 0.10 significa aproximadamente +/- 0,10 ponto percentual,
# usando uma estimativa conservadora com 95% de confianca.
ERRO_MAXIMO_PERCENTUAL = 0.10

# A simulacao trabalha em lotes e verifica o erro ao fim de cada lote.
TAMANHO_LOTE_SIMULACAO = 10_000

# Evita simulacoes curtas demais e limita o tempo total.
MINIMO_SIMULACOES = 100_000
MAXIMO_SIMULACOES = 5_000_000

# Mantem os resultados reproduziveis.
SEMENTE_SIMULACAO = 42
