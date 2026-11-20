##f
# tabelas.py
# Le os 4 CSVs JA QUANTIFICADOS (um por vez, em streaming) e gera as tabelas.
# Uma unica execucao processa os 4 arquivos; memoria constante: por arquivo guarda
# so o top 10, a tabela "ocorrencias -> quantas chaves" e contadores por ano.
#
# Entradas (delimitador | ; a contagem e a coluna que comeca com 'OCORRENCIAS'):
#   N    NOME-DO-EVENTO | OCORRENCIAS-EVENTO
#   NA   NOME-DO-EVENTO | ANO-DO-EVENTO | OCORRENCIAS-EVENTO-ANO
#   NPA  NOME-DO-EVENTO | PAIS-DO-EVENTO | ANO-DO-EVENTO | OCORRENCIAS-EVENTO-PAIS-ANO
#   NCA  NOME-DO-EVENTO | CIDADE-DO-EVENTO | ANO-DO-EVENTO | OCORRENCIAS-EVENTO-CIDADE-ANO
#
# Saidas (em DIR_SAIDA, delimitador ;):
#   top10_{N,NA,NPA,NCA}.csv  OCORRENCIAS;{colunas da chave}
#   eventosPorAno.csv         CONJUNTO;ANO;DISTINTOS;OCORRENCIAS
#   eventosPorFaixas.csv      CONJUNTO;INICIO;FIM;FAIXA;QTD-EVENTOS;OCORRENCIAS
#   resumo.csv                CONJUNTO;...estatisticas...
#
# Definicoes:
#   - "chave" = uma linha do arquivo (o evento distinto naquele conjunto).
#   - DISTINTOS (por ano) = numero de chaves do conjunto naquele ano.
#     Existe so para NA, NPA e NCA (o N nao tem ano).
#   - Linhas sem NOME-DO-EVENTO sao excluidas e reportadas; linhas invalidas
#     (colunas faltando / contagem nao numerica) tambem. Nada some em silencio.

import csv
import heapq
import os
import time
from bisect import bisect_right
from collections import Counter

# --- caminhos (preencher) ----------------------------------------------------
ARQUIVOS = {
    'N':   r'D:\BACKUP\Magela\conjuntoN_ordenado.csv',    # conjuntoN_ordenado.csv
    'NA':  r'D:\BACKUP\Magela\conjuntoNA_ordenado.csv',    # conjuntoNA_ordenado.csv
    'NPA': r'D:\BACKUP\Magela\conjuntoNPA_ordenado.csv',    # conjuntoNPA_ordenado.csv
    'NCA': r'D:\BACKUP\Magela\conjuntoNCA_ordenado.csv',    # conjuntoNCA_ordenado.csv
}
DIR_SAIDA = r'D:\BACKUP\Magela\resultados'    # pasta de saida (criada se nao existir)

# --- parametros --------------------------------------------------------------
DELIMITADOR_ENTRADA = '|'
DELIMITADOR_SAIDA = ';'
INTERVALO_LOG = 1000000
LIMITE_TESTE = None         # ex.: 500_000 para validar com parte do arquivo
ANO_MIN, ANO_MAX = 1900, 2030
TAMANHO_TOP = 10

# inicio de cada faixa de ocorrencias (o fim e o inicio da proxima - 1)
LIMITES_FAIXAS = [0, 12, 21, 51, 101, 201, 501, 1001, 5001, 10001, 100001]


def ano_valido(ano: str) -> bool:
    return ano.isdigit() and ANO_MIN <= int(ano) <= ANO_MAX


def indice_ocorrencias(cabecalho: list) -> int:
    """Posicao da coluna de contagem (nome varia por arquivo, ex.: OCORRENCIAS-EVENTO-ANO)."""
    for i, coluna in enumerate(cabecalho):
        if coluna.startswith('OCORRENCIAS'):
            return i
    raise ValueError(f'coluna OCORRENCIAS* nao encontrada no cabecalho: {cabecalho}')


def faixa(qtd: int) -> tuple:
    """(inicio, fim, rotulo) da faixa que contem `qtd`."""
    i = max(bisect_right(LIMITES_FAIXAS, qtd) - 1, 0)
    inicio = LIMITES_FAIXAS[i]
    fim = LIMITES_FAIXAS[i + 1] - 1 if i + 1 < len(LIMITES_FAIXAS) else None
    if fim is None:
        rotulo = f'{inicio}+'
    elif fim == inicio:
        rotulo = str(inicio)
    else:
        rotulo = f'{inicio}-{fim}'
    return inicio, fim, rotulo

