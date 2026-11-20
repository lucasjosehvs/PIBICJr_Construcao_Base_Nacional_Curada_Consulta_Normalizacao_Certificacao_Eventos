##f
# quantificar.py
# Conta as ocorrencias de cada chave dos 4 conjuntos, lendo o CSV JA NORMALIZADO
# em UMA unica passada (streaming: o arquivo nunca e carregado inteiro na RAM).
#
# Entrada (delimitador ;) - as colunas abaixo, em qualquer ordem:
#   NOME-DO-EVENTO ; ANO-DO-EVENTO ; PAIS-DO-EVENTO ; CIDADE-DO-EVENTO
#
# Saidas (em DIR_SAIDA, ordenadas por OCORRENCIAS decrescente):
#   Conjunto1_quantificado.csv   OCORRENCIAS;NOME-DO-EVENTO
#   Conjunto2_quantificado.csv   OCORRENCIAS;NOME-DO-EVENTO;ANO-DO-EVENTO
#   Conjunto3_quantificado.csv   OCORRENCIAS;NOME-DO-EVENTO;ANO-DO-EVENTO;PAIS-DO-EVENTO
#   Conjunto4_quantificado.csv   OCORRENCIAS;NOME-DO-EVENTO;ANO-DO-EVENTO;CIDADE-DO-EVENTO
#
# Linhas sem NOME-DO-EVENTO ou com colunas faltando sao contadas e reportadas
# (nada e descartado em silencio).

import csv
import os
import time
from collections import Counter

# --- caminhos (preencher) ----------------------------------------------------
ENTRADA = r'E:\Magela\conjuntoN_ordenado.csv'      # CSV normalizado
DIR_SAIDA = r'E:\Magela\saidas'    # pasta de saida (criada se nao existir)

# --- parametros --------------------------------------------------------------
DELIMITADOR = ';'
SEPARADOR = '|'            # une os campos da chave; texto normalizado nao tem '|'
INTERVALO_LOG = 1_000_000
LIMITE_TESTE = None        # ex.: 500_000 para validar com parte do arquivo

COLUNAS = ['NOME-DO-EVENTO', 'ANO-DO-EVENTO', 'PAIS-DO-EVENTO', 'CIDADE-DO-EVENTO']

# Cabecalhos de saida. A montagem das chaves esta no loop de main()
# (mantenha os dois em sincronia se mudar a definicao de algum conjunto).
CONJUNTOS = {
    'Conjunto1': ['NOME-DO-EVENTO'],
    'Conjunto2': ['NOME-DO-EVENTO', 'ANO-DO-EVENTO'],
    'Conjunto3': ['NOME-DO-EVENTO', 'ANO-DO-EVENTO', 'PAIS-DO-EVENTO'],
    'Conjunto4': ['NOME-DO-EVENTO', 'ANO-DO-EVENTO', 'CIDADE-DO-EVENTO'],
}

def gravar_conjunto(nome_conjunto: str, contador: Counter) -> None:
    caminho = os.path.join(DIR_SAIDA, f'{nome_conjunto}_quantificado.csv')
    with open(caminho, mode='w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f, delimiter=DELIMITADOR)
        escritor.writerow(['OCORRENCIAS'] + CONJUNTOS[nome_conjunto])
        for chave, qtd in contador.most_common():
            escritor.writerow([qtd, *chave.split(SEPARADOR)])

    print(f'  {nome_conjunto}: {len(contador):>10} chaves distintas | '
          f'{sum(contador.values()):>10} ocorrencias')

def main():
    print('=== quantificar conjuntos ===')
    inicio = time.time()

    if not os.path.exists(ENTRADA):
        print(f'[ERRO] arquivo de entrada nao encontrado: {ENTRADA}')
        return
    os.makedirs(DIR_SAIDA, exist_ok=True)

    c1, c2, c3, c4 = Counter(), Counter(), Counter(), Counter()
    total = sem_nome = invalidas = 0

    print('[1] Contando chaves...')
    with open(ENTRADA, mode='r', newline='', encoding='utf-8') as f:
        leitor = csv.reader(f, delimiter=DELIMITADOR)
        cabecalho = next(leitor)
        i_nome, i_ano, i_pais, i_cidade = (cabecalho.index(c) for c in COLUNAS)
        ultimo_indice = max(i_nome, i_ano, i_pais, i_cidade)

        for linha in leitor:
            if LIMITE_TESTE and total >= LIMITE_TESTE:
                break
            total += 1

            if len(linha) <= ultimo_indice:
                invalidas += 1
                continue

            nome = linha[i_nome]
            if not nome:
                sem_nome += 1
                continue

            ano = linha[i_ano]
            c1[nome] += 1
            c2[f'{nome}{SEPARADOR}{ano}'] += 1
            c3[f'{nome}{SEPARADOR}{ano}{SEPARADOR}{linha[i_pais]}'] += 1
            c4[f'{nome}{SEPARADOR}{ano}{SEPARADOR}{linha[i_cidade]}'] += 1

            if total % INTERVALO_LOG == 0:
                print(f'  {total:>10} linhas processadas...')

    validas = total - sem_nome - invalidas
    print(f'  linhas lidas:            {total}')
    print(f'  linhas validas:          {validas}')
    print(f'  sem nome (descartadas):  {sem_nome}')
    print(f'  colunas faltando:        {invalidas}')

    print('\n[2] Gravando conjuntos (libera cada contador apos gravar)...')
    contadores = {'Conjunto1': c1, 'Conjunto2': c2, 'Conjunto3': c3, 'Conjunto4': c4}
    del c1, c2, c3, c4      # so o dict referencia os contadores -> pop() libera a RAM
    for nome_conjunto in list(contadores):
        gravar_conjunto(nome_conjunto, contadores.pop(nome_conjunto))

    print(f'\nConcluido em {time.time() - inicio:.2f}s')
    print(f'Resultados em: {DIR_SAIDA}')

if __name__ == '__main__':
    main()