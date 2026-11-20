# tabelasDatawrapper.py
# Gera os CSVs da pasta dw/ a partir das saidas ja quantificadas (eventosPor*.csv,
# top10_*.csv). Entrada: pasta de saidas do projeto. Saida: subpasta dw/ (delimitador ,).
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dadosMapaBrasil import chave_cidade            # chave normalizada do projeto
from dadosMapaMundial import ISO3                    # nome normalizado -> ISO3

PASTA = r'D:\BACKUP\Magela\resultados'
DIR_DW = os.path.join(PASTA, 'dw')
ARQ_ESTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'estados.csv')
ARQ_MUNICIPIOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'municipios.csv')

NOMES_PAIS = {
    'AFG': 'Afeganistão', 'AGO': 'Angola', 'ALB': 'Albânia', 'AND': 'Andorra',
    'ARE': 'Emirados Árabes Unidos', 'ARG': 'Argentina', 'ARM': 'Armênia',
    'ASM': 'Samoa Americana', 'AUS': 'Austrália', 'AUT': 'Áustria', 'AZE': 'Azerbaijão',
    'BDI': 'Burundi', 'BEL': 'Bélgica', 'BEN': 'Benim', 'BFA': 'Burkina Faso',
    'BGD': 'Bangladesh', 'BGR': 'Bulgária', 'BHR': 'Bahrein', 'BHS': 'Bahamas',
    'BIH': 'Bósnia e Herzegovina', 'BLR': 'Bielorrússia', 'BLZ': 'Belize',
    'BOL': 'Bolívia', 'BRA': 'Brasil', 'BRB': 'Barbados', 'BRN': 'Brunei',
    'BTN': 'Butão', 'BWA': 'Botsuana', 'CAN': 'Canadá', 'CHE': 'Suíça',
    'CHL': 'Chile', 'CHN': 'China', 'CIV': 'Costa do Marfim', 'CMR': 'Camarões',
    'COD': 'RD Congo', 'COG': 'Congo', 'COL': 'Colômbia', 'CPV': 'Cabo Verde',
    'CRI': 'Costa Rica', 'CUB': 'Cuba', 'CYP': 'Chipre', 'CZE': 'República Tcheca',
    'DEU': 'Alemanha', 'DJI': 'Djibuti', 'DMA': 'Dominica', 'DNK': 'Dinamarca',
    'DOM': 'República Dominicana', 'DZA': 'Argélia', 'ECU': 'Equador', 'EGY': 'Egito',
    'ERI': 'Eritreia', 'ESP': 'Espanha', 'EST': 'Estônia', 'ETH': 'Etiópia',
    'FIN': 'Finlândia', 'FRA': 'França', 'GAB': 'Gabão',
    'GBR': 'Reino Unido', 'GEO': 'Geórgia', 'GHA': 'Gana', 'GIN': 'Guiné',
    'GMB': 'Gâmbia', 'GNB': 'Guiné-Bissau', 'GNQ': 'Guiné Equatorial',
    'GRC': 'Grécia', 'GRD': 'Granada', 'GTM': 'Guatemala', 'GUF': 'Guiana Francesa',
    'GUY': 'Guiana', 'HND': 'Honduras', 'HRV': 'Croácia', 'HTI': 'Haiti',
    'HUN': 'Hungria', 'IDN': 'Indonésia', 'IRL': 'Irlanda', 'IRN': 'Irã',
    'IRQ': 'Iraque', 'ISL': 'Islândia', 'ISR': 'Israel', 'ITA': 'Itália',
    'JAM': 'Jamaica', 'JOR': 'Jordânia', 'JPN': 'Japão', 'KEN': 'Quênia',
    'KAZ': 'Cazaquistão', 'KHM': 'Camboja', 'KOR': 'Coreia do Sul', 'LAO': 'Laos',
    'LBN': 'Líbano', 'LBR': 'Libéria', 'LBY': 'Líbia', 'LCA': 'Santa Lúcia',
    'LIE': 'Liechtenstein', 'LKA': 'Sri Lanka', 'LSO': 'Lesoto', 'LTU': 'Lituânia',
    'LUX': 'Luxemburgo', 'LVA': 'Letônia', 'MAC': 'Macau', 'MDG': 'Madagascar',
    'MDV': 'Maldivas', 'MEX': 'México', 'MKD': 'Macedônia do Norte', 'MLI': 'Mali',
    'MLT': 'Malta', 'MMR': 'Mianmar', 'MNE': 'Montenegro', 'MNG': 'Mongólia',
    'MOZ': 'Moçambique', 'MRT': 'Mauritânia', 'MUS': 'Maurício', 'MYS': 'Malásia',
    'NAM': 'Namíbia', 'NER': 'Níger', 'NGA': 'Nigéria', 'NIC': 'Nicarágua',
    'NLD': 'Países Baixos', 'NOR': 'Noruega', 'NPL': 'Nepal', 'NZL': 'Nova Zelândia',
    'OMN': 'Omã', 'PAK': 'Paquistão', 'PAN': 'Panamá', 'PER': 'Peru',
    'PHL': 'Filipinas', 'POL': 'Polônia', 'PRI': 'Porto Rico', 'PRK': 'Coreia do Norte',
    'PRT': 'Portugal', 'PRY': 'Paraguai', 'QAT': 'Catar', 'ROU': 'Romênia',
    'RUS': 'Rússia', 'RWA': 'Ruanda', 'SAU': 'Arábia Saudita', 'SDN': 'Sudão',
    'SEN': 'Senegal', 'SGP': 'Singapura', 'SLV': 'El Salvador', 'SLE': 'Serra Leoa',
    'SMR': 'San Marino', 'SOM': 'Somália', 'SRB': 'Sérvia', 'STP': 'São Tomé e Príncipe',
    'SUR': 'Suriname', 'SWE': 'Suécia', 'SVK': 'Eslováquia', 'SVN': 'Eslovênia',
    'SYR': 'Síria', 'THA': 'Tailândia', 'TJK': 'Tajiquistão', 'TKM': 'Turcomenistão',
    'TLS': 'Timor-Leste', 'TGO': 'Togo', 'TTO': 'Trinidad e Tobago', 'TUN': 'Tunísia',
    'TUR': 'Turquia', 'TZA': 'Tanzânia', 'UGA': 'Uganda', 'UKR': 'Ucrânia',
    'URY': 'Uruguai', 'USA': 'Estados Unidos', 'UZB': 'Uzbequistão', 'VAT': 'Vaticano',
    'VEN': 'Venezuela', 'VNM': 'Vietnã', 'ZAF': 'África do Sul', 'ZMB': 'Zâmbia',
    'ZWE': 'Zimbábue',
}

