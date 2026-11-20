# -*- coding: utf-8 -*-
##f
# Baixa/le municipios.csv + estados.csv do repo kelvins/municipios-brasileiros
# e gera um dicionario CIDADE_NORMALIZADA -> UF (ou AMBIGUO:UF1|UF2),
# salvo em JSON.
#
# URLs das bases IBGE:
# https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv
# https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/estados.csv

import csv
import io
import json
import os
import unicodedata
import urllib.request

# --- caminhos ---
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
ARQ_MUNICIPIOS = os.path.join(DIR_BASE, 'municipios.csv')
ARQ_ESTADOS = os.path.join(DIR_BASE, 'estados.csv')
ARQ_SAIDA = os.path.join(DIR_BASE, 'mapaCidadeUF.json')

URL_MUNICIPIOS = 'https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv'
URL_ESTADOS = 'https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/estados.csv'

# conectores que o normalizacaoGeral.py pode remover incorretamente
CONECTORES = {'de', 'do', 'da', 'dos', 'das', 'e'}


def baixar_se_nao_existe(caminho: str, url: str) -> None:
    if os.path.exists(caminho):
        print(f'  [ok] {os.path.basename(caminho)} ja existe localmente')
        return
    print(f'  [download] baixando {os.path.basename(caminho)}...')
    dados = urllib.request.urlopen(url).read().decode('utf-8')
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(dados)
    print(f'  [ok] salvo em {caminho}')


def normalizar(nome: str) -> str:
    """Maiusculas, sem acento, espacos extras."""
    nome = nome.strip().upper()
    nfd = unicodedata.normalize('NFD', nome)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')


def sem_conectores(nome: str) -> str:
    """Remove conectores (de, do, da, dos, das, e) para heuristica."""
    return ' '.join(p for p in nome.split() if p.lower() not in CONECTORES)


def carregar_estados(caminho: str) -> dict[int, str]:
    """codigo_uf -> sigla UF."""
    mapa = {}
    with open(caminho, 'r', encoding='utf-8-sig') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            codigo = int(linha['codigo_uf'])
            uf = linha['uf'].strip()
            mapa[codigo] = uf
    print(f'  estados carregados: {len(mapa)} UFs')
    return mapa


def carregar_municipios(caminho: str, mapa_uf: dict[int, str]) -> dict[str, str]:
    """CIDADE_NORMALIZADA -> UF (ou AMBIGUO:UF1|UF2)."""
    # etapa 1: agrupar por nome normalizado
    por_nome: dict[str, list[str]] = {}
    with open(caminho, 'r', encoding='utf-8-sig') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            nome = linha['nome'].strip()
            codigo_uf = int(linha['codigo_uf'])
            uf = mapa_uf.get(codigo_uf, '')
            if not uf:
                continue
            chave = normalizar(nome)
            por_nome.setdefault(chave, []).append(uf)

    # etapa 2: resolver unico vs ambiguo
    mapa_cidade: dict[str, str] = {}
    for chave, ufs in por_nome.items():
        ufs_distintas = sorted(set(ufs))
        if len(ufs_distintas) == 1:
            mapa_cidade[chave] = ufs_distintas[0]
        else:
            mapa_cidade[chave] = 'AMBIGUO:' + '|'.join(ufs_distintas)

    print(f'  cidades mapeadas: {len(mapa_cidade)} nomes distintos')
    ambigos = sum(1 for v in mapa_cidade.values() if v.startswith('AMBIGUO'))
    print(f'  ambiguidades: {ambigos} ({100*ambigos/len(mapa_cidade):.1f}%)')
    return mapa_cidade


def main():
    print('=== mapaCidadeUF ===')

    print('\n[1] Verificando/baixando bases IBGE...')
    baixar_se_nao_existe(ARQ_MUNICIPIOS, URL_MUNICIPIOS)
    baixar_se_nao_existe(ARQ_ESTADOS, URL_ESTADOS)

    print('\n[2] Carregando estados...')
    mapa_uf = carregar_estados(ARQ_ESTADOS)

    print('\n[3] Carregando municipios...')
    mapa_cidade = carregar_municipios(ARQ_MUNICIPIOS, mapa_uf)

    # adicionar heuristica: versao sem conectores -> mapeamento reverso
    heuristica: dict[str, str] = {}
    for chave, uf in mapa_cidade.items():
        h = sem_conectores(chave)
        if h != chave and h not in mapa_cidade:
            heuristica[h] = uf

    mapa_completo = {**mapa_cidade, **heuristica}

    print(f'\n[4] Salvando mapa em {ARQ_SAIDA}...')
    with open(ARQ_SAIDA, 'w', encoding='utf-8') as f:
        json.dump(mapa_completo, f, ensure_ascii=False, indent=2)

    print(f'  total de chaves no mapa: {len(mapa_completo)}')
    print('  (inclui chaves heuristicas sem conectores para casamento)')
    print('\nConcluido.')


if __name__ == '__main__':
    main()
