# Magela - Lattes CV Data Extraction

## What this is

Python scripts that extract structured data from Brazilian Lattes CV XML files (zip-wrapped) and output CSVs. Two independent sub-projects with similar but diverged code:

- **ProjetoMagelaAO** - older version; has `extratorEventosPrimeiraLeitura.py` (first-pass)
- **ProjetoMagelaAU** - newer version; has `extratorEventosFinal.py` (final-pass) and `filtroEventosINICIALCSV.py` (row filtering)
- **Exemplo Curriculos** - sample Lattes CV zips organized by CPF prefix (`00/`, `01/`, ...)

Both projects have `extratorEventosSegundaLeitura.py` and `extrator_preprint.py` (nearly identical between AO/AU).

## Running scripts

No package manager or build step. Scripts are standalone Python 3.

### Phase 1 - XML extraction (ProjetoMagelaAO / ProjetoMagelaAU)

```bash
python extratorEventosPrimeiraLeitura.py   # AO first-pass
python extratorEventosSegundaLeitura.py    # AO/AU second-pass
python extratorEventosFinal.py             # AU final-pass
python extrator_preprint.py                # article/preprint extraction
python filtroEventosINICIALCSV.py          # AU: filter events CSV
python pegarAlgumasLinhas.py               # AO: sample rows (uses pandas)
python pegararquivos.py                    # AU: sample rows (uses pandas)
```

### Phase 2 - City→UF mapping and occurrence counting (H:\Magela\Arquvios2Semestre\)

```bash
python mapaCidadeUF.py                     # builds mapaCidadeUF.json from IBGE data
python geradorNomeEstado.py                # adds UF column to events → nomeEstado.csv
python contadorOcorrencias.py              # counts by name, name+city, name+UF
```

**Execution order**: `mapaCidadeUF.py` → `geradorNomeEstado.py` → `contadorOcorrencias.py`

### Phase 3 - Results mapping: tables, charts, world/Brazil heatmaps (H:\Magela\mapasResultados\)

Newer suite driven by `utilitarios.py` (paths + the 4 final sets live there). All outputs `;`-delimited, written to `mapasResultados\saidas\`.

```bash
python quantificar.py          # quantify the 4 sets (NOME / +ANO / +PAIS / +CIDADE); only step that reads + normalizes the raw CSV (writes saidas\normalizado.csv)
python tabelas.py              # top10, events-per-year, events-per-band, summary (reads normalized CSVs only)
python graficos.py             # 3 PNGs (matplotlib; needs `pip install matplotlib`)
python dadosMapaMundial.py     # events by PAIS + ISO-3 codes → world choropleth data (reads normalizado.csv)
python dadosMapaBrasil.py      # city→UF via IBGE kelvins/municipios-brasileiros + ambiguity margins (reads normalizado.csv)
```

Normalization happens exactly once in `quantificar.py`; the intermediate
`saidas\normalizado.csv` (NOME;ANO;PAIS;CIDADE, one row per raw line) is the
only feed for tabelas/mapa scripts — they never re-read or re-normalize the raw
CSV. If inputs are already normalized upstream, point `utilitarios.CSV_ENTRADA`
at that file and keep `quantificar` as-is.

Order matters: quantificar → tabelas → graficos; every script reads only
`saidas\*.csv` (never the raw CSV directly). Do not mix these `;` outputs with
the `|`-delimited Conjunto files.

**Before running any script**: update the hardcoded paths at the top of the file (`pastaCurriculos`, `saidaCSV`, `base_dir`, `curriculos`, `result_dir`, `caminhoEntrada`, `caminhoSaida`). These point to absolute Windows paths that must match your local data layout.

## Critical gotchas

- **CSV delimiters differ**: event scripts use `;` (semicolon); `extrator_preprint.py` uses `,` (comma); `exemploConjunto4.csv` uses `|` (pipe). Mixing them up will corrupt downstream analysis.
- **Paths are hardcoded in every file** - no config files or CLI args. Each script must be edited before first run.
- **AO vs AU are not interchangeable**: `extratorEventosPrimeiraLeitura.py` (AO) and `extratorEventosFinal.py` (AU) look similar but have subtle differences in field mapping (e.g., ORGANIZACAO-DE-EVENTO uses `TITULO` in AU second-leitura, not `NOME-DO-EVENTO`).
- **`extratorEventosSegundaLeitura.py` exists in both projects** - they are nearly identical but confirm which copy you're editing.
- **Preprint detection**: the `formas_preprint` set includes accented variants (`PRÉ PRINT`, `PRÉ-PRINT`, `PRÉPRINT`). The check normalizes to `.upper()` first.
- **City→UF mapping caveat**: `normalizacaoGeral.py` may remove stopwords from CIDADE-DO-EVENTO (e.g., "São José dos Campos" → "jose campos"), breaking exact match with IBGE data. The `mapaCidadeUF.json` includes heuristic keys (connectors removed) to handle this. ~4.5% of distinct city names are ambiguous (exist in multiple UFs) and get `AMBIGUO` status.

## Data format

- Input: zipped Lattes XML CVs (one XML per zip, named `{cpf}.xml`)
- Expected folder structure: `pastaCurriculos/{00-99}/{cpf}.zip` (two-digit prefix subfolders)
- Output: CSV files in `saidaCSV/` or `result_dir/`
- Event CSV columns: IDENTIFICADOR, TIPO-REGISTRO, NOME-DO-EVENTO, TIPO-DE-EVENTO, CLASSIFICACAO-DO-EVENTO, ANO-DO-EVENTO, PAIS-DO-EVENTO, CIDADE-DO-EVENTO, LOCAL-DO-EVENTO, CODIGO-INSTITUICAO-PROMOTORA, INSTITUICAO-PROMOTORA, DURACAO-EM-SEMANAS
- Article CSV columns: TITULO-DO-ARTIGO, ANO, NATUREZA, LOCAL-NATUREZA, MEIO-DE-DIVULGACAO, ... (24 columns)
- `exemploConjunto4.csv` columns: NOME-DO-EVENTO|ANO-DO-EVENTO|PAIS-DO-EVENTO|CIDADE-DO-EVENTO (pipe-delimited)
- `nomeEstado.csv` columns: NOME-DO-EVENTO;ESTADO;STATUS-MAPEAMENTO (semicolon-delimited)
- `contagemPor*.csv` columns: OCORRENCIAS;NOME-DO-EVENTO[;CIDADE-DO-EVENTO|ESTADO] (semicolon-delimited, sorted descending)

## Dependencies

- Python 3.10+ (uses `tuple[str, str]` type hints)
- `pandas` - only in `pegarAlgumasLinhas.py` / `pegararquivos.py`
- Everything else is stdlib: `csv`, `os`, `io`, `time`, `zipfile`, `xml.etree.ElementTree`, `glob`, `json`, `unicodedata`, `urllib.request`, `collections.defaultdict`

## Code style

- Portuguese variable/function names throughout (e.g., `escritor_eventos`, `abridorDosZIP`, `lerOsXML`)
- No type checker, linter, or formatter configured
- No tests exist
- Comment style: inline `#` notes, some `##f` markers at top of files