DECADAS = [('ate_1999', None, 1999), ('2000_2009', 2000, 2009),
           ('2010_2019', 2010, 2019), ('2020_2024', 2020, 2024),
           ('2025_e_depois', 2025, None)]

QUALIDADE_FAIXAS = [(20, 'Boa (até 20% ambíguas)'), (60, 'Média (20–60%)'),
                    (None, 'Baixa (acima de 60%)')]


def ler(delimitador=';'):
    def decorador(nome):
        caminho = os.path.join(PASTA, nome)
        with open(caminho, encoding='utf-8') as f:
            return list(csv.DictReader(f, delimiter=delimitador))
    return decorador


def gravar_dw(nome, cabecalho, linhas):
    caminho = os.path.join(DIR_DW, nome)
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f, lineterminator='\n')
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)
    print(f'  salvo: {caminho}')


def carregar_estados():
    with open(ARQ_ESTADOS, encoding='utf-8-sig') as f:
        return {l['uf']: l for l in csv.DictReader(f)}


def carregar_municipios(siglas):
    indice = {}
    with open(ARQ_MUNICIPIOS, encoding='utf-8') as f:
        for l in csv.DictReader(f):
            uf = siglas.get(l['codigo_uf'])
            if not uf:
                continue
            chave = (chave_cidade(l['nome']), uf)
            indice.setdefault(chave, (l['nome'], l['latitude'], l['longitude'], l['codigo_ibge']))
    return indice


def faixa_qualidade(pct):
    for limite, rotulo in QUALIDADE_FAIXAS:
        if limite is None or pct <= limite:
            return rotulo


def decada(ano):
    for nome, ini, fim in DECADAS:
        if (ini is None or ano >= ini) and (fim is None or ano <= fim):
            return nome
    return None


