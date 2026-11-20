##f
# graficosGenericos.py
# Gera os graficos dos top10 de eventos genericos e nao genericos.
# Entrada: top10_{N,NA,NPA,NCA}_{genericas,nao_genericas}.csv em PASTA.
# Saida: graficos/02{a,b,c,d}_top10_{conjunto}_{genericas,nao_genericas}.png
# Mantem titulo, cor e fonte do gerarVisualizacao.py.

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import gerarVisualizacao as gv

PASTA = r'E:\Magela\mapasResultados\saidas'
SAIDA = Path(PASTA) / 'graficos'

TITULOS = {
    'N': ('10 eventos genéricos mais registrados (nome do evento)',
          '10 eventos não genéricos mais registrados (nome do evento)'),
    'NA': ('10 edições de eventos genéricos mais registradas (nome + ano)',
           '10 edições de eventos não genéricos mais registradas (nome + ano)'),
    'NPA': ('10 edições genéricas mais registradas, com país (nome + país + ano)',
            '10 edições não genéricas mais registradas, com país (nome + país + ano)'),
    'NCA': ('10 edições genéricas mais registradas, com cidade (nome + cidade + ano)',
            '10 edições não genéricas mais registradas, com cidade (nome + cidade + ano)'),
}
ARQUIVOS = {'N': '02a', 'NA': '02b', 'NCA': '02c', 'NPA': '02d'}
SUBTITULO = 'Cada cor é um evento; edições do mesmo evento repetem a cor'


def rotulos(df, conjunto):
    nome = df['NOME-DO-EVENTO'].str.capitalize()
    if conjunto == 'N':
        return nome
    if conjunto == 'NA':
        return nome + ' (' + df['ANO-DO-EVENTO'].astype(str) + ')'
    if conjunto == 'NPA':
        return (nome + ' – ' + df['PAIS-DO-EVENTO'].str.title() +
                ' (' + df['ANO-DO-EVENTO'].astype(str) + ')')
    return (nome + ' – ' + df['CIDADE-DO-EVENTO'].str.title() +
            ' (' + df['ANO-DO-EVENTO'].astype(str) + ')')


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    print('=== graficos top10 genericas / nao genericas ===')
    for conjunto, (titulo_gen, titulo_nao) in TITULOS.items():
        for rotulo, titulo in [('genericas', titulo_gen), ('nao_genericas', titulo_nao)]:
            arquivo = f'top10_{conjunto}_{rotulo}.csv'
            df = pd.read_csv(os.path.join(PASTA, arquivo), sep=';',
                             keep_default_na=False, encoding='utf-8')
            df['rotulo'] = rotulos(df, conjunto)
            nome_png = f'{ARQUIVOS[conjunto]}_top10_{conjunto}_{rotulo}.png'
            subtitulo = '' if conjunto == 'N' else SUBTITULO
            gv.grafico_top10(df, 'rotulo', titulo, nome_png, SAIDA, subtitulo)
            print(f'  salvo: {SAIDA / nome_png}')


if __name__ == '__main__':
    main()
