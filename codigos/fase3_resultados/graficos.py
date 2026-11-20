##f
# graficos.py
# Gera os graficos PNG a partir das tabelas do tabelas.py.
#
# Entrada (em DIR_SAIDA): eventosPorAno.csv, eventosPorFaixas.csv, top10_{N,NA,NPA,NCA}.csv
# Saidas  (em DIR_SAIDA):
#   graficoEventosPorAno.png     uma linha por conjunto com ano (NA, NPA, NCA)
#   graficoEventosPorFaixas.png  distribuicao por faixa de ocorrencias (eixo Y log)
#   graficoTop10.png             barras do top 10 de cada conjunto
#
# Dependencia: matplotlib (pip install matplotlib)

import csv
import os

import matplotlib
matplotlib.use('Agg')          # so grava arquivo: nao precisa de janela/interface
import matplotlib.pyplot as plt

# --- caminho (preencher) -----------------------------------------------------
DIR_SAIDA = r'D:\BACKUP\Magela\resultados'    # a mesma pasta usada no tabelas.py

# --- parametros --------------------------------------------------------------
DELIMITADOR = ';'          # delimitador das SAIDAS do tabelas.py
CONJUNTOS = ['N', 'NA', 'NPA', 'NCA']      # mesmos rotulos do tabelas.py
DPI = 150
LIMITE_ROTULO = 40             # caracteres do rotulo das barras do top 10


def ler_tabela(nome_arquivo: str) -> list:
    """Le um CSV e devolve uma lista de dicts {coluna: valor}."""
    caminho = os.path.join(DIR_SAIDA, nome_arquivo)
    with open(caminho, mode='r', newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter=DELIMITADOR))


def salvar(fig, nome_arquivo: str) -> None:
    caminho = os.path.join(DIR_SAIDA, nome_arquivo)
    fig.tight_layout()
    fig.savefig(caminho, dpi=DPI)
    plt.close(fig)
    print(f'  salvo: {caminho}')


def grafico_eventos_por_ano() -> None:
    series = {}
    for linha in ler_tabela('eventosPorAno.csv'):
        series.setdefault(linha['CONJUNTO'], []).append(
            (int(linha['ANO']), int(linha['DISTINTOS'])))

    fig, eixo = plt.subplots(figsize=(12, 6))
    for conjunto, pontos in sorted(series.items()):
        pontos.sort()
        eixo.plot([p[0] for p in pontos], [p[1] for p in pontos],
                  marker='o', markersize=2, linewidth=1.5, label=conjunto)

    eixo.set_xlabel('Ano')
    eixo.set_ylabel('Chaves distintas por ano')
    eixo.set_title('Número de eventos registrados por ano')
    eixo.legend()
    eixo.grid(True, linestyle='--', alpha=0.5)
    salvar(fig, 'graficoEventosPorAno.png')


def grafico_eventos_por_faixas() -> None:
    faixas = {}                # INICIO -> rotulo (define a ordem no eixo X)
    valores = {}               # conjunto -> {INICIO: quantidade de chaves}
    for linha in ler_tabela('eventosPorFaixas.csv'):
        inicio = int(linha['INICIO'])
        faixas[inicio] = linha['FAIXA']
        valores.setdefault(linha['CONJUNTO'], {})[inicio] = int(linha['QTD-EVENTOS'])

    ordem = sorted(faixas)
    fig, eixo = plt.subplots(figsize=(12, 6))
    for conjunto, por_faixa in sorted(valores.items()):
        # faixa vazia vira lacuna (0 nao existe em escala log)
        eixo.plot([faixas[i] for i in ordem],
                  [por_faixa.get(i, float('nan')) for i in ordem],
                  marker='o', markersize=3, linewidth=1.5, label=conjunto)

    eixo.set_xlabel('Faixa de registros')
    eixo.set_ylabel('Quantidade de chaves na faixa (escala log)')
    eixo.set_title('Distribuição por quantidade de registros')
    eixo.set_yscale('log')
    eixo.legend()
    eixo.grid(True, linestyle='--', alpha=0.5)
    plt.setp(eixo.get_xticklabels(), rotation=45, ha='right')
    salvar(fig, 'graficoEventosPorFaixas.png')


def grafico_top10() -> None:
    fig, eixos = plt.subplots(2, 2, figsize=(14, 9))

    for eixo, conjunto in zip(eixos.flatten(), CONJUNTOS):
        arquivo = f'top10_{conjunto}.csv'
        if not os.path.exists(os.path.join(DIR_SAIDA, arquivo)):
            print(f'  [aviso] nao encontrado: {arquivo}')
            continue

        nomes, valores = [], []
        for linha in reversed(ler_tabela(arquivo)):      # maior fica no topo
            chave = ' | '.join(v for coluna, v in linha.items() if coluna != 'OCORRENCIAS')
            if len(chave) > LIMITE_ROTULO:
                chave = chave[:LIMITE_ROTULO - 3] + '...'
            nomes.append(chave)
            valores.append(int(linha['OCORRENCIAS']))

        eixo.barh(nomes, valores, color='steelblue')
        eixo.set_title(f'{conjunto} - top 10')
        eixo.set_xlabel('Registros')

    fig.suptitle('Top 10 eventos registrados por conjunto', fontsize=14)
    salvar(fig, 'graficoTop10.png')


def main():
    print('=== gráficos de resultados ===')
    for arquivo in ('eventosPorAno.csv', 'eventosPorFaixas.csv'):
        if not os.path.exists(os.path.join(DIR_SAIDA, arquivo)):
            print(f'[ERRO] rode o tabelas.py antes (falta {arquivo}).')
            return

    print('\n[1] Eventos por ano...')
    grafico_eventos_por_ano()
    print('\n[2] Distribuição por faixas...')
    grafico_eventos_por_faixas()
    print('\n[3] Top 10 por conjunto...')
    grafico_top10()

    print(f'\nResultados em: {DIR_SAIDA}')


if __name__ == '__main__':
    main()