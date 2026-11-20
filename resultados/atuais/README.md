# Resultados - registros de eventos dos currículos Lattes

Pasta gerada a partir dos 4 conjuntos quantificados do projeto Magela. Todos os
números desta página são os das saídas aqui presentes.

## Os 4 conjuntos

| Conjunto | Chave |
|---|---|
| N | `NOME-DO-EVENTO` |
| NA | `NOME-DO-EVENTO \| ANO-DO-EVENTO` |
| NPA | `NOME-DO-EVENTO \| ANO-DO-EVENTO \| PAIS-DO-EVENTO` |
| NCA | `NOME-DO-EVENTO \| ANO-DO-EVENTO \| CIDADE-DO-EVENTO` |

As chaves são normalizadas (minúsculas, sem acentos, sem pontuação, stopwords e
numerais). Os textos dos gráficos e tabelas usam "registrados".

## Totais (`resumo.csv`)

81.029.436 ocorrências no arquivo bruto, contadas de forma idêntica nos 4 conjuntos.

| | N | NA | NPA | NCA |
|---|---:|---:|---:|---:|
| Chaves distintas | 18.817.656 | 23.952.738 | 24.366.351 | 29.189.950 |
| Média de ocorrências | 4,31 | 3,38 | 3,33 | 2,78 |
| Mediana | 1 | 1 | 1 | 1 |
| Máxima | 134.667 | 14.557 | 14.554 | 12.210 |
| Eventos genéricos (1 ocorrência) | 13.843.554 | 17.716.360 | 18.126.764 | 22.454.830 |
| Cobertura do top 10 | 1,15% | 0,13% | 0,13% | 0,12% |
| Linhas sem nome | 13.173 | 13.173 | 13.173 | 13.173 |
| Linhas inválidas | 0 | 0 | 0 | 0 |

Os eventos genéricos (uma única ocorrência) são a maioria das chaves em todos os
conjuntos — de 73,6% (N) a 76,9% (NCA) — e são quantificados, não removidos.

Máximos: no N, "reuniao anual sbpc" (134.667); no NA e no NPA, "congresso
nacional multidisciplinar covid" de 2021 (14.557 e 14.554); no NCA, "congresso
brasileiro saude coletiva" em porto alegre em 2012 (12.210).

## Faixas de ocorrências (`eventosPorFaixas.csv`)

Faixas: 0-11, 12-20, 21-50, 51-100, 101-200, 201-500, 501-1000, 1001-5000,
5001-10000, 10001-100000, 100001+.

A faixa 0-11 é a maior em todos os conjuntos:

| Conjunto | Eventos na faixa 0-11 | Ocorrências na faixa 0-11 |
|---|---:|---:|
| N | 18.190.402 | 28.836.165 (35,6% do total) |
| NA | 23.150.968 | 36.536.941 |
| NPA | 23.571.306 | 36.945.541 |
| NCA | 28.424.521 | 42.693.406 |

No N, a faixa 10001-100000 tem só 334 eventos, mas 7.268.967 ocorrências.

## Série por ano (`eventosPorAno.csv`)

121 anos distintos, de 1900 a 2030, para NA, NPA e NCA (o N não tem ano).
Pico em 2017: 4.288.149 ocorrências e 1.186.781 eventos distintos no NA; no NCA
o maior número de eventos distintos é em 2020 (1.578.145).

## Top 10 (`top10_*.csv`)

- `top10_N.csv` — 10 nomes de evento mais registrados.
- `top10_NA.csv` / `top10_NPA.csv` / `top10_NCA.csv` — 10 edições mais
  registradas (nome + ano, nome + país + ano, nome + cidade + ano).
- `top10_{N,NA,NPA,NCA}_genericas.csv` e `..._nao_genericas.csv` — os mesmos
  top 10, separados por evento genérico e não genérico. Genérico: nome formado
  só por tipo + tema de atividade acadêmica ampla (iniciação científica,
  extensão, ensino, pesquisa, ciência e tecnologia, semana acadêmica), sem
  sigla, instituição ou nome próprio — ex.: `congresso iniciacao cientifica`.
  Não genérico: tem esse qualificador — ex.: `reuniao anual sbpc`,
  `congresso iniciacao cientifica unesp`.

## Mapeamento cidade → UF (`eventosPorCidadeUF.csv`, `relatorio*.csv`)

29.189.950 chaves NCA processadas (detalhes em `relatorioMapeamento.csv`):

