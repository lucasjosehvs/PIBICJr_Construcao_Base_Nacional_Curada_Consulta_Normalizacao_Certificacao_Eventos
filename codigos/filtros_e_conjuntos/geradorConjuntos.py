import csv
import os
import time

csvEntrada = r''
saidaCSV = r''

csvConjunto1 = os.path.join(saidaCSV, 'Conjunto1.csv')
csvConjunto2 = os.path.join(saidaCSV, 'Conjunto2.csv')
csvConjunto3 = os.path.join(saidaCSV, 'Conjunto3.csv')
csvConjunto4 = os.path.join(saidaCSV, 'Conjunto4.csv')

intervaloFlush = 5000
separador = '|'

def main():
    os.makedirs(saidaCSV, exist_ok=True)
    inicio = time.time()
    contagemTotal = 0

    with open(csvEntrada, mode='r', newline='', encoding='utf-8') as f_entrada, \
        open(csvConjunto1, mode='w', newline='', encoding='utf-8') as f1, \
        open(csvConjunto2, mode='w', newline='', encoding='utf-8') as f2, \
        open(csvConjunto3, mode='w', newline='', encoding='utf-8') as f3, \
        open(csvConjunto4, mode='w', newline='', encoding='utf-8') as f4:

        leitor = csv.reader(f_entrada, delimiter=';')
        cabecalho = next(leitor)

        indiceNome = cabecalho.index('NOME-DO-EVENTO')
        indiceAno = cabecalho.index('ANO-DO-EVENTO')
        indicePais = cabecalho.index('PAIS-DO-EVENTO')
        indiceCidade = cabecalho.index('CIDADE-DO-EVENTO')

        f1.write('NOME-DO-EVENTO\n')
        f2.write('NOME-DO-EVENTO|ANO-DO-EVENTO\n')
        f3.write('NOME-DO-EVENTO|ANO-DO-EVENTO|PAIS-DO-EVENTO\n')
        f4.write('NOME-DO-EVENTO|ANO-DO-EVENTO|PAIS-DO-EVENTO|CIDADE-DO-EVENTO\n')

        for linha in leitor:
            contagemTotal += 1

            nome = linha[indiceNome]
            ano = linha[indiceAno]
            pais = linha[indicePais]
            cidade = linha[indiceCidade]

            chave1 = nome
            chave2 = chave1 + separador + ano
            chave3 = chave2 + separador + pais
            chave4 = chave3 + separador + cidade

            f1.write(chave1 + '\n')
            f2.write(chave2 + '\n')
            f3.write(chave3 + '\n')
            f4.write(chave4 + '\n')

            if contagemTotal % intervaloFlush == 0:
                for f in (f1, f2, f3, f4):
                    f.flush()

    tempo_total = time.time() - inicio
    print()
    print(f'{contagemTotal} linhas ')
    print(f'tempo total {tempo_total:.1f} s')
    print()

if __name__ == '__main__':
    main()