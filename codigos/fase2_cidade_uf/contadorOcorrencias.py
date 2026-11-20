# -*- coding: utf-8 -*-
##f
# Fase 2: conta ocorrencias por NOME-DO-EVENTO, por NOME+CIDADE e por
# NOME+UF, gerando 3 CSVs ordenados por ocorrencia decrescente.
#
# Entradas:
#   - arquivoEntrada (Conjunto4) para contagem por nome e por nome+cidade
#   - arquivoNomeEstado (saida da fase 1) para contagem por nome+UF
#
# Saidas (todas com ; como delimitador):
#   - contagemPorNome.csv       OCORRENCIAS;NOME-DO-EVENTO
#   - contagemPorNomeCidade.csv OCORRENCIAS;NOME-DO-EVENTO;CIDADE-DO-EVENTO
#   - contagemPorNomeUF.csv     OCORRENCIAS;NOME-DO-EVENTO;ESTADO

import csv
import os
import time
from collections import defaultdict

# --- caminhos ---
DIR_BASE = os.path.dirname(os.path.abspath(__file__))

arquivoEntrada    = os.path.join(DIR_BASE, 'exemploConjunto4.csv')
arquivoNomeEstado = os.path.join(DIR_BASE, 'nomeEstado.csv')

saidaPorNome       = os.path.join(DIR_BASE, 'contagemPorNome.csv')
saidaPorNomeCidade = os.path.join(DIR_BASE, 'contagemPorNomeCidade.csv')
saidaPorNomeUF     = os.path.join(DIR_BASE, 'contagemPorNomeUF.csv')

DELIMITADOR_ENTRADA = '|'
DELIMITADOR_SAIDA   = ';'

INTERVALO_PRINT = 50


def contar_por_nome(caminho: str) -> dict[str, int]:
    contagem: dict[str, int] = defaultdict(int)
    total = 0
    with open(caminho, 'r', encoding='utf-8') as f:
        leitor = csv.reader(f, delimiter=DELIMITADOR_ENTRADA)
        next(leitor)  # pular cabecalho
        for linha in leitor:
            if len(linha) < 4:
                continue
            nome = linha[0].strip()
            contagem[nome] += 1
            total += 1
            if total % INTERVALO_PRINT == 0 and total % 10000 == 0:
                print(f'  [nome] {total:>8} linhas...')
    print(f'  [nome] total: {total} linhas, {len(contagem)} chaves distintas')
    return dict(contagem)


def contar_por_nome_cidade(caminho: str) -> dict[tuple[str, str], int]:
    contagem: dict[tuple[str, str], int] = defaultdict(int)
    total = 0
    with open(caminho, 'r', encoding='utf-8') as f:
        leitor = csv.reader(f, delimiter=DELIMITADOR_ENTRADA)
        next(leitor)
        for linha in leitor:
            if len(linha) < 4:
                continue
            nome   = linha[0].strip()
            cidade = linha[3].strip()
            contagem[(nome, cidade)] += 1
            total += 1
            if total % INTERVALO_PRINT == 0 and total % 10000 == 0:
                print(f'  [nome+cidade] {total:>8} linhas...')
    print(f'  [nome+cidade] total: {total} linhas, {len(contagem)} chaves distintas')
    return dict(contagem)


def contar_por_nome_uf(caminho: str) -> dict[tuple[str, str], int]:
    contagem: dict[tuple[str, str], int] = defaultdict(int)
    total = 0
    with open(caminho, 'r', encoding='utf-8') as f:
        leitor = csv.reader(f, delimiter=DELIMITADOR_SAIDA)
        next(leitor)
        for linha in leitor:
            if len(linha) < 3:
                continue
            nome = linha[0].strip()
            uf   = linha[1].strip()
            if not uf:
                continue  # pular sem UF mapeada
            contagem[(nome, uf)] += 1
            total += 1
            if total % INTERVALO_PRINT == 0 and total % 10000 == 0:
                print(f'  [nome+uf] {total:>8} linhas...')
    print(f'  [nome+uf] total: {total} linhas, {len(contagem)} chaves distintas')
    return dict(contagem)


def salvar_por_nome(contagem: dict[str, int], caminho: str) -> None:
    ordenado = sorted(contagem.items(), key=lambda x: -x[1])
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f, delimiter=DELIMITADOR_SAIDA)
        escritor.writerow(['OCORRENCIAS', 'NOME-DO-EVENTO'])
        for chave, qtd in ordenado:
            escritor.writerow([qtd, chave])
    print(f'  salvo: {caminho} ({len(ordenado)} linhas)')


def salvar_por_chave(contagem: dict[tuple[str, str], int],
                     caminho: str, colunas: list[str]) -> None:
    ordenado = sorted(contagem.items(), key=lambda x: -x[1])
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f, delimiter=DELIMITADOR_SAIDA)
        escritor.writerow(['OCORRENCIAS'] + colunas)
        for chave, qtd in ordenado:
            escritor.writerow([qtd] + list(chave))
    print(f'  salvo: {caminho} ({len(ordenado)} linhas)')


def main():
    print('=== contadorOcorrencias ===')
    inicio = time.time()

    # --- contagem por nome ---
    print('\n[1] Contando por NOME-DO-EVENTO...')
    c_nome = contar_por_nome(arquivoEntrada)
    print('  [1b] Salvando...')
    salvar_por_nome(c_nome, saidaPorNome)

    # --- contagem por nome + cidade ---
    print('\n[2] Contando por NOME + CIDADE...')
    c_nome_cidade = contar_por_nome_cidade(arquivoEntrada)
    print('  [2b] Salvando...')
    salvar_por_chave(c_nome_cidade, saidaPorNomeCidade,
                     ['NOME-DO-EVENTO', 'CIDADE-DO-EVENTO'])

    # --- contagem por nome + UF ---
    print('\n[3] Contando por NOME + UF...')
    if not os.path.exists(arquivoNomeEstado):
        print(f'  [ERRO] arquivo nao encontrado: {arquivoNomeEstado}')
        print('  Execute geradorNomeEstado.py primeiro (fase 1).')
        return
    c_nome_uf = contar_por_nome_uf(arquivoNomeEstado)
    print('  [3b] Salvando...')
    salvar_por_chave(c_nome_uf, saidaPorNomeUF,
                     ['NOME-DO-EVENTO', 'ESTADO'])

    tempo_total = time.time() - inicio
    print(f'\nConcluido em {tempo_total:.2f}s')


if __name__ == '__main__':
    main()
