import csv
import os
import re
import time
import unicodedata
import nltk
from nltk.corpus import stopwords

csvEntrada = r''
saidaCSV = r''

csvNormalizado = os.path.join(saidaCSV, 'csvFiltro4.csv')

intervaloFlush = 5000

COLUNAS = [
    'NOME-DO-EVENTO',
    'TIPO-DE-EVENTO',
    'CLASSIFICACAO-DO-EVENTO',
    'PAIS-DO-EVENTO',
    'CIDADE-DO-EVENTO',
    'LOCAL-DO-EVENTO',
    'INSTITUICAO-PROMOTORA',
]

COLUNAano = 'ANO-DO-EVENTO'

def carregarStopwordsNLTK() -> list:
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    return stopwords.words('portuguese') + stopwords.words('english')

regexPontos = re.compile(r'[^\w\s]|_')
regexOrdinal = re.compile(r'^\d+(o|a|º|ª|st|nd|rd|th|an)?$', re.IGNORECASE)
regexRomano = re.compile(r'^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$', re.IGNORECASE)

def removerAcentos(texto: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

stopwordsLista = carregarStopwordsNLTK()
STOPWORDS = {removerAcentos(palavra) for palavra in stopwordsLista}
STOPWORDS.discard('sao')
STOPWORDS = frozenset(STOPWORDS)

def NumeroOrRomano(palavra: str) -> bool:
    if palavra == '' or palavra.isdigit():
        return True
    if regexOrdinal.fullmatch(palavra):
        return True
    if regexRomano.fullmatch(palavra):
        return True
    return False

def normalizarTexto(texto: str) -> str:
    if texto is None or texto == '':
        return ''
    texto = texto.lower()
    texto = removerAcentos(texto)
    texto = regexPontos.sub(' ', texto)

    palavrasFinais = []
    for palavra in texto.split():
        if NumeroOrRomano(palavra):
            continue
        if palavra in STOPWORDS:
            continue
        palavrasFinais.append(palavra)

    return ' '.join(palavrasFinais)

regexAno = re.compile(r'^(\d+)[.,]0+$')

def limparAno(valor: str) -> str:
    valor = valor.strip()
    if valor == '':
        return ''
    encontrado = regexAno.match(valor)
    return encontrado.group(1) if encontrado else valor

def main():
    os.makedirs(saidaCSV, exist_ok=True)
    inicio = time.time()

    contagemTotal = 0
    contagemAnoCorrigido = 0

    with open(csvEntrada, mode='r', newline='', encoding='utf-8') as f_entrada, \
         open(csvNormalizado, mode='w', newline='', encoding='utf-8') as f_saida:

        leitor = csv.reader(f_entrada, delimiter=';')
        escritor = csv.writer(f_saida, delimiter=';')

        cabecalho = next(leitor)
        escritor.writerow(cabecalho)

        indicesNormalizar = [cabecalho.index(coluna) for coluna in COLUNAS]
        indiceAno = cabecalho.index(COLUNAano)

        for linha in leitor:
            contagemTotal += 1

            for indice in indicesNormalizar:
                linha[indice] = normalizarTexto(linha[indice])

            anoOriginal = linha[indiceAno]
            anoLimpo = limparAno(anoOriginal)
            linha[indiceAno] = anoLimpo

            escritor.writerow(linha)

            if contagemTotal % intervaloFlush == 0:
                f_saida.flush()

    tempo_total = time.time() - inicio
    print()
    print(f'{contagemTotal} linhas')
    print(f'tempo total {tempo_total:.1f} s')

if __name__ == '__main__':
    main()