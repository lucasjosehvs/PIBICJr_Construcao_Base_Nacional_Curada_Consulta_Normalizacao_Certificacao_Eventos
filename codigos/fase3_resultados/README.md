# mapasResultados — Mapeamento e apresentação de resultados

Scripts de mapeamento dos **4 conjuntos finais** de eventos a partir do CSV bruto,
para construir tabelas, gráficos e os dados de mapas de calor (mundo e Brasil).

## Os 4 conjuntos (chaves quantificadas no CSV bruto)

| Conjunto | Chave |
|---|---|
| Conjunto1 | `NOME-DO-EVENTO` |
| Conjunto2 | `NOME-DO-EVENTO \| ANO-DO-EVENTO` |
| Conjunto3 | `NOME-DO-EVENTO \| ANO-DO-EVENTO \| PAIS-DO-EVENTO` |
| Conjunto4 | `NOME-DO-EVENTO \| ANO-DO-EVENTO \| CIDADE-DO-EVENTO` |

Cada arquivo `ConjuntoX_quantificado.csv` traz `OCORRENCIAS` + as colunas da chave,
ordenado por ocorrência decrescente. As chaves são normalizadas (minúsculas, sem
acentos, sem pontuação/stopwords/numerais — mesmas regras do `normalizacaoGeral.py`).

> Onde configurar: caminhos e a definição dos conjuntos ficam no topo de
> **`utilitarios.py`** (`CSV_ENTRADA`, `DIR_SAIDA`, `CONJUNTOS`).
>
> A normalização é **uma única vez**: só o `quantificar.py` lê o CSV bruto e
> aplica as regras (minúsculas, sem acentos, sem pontuação/stopwords/numerais).
> Ele também grava `saidas\normalizado.csv` (as 4 colunas já normalizadas, uma
> linha por linha do bruto), que é o **único** insumo dos scripts seguintes —
> eles nunca leem/normalizam o bruto de novo.

## Ordem de execução

```bash
python quantificar.py          # 1. quantifica os 4 conjuntos no bruto (+ normalizado.csv)
python tabelas.py              # 2. top10, eventos por ano/faixa, resumo
python graficos.py             # 3. gráficos PNG (requer matplotlib)
python dadosMapaMundial.py     # 4. eventos por país (+ ISO-3) p/ mapa mundo
python dadosMapaBrasil.py      # 5. cidade→UF (+ margens) p/ mapa Brasil
```

Use o Python do projeto (tem pandas/nltk/matplotlib), ex.:
```
C:\Users\PICHAU\Desktop\PadronizacoesMagela - 2S\.venv\Scripts\python.exe
```
(Ou `pip install matplotlib` num venv próprio para o passo 3.)

## O que cada script gera (pasta `saidas\`)

- `normalizado.csv` — intermediário já normalizado (`NOME;ANO;PAIS;CIDADE`,
  1 linha por linha do bruto); fonte única de `tabelas.py`, `dadosMapaMundial.py`
  e `dadosMapaBrasil.py`.
- `Conjunto1..4_quantificado.csv` — ocorrências de cada chave (base de tudo).
- `top10_Conjunto1..4.csv` — **10 primeiros lugares** com mais eventos, por conjunto.
- `eventosPorAno.csv` — série por ano para os 4 conjuntos
  (colunas `CONJUNTO;ANO;DISTINTOS;OCORRENCIAS`).
- `eventosPorFaixas.csv` — distribuição **em faixas** de ocorrências (1, 2-3, 4-5,
  6-10, ..., 501-1000, 1001+), com `QTD-EVENTOS` (chaves) e `OCORRENCIAS`.
- `resumo.csv` — totais, chaves distintas, média/mediana/máximo, top-10 e cobertura.
- `graficoEventosPorAno.png` — 4 linhas (um por conjunto).
- `graficoEventosPorFaixas.png` — 4 linhas, eixo Y em escala log.
- `graficoTop10.png` — barras do top 10 de cada conjunto.
- `eventosPorPais.csv` / `eventosPorPaisAno.csv` — dados do **mapa mundial**
  (+ `CODIGO-ISO3` para usar direto em choropleth).
- `eventosPorPaisSemCodigo.csv` — países sem ISO mapeado (margem).
- `eventosPorUF.csv` / `eventosPorUFAno.csv` / `eventosPorCidadeUF.csv` — dados do
  **mapa Brasil** (por UF/cidade, com `CODIGO-IBGE` e `OCORRENCIAS-AMBIGUAS`).
- `relatorioMapeamento.csv` — status de mapeamento cidade→UF (margens de erro).
- `relatorioCidadesAmbiguas.csv` — cidades repetidas em mais de uma UF.

Obs.: Municípios/estados do IBGE (`municipios.csv`, `estados.csv` — repo
`kelvins/municipios-brasileiros`) são baixados automaticamente na primeira execução
do `dadosMapaBrasil.py`.

## Regras do mapeamento Brasil

- País fora de `{'', 'brasil', 'brazil'}` → excluído (`EXTERIOR`).
- Cidade normalizada (sem acento, maiúsculas) buscada no cadastro do IBGE; se não
  bate, tenta heurística sem conectores (de/do/da/dos/das/e).
- **Cidade com nome repetido em mais de uma UF (ambígua)** → contabilizada em
  **todas** as UFs candidatas e listada em `relatorioCidadesAmbiguas.csv`, para
  apresentar as margens de erro (colunas `OCORRENCIAS-AMBIGUAS` / `AMBIGUA`).

## Como continuar (próximos passos recomendados)

Usar `utilitarios.py` como único ponto de configuração; a normalização já foi
aplicada uma vez e os insumos deste pipeline são os CSVs de `saidas\`. Confira o
`resumo.csv` (a cobertura top-10 cai de
   ~8% no Conjunto1 para ~2% no Conjunto4 — bem comportado para apresentação).
2. **Revisar uma observação dos dados**: todas as ocorrências saíram **pares**
   (ex.: nada com 1–3 ocorrências, valores 4, 8, 10, ...). Confirme se a base bruta
   não tem duplicação estrutural (ex.: duas leituras/módulos mesclados) antes de
   apresentar números absolutos; os dados relativos (ranking, % ) não mudam.
3. **Mapas com Plotly** (1 comando): 
   - Mundo: `px.choropleth(dados, locations='CODIGO-ISO3', color='OCORRENCIAS', hover_name='PAIS-DO-EVENTO')` 
   - Brasil: `px.choropleth(dados, locations='CODIGO-IBGE', animation_frame='ANO', color='OCORRENCIAS', scope='south america')` (dados: `eventosPorUF.csv`/`eventosPorUFAno.csv`)
   - Pontos por cidade: `px.scatter_mapbox(...)` com `eventosPorCidadeUF.csv`.
4. **Apresentação**: os CSVs de `saidas\` são a fonte para Streamlit/Quarto/Excel.
   O `graficoEventosPorAno.png` e o `graficoEventosPorFaixas.png` já saem prontos.
5. **Novidades do Conjunto4**: se quiser o formato antigo com PAÍS, troque a linha
   do `Conjunto4` em `utilitarios.py` para incluir `'PAIS-DO-EVENTO'`.