# -*- coding: utf-8 -*-
##f
# Fase 1: le o dataset principal (Conjunto4), aplica o mapaCidadeUF e
# gera um arquivo so com NOME-DO-EVENTO;ESTADO + STATUS-MAPEAMENTO.
#
# Status possiveis:
#   OK              -> casamento exato (normalizado)
#   OK-HEURISTICO   -> casamento apos remover conectores
#   AMBIGUO         -> nome de cidade existe em mais de uma UF
#   NAO-ENCONTRADO  -> cidade nao encontrada no mapa
#   EXTERIOR        -> pais nao e Brasil
#   SEM-CIDADE      -> campo cidade vazio

import csv
import json
import os
import time
import unicodedata

# --- caminhos ---
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
ARQ_MAPA = os.path.join(DIR_BASE, 'mapaCidadeUF.json')

arquivoEntrada = os.path.join(DIR_BASE, 'exemploConjunto4.csv')
arquivoSaida   = os.path.join(DIR_BASE, 'nomeEstado.csv')

DELIMITADOR_ENTRADA = '|'
DELIMITADOR_SAIDA   = ';'

INTERVALO_PRINT = 50
INTERVALO_FLUSH = 200

COLUNAS_SAIDA = ['NOME-DO-EVENTO', 'ESTADO', 'STATUS-MAPEAMENTO']

# pais considerado brasil
PAISES_BRASIL = {'', 'brasil', 'brazil'}

# conectores para heuristica (mesmos do mapaCidadeUF)
CONECTORES = {'de', 'do', 'da', 'dos', 'das', 'e'}


def normalizar(nome: str) -> str:
    nome = nome.strip().upper()
    nfd = unicodedata.normalize('NFD', nome)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')


def sem_conectores(nome: str) -> str:
    return ' '.join(p for p in nome.split() if p.lower() not in CONECTORES)


def carregar_mapa(caminho: str) -> dict[str, str]:
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)


def mapear_uf(cidade: str, pais: str, mapa: dict[str, str]) -> tuple[str, str]:
    """Retorna (UF, STATUS)."""
    # filtrar por pais
    if pais.strip().lower() not in PAISES_BRASIL:
        return ('', 'EXTERIOR')

    cidade = cidade.strip()
    if not cidade:
        return ('', 'SEM-CIDADE')

    chave = normalizar(cidade)

    # tentativa 1: casamento exato
    if chave in mapa:
        uf = mapa[chave]
        if uf.startswith('AMBIGUO'):
            return ('', uf)  # retorna AMBIGUO:UF1|UF2
        return (uf, 'OK')

    # tentativa 2: heuristica (sem conectores)
    chave_h = sem_conectores(chave)
    if chave_h in mapa:
        uf = mapa[chave_h]
        if uf.startswith('AMBIGUO'):
            return ('', uf)
        return (uf, 'OK-HEURISTICO')

    return ('', 'NAO-ENCONTRADO')


def main():
    print('=== geradorNomeEstado ===')
    inicio = time.time()

    print(f'[1] Carregando mapa de {ARQ_MAPA}...')
    mapa = carregar_mapa(ARQ_MAPA)
    print(f'  chaves no mapa: {len(mapa)}')

    print(f'\n[2] Processando {arquivoEntrada}...')
    os.makedirs(os.path.dirname(arquivoSaida), exist_ok=True)

    contagemTotal = 0
    contagemStatus = {}

    with open(arquivoEntrada, 'r', encoding='utf-8') as f_in, \
         open(arquivoSaida, 'w', newline='', encoding='utf-8') as f_out:

        leitor   = csv.reader(f_in, delimiter=DELIMITADOR_ENTRADA)
        escritor = csv.writer(f_out, delimiter=DELIMITADOR_SAIDA)

        cabecalho = next(leitor)
        escritor.writerow(COLUNAS_SAIDA)

        for linha in leitor:
            if len(linha) < 4:
                continue

            nome_evento = linha[0].strip()
            pais        = linha[2].strip()
            cidade      = linha[3].strip()

            uf, status = mapear_uf(cidade, pais, mapa)

            # simplificar AMBIGUO:UF1|UF2 para exibicao
            uf_saida = uf
            status_saida = status
            if status.startswith('AMBIGUO'):
                uf_saida = 'DESCONHECIDA'
                status_saida = 'AMBIGUO'

            escritor.writerow([nome_evento, uf_saida, status_saida])

            contagemTotal += 1
            contagemStatus[status_saida] = contagemStatus.get(status_saida, 0) + 1

            if contagemTotal % INTERVALO_PRINT == 0:
                print(f'  {contagemTotal:>8} linhas processadas...')

            if contagemTotal % INTERVALO_FLUSH == 0:
                f_out.flush()

    tempo_total = time.time() - inicio
    print(f'\n[3] Resultado:')
    print(f'  total lido:       {contagemTotal}')
    for status, qtd in sorted(contagemStatus.items(), key=lambda x: -x[1]):
        pct = 100 * qtd / contagemTotal if contagemTotal else 0
        print(f'  {status:<20} {qtd:>8}  ({pct:.2f}%)')
    print(f'\n  saida: {arquivoSaida}')
    print(f'  tempo: {tempo_total:.2f}s')


if __name__ == '__main__':
    main()
