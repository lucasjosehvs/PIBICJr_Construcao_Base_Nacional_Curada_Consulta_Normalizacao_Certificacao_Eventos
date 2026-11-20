##f
# dadosMapaBrasil.py
# Agrega os eventos por UF (mapa de calor do Brasil) cruzando a CIDADE com o
# cadastro de municipios/estados do IBGE (repo kelvins/municipios-brasileiros).
#
# Entrada: conjuntoNCA_ordenado.csv (ja quantificado; delimitador |)
#   NOME-DO-EVENTO | CIDADE-DO-EVENTO | ANO-DO-EVENTO | OCORRENCIAS-EVENTO-CIDADE-ANO
#   Se o arquivo tiver tambem PAIS-DO-EVENTO, linhas de fora do Brasil viram EXTERIOR.
#
# Saidas (em DIR_SAIDA, delimitador ;):
#   eventosPorUF.csv              CODIGO-IBGE;ESTADO;OCORRENCIAS;OCORRENCIAS-AMBIGUAS;EVENTOS-DISTINTOS
#   eventosPorUFAno.csv           ESTADO;ANO;OCORRENCIAS                    (mapa animado)
#   eventosPorCidadeUF.csv        CIDADE-DO-EVENTO;ESTADO;OCORRENCIAS;EVENTOS-DISTINTOS;AMBIGUA
#   relatorioMapeamento.csv       STATUS;CHAVES;OCORRENCIAS;PERCENTUAL-CHAVES;PERCENTUAL-OCORRENCIAS
#   relatorioCidadesAmbiguas.csv  CIDADE-DO-EVENTO;ESTADOS-ENVOLVIDOS;OCORRENCIAS
#   cidadesNaoEncontradas.csv     CIDADE-DO-EVENTO;OCORRENCIAS  (maiores primeiro; base p/ novos APELIDOS)
#
# Regras:
#   - A chave do IBGE e gerada pela MESMA normalizacao do texto de entrada, entao
#     os dois lados do cruzamento sao simetricos (sem heuristica de conectores).
#   - Cidade que existe em mais de uma UF (AMBIGUO) conta em TODAS as UFs candidatas
#     e e reportada para o calculo da margem de erro.
#   - APELIDOS: nomes usuais que nao sao municipio (distritos, grafias) -> chave IBGE.
#     Contam como OK-APELIDO no relatorio, para auditoria.
#   - OCORRENCIAS = soma da contagem (mencoes). EVENTOS-DISTINTOS = numero de linhas
#     (chaves nome|cidade|ano) mapeadas, ou seja, edicoes distintas de evento.
#   - Linhas sem NOME-DO-EVENTO sao excluidas e reportadas (SEM-NOME).
#
# Dependencia: nltk (stopwords pt+en, as mesmas usadas na normalizacao do projeto).

import csv
import os
import re
import time
import unicodedata
from collections import Counter, defaultdict

import nltk
from nltk.corpus import stopwords

# --- caminhos (preencher) -----------------------------------------------------
ENTRADA = r'D:\BACKUP\Magela\conjuntoNCA_ordenado.csv'          # conjuntoNCA_ordenado.csv
ARQ_ESTADOS = r'D:\BACKUP\Magela\csvs\estados.csv'      # estados.csv do IBGE
ARQ_MUNICIPIOS = r'D:\BACKUP\Magela\csvs\municipios.csv'   # municipios.csv do IBGE
DIR_SAIDA = r'D:\BACKUP\Magela\resultados'        # pasta de saida (criada se nao existir)

# --- parametros --------------------------------------------------------------
DELIMITADOR_ENTRADA = '|'
DELIMITADOR_SAIDA = ';'
INTERVALO_LOG = 1000000
LIMITE_TESTE = None            # ex.: 500_000 linhas, para validar antes
LIMITE_NAO_ENCONTRADAS = 2000  # linhas gravadas em cidadesNaoEncontradas.csv
MAX_NAO_ENCONTRADAS = 500000  # teto de cidades distintas em memoria (protege a RAM)
ANO_MIN, ANO_MAX = 1900, 2030
PAISES_BRASIL = {'', 'brasil', 'brazil'}    # so vale se o arquivo tiver PAIS-DO-EVENTO

