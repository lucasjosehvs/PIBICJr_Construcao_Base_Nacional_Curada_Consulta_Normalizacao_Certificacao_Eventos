##f
# dadosMapaMundial.py
# Agrega os eventos por PAIS-DO-EVENTO para o mapa de calor mundial (choropleth),
# com o codigo ISO-3 para uso direto em plotly/folium.
#
# Entrada: conjuntoNPA_ordenado.csv (ja quantificado; delimitador |)
#   NOME-DO-EVENTO | PAIS-DO-EVENTO | ANO-DO-EVENTO | OCORRENCIAS-EVENTO-PAIS-ANO
#
# Saidas (em DIR_SAIDA, delimitador ;):
#   eventosPorPais.csv           PAIS-DO-EVENTO;OCORRENCIAS;EVENTOS-DISTINTOS;
#                                ANO-MIN;ANO-MAX;CODIGO-ISO3
#   eventosPorPaisAno.csv        PAIS-DO-EVENTO;ANO;OCORRENCIAS   (mapa animado)
#   eventosPorPaisSemCodigo.csv  PAIS-DO-EVENTO;OCORRENCIAS       (margem: sem ISO)
#
# Definicoes:
#   - OCORRENCIAS        = soma da contagem (mencoes nos curriculos).
#   - EVENTOS-DISTINTOS  = numero de linhas (chaves nome|pais|ano) do pais, ou seja,
#                          edicoes distintas de evento. Conta sem guardar nomes na RAM.
#   - Linhas sem NOME-DO-EVENTO sao excluidas e reportadas.

import csv
import os
import time
from collections import Counter

# --- caminhos (preencher) -----------------------------------------------------
ENTRADA = r'D:\BACKUP\Magela\conjuntoNPA_ordenado.csv'      # conjuntoNPA_ordenado.csv
DIR_SAIDA = r'D:\BACKUP\Magela\resultados'    # pasta de saida (criada se nao existir)

# --- parametros --------------------------------------------------------------
DELIMITADOR_ENTRADA = '|'
DELIMITADOR_SAIDA = ';'
INTERVALO_LOG = 1000000
LIMITE_TESTE = None          # ex.: 500_000 linhas, para validar antes
ANO_MIN, ANO_MAX = 1900, 2030
SEM_PAIS = '(sem-pais)'