def tabela_uf(estados):
    linhas = []
    for l in ler()('eventosPorUF.csv'):
        uf = l['ESTADO']
        brutas = int(l['OCORRENCIAS'])
        ambiguas = int(l['OCORRENCIAS-AMBIGUAS'])
        pct = round(100 * ambiguas / brutas, 1) if brutas else 0.0
        e = estados[uf]
        linhas.append([uf, e['nome'], e['codigo_uf'], e['regiao'],
                       brutas - ambiguas, ambiguas, brutas, pct,
                       faixa_qualidade(pct), int(l['EVENTOS-DISTINTOS'])])
    gravar_dw('01_brasil_uf.csv',
              ['UF', 'NOME_UF', 'CODIGO_IBGE', 'REGIAO', 'OCORRENCIAS_CERTAS',
               'OCORRENCIAS_AMBIGUAS', 'OCORRENCIAS_BRUTAS', 'PCT_AMBIGUAS',
               'QUALIDADE_MAPEAMENTO', 'EVENTOS_DISTINTOS'], linhas)


def tabela_uf_decadas(estados):
    agregado = {}
    for l in ler()('eventosPorUFAno.csv'):
        d = decada(int(l['ANO']))
        if d:
            agregado.setdefault(l['ESTADO'], {}).setdefault(d, 0)
            agregado[l['ESTADO']][d] += int(l['OCORRENCIAS'])
    colunas = [d[0] for d in DECADAS]
    linhas = []
    for uf in sorted(agregado):
        valores = [agregado[uf].get(c, 0) for c in colunas]
        linhas.append([uf, estados[uf]['nome']] + valores + [sum(valores)])
    gravar_dw('02_brasil_uf_por_decada.csv', ['UF', 'NOME_UF'] + colunas + ['TOTAL'], linhas)


def tabela_paises():
    dados = [l for l in ler()('eventosPorPais.csv') if l['CODIGO-ISO3']]
    dados.sort(key=lambda l: -int(l['OCORRENCIAS']))
    com_brasil = [[l['CODIGO-ISO3'], NOMES_PAIS.get(l['CODIGO-ISO3'], l['PAIS-DO-EVENTO'].title()),
                   int(l['OCORRENCIAS']), int(l['EVENTOS-DISTINTOS']),
                   int(l['ANO-MIN']), int(l['ANO-MAX'])] for l in dados]
    gravar_dw('03a_mundo_paises_com_brasil.csv',
              ['ISO3', 'PAIS', 'OCORRENCIAS', 'EVENTOS_DISTINTOS', 'ANO_MIN', 'ANO_MAX'],
              com_brasil)
    gravar_dw('03b_mundo_paises_sem_brasil.csv',
              ['ISO3', 'PAIS', 'OCORRENCIAS', 'EVENTOS_DISTINTOS', 'ANO_MIN', 'ANO_MAX'],
              [l for l in com_brasil if l[0] != 'BRA'])


def tabela_paises_decadas():
    nomes = {l['PAIS-DO-EVENTO']: l['CODIGO-ISO3'] for l in ler()('eventosPorPais.csv')}
    agregado = {}
    for l in ler()('eventosPorPaisAno.csv'):
        iso = nomes.get(l['PAIS-DO-EVENTO'])
        if not iso or iso == 'BRA':
            continue
        d = decada(int(l['ANO']))
        if d:
            agregado.setdefault(iso, {}).setdefault(d, 0)
            agregado[iso][d] += int(l['OCORRENCIAS'])
    colunas = [d[0] for d in DECADAS]
    linhas = []
    for iso, por_decada in sorted(agregado.items(), key=lambda i: -sum(i[1].values())):
        valores = [por_decada.get(c, 0) for c in colunas]
        linhas.append([iso, NOMES_PAIS.get(iso, iso)] + valores + [sum(valores)])
    gravar_dw('04_mundo_paises_por_decada_sem_brasil.csv',
              ['ISO3', 'PAIS'] + colunas + ['TOTAL'], linhas)