# nome usual (ja normalizado) -> nome do municipio no IBGE (sera normalizado igual).
# Complete a partir do cidadesNaoEncontradas.csv.
APELIDOS = {
    'buzios': 'Armação dos Búzios',
    'santana livramento': "Sant'Ana do Livramento",
    'porto galinhas': 'Ipojuca',              # distrito de Ipojuca-PE
    'costa sauipe': 'Mata de São João',       # distrito de Mata de Sao Joao-BA
    'distrito federal': 'Brasília',
    'sao joao del': 'São João del-Rei',       # grafia truncada frequente
}

# --- normalizacao da chave (ESPELHA a normalizacao do projeto) ----------------
# Se a normalizacao final mudar (ex.: passar a preservar stopwords em cidades),
# ajuste APENAS chave_cidade() abaixo.
REGEX_PONTOS = re.compile(r'[^\w\s]|_')
REGEX_ORDINAL = re.compile(r'^\d+(o|a|º|ª|st|nd|rd|th|an)?$', re.IGNORECASE)
REGEX_ROMANO = re.compile(
    r'^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$', re.IGNORECASE)


def remover_acentos(texto: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn')


def carregar_stopwords() -> frozenset:
    try:
        lista = stopwords.words('portuguese') + stopwords.words('english')
    except LookupError:
        nltk.download('stopwords', quiet=True)
        lista = stopwords.words('portuguese') + stopwords.words('english')
    palavras = {remover_acentos(p) for p in lista}
    palavras.discard('sao')          # mesmo ajuste da normalizacao do projeto
    return frozenset(palavras)


STOPWORDS = carregar_stopwords()


def chave_cidade(texto: str) -> str:
    texto = REGEX_PONTOS.sub(' ', remover_acentos(texto.lower()))
    return ' '.join(
        p for p in texto.split()
        if not (p.isdigit() or REGEX_ORDINAL.fullmatch(p)
                or REGEX_ROMANO.fullmatch(p) or p in STOPWORDS))


# --- referencias do IBGE ------------------------------------------------------
def carregar_estados() -> dict:
    """codigo_uf -> sigla."""
    with open(ARQ_ESTADOS, mode='r', newline='', encoding='utf-8-sig') as f:
        # Mudado para usar 'COD' e 'SIGLA' de acordo com o estados.csv real
        return {int(l['COD']): l['SIGLA'].strip() for l in csv.DictReader(f)}


def carregar_mapa_cidades(mapa_uf: dict) -> dict:
    """chave normalizada da cidade -> lista ordenada de UFs (mais de 1 = ambigua)."""
    por_chave = defaultdict(set)
    with open(ARQ_MUNICIPIOS, mode='r', newline='', encoding='utf-8-sig') as f:
        for linha in csv.DictReader(f):
            chave = chave_cidade(linha['NOME']) # Ajustado para 'NOME' em maiúsculo se necessário
            uf = mapa_uf.get(int(linha['COD UF'])) # Mudado de 'codigo_uf' para 'COD UF'
            if chave and uf:
                por_chave[chave].add(uf)
    return {chave: sorted(ufs) for chave, ufs in por_chave.items()}



def carregar_apelidos(mapa_cidades: dict) -> dict:
    """apelido -> chave IBGE; descarta (com aviso) apelidos que nao existem no IBGE."""
    apelidos = {}
    for apelido, municipio in APELIDOS.items():
        chave = chave_cidade(municipio)
        if chave in mapa_cidades:
            apelidos[apelido] = chave
        else:
            print(f'  [aviso] apelido ignorado ({apelido!r}): {municipio!r} nao existe no IBGE')
    return apelidos


# --- utilitarios --------------------------------------------------------------
def ano_valido(ano: str) -> bool:
    return ano.isdigit() and ANO_MIN <= int(ano) <= ANO_MAX


def indice_ocorrencias(cabecalho: list) -> int:
    for i, coluna in enumerate(cabecalho):
        if coluna.startswith('OCORRENCIAS'):
            return i
    raise ValueError(f'coluna OCORRENCIAS* nao encontrada no cabecalho: {cabecalho}')


def gravar(nome_arquivo: str, cabecalho: list, linhas) -> None:
    caminho = os.path.join(DIR_SAIDA, nome_arquivo)
    with open(caminho, mode='w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f, delimiter=DELIMITADOR_SAIDA)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)
    print(f'  salvo: {caminho}')


def main():
    print('=== dados mapa Brasil ===')
    inicio = time.time()

    for caminho in (ENTRADA, ARQ_ESTADOS, ARQ_MUNICIPIOS):
        if not os.path.exists(caminho):
            print(f'[ERRO] arquivo nao encontrado: {caminho}')
            return
    os.makedirs(DIR_SAIDA, exist_ok=True)

    print('[1] Carregando estados e municipios do IBGE...')
    mapa_uf = carregar_estados()
    mapa_cidades = carregar_mapa_cidades(mapa_uf)
    apelidos = carregar_apelidos(mapa_cidades)
    ambiguas_ibge = sum(1 for ufs in mapa_cidades.values() if len(ufs) > 1)
    print(f'  {len(mapa_uf)} estados | {len(mapa_cidades)} chaves de cidade '
          f'({ambiguas_ibge} em mais de uma UF) | {len(apelidos)} apelidos')

    ocorrencias_uf = Counter()
    ambiguas_uf = Counter()
    eventos_uf = Counter()                   # linhas (edicoes distintas) por UF
    ocorrencias_uf_ano = Counter()
    ocorrencias_cidade_uf = Counter()
    eventos_cidade_uf = Counter()
    ocorrencias_cidade_ambigua = Counter()
    nao_encontradas = Counter()              # cidade -> ocorrencias (limitado por MAX_NAO_ENCONTRADAS)
    ocorrencias_nao_listadas = 0             # nao encontradas alem do teto (so entram no total)
    status_chaves = Counter()                # status -> linhas
    status_ocorrencias = Counter()           # status -> ocorrencias

    print('\n[2] Processando eventos...')
    with open(ENTRADA, mode='r', newline='', encoding='utf-8-sig') as f:
        leitor = csv.reader(f, delimiter=DELIMITADOR_ENTRADA)
        cabecalho = next(leitor)
        i_oc = indice_ocorrencias(cabecalho)
        i_nome = cabecalho.index('NOME-DO-EVENTO')
        i_cidade = cabecalho.index('CIDADE-DO-EVENTO')
        i_ano = cabecalho.index('ANO-DO-EVENTO')
        i_pais = cabecalho.index('PAIS-DO-EVENTO') if 'PAIS-DO-EVENTO' in cabecalho else None
        n_colunas = len(cabecalho)
        if i_pais is None:
            print('  [aviso] arquivo sem PAIS-DO-EVENTO: nao ha como excluir cidades do exterior.\n'
                  '          Homonimos de municipios brasileiros (ex.: Coimbra, Braga, Porto)\n'
                  '          entram no mapa; veja a margem no README.')

        for n, linha in enumerate(leitor, start=1):
            if LIMITE_TESTE and n > LIMITE_TESTE:
                break
            if len(linha) < n_colunas:
                status_chaves['LINHA-INVALIDA'] += 1
                continue
            try:
                ocorrencias = int(linha[i_oc])
            except ValueError:
                status_chaves['LINHA-INVALIDA'] += 1
                continue

            cidade, ano = linha[i_cidade], linha[i_ano]

            # --- classifica a linha (status) ---
            ufs = ()
            if not linha[i_nome]:
                status = 'SEM-NOME'
            elif i_pais is not None and linha[i_pais] not in PAISES_BRASIL:
                status = 'EXTERIOR'
            elif not cidade:
                status = 'SEM-CIDADE'
            else:
                ufs = mapa_cidades.get(cidade)
                status = 'OK'
                if not ufs and cidade in apelidos:
                    cidade = apelidos[cidade]
                    ufs = mapa_cidades[cidade]
                    status = 'OK-APELIDO'
                if not ufs:
                    status = 'NAO-ENCONTRADO'
                    if cidade in nao_encontradas or len(nao_encontradas) < MAX_NAO_ENCONTRADAS:
                        nao_encontradas[cidade] += ocorrencias
                    else:                # arquivo vem ordenado: o que sobra e cauda de baixa frequencia
                        ocorrencias_nao_listadas += ocorrencias
                elif len(ufs) > 1:
                    status = 'AMBIGUO'
                    ocorrencias_cidade_ambigua[cidade] += ocorrencias

            status_chaves[status] += 1
            status_ocorrencias[status] += ocorrencias

            # --- agrega (so linhas mapeadas; ambigua conta em todas as UFs candidatas) ---
            if ufs:
                ambigua = len(ufs) > 1
                ano_ok = ano_valido(ano)
                for uf in ufs:
                    ocorrencias_uf[uf] += ocorrencias
                    eventos_uf[uf] += 1
                    ocorrencias_cidade_uf[(cidade, uf)] += ocorrencias
                    eventos_cidade_uf[(cidade, uf)] += 1
                    if ambigua:
                        ambiguas_uf[uf] += ocorrencias
                    if ano_ok:
                        ocorrencias_uf_ano[(uf, ano)] += ocorrencias

            if n % INTERVALO_LOG == 0:
                print(f'  {n:>10} linhas lidas...')

    print('\n[3] Gravando resultados...')
    codigo_sigla = {sigla: codigo for codigo, sigla in mapa_uf.items()}
    total_chaves = sum(status_chaves.values())
    total_ocorrencias = sum(status_ocorrencias.values())

    gravar('eventosPorUF.csv',
           ['CODIGO-IBGE', 'ESTADO', 'OCORRENCIAS', 'OCORRENCIAS-AMBIGUAS', 'EVENTOS-DISTINTOS'],
           ([codigo_sigla.get(uf, ''), uf, qtd, ambiguas_uf[uf], eventos_uf[uf]]
            for uf, qtd in ocorrencias_uf.most_common()))

    gravar('eventosPorUFAno.csv',
           ['ESTADO', 'ANO', 'OCORRENCIAS'],
           ([uf, ano, qtd] for (uf, ano), qtd in sorted(ocorrencias_uf_ano.items())))

    gravar('eventosPorCidadeUF.csv',
           ['CIDADE-DO-EVENTO', 'ESTADO', 'OCORRENCIAS', 'EVENTOS-DISTINTOS', 'AMBIGUA'],
           ([cidade, uf, qtd, eventos_cidade_uf[(cidade, uf)],
             int(cidade in ocorrencias_cidade_ambigua)]
            for (cidade, uf), qtd in ocorrencias_cidade_uf.most_common()))

    gravar('relatorioMapeamento.csv',
           ['STATUS', 'CHAVES', 'OCORRENCIAS', 'PERCENTUAL-CHAVES', 'PERCENTUAL-OCORRENCIAS'],
           ([s, status_chaves[s], status_ocorrencias[s],
             round(100 * status_chaves[s] / max(total_chaves, 1), 2),
             round(100 * status_ocorrencias[s] / max(total_ocorrencias, 1), 2)]
            for s, _ in status_ocorrencias.most_common()))

    gravar('relatorioCidadesAmbiguas.csv',
           ['CIDADE-DO-EVENTO', 'ESTADOS-ENVOLVIDOS', 'OCORRENCIAS'],
           ([cidade, '|'.join(mapa_cidades[cidade]), qtd]
            for cidade, qtd in ocorrencias_cidade_ambigua.most_common()))

    gravar('cidadesNaoEncontradas.csv',
           ['CIDADE-DO-EVENTO', 'OCORRENCIAS'],
           nao_encontradas.most_common(LIMITE_NAO_ENCONTRADAS))

    print('\n[4] Resumo e margens de erro (percentual das OCORRENCIAS):')
    print(f'  linhas: {total_chaves} | ocorrencias: {total_ocorrencias}')
    for s, qtd in status_ocorrencias.most_common():
        print(f'  {s:<16} {qtd:>12}  ({100 * qtd / max(total_ocorrencias, 1):.2f}%)')
    if status_chaves['LINHA-INVALIDA']:
        print(f'  LINHA-INVALIDA   {status_chaves["LINHA-INVALIDA"]:>12} linhas (sem contagem valida)')
    if ocorrencias_nao_listadas:
        print(f'  [aviso] {ocorrencias_nao_listadas} ocorrencias NAO-ENCONTRADO fora do teto de '
              f'{MAX_NAO_ENCONTRADAS} cidades (contadas no relatorio, ausentes de cidadesNaoEncontradas.csv)')
    if ocorrencias_cidade_ambigua:
        print(f'\n  cidades ambiguas: {len(ocorrencias_cidade_ambigua)} '
              f'({sum(ocorrencias_cidade_ambigua.values())} ocorrencias) -> '
              f'contadas em todas as UFs candidatas (relatorioCidadesAmbiguas.csv)')

    print(f'\nConcluido em {time.time() - inicio:.2f}s')
    print(f'Resultados em: {DIR_SAIDA}')


if __name__ == '__main__':
    main()