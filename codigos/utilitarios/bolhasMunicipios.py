##f

import os
import re
import unicodedata
import pandas as pd
import matplotlib.pyplot as plt

#caminhos (preencher)
csvCidades = r'D:\BACKUP\Magela\resultados\eventosPorCidadeUF.csv'
csvCoordenadas = r'D:\BACKUP\Magela\csvs\municipiosCoordenadas.csv'   #latitude/longitude por município (kelvins/municipios-brasileiros)
geoUF = r''                    #opcional: GeoJSON dos estados para o contorno (ex.: pasta geo\). Vazio = sem contorno
saida = r'D:\BACKUP\Magela\resultados\mapas'

#parametros
COLUNA_TAMANHO = 'OCORRENCIAS'   #ou 'EVENTOS-DISTINTOS'
EXPOENTE = 0.5                   #area da bolha ~ valor**EXPOENTE (1 = proporcional, 0.5 = suaviza SP)
TAMANHO_MAX = 2500               #area da maior bolha (pontos^2)
TAMANHO_MIN = 3
QTD_ROTULOS = 15                 #cidades com nome escrito no mapa
LIMITE_TESTE = None              #ex.: 5000 para testar com poucas linhas

#codigo IBGE da UF -> sigla
UF = {
    11: 'RO', 12: 'AC', 13: 'AM', 14: 'RR', 15: 'PA', 16: 'AP', 17: 'TO',
    21: 'MA', 22: 'PI', 23: 'CE', 24: 'RN', 25: 'PB', 26: 'PE', 27: 'AL', 28: 'SE', 29: 'BA',
    31: 'MG', 32: 'ES', 33: 'RJ', 35: 'SP',
    41: 'PR', 42: 'SC', 43: 'RS',
    50: 'MS', 51: 'MT', 52: 'GO', 53: 'DF',
}

#funcoes
#stopwords: usa o nltk (igual a normalizacaoGeral) e cai numa lista curta se nao houver
def carregarStopwords() -> set:
    try:
        from nltk.corpus import stopwords
        palavras = set(stopwords.words('portuguese')) | set(stopwords.words('english'))
    except Exception:
        palavras = {'de', 'da', 'do', 'das', 'dos', 'e', 'd', 'a', 'o', 'em', 'na', 'no'}
    return {normalizar(p) for p in palavras} - {'sao'}

def normalizar(texto: str) -> str:
    texto = unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode().lower()
    texto = re.sub(r'[^a-z0-9 ]', ' ', texto)
    return ' '.join(texto.split())

def tirarStop(texto: str) -> str:
    return ' '.join(p for p in texto.split() if p not in STOP)

#varias grafias do mesmo municipio (a normalizacao do pipeline nao e igual a do IBGE)
def chaves(nome: str) -> set:
    base = normalizar(nome)
    colado = normalizar(str(nome).replace("'", ''))
    return {base, colado, tirarStop(base), tirarStop(colado)}

#(chave, UF) -> linha do municipio
def montarDicionario(municipios: pd.DataFrame):
    dicionario = {}
    colisoes = 0
    for linha in municipios.itertuples():
        for chave in chaves(linha.nome):
            if (chave, linha.uf) in dicionario and dicionario[(chave, linha.uf)] != linha.codigo_ibge:
                colisoes += 1
                continue
            dicionario[(chave, linha.uf)] = linha.codigo_ibge
    return dicionario, colisoes

def tamanho(valor, maximo):
    return max(TAMANHO_MIN, TAMANHO_MAX * (valor / maximo) ** EXPOENTE)