def tabela_cidades(estados):
    siglas = {codigo: uf for uf, codigo in ((u, e['codigo_uf']) for u, e in estados.items())}
    municipios = carregar_municipios(siglas)
    com_ponto, sem_ponto = [], []
    for l in ler()('eventosPorCidadeUF.csv'):
        if l['AMBIGUA'] == '1':
            continue
        registro = municipios.get((chave_cidade(l['CIDADE-DO-EVENTO']), l['ESTADO']))
        if registro:
            nome, lat, lon, codigo = registro
            com_ponto.append([nome, l['ESTADO'], int(l['OCORRENCIAS']),
                              int(l['EVENTOS-DISTINTOS']), lat, lon, codigo])
        else:
            sem_ponto.append([l['CIDADE-DO-EVENTO'], l['ESTADO'], int(l['OCORRENCIAS'])])
    com_ponto.sort(key=lambda l: -l[2])
    sem_ponto.sort(key=lambda l: -l[2])
    gravar_dw('05_brasil_cidades_pontos.csv',
              ['CIDADE', 'UF', 'OCORRENCIAS', 'EVENTOS_DISTINTOS', 'LATITUDE',
               'LONGITUDE', 'CODIGO_IBGE_MUNICIPIO'], com_ponto)
    gravar_dw('05b_cidades_sem_coordenada_para_revisar.csv',
              ['CIDADE-DO-EVENTO', 'ESTADO', 'OCORRENCIAS'], sem_ponto)


def tabela_anos():
    conjuntos = ('NA', 'NCA', 'NPA')
    dados = {c: {} for c in conjuntos}
    for l in ler()('eventosPorAno.csv'):
        if l['CONJUNTO'] in dados:
            dados[l['CONJUNTO']][int(l['ANO'])] = (int(l['DISTINTOS']), int(l['OCORRENCIAS']))
    anos = sorted(set().union(*[set(d) for d in dados.values()]))
    linhas = []
    for ano in anos:
        linha = [ano]
        for c in conjuntos:
            linha.append(dados[c].get(ano, (0, 0))[0])
        for c in conjuntos:
            linha.append(dados[c].get(ano, (0, 0))[1])
        linhas.append(linha)
    gravar_dw('06_linha_eventos_por_ano.csv',
              ['Ano', 'Eventos distintos (NA)', 'Eventos distintos (NCA)',
               'Eventos distintos (NPA)', 'Ocorrências (NA)', 'Ocorrências (NCA)',
               'Ocorrências (NPA)'], linhas)


def tabela_faixas():
    ordem, valores = [], {}
    for l in ler()('eventosPorFaixas.csv'):
        faixa = l['FAIXA']
        if faixa not in ordem:
            ordem.append(faixa)
        valores[(faixa, l['CONJUNTO'])] = int(l['QTD-EVENTOS'])
    linhas = [[f] + [valores.get((f, c), '') for c in ('N', 'NA', 'NCA', 'NPA')] for f in ordem]
    gravar_dw('07_colunas_faixas_de_ocorrencias.csv',
              ['Faixa de ocorrências', 'N', 'NA', 'NCA', 'NPA'], linhas)


def tabela_top10():
    def evento(nome):
        return nome.capitalize()

    for conjunto, colunas in [('N', ['Evento', 'Ocorrências']),
                              ('NA', ['Evento', 'Ano', 'Ocorrências']),
                              ('NCA', ['Evento', 'Cidade', 'Ano', 'Ocorrências']),
                              ('NPA', ['Evento', 'País', 'Ano', 'Ocorrências'])]:
        linhas = []
        for i, l in enumerate(ler()(f'top10_{conjunto}.csv'), start=1):
            valores = [evento(l['NOME-DO-EVENTO'])]
            if 'Cidade' in colunas:
                valores.append(l['CIDADE-DO-EVENTO'].title())
            if 'País' in colunas:
                iso = ISO3.get(l['PAIS-DO-EVENTO'])
                valores.append(NOMES_PAIS.get(iso, l['PAIS-DO-EVENTO'].title()))
            if 'Ano' in colunas:
                valores.append(l['ANO-DO-EVENTO'])
            valores.append(int(l['OCORRENCIAS']))
            linhas.append([i] + valores)
        gravar_dw(f'08_tabela_top10_{conjunto}.csv', ['Posição'] + colunas, linhas)


def main():
    os.makedirs(DIR_DW, exist_ok=True)
    print('=== tabelas Datawrapper (dw/) ===')
    estados = carregar_estados()
    tabela_uf(estados)
    tabela_uf_decadas(estados)
    tabela_paises()
    tabela_paises_decadas()
    tabela_cidades(estados)
    tabela_anos()
    tabela_faixas()
    tabela_top10()
    print(f'\nResultados em: {DIR_DW}')


if __name__ == '__main__':
    main()