# ISO-3 -> variantes do nome do pais JA NORMALIZADAS (minusculas, sem acento,
# sem stopwords: "Estados Unidos da America" -> 'estados unidos america').
# Para completar: rode, abra eventosPorPaisSemCodigo.csv e adicione as variantes.
PAISES_ISO3 = {
    'AFG': ['afeganistao'],
    'AGO': ['angola'],
    'ALB': ['albania'],
    'AND': ['andorra'],
    'ARE': ['emirados arabes', 'emirados arabes unidos'],
    'ARG': ['argentina'],
    'ARM': ['armenia'],
    'ASM': ['samoa americana'],
    'AUS': ['australia'],
    'AUT': ['austria'],
    'AZE': ['azerbaijao'],
    'BDI': ['burundi'],
    'BEL': ['belgica'],
    'BEN': ['benin'],
    'BFA': ['burkina faso'],
    'BGD': ['bangladesh'],
    'BGR': ['bulgaria'],
    'BHR': ['bahrein'],
    'BHS': ['bahamas'],
    'BIH': ['bosnia'],
    'BLR': ['belarus', 'bielorussia'],
    'BLZ': ['belize'],
    'BOL': ['bolivia'],
    'BRA': ['brasil', 'brazil'],
    'BRB': ['barbados'],
    'BRN': ['brunei'],
    'BTN': ['butao'],
    'BWA': ['botswana'],
    'CAN': ['canada'],
    'CHE': ['suica'],
    'CHL': ['chile'],
    'CHN': ['china'],
    'CIV': ['costa do marfim'],
    'CMR': ['camaroes'],
    'COD': ['rd congo'],
    'COG': ['congo'],
    'COL': ['colombia'],
    'CPV': ['cabo verde'],
    'CRI': ['costa rica'],
    'CUB': ['cuba'],
    'CYP': ['chipre'],
    'CZE': ['republica tcheca', 'tcheca', 'tchequia'],
    'DEU': ['alemanha'],
    'DJI': ['djibuti'],
    'DMA': ['dominica'],
    'DNK': ['dinamarca'],
    'DOM': ['republica dominicana'],
    'DZA': ['argelia'],
    'ECU': ['equador'],
    'EGY': ['egito'],
    'ERI': ['eritreia'],
    'ESP': ['espana', 'espanha', 'espanhola'],
    'EST': ['estonia'],
    'ETH': ['etiopia'],
    'FIN': ['finlandia'],
    'FRA': ['franca'],
    'GAB': ['gabao'],
    'GBR': ['reino unido', 'inglaterra', 'escocia', 'gales', 'gra bretanha'],
    'GEO': ['georgia'],
    'GHA': ['gana'],
    'GIN': ['guine'],
    'GMB': ['gambia'],
    'GNB': ['guine bissau'],
    'GNQ': ['guine equatorial'],
    'GRC': ['grecia'],
    'GRD': ['granada'],
    'GTM': ['guatemala'],
    'GUF': ['guiana francesa'],
    'GUY': ['guiana'],
    'HKG': ['hong kong'],
    'HND': ['honduras'],
    'HRV': ['croacia'],
    'HTI': ['haiti'],
    'HUN': ['hungria'],
    'IDN': ['indonesia'],
    'IND': ['india'],
    'IRL': ['irlanda'],
    'IRN': ['ira'],
    'IRQ': ['iraque'],
    'ISL': ['islandia'],
    'ISR': ['israel'],
    'ITA': ['italia'],
    'JAM': ['jamaica'],
    'JOR': ['jordania'],
    'JPN': ['japao'],
    'KAZ': ['cazaquistao'],
    'KEN': ['kenia'],
    'KGZ': ['quirguistao'],
    'KHM': ['camboja'],
    'KOR': ['coreia sul', 'corea sul', 'coreia do sul', 'correia do sul'],
    'KWT': ['kuwait'],
    'LAO': ['laos'],
    'LBN': ['libano'],
    'LBR': ['liberia'],
    'LBY': ['libia'],
    'LCA': ['santa lucia'],
    'LIE': ['liechtenstein'],
    'LKA': ['sri lanka'],
    'LSO': ['lesoto'],
    'LTU': ['lituania'],
    'LUX': ['luxemburgo'],
    'LVA': ['letonia'],
    'MAR': ['marrocos'],
    'MCO': ['monaco'],
    'MDA': ['moldavia'],
    'MDG': ['madagascar'],
    'MDV': ['maldivas'],
    'MEX': ['mexico'],
    'MKD': ['macedonia'],
    'MLI': ['mali'],
    'MLT': ['malta'],
    'MMR': ['mianmar'],
    'MNE': ['montenegro'],
    'MNG': ['mongolia'],
    'MOZ': ['mocambique'],
    'MRT': ['mauritania'],
    'MUS': ['mauricio'],
    'MWI': ['malawi'],
    'MYS': ['malasia'],
    'NAM': ['namibia'],
    'NER': ['niger'],
    'NGA': ['nigeria'],
    'NIC': ['nicaragua'],
    'NLD': ['holanda', 'paises baixos'],
    'NOR': ['noruega'],
    'NPL': ['nepal'],
    'NZL': ['nova zelandia'],
    'OMN': ['oma'],
    'PAK': ['paquistao'],
    'PAN': ['panama'],
    'PER': ['peru'],
    'PHL': ['filipinas'],
    'POL': ['polonia'],
    'PRI': ['porto rico'],
    'PRK': ['coreia norte'],
    'PRT': ['portugal'],
    'PRY': ['paraguai'],
    'PSE': ['palestina'],
    'QAT': ['catar'],
    'ROU': ['romenia'],
    'RUS': ['russia'],
    'RWA': ['ruanda'],
    'SAU': ['arabia saudita'],
    'SDN': ['sudao'],
    'SEN': ['senegal'],
    'SGP': ['singapura'],
    'SLE': ['serra leoa'],
    'SLV': ['salvador', 'el salvador'],
    'SMR': ['san marino'],
    'SOM': ['somalia'],
    'SRB': ['servia'],
    'SSD': ['sudao sul'],
    'STP': ['sao tome principe'],
    'SUR': ['suriname'],
    'SVK': ['eslovaquia'],
    'SVN': ['eslovenia'],
    'SWE': ['suecia'],
    'SYR': ['siria'],
    'TCD': ['chade'],
    'TGO': ['togo'],
    'THA': ['tailandia'],
    'TJK': ['tadjiquistao'],
    'TKM': ['turcomenistao'],
    'TLS': ['timor leste'],
    'TTO': ['trinidad tobago'],
    'TUN': ['tunisia'],
    'TUR': ['turquia'],
    'TWN': ['taiwan'],
    'TZA': ['tanzania'],
    'UGA': ['uganda'],
    'UKR': ['ukraina', 'ucrania', 'ukraine'],
    'URY': ['uruguai'],
    'USA': ['estados unidos', 'estados unidos america', 'eua', 'usa'],
    'UZB': ['uzbequistao'],
    'VAT': ['vaticano'],
    'VEN': ['venezuela'],
    'VNM': ['vietname', 'vietna'],
    'YEM': ['iemen'],
    'ZAF': ['africa do sul', 'africa sul'],
    'ZMB': ['zambia'],
    'ZWE': ['zimbabue'],
}