def gerarPNG(dados: pd.DataFrame, caminho: str, nota: str) -> None:
    dados = dados.sort_values(COLUNA_TAMANHO, ascending=False)    #bolhas grandes embaixo
    maximo = dados[COLUNA_TAMANHO].max()
    fig, ax = plt.subplots(figsize=(10, 10))

    if geoUF and os.path.exists(geoUF):
        import geopandas
        geopandas.read_file(geoUF).plot(ax=ax, color='#f2f2f2', edgecolor='white', linewidth=0.6)

    ax.scatter(dados['longitude'], dados['latitude'],
               s=[tamanho(v, maximo) for v in dados[COLUNA_TAMANHO]],
               color='#0072B2', alpha=0.45, edgecolors='white', linewidths=0.3)

    for linha in dados.head(QTD_ROTULOS).itertuples():
        ax.annotate(f'{linha.nome} ({linha.uf})', (linha.longitude, linha.latitude),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)

    for referencia in (10_000, 100_000, 1_000_000):
        if referencia < maximo:
            ax.scatter([], [], s=tamanho(referencia, maximo), color='#0072B2', alpha=0.45,
                       label=f'{referencia:,}'.replace(',', '.'))
    rotulo = 'Ocorrências' if COLUNA_TAMANHO == 'OCORRENCIAS' else 'Eventos distintos'
    ax.legend(title=rotulo, loc='lower left', frameon=False, labelspacing=1.4)

    ax.set_xlim(-74.5, -33)
    ax.set_ylim(-34.5, 5.8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Eventos do Lattes por município', fontsize=15, fontweight='bold', loc='left')
    fig.text(0.02, 0.02, nota, fontsize=8, color='#555555', wrap=True)
    fig.savefig(caminho, dpi=200, bbox_inches='tight')
    plt.close(fig)

def gerarHTML(dados: pd.DataFrame, caminho: str) -> None:
    try:
        import plotly.express as px
    except ImportError:
        print('plotly nao instalado: HTML nao gerado')
        return
    dados = dados.copy()
    dados['tam'] = dados[COLUNA_TAMANHO] ** EXPOENTE
    fig = px.scatter_geo(dados, lat='latitude', lon='longitude', size='tam', size_max=45,
                         color='uf', hover_name='nome',
                         hover_data={'OCORRENCIAS': ':,', 'EVENTOS-DISTINTOS': ':,',
                                     'tam': False, 'latitude': False, 'longitude': False, 'uf': True},
                         title='Eventos do Lattes por município')
    fig.update_geos(scope='south america', lataxis_range=[-34.5, 5.8], lonaxis_range=[-74.5, -33],
                    showcountries=True, showland=True, landcolor='#f2f2f2')
    fig.write_html(caminho, include_plotlyjs='cdn')

#principal
def main():
    global STOP
    STOP = carregarStopwords()
    os.makedirs(saida, exist_ok=True)

    municipios = pd.read_csv(csvCoordenadas, sep=',')
    municipios['uf'] = municipios['codigo_uf'].map(UF)
    dicionario, colisoes = montarDicionario(municipios)

    eventos = pd.read_csv(csvCidades, sep=';', dtype={'ESTADO': str}, nrows=LIMITE_TESTE)
    total = eventos['OCORRENCIAS'].sum()
    eventos = eventos[eventos['AMBIGUA'] == 0].copy()          #ambiguas ficam de fora, como no mapa por UF
    semAmbiguas = eventos['OCORRENCIAS'].sum()

    #acha o codigo IBGE de cada linha (tenta a grafia do CSV e a sem stopwords)
    def achar(linha):
        cidade = str(linha['CIDADE-DO-EVENTO'])
        for chave in (cidade, tirarStop(cidade)):
            codigo = dicionario.get((chave, linha['ESTADO']))
            if codigo is not None:
                return codigo
        return None

    eventos['codigo_ibge'] = eventos.apply(achar, axis=1)
    achados = eventos[eventos['codigo_ibge'].notna()]
    perdidos = eventos[eventos['codigo_ibge'].isna()].sort_values('OCORRENCIAS', ascending=False)
    perdidos.to_csv(os.path.join(saida, 'municipiosSemCoordenada.csv'), sep=';', index=False)

    #varias grafias podem cair no mesmo municipio: soma
    agrupado = (achados.groupby('codigo_ibge')[['OCORRENCIAS', 'EVENTOS-DISTINTOS']].sum().reset_index()
                .merge(municipios[['codigo_ibge', 'nome', 'uf', 'latitude', 'longitude']], on='codigo_ibge'))

    cobertura = agrupado['OCORRENCIAS'].sum()
    nota = (f'Fonte: currículos Lattes (CNPq) — processamento próprio. Coordenadas: IBGE (kelvins/municipios-brasileiros). '
            f'Exclui cidades ambíguas; este mapa representa {cobertura / total:.1%} das ocorrências com cidade. '
            f'Área da bolha proporcional a (valor)^{EXPOENTE}.')

    gerarPNG(agrupado, os.path.join(saida, 'bolhasMunicipios.png'), nota)
    gerarHTML(agrupado, os.path.join(saida, 'bolhasMunicipios.html'))

    print(f'linhas sem ambiguas: {len(eventos)}')
    print(f'ocorrencias totais: {total:,}'.replace(',', '.'))
    print(f'  ambiguas (fora do mapa): {(total - semAmbiguas):,}'.replace(',', '.'))
    print(f'  sem coordenada (ver municipiosSemCoordenada.csv): {perdidos["OCORRENCIAS"].sum():,}'.replace(',', '.'))
    print(f'  no mapa: {cobertura:,} em {len(agrupado)} municipios'.replace(',', '.'))
    print(f'colisoes de nome na mesma UF: {colisoes}')
    print(perdidos.head(10)[['CIDADE-DO-EVENTO', 'ESTADO', 'OCORRENCIAS']].to_string(index=False))

if __name__ == '__main__':
    main()