| Status | Ocorrências | % |
|---|---:|---:|
| OK | 64.024.099 | 79,00% |
| NAO-ENCONTRADO | 6.575.212 | 8,11% |
| AMBIGUO | 5.660.554 | 6,98% |
| SEM-CIDADE | 4.519.996 | 5,58% |
| OK-APELIDO | 249.575 | 0,31% |
| SEM-NOME | 13.173 | 0,02% |

- 5.266 cidades brasileiras distintas mapeadas, contra 5.571 municípios do IBGE;
  27 UFs.
- 251 nomes de cidade ambíguos (`relatorioCidadesAmbiguas.csv`), com 5.660.554
  ocorrências: belem (AL|PA|PB) 1.512.161; santa maria (PA|RN|RS) 847.581;
  campo grande (AL|MS) 472.230.
- SP concentra 14.995.727 ocorrências, 5,7% ambíguas; AC é a de pior qualidade,
  com 97,6% ambíguas.
- Entre os não encontrados: online 350.301, lisboa 163.466, paris 97.893
  (`cidadesNaoEncontradas.csv`, 2.000 primeiros).

## Mapa mundial (`eventosPorPais.csv`)

247 países distintos, de 1900 a 2030. Brasil 77.224.917 ocorrências; Estados
Unidos 799.933; Portugal 380.345. 80 países sem código ISO-3, somando 16.062
ocorrências (0,02% do total) — `eventosPorPaisSemCodigo.csv`.

## Arquivos

Raiz (`;` como delimitador, exceto onde indicado):

- `resumo.csv` — estatísticas por conjunto.
- `top10_{N,NA,NPA,NCA}.csv` — top 10 por conjunto.
- `top10_{N,NA,NPA,NCA}_{genericas,nao_genericas}.csv` — top 10 separado por
  evento genérico e não genérico.
- `eventosPorAno.csv` — `CONJUNTO;ANO;DISTINTOS;OCORRENCIAS`.
- `eventosPorFaixas.csv` — `CONJUNTO;INICIO;FIM;FAIXA;QTD-EVENTOS;OCORRENCIAS`.
- `eventosPorPais.csv`, `eventosPorPaisAno.csv`, `eventosPorUF.csv`,
  `eventosPorUFAno.csv`, `eventosPorCidadeUF.csv` — séries dos mapas.
- `relatorioMapeamento.csv`, `relatorioCidadesAmbiguas.csv`,
  `cidadesNaoEncontradas.csv` — diagnóstico do mapeamento cidade → UF.
- `graficoEventosPorAno.png`, `graficoEventosPorFaixas.png`,
  `graficoTop10.png`, `MapaBrasilEventosPorUF.png`,
  `MapaMundiEventosPorPaisSemBrasil.png` — gráficos.

Subpastas:

- `graficos/` — 15 PNGs (série anual, top 10 dos 4 conjuntos, top 10 genéricos
  e não genéricos, faixas, UF).
- `mapas/` — Brasil e mundo em PNG e HTML interativo.
- `tabelas/` — `tabelas_formatadas.xlsx` e CSVs para Datawrapper/Flourish.
- `dw/` — 13 CSVs com delimitador `,` para o Datawrapper (UF, UF por década,
  países com/sem Brasil, países por década, cidades com coordenada, cidades sem
  coordenada para revisão, série anual, faixas em colunas, top 10 dos 4 conjuntos).
- `geo/` — `brasil_uf.geojson` e `paises.geojson`.

## Como foi gerado

Scripts em `códigos\mapasResultados\` (E: `mapasResultados\`), nesta ordem:

```
python quantificar.py          # quantifica os 4 conjuntos no CSV bruto
python tabelas.py              # top10, ano, faixas, resumo
python graficos.py             # PNGs da raiz
python dadosMapaMundial.py     # países + ISO-3
python dadosMapaBrasil.py      # cidade → UF + relatórios
python gerarVisualizacao.py    # graficos/, mapas/, tabelas/, geo/
python tabelasDatawrapper.py   # dw/
python top10Genericos.py N     # top10 genéricas/não genéricas (repetir p/ NA, NPA, NCA)
python graficosGenericos.py    # PNGs dos top10 genéricas/não genéricas
```

Entradas: os 4 arquivos `conjunto*_ordenado.csv` (um `.rar` por conjunto em
`csvs\`). Saída: esta pasta (`resultados\`; no E:, `mapasResultados\saidas\`).
