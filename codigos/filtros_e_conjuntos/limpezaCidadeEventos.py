import csv
import os
import re
import time

csvEntrada = r''
saidaCSV = r''

csvCidadeFiltrada = os.path.join(saidaCSV, 'csvFiltro3.csv')

intervaloFlush = 500000
COLUNACIDADE = 'CIDADE-DO-EVENTO'
COLUNACIDADELIMPA = 'CIDADE-DO-EVENTO-LIMPA' #só para teste inicial

regexCidade = re.compile(r'^[^\W\d_]+(?:\s+[^\W\d_]+)*', re.UNICODE)

def limparCidade(texto: str) -> str:
    texto = texto.strip()
    if texto == '':
        return ''
    encontrado = regexCidade.match(texto)
    return encontrado.group(0).strip() if encontrado else ''

def main():
    os.makedirs(saidaCSV, exist_ok=True)
    inicio = time.time()

    contagemTotal = 0
    contagemAlterada = 0
    contagemVazia = 0

    with open(csvEntrada, mode='r', newline='', encoding='utf-8') as f_entrada, \
            open(csvCidadeFiltrada, mode='w', newline='', encoding='utf-8') as f_saida:

        leitor = csv.reader(f_entrada, delimiter=';')
        escritor = csv.writer(f_saida, delimiter=';')

        cabecalho = next(leitor)
        indiceCidade = cabecalho.index(COLUNACIDADE)
        escritor.writerow(cabecalho)

        for linha in leitor:
            contagemTotal += 1

            cidadeOriginal = linha[indiceCidade]
            cidadeLimpa = limparCidade(cidadeOriginal)

            linha[indiceCidade] = cidadeLimpa
            escritor.writerow(linha)

            if contagemTotal % intervaloFlush == 0:
                f_saida.flush()

    tempo_total = time.time() - inicio
    print()
    print(f'{contagemTotal} linhas')
    print(f'tempo total: {tempo_total:.1f} s')


if __name__ == '__main__':
    main()