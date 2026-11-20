import csv
import os
import time
import hashlib

csvEntrada = r''
saidaCSV = r''

csvDuplicadasRemovidas = os.path.join(saidaCSV, 'Conjunto1.csv')

intervaloFlush = 300000

COLUNAS = [
    'IDENTIFICADOR',
    'TIPO-REGISTRO',
    'NOME-DO-EVENTO',
    'TIPO-DE-EVENTO',
    'CLASSIFICACAO-DO-EVENTO',
    'ANO-DO-EVENTO',
    'PAIS-DO-EVENTO',
    'CIDADE-DO-EVENTO',
    'LOCAL-DO-EVENTO',
    'CODIGO-INSTITUICAO-PROMOTORA',
    'INSTITUICAO-PROMOTORA',
    'DURACAO-EM-SEMANAS',
]

separadorHash = '\x1f'

def hashDaLinha(linha: dict) -> bytes:
    ass = separadorHash.join(linha.get(coluna, '')for coluna in COLUNAS)
    return hashlib.md5(ass.encode('utf-8')).digest()

def main():
    os.makedirs(saidaCSV, exist_ok=True)
    inicio = time.time()
    contagemTotal = 0
    contagemMantidas = 0
    contagemDuplicadas = 0
    hashesVistos = set()

    with open(csvEntrada, newline='', encoding='utf-8', mode='r') as f_entrada, \
         open(csvDuplicadasRemovidas, mode='w', newline='', encoding='utf-8') as f_saida:

        leitor = csv.DictReader(f_entrada, delimiter=';')

        escritor = csv.DictWriter(f_saida, delimiter=';', fieldnames=COLUNAS)
        escritor.writeheader()

        for linha in leitor:
            contagemTotal += 1
            h = hashDaLinha(linha)

            if h not in hashesVistos:
                hashesVistos.add(h)
                contagemMantidas += 1
                escritor.writerow(linha)
            else:
                contagemDuplicadas += 1
            if contagemTotal % intervaloFlush == 0:
                f_saida.flush()

    tempo_total = time.time() - inicio
    print()
    print(f'linhas lidas {contagemTotal}')
    print(f'linhas mantidas {contagemMantidas}')
    print(f'linhas duplicadas removidas {contagemDuplicadas}')
    print(f'tempo total {tempo_total:.1f} s')

if __name__ == '__main__':
    main()



















