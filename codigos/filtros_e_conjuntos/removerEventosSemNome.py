import csv
import os
import time

csvEntrada = r''
saidaCSV = r''

csvFiltrado = os.path.join(saidaCSV, 'csvFiltradoEventosSemNome.csv')

intervaloLog = 5000
intervaloFlush = 500000

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

def nomeEventoVazio(linha: dict) -> bool:
    nome = linha.get('NOME-DO-EVENTO', '')
    return nome is None or nome.strip() == ''

def main():
    os.makedirs(saidaCSV, exist_ok=True)
    inicio = time.time()
    contagemTotal = 0
    contagemMantidas = 0
    contagemDescartadas = 0

    with open(csvEntrada, mode='r', newline='', encoding='utf-8') as f_entrada, \
            open(csvFiltrado, mode='w', newline='', encoding='utf-8') as f_saida:

        leitor = csv.DictReader(f_entrada, delimiter=';')
        escritor = csv.DictWriter(f_saida, delimiter=';', fieldnames=COLUNAS)
        escritor.writeheader()

        for linha in leitor:
            contagemTotal += 1

            if nomeEventoVazio(linha):
                contagemDescartadas += 1
            else:
                contagemMantidas += 1
                escritor.writerow(linha)

            if contagemTotal % intervaloFlush == 0:
                f_saida.flush()


    tempo_total = time.time() - inicio
    print()
    print(f'linhas lidas {contagemTotal}')
    print(f'linhas mantidas {contagemMantidas}')
    print(f'linhas descartadas {contagemDescartadas}')
    print(f'tempo total {tempo_total:.1f} s')
    print()

if __name__ == '__main__':
                main()
