# nome normalizado -> ISO-3 (inverte o dicionario acima)
ISO3 = {nome: iso for iso, nomes in PAISES_ISO3.items() for nome in nomes}


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
    print('=== dados mapa mundial ===')
    inicio = time.time()

    if not os.path.exists(ENTRADA):
        print(f'[ERRO] arquivo nao encontrado: {ENTRADA}')
        return
    os.makedirs(DIR_SAIDA, exist_ok=True)

    ocorrencias_pais = Counter()
    eventos_pais = Counter()                 # linhas (edicoes distintas) por pais
    ano_min_pais = {}
    ano_max_pais = {}
    ocorrencias_pais_ano = Counter()
    invalidas = sem_nome = ocorrencias_sem_nome = 0

    print('[1] Agregando por pais...')
    with open(ENTRADA, mode='r', newline='', encoding='utf-8-sig') as f:
        leitor = csv.reader(f, delimiter=DELIMITADOR_ENTRADA)
        cabecalho = next(leitor)
        i_oc = indice_ocorrencias(cabecalho)
        i_nome = cabecalho.index('NOME-DO-EVENTO')
        i_pais = cabecalho.index('PAIS-DO-EVENTO')
        i_ano = cabecalho.index('ANO-DO-EVENTO')
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

            pais = linha[i_pais] or SEM_PAIS
            ano = linha[i_ano]

            ocorrencias_pais[pais] += ocorrencias
            eventos_pais[pais] += 1

            if ano_valido(ano):
                ano_int = int(ano)
                ano_min_pais[pais] = min(ano_min_pais.get(pais, ano_int), ano_int)
                ano_max_pais[pais] = max(ano_max_pais.get(pais, ano_int), ano_int)
                ocorrencias_pais_ano[(pais, ano)] += ocorrencias

            if n % INTERVALO_LOG == 0:
                print(f'  {n:>10} linhas lidas...')

    print(f'  sem nome (excluidas): {sem_nome} linhas ({ocorrencias_sem_nome} ocorrencias) | '
          f'invalidas: {invalidas}')

    print('\n[2] Gravando resultados...')
    gravar('eventosPorPais.csv',
           ['PAIS-DO-EVENTO', 'OCORRENCIAS', 'EVENTOS-DISTINTOS',
            'ANO-MIN', 'ANO-MAX', 'CODIGO-ISO3'],
           ([pais, qtd, eventos_pais[pais],
             ano_min_pais.get(pais, ''), ano_max_pais.get(pais, ''),
             ISO3.get(pais, '')]
            for pais, qtd in ocorrencias_pais.most_common()))

    gravar('eventosPorPaisAno.csv',
           ['PAIS-DO-EVENTO', 'ANO', 'OCORRENCIAS'],
           ([pais, ano, qtd] for (pais, ano), qtd in sorted(ocorrencias_pais_ano.items())))

    sem_codigo = [(pais, qtd) for pais, qtd in ocorrencias_pais.most_common()
                  if pais not in ISO3]
    gravar('eventosPorPaisSemCodigo.csv', ['PAIS-DO-EVENTO', 'OCORRENCIAS'], sem_codigo)

    print('\n[3] Resumo (top 15):')
    for pais, qtd in ocorrencias_pais.most_common(15):
        print(f'  {pais:<32} {qtd:>10}')

    total = sum(ocorrencias_pais.values())
    total_sem = sum(qtd for _, qtd in sem_codigo)
    print(f'\n  paises sem ISO-3: {len(sem_codigo)} '
          f'({total_sem} ocorrencias = {100 * total_sem / max(total, 1):.2f}% do total)'
          f' -> eventosPorPaisSemCodigo.csv')

    print(f'\nConcluido em {time.time() - inicio:.2f}s')
    print(f'Resultados em: {DIR_SAIDA}')


if __name__ == '__main__':
    main()