def valor_na_posicao(freq: Counter, posicao: int) -> int:
    """Valor na `posicao` (base 0) da lista ordenada, sem montar a lista."""
    acumulado = 0
    for valor in sorted(freq):
        acumulado += freq[valor]
        if posicao < acumulado:
            return int(valor)
    raise IndexError(f'posicao {posicao} fora do intervalo (total de chaves: {acumulado})')


def mediana(freq: Counter, n: int):
    if n % 2:
        return valor_na_posicao(freq, n // 2)
    return (valor_na_posicao(freq, n // 2 - 1) + valor_na_posicao(freq, n // 2)) / 2


def gravar(nome_arquivo: str, cabecalho: list, linhas: list) -> None:
    caminho = os.path.join(DIR_SAIDA, nome_arquivo)
    with open(caminho, mode='w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f, delimiter=DELIMITADOR_SAIDA)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)
    print(f'  salvo: {caminho} ({len(linhas)} linhas)')


def ler_conjunto(sigla: str, caminho: str) -> dict:
    """Uma passada no arquivo; devolve so agregados pequenos."""
    freq = Counter()             # ocorrencias -> quantidade de chaves
    heap = []                    # top N: (ocorrencias, -n_linha, linha); correto mesmo fora de ordem
    chaves_por_ano = Counter()
    ocorrencias_por_ano = Counter()
    ocorrencias_ano_invalido = 0
    invalidas = sem_nome = ocorrencias_sem_nome = 0

    with open(caminho, mode='r', newline='', encoding='utf-8-sig') as f:
        leitor = csv.reader(f, delimiter=DELIMITADOR_ENTRADA)
        cabecalho = next(leitor)
        i_oc = indice_ocorrencias(cabecalho)
        i_nome = cabecalho.index('NOME-DO-EVENTO')
        i_ano = cabecalho.index('ANO-DO-EVENTO') if 'ANO-DO-EVENTO' in cabecalho else None
        n_colunas = len(cabecalho)

        for n, linha in enumerate(leitor, start=1):
            if LIMITE_TESTE and n > LIMITE_TESTE:
                break
            if len(linha) < n_colunas:
                invalidas += 1
                continue
            try:
                ocorrencias = int(linha[i_oc])
            except ValueError:
                invalidas += 1
                continue

            if not linha[i_nome]:
                sem_nome += 1
                ocorrencias_sem_nome += ocorrencias
                continue

            freq[ocorrencias] += 1

            if len(heap) < TAMANHO_TOP:
                heapq.heappush(heap, (ocorrencias, -n, linha))
            elif ocorrencias > heap[0][0]:       # com o arquivo ordenado, quase nunca entra aqui
                heapq.heapreplace(heap, (ocorrencias, -n, linha))

            if i_ano is not None:
                ano = linha[i_ano]
                if ano_valido(ano):
                    chaves_por_ano[ano] += 1
                    ocorrencias_por_ano[ano] += ocorrencias
                else:
                    ocorrencias_ano_invalido += ocorrencias

            if n % INTERVALO_LOG == 0:
                print(f'  {sigla}: {n:>10} linhas lidas...')

    top10 = [(oc, [v for j, v in enumerate(linha) if j != i_oc])
             for oc, _, linha in sorted(heap, reverse=True)]
    print(f'  lido {sigla}: {sum(freq.values())} chaves | sem nome: {sem_nome} '
          f'({ocorrencias_sem_nome} ocorrencias) | invalidas: {invalidas}')
    return {
        'colunas_chave': [c for j, c in enumerate(cabecalho) if j != i_oc],
        'freq': freq,
        'top10': top10,
        'tem_ano': i_ano is not None,
        'chaves_por_ano': chaves_por_ano,
        'ocorrencias_por_ano': ocorrencias_por_ano,
        'ocorrencias_ano_invalido': ocorrencias_ano_invalido,
        'invalidas': invalidas,
        'ocorrencias_sem_nome': ocorrencias_sem_nome,
    }


def gerar_top10(dados: dict) -> None:
    for sigla, d in dados.items():
        print(f'\n  == {sigla} (top {TAMANHO_TOP}) ==')
        for posicao, (oc, chave) in enumerate(d['top10'], start=1):
            print(f'  {posicao:>2}. {oc:>8}  {" | ".join(chave)}')
        gravar(f'top10_{sigla}.csv', ['OCORRENCIAS'] + d['colunas_chave'],
               [[oc] + chave for oc, chave in d['top10']])


def gerar_por_ano(dados: dict) -> None:
    linhas = []
    for sigla, d in dados.items():
        if not d['tem_ano']:
            continue
        for ano in sorted(d['chaves_por_ano']):
            linhas.append([sigla, ano, d['chaves_por_ano'][ano], d['ocorrencias_por_ano'][ano]])
        if d['ocorrencias_ano_invalido']:
            print(f'  [aviso] {sigla}: {d["ocorrencias_ano_invalido"]} ocorrencias com ano '
                  f'vazio/fora de {ANO_MIN}-{ANO_MAX} (fora da serie)')
    gravar('eventosPorAno.csv', ['CONJUNTO', 'ANO', 'DISTINTOS', 'OCORRENCIAS'], linhas)


def gerar_por_faixas(dados: dict) -> None:
    linhas = []
    for sigla, d in dados.items():
        por_faixa = {}
        for ocorrencias, qtd_chaves in d['freq'].items():
            acumulado = por_faixa.setdefault(faixa(ocorrencias), [0, 0])
            acumulado[0] += qtd_chaves                  # chaves na faixa
            acumulado[1] += ocorrencias * qtd_chaves    # ocorrencias na faixa
        for (inicio, fim, rotulo), (qtd, total) in sorted(por_faixa.items()):
            linhas.append([sigla, inicio, fim if fim else '', rotulo, qtd, total])
    gravar('eventosPorFaixas.csv',
           ['CONJUNTO', 'INICIO', 'FIM', 'FAIXA', 'QTD-EVENTOS', 'OCORRENCIAS'], linhas)


def gerar_resumo(dados: dict) -> None:
    linhas = []
    for sigla, d in dados.items():
        freq = d['freq']
        if not freq:
            continue
        n_chaves = sum(freq.values())
        total = sum(valor * qtd for valor, qtd in freq.items())
        top10_total = sum(oc for oc, _ in d['top10'])
        impares = sum(qtd for valor, qtd in freq.items() if valor % 2)
        genericos = freq.get(1, 0)
        linhas.append([
            sigla, total, n_chaves,
            round(total / n_chaves, 2), mediana(freq, n_chaves), max(freq),
            freq.get(1, 0), top10_total, round(100 * top10_total / total, 2),
            impares, d['ocorrencias_sem_nome'], d['invalidas'],
            genericos, genericos,
        ])
        print(f'  {sigla}: {n_chaves} chaves | {total} ocorrencias | '
              f'{impares} chaves com ocorrencia impar')
    gravar('resumo.csv',
           ['CONJUNTO', 'OCORRENCIAS-TOTAIS', 'CHAVES-DISTINTAS',
            'MEDIA-OCORRENCIAS', 'MEDIANA-OCORRENCIAS', 'MAXIMA-OCORRENCIA',
            'EVENTOS-UNICOS', 'OCORRENCIAS-TOP10', 'COBERTURA-TOP10-PERCENT',
            'CHAVES-COM-OCORRENCIA-IMPAR', 'OCORRENCIAS-SEM-NOME', 'LINHAS-INVALIDAS',
            'EVENTOS-GENERICOS', 'OCORRENCIAS-GENERICAS'],
           linhas)


def main():
    print('=== tabelas de resultados ===')
    inicio = time.time()

    for sigla, caminho in ARQUIVOS.items():
        if not os.path.exists(caminho):
            print(f'[ERRO] arquivo nao encontrado ({sigla}): {caminho}')
            return
    os.makedirs(DIR_SAIDA, exist_ok=True)

    print('[0] Lendo os conjuntos (um arquivo por vez)...')
    dados = {sigla: ler_conjunto(sigla, caminho) for sigla, caminho in ARQUIVOS.items()}

    print('\n[1] Top 10 por conjunto...')
    gerar_top10(dados)
    print('\n[2] Eventos por ano...')
    gerar_por_ano(dados)
    print('\n[3] Eventos por faixa de ocorrencias...')
    gerar_por_faixas(dados)
    print('\n[4] Resumo por conjunto...')
    gerar_resumo(dados)

    print(f'\nConcluido em {time.time() - inicio:.2f}s')
    print(f'Resultados em: {DIR_SAIDA}')


if __name__ == '__main__':
    main()