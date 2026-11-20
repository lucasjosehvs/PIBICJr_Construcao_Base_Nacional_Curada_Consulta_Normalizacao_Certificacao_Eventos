import csv

# --- caminhos ---
caminhoEntrada = r'F:\ProjetoMagela\CSVMagela\cincomilprimeiraslinhas.csv'
caminhoSaida   = r'F:\ProjetoMagela\CSVMagela\exemplosLinhas.csv'
DELIMITADOR = ';'

# Limite para teste rápido antes do full run (None = processa tudo)
LIMITE_TESTE = None

# --- critério de descarte ---
# Uma linha é descartada se TODOS os campos abaixo estiverem vazios simultaneamente.
# Qualquer um preenchido é suficiente para manter o registro.
#
# Racional:
#   NOME-DO-EVENTO      → identificador primário do evento
#   LOCAL-DO-EVENTO     → endereço/espaço físico concreto
#   CIDADE-DO-EVENTO    → localização geográfica
#   INSTITUICAO-PROMOTORA → entidade responsável pelo evento
#
# ANO-DO-EVENTO é intencionalmente excluído do critério:
#   100% dos registros têm ano preenchido, portanto nunca discrimina nada.
#
# Nota sobre ORGANIZACAO-DE-EVENTO:
#   Esse tipo nunca possui NOME-DO-EVENTO por limitação estrutural do schema XML
#   do Lattes (o atributo simplesmente não existe em DETALHAMENTO-DA-ORGANIZACAO-DE-EVENTO).
#   Registros desse tipo são mantidos se tiverem LOCAL, CIDADE ou INSTITUICAO preenchidos.
#   Registros sem nenhum dos 4 campos são descartados por não conterem dado identificador.

CAMPOS_CHAVE = [
    'NOME-DO-EVENTO',
    'LOCAL-DO-EVENTO',
    'CIDADE-DO-EVENTO',
    'INSTITUICAO-PROMOTORA',
]


def main():
    contagemTotal    = 0
    contagemMantidas = 0
    removidasPorTipo = {}

    with open(caminhoEntrada, mode='r', newline='', encoding='utf-8') as f_in, \
         open(caminhoSaida,   mode='w', newline='', encoding='utf-8') as f_out:

        leitor   = csv.reader(f_in, delimiter=DELIMITADOR)
        escritor = csv.writer(f_out, delimiter=DELIMITADOR)

        cabecalho = next(leitor)
        escritor.writerow(cabecalho)

        # Mapeia nome da coluna → índice (robusto a reordenações futuras do CSV)
        indice  = {coluna: i for i, coluna in enumerate(cabecalho)}
        idxChave = [indice[c] for c in CAMPOS_CHAVE]
        idxTipo  = indice['TIPO-REGISTRO']

        for linha in leitor:
            contagemTotal += 1

            # Mantém se ao menos 1 campo chave estiver preenchido
            if any(linha[i].strip() for i in idxChave):
                escritor.writerow(linha)
                contagemMantidas += 1
            else:
                tipo = linha[idxTipo]
                removidasPorTipo[tipo] = removidasPorTipo.get(tipo, 0) + 1

            if contagemTotal % 2_000_000 == 0:
                print(f'{contagemTotal:>12} linhas processadas...')

            if LIMITE_TESTE is not None and contagemTotal >= LIMITE_TESTE:
                print(f'--- limite de teste ({LIMITE_TESTE}) atingido ---')
                break

    removidas = contagemTotal - contagemMantidas
    print(f'\ntotal lido:  {contagemTotal}')
    print(f'mantidas:    {contagemMantidas}')
    print(f'removidas:   {removidas}')
    print('\nremovidas por TIPO-REGISTRO:')
    for tipo, qtd in sorted(removidasPorTipo.items(), key=lambda x: -x[1]):
        pct = 100 * qtd / contagemTotal if contagemTotal else 0
        print(f'  {tipo:<48} {qtd:>8}  ({pct:.2f}% do total)')


if __name__ == '__main__':
    main()